from pathlib import Path
import subprocess,json,hashlib
p=Path(__file__).resolve().parent;(p/'timing-bin').mkdir(exist_ok=True)
s=(p/'probe.cpp').read_text();s=s[:s.index(' unsigned cases=0;')];s='#include <time.h>\n'+s
s+=r'''
 VkPhysicalDeviceProperties props;vkGetPhysicalDeviceProperties(pd,&props);
 VkQueryPoolCreateInfo qpi{VK_STRUCTURE_TYPE_QUERY_POOL_CREATE_INFO};qpi.queryType=VK_QUERY_TYPE_TIMESTAMP;qpi.queryCount=2;VkQueryPool qp;vkcheck(vkCreateQueryPool(dev,&qpi,nullptr,&qp),"querypool");
 auto now_ns=[](){timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return uint64_t(t.tv_sec)*1000000000ull+t.tv_nsec;};
 auto sync=[&](VkAccessFlags src,VkAccessFlags dst){VkMemoryBarrier b{VK_STRUCTURE_TYPE_MEMORY_BARRIER};b.srcAccessMask=src;b.dstAccessMask=dst;vkCmdPipelineBarrier(cb,VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,0,1,&b,0,nullptr,0,nullptr);};
 for(uint32_t cols:{1u,2u})for(uint32_t replicas:{1u,8u}){
  const uint32_t k=5120,rows=17408;size_t blocks=rows*(k/256),weight_bytes=blocks*112,stride=(weight_bytes+255)&~size_t(255),nb=cols*(k/128)*144,nout=rows*cols;
  Buffer bufs[]={alloc(stride*replicas),alloc(stride*replicas),alloc(nb),alloc(nout*4),alloc(nout*4),alloc(nout*4),alloc(nout*4),alloc(4)};
  std::vector<unsigned char>a(weight_bytes),b(weight_bytes),y(nb);
  for(auto*data:{&a,&b})for(size_t ib=0;ib<blocks;++ib){auto*w=data->data()+ib*112;for(int j=0;j<108;++j)w[j]=rnd()&255;_Float16 d=(_Float16)((ib%2?-1.f:1.f)/512.f);memcpy(w+108,&d,2);w[110]=w[111]=0;}
  for(uint32_t r=0;r<replicas;++r){memcpy(bufs[0].ptr+256+r*stride,a.data(),weight_bytes);memcpy(bufs[1].ptr+256+r*stride,b.data(),weight_bytes);}
  for(uint32_t c=0;c<cols;++c)for(uint32_t ib=0;ib<k/32;++ib){int sum=0;for(int j=0;j<32;++j){int v=int(rnd()%255)-127;sum+=v;y[(c*k/128+ib/4)*144+16+(ib%4)*32+j]=uint8_t(v);}_Float16 d=(_Float16)(1.f/16.f),sd=(_Float16)(sum/16.f);size_t off=(c*k/128+ib/4)*144+(ib%4)*4;memcpy(y.data()+off,&d,2);memcpy(y.data()+off+2,&sd,2);}memcpy(bufs[2].ptr+256,y.data(),nb);
  VkDescriptorPoolSize dps{VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,replicas*20};VkDescriptorPoolCreateInfo dpi{VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO};dpi.maxSets=replicas*4;dpi.poolSizeCount=1;dpi.pPoolSizes=&dps;VkDescriptorPool dp;vkcheck(vkCreateDescriptorPool(dev,&dpi,nullptr,&dp),"descriptorpool");std::vector<VkDescriptorSet>sets(replicas*4);std::vector<VkDescriptorSetLayout>ls(replicas*4,layout);VkDescriptorSetAllocateInfo da{VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO};da.descriptorPool=dp;da.descriptorSetCount=ls.size();da.pSetLayouts=ls.data();vkcheck(vkAllocateDescriptorSets(dev,&da,sets.data()),"sets");
  int idx[4][5]={{0,2,3,7,7},{1,2,4,7,7},{3,4,5,7,7},{0,2,6,1,7}};
  for(uint32_t r=0;r<replicas;++r)for(int d=0;d<4;++d){VkDescriptorBufferInfo db[5];VkWriteDescriptorSet wr[5]{};for(int j=0;j<5;++j){int z=idx[d][j];auto&bf=bufs[z];db[j]={bf.b,z<2?256+r*stride:256,z<2?weight_bytes:bf.size-512};wr[j]={VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET};wr[j].dstSet=sets[r*4+d];wr[j].dstBinding=j;wr[j].descriptorCount=1;wr[j].descriptorType=VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;wr[j].pBufferInfo=&db[j];}vkUpdateDescriptorSets(dev,5,wr,0,nullptr);}
  uint32_t pc[]={k,k,k,rows,0,k,rows,0,0,1,1,1,1};uint32_t gp[]={uint32_t(nout),rows,rows,2,0,0,1,rows,uint32_t(nout),uint32_t(nout),1,rows,uint32_t(nout),uint32_t(nout),1,rows,uint32_t(nout),uint32_t(nout),cols,1,0,0,0,0,0,0,0};divmagic(nout,gp[21],gp[22]);divmagic(nout,gp[23],gp[24]);divmagic(rows,gp[25],gp[26]);
  auto record=[&](uint32_t mode,uint32_t n,uint32_t start,bool timed){
   vkcheck(vkResetCommandBuffer(cb,0),"reset");VkCommandBufferBeginInfo bi{VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};vkcheck(vkBeginCommandBuffer(cb,&bi),"begin");VkMemoryBarrier host{VK_STRUCTURE_TYPE_MEMORY_BARRIER};host.srcAccessMask=VK_ACCESS_HOST_WRITE_BIT;host.dstAccessMask=VK_ACCESS_SHADER_READ_BIT|VK_ACCESS_SHADER_WRITE_BIT;vkCmdPipelineBarrier(cb,VK_PIPELINE_STAGE_HOST_BIT,VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,0,1,&host,0,nullptr,0,nullptr);
   if(timed){vkCmdResetQueryPool(cb,qp,0,2);vkCmdWriteTimestamp(cb,VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,qp,0);}
   for(uint32_t i=0;i<n;++i){auto*ds=sets.data()+((start+i)%replicas)*4;
    if(mode==0){
     pc[3]=rows;vkCmdBindPipeline(cb,VK_PIPELINE_BIND_POINT_COMPUTE,pipes[(cols-1)*2]);vkCmdPushConstants(cb,pl,VK_SHADER_STAGE_COMPUTE_BIT,0,sizeof(pc),pc);
     // Independent gate/up can overlap, as in the native command profile.
     for(int j=0;j<2;++j){vkCmdBindDescriptorSets(cb,VK_PIPELINE_BIND_POINT_COMPUTE,pl,0,1,ds+j,0,nullptr);vkCmdDispatch(cb,(rows+cols-1)/cols,1,1);}
     sync(VK_ACCESS_SHADER_WRITE_BIT,VK_ACCESS_SHADER_READ_BIT);
     vkCmdBindPipeline(cb,VK_PIPELINE_BIND_POINT_COMPUTE,pipes[4]);vkCmdPushConstants(cb,pl,VK_SHADER_STAGE_COMPUTE_BIT,0,sizeof(gp),gp);vkCmdBindDescriptorSets(cb,VK_PIPELINE_BIND_POINT_COMPUTE,pl,0,1,ds+2,0,nullptr);vkCmdDispatch(cb,(nout+511)/512,1,1);
    }else{pc[3]=2*rows;vkCmdBindPipeline(cb,VK_PIPELINE_BIND_POINT_COMPUTE,pipes[(cols-1)*2+1]);vkCmdPushConstants(cb,pl,VK_SHADER_STAGE_COMPUTE_BIT,0,sizeof(pc),pc);vkCmdBindDescriptorSets(cb,VK_PIPELINE_BIND_POINT_COMPUTE,pl,0,1,ds+3,0,nullptr);vkCmdDispatch(cb,rows,1,1);}
    sync(VK_ACCESS_SHADER_READ_BIT|VK_ACCESS_SHADER_WRITE_BIT,VK_ACCESS_SHADER_READ_BIT|VK_ACCESS_SHADER_WRITE_BIT);
   }
   if(timed)vkCmdWriteTimestamp(cb,VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,qp,1);VkMemoryBarrier end{VK_STRUCTURE_TYPE_MEMORY_BARRIER};end.srcAccessMask=VK_ACCESS_SHADER_WRITE_BIT;end.dstAccessMask=VK_ACCESS_HOST_READ_BIT;vkCmdPipelineBarrier(cb,VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,VK_PIPELINE_STAGE_HOST_BIT,0,1,&end,0,nullptr,0,nullptr);vkcheck(vkEndCommandBuffer(cb),"end");
  };
  auto submit=[&](){VkSubmitInfo sub{VK_STRUCTURE_TYPE_SUBMIT_INFO};sub.commandBufferCount=1;sub.pCommandBuffers=&cb;vkcheck(vkQueueSubmit(queue,1,&sub,fence),"submit");vkcheck(vkWaitForFences(dev,1,&fence,VK_TRUE,10000000000ull),"wait");vkResetFences(dev,1,&fence);};
  for(uint32_t r=0;r<replicas;++r){record(0,1,r,false);submit();record(1,1,r,false);submit();require(!memcmp(bufs[5].ptr+256,bufs[6].ptr+256,nout*4),"full replica GLU outputs exact");}
  printf("PAIR_VALIDATED cols=%u replicas=%u outputs=%zu weight_bytes=%zu\n",cols,replicas,nout,2*weight_bytes*replicas);fflush(stdout);
  for(uint32_t mode=0;mode<2;++mode){record(mode,64,0,false);submit();}
  for(uint32_t block=0;block<6;++block)for(uint32_t arm=0;arm<4;++arm){uint32_t mode=(arm==1||arm==2)?1:0;if(block%2)mode=1-mode;record(mode,1024,0,true);uint64_t start=now_ns();printf("PAIR_ARM_BEGIN cols=%u replicas=%u block=%u arm=%u mode=%u ns=%llu\n",cols,replicas,block,arm,mode,(unsigned long long)start);fflush(stdout);submit();uint64_t finish=now_ns(),ticks[2];vkcheck(vkGetQueryPoolResults(dev,qp,0,2,sizeof(ticks),ticks,sizeof(uint64_t),VK_QUERY_RESULT_64_BIT|VK_QUERY_RESULT_WAIT_BIT),"timestamps");require(!memcmp(bufs[5].ptr+256,bufs[6].ptr+256,nout*4),"timed GLU output bytes exact");printf("PAIR_TIMING cols=%u replicas=%u block=%u arm=%u mode=%u repeats=1024 start_ns=%llu end_ns=%llu us=%.9f\n",cols,replicas,block,arm,mode,(unsigned long long)start,(unsigned long long)finish,double(ticks[1]-ticks[0])*props.limits.timestampPeriod/1000/1024);fflush(stdout);}
  for(auto&bf:bufs)for(size_t j=0;j<256;++j)require(bf.ptr[j]==0xa5&&bf.ptr[bf.size-256+j]==0xa5,"buffer guard");for(uint32_t r=0;r<replicas;++r){require(!memcmp(bufs[0].ptr+256+r*stride,a.data(),weight_bytes),"gate unchanged");require(!memcmp(bufs[1].ptr+256+r*stride,b.data(),weight_bytes),"up unchanged");}require(!memcmp(bufs[2].ptr+256,y.data(),nb),"activation unchanged");
  vkDestroyDescriptorPool(dev,dp,nullptr);for(auto&bf:bufs){vkUnmapMemory(dev,bf.m);vkDestroyBuffer(dev,bf.b,nullptr);vkFreeMemory(dev,bf.m,nullptr);}
 }
 printf("PAIR_TIMING_COMPLETE\n");vkDeviceWaitIdle(dev);vkDestroyQueryPool(dev,qp,nullptr);for(auto pipe:pipes)vkDestroyPipeline(dev,pipe,nullptr);vkDestroyFence(dev,fence,nullptr);vkDestroyCommandPool(dev,pool,nullptr);vkDestroyPipelineLayout(dev,pl,nullptr);vkDestroyDescriptorSetLayout(dev,layout,nullptr);vkDestroyDevice(dev,nullptr);vkDestroyInstance(inst,nullptr);
}
'''
(p/'timing.cpp').write_text(s);cmd=['clang++','-std=c++17','-O2',str(p/'timing.cpp'),'-lvulkan','-o',str(p/'timing-bin/operator_bench_timed')];subprocess.run(cmd,check=True)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'timing-build.json').write_text(json.dumps(dict(command=cmd,source_sha256=sha(p/'timing.cpp'),binary_sha256=sha(p/'timing-bin/operator_bench_timed')),indent=2)+'\n');print('PAIR_TIMING_BUILT')
