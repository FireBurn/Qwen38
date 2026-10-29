from pathlib import Path
import json,subprocess,hashlib
p=Path(__file__).resolve().parent;q=p.parent/'q3-pad112';s=(q/'production-probe.cpp').read_text();s=s[:s.index(' unsigned cases=0;')]
s=s.replace('VkPipeline pipes[6];const char*names[]={"native","pad16","pad32","native","pad16","pad32"};','VkPipeline pipes[5];const char*names[]={"pad16","pair","pad16","pair","swiglu_ref"};').replace('i<6;++i','i<5;++i').replace('names[i]+"_subgroup_no_shmem.spv"','names[i]+(i==4?".spv":"_subgroup_no_shmem.spv")').replace('values[]={64,uint32_t(i/3+1),uint32_t(i/3+1)}','values[]={64,uint32_t(i%2?2:i/2+1),uint32_t(i/2+1)}').replace('pi.stage.pSpecializationInfo=&spec;','pi.stage.pSpecializationInfo=i==4?nullptr:&spec;').replace('i/3+1','i/2+1').replace('range{VK_SHADER_STAGE_COMPUTE_BIT,0,52}','range{VK_SHADER_STAGE_COMPUTE_BIT,0,128}')
s+=r'''
 auto divmagic=[](uint32_t d,uint32_t&mp,uint32_t&L){L=0;while((uint32_t(1)<<L)<d)++L;mp=uint32_t((uint64_t(1)<<32)*((uint64_t(1)<<L)-d)/d+1);};
 unsigned cases=0;
 for(uint32_t cols:{1u,2u})for(uint32_t k:{256u,512u,1024u,4096u,5120u,17408u})for(uint32_t rows:{1u,2u,3u,4u,7u,15u}){
  size_t blocks=rows*(k/256),nb=cols*(k/128)*144,nout=rows*cols;
  Buffer bufs[]={alloc(blocks*112),alloc(blocks*112),alloc(nb),alloc(nout*4),alloc(nout*4),alloc(nout*4),alloc(nout*4),alloc(4)};
  VkDescriptorPoolSize dps{VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,20};VkDescriptorPoolCreateInfo dpi{VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO};dpi.maxSets=4;dpi.poolSizeCount=1;dpi.pPoolSizes=&dps;VkDescriptorPool dp;vkcheck(vkCreateDescriptorPool(dev,&dpi,nullptr,&dp),"descriptor pool");VkDescriptorSet sets[4];VkDescriptorSetLayout ls[]={layout,layout,layout,layout};VkDescriptorSetAllocateInfo da{VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO};da.descriptorPool=dp;da.descriptorSetCount=4;da.pSetLayouts=ls;vkcheck(vkAllocateDescriptorSets(dev,&da,sets),"descriptor sets");
  for(int phase=0;phase<4;++phase){
   for(unsigned which=0;which<2;++which)for(size_t ib=0;ib<blocks;++ib){auto*a=bufs[which].ptr+256+ib*112;for(int j=0;j<108;++j)a[j]=rnd()&255;_Float16 d=phase==3&&ib%3==0?(_Float16)0:(_Float16)((ib%2?-1.f:1.f)/512.f);memcpy(a+108,&d,2);a[110]=a[111]=0;}
   auto*y=bufs[2].ptr+256;memset(y,0,nb);std::vector<int>acts(cols*k);
   for(uint32_t c=0;c<cols;++c)for(uint32_t ib=0;ib<k/32;++ib){int sum=0;for(int j=0;j<32;++j){int v=phase==0?0:phase==1?((ib%2)?127:-127):phase==2?int(rnd()%255)-127:int((ib*32+j)%9)-4;acts[c*k+ib*32+j]=v;sum+=v;y[(c*k/128+ib/4)*144+16+(ib%4)*32+j]=uint8_t(v);}_Float16 d=(_Float16)(1.f/16.f),sd=(_Float16)(sum/16.f);size_t off=(c*k/128+ib/4)*144+(ib%4)*4;memcpy(y+off,&d,2);memcpy(y+off+2,&sd,2);}
   std::vector<std::vector<unsigned char>> saved;for(int z=0;z<3;++z)saved.emplace_back(bufs[z].ptr+256,bufs[z].ptr+bufs[z].size-256);
   std::vector<std::vector<float>>oracle(2,std::vector<float>(nout));
   for(unsigned which=0;which<2;++which)for(uint32_t c=0;c<cols;++c)for(uint32_t row=0;row<rows;++row){double total=0;for(uint32_t x=0;x<k;++x){const auto*w=saved[which].data()+(row*(k/256)+x/256)*112;uint32_t sub=(x%256)/32,half=(x%32)/16,iqs=half*4,iqsk=sub*8+iqs,qi=(iqsk/32)*8+iqsk%8,shift=(iqsk%32/8)*2,hs=iqsk/8,word=(x%16)/4,byte=x%4;int q=((w[32+(qi+word)*4+byte]>>shift)&3)+4*((w[(iqs+word)*4+byte]>>hs)&1)-4;uint32_t is=iqsk/4;int scale=(((w[96+is%8]>>(4*(is/8)))&15)|(((w[104+is%4]>>(2*(is/4)))&3)<<4))-32;_Float16 d;memcpy(&d,w+108,2);total+=double(q)*scale*double(d)*acts[c*k+x]/16.0;}oracle[which][c*rows+row]=float(total);}
   for(unsigned order=0;order<2;++order){
    for(int z=3;z<7;++z)memset(bufs[z].ptr+256,0xa5,nout*4);
    int idx[4][5]={{int(order),2,3,7,7},{int(1-order),2,4,7,7},{3,4,5,7,7},{int(order),2,6,int(1-order),7}};
    for(int d=0;d<4;++d){VkDescriptorBufferInfo db[5];VkWriteDescriptorSet wr[5]{};for(int j=0;j<5;++j){auto&bf=bufs[idx[d][j]];db[j]={bf.b,256,bf.size-512};wr[j]={VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET};wr[j].dstSet=sets[d];wr[j].dstBinding=j;wr[j].descriptorCount=1;wr[j].descriptorType=VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;wr[j].pBufferInfo=&db[j];}vkUpdateDescriptorSets(dev,5,wr,0,nullptr);}
    vkcheck(vkResetCommandBuffer(cb,0),"reset");VkCommandBufferBeginInfo bi{VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};vkcheck(vkBeginCommandBuffer(cb,&bi),"begin");VkMemoryBarrier host{VK_STRUCTURE_TYPE_MEMORY_BARRIER};host.srcAccessMask=VK_ACCESS_HOST_WRITE_BIT;host.dstAccessMask=VK_ACCESS_SHADER_READ_BIT|VK_ACCESS_SHADER_WRITE_BIT;vkCmdPipelineBarrier(cb,VK_PIPELINE_STAGE_HOST_BIT,VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,0,1,&host,0,nullptr,0,nullptr);
    uint32_t pc[]={k,k,k,rows,k*rows,k,rows,0,0,1,1,1,1};
    for(int step=0;step<4;++step){
     vkCmdBindDescriptorSets(cb,VK_PIPELINE_BIND_POINT_COMPUTE,pl,0,1,&sets[step],0,nullptr);
     if(step==2){uint32_t gp[]={uint32_t(nout),rows,rows,2,0,0,1,rows,uint32_t(nout),uint32_t(nout),1,rows,uint32_t(nout),uint32_t(nout),1,rows,uint32_t(nout),uint32_t(nout),cols,1,0,0,0,0,0,0,0};divmagic(nout,gp[21],gp[22]);divmagic(nout,gp[23],gp[24]);divmagic(rows,gp[25],gp[26]);vkCmdPushConstants(cb,pl,VK_SHADER_STAGE_COMPUTE_BIT,0,sizeof(gp),gp);vkCmdBindPipeline(cb,VK_PIPELINE_BIND_POINT_COMPUTE,pipes[4]);uint32_t groups=(nout+511)/512;require(groups<=16,"GLU probe bounded");vkCmdDispatch(cb,groups,1,1);}
     else{pc[3]=step==3?2*rows:rows;vkCmdPushConstants(cb,pl,VK_SHADER_STAGE_COMPUTE_BIT,0,sizeof(pc),pc);vkCmdBindPipeline(cb,VK_PIPELINE_BIND_POINT_COMPUTE,pipes[(cols-1)*2+(step==3)]);uint32_t groups=step==3?rows:(rows+cols-1)/cols;require(groups<=16,"matrix probe bounded");vkCmdDispatch(cb,groups,1,1);}
     VkMemoryBarrier dep{VK_STRUCTURE_TYPE_MEMORY_BARRIER};dep.srcAccessMask=VK_ACCESS_SHADER_WRITE_BIT;dep.dstAccessMask=VK_ACCESS_SHADER_READ_BIT|VK_ACCESS_SHADER_WRITE_BIT;vkCmdPipelineBarrier(cb,VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,0,1,&dep,0,nullptr,0,nullptr);
    }
    VkMemoryBarrier end{VK_STRUCTURE_TYPE_MEMORY_BARRIER};end.srcAccessMask=VK_ACCESS_SHADER_WRITE_BIT;end.dstAccessMask=VK_ACCESS_HOST_READ_BIT;vkCmdPipelineBarrier(cb,VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,VK_PIPELINE_STAGE_HOST_BIT,0,1,&end,0,nullptr,0,nullptr);vkcheck(vkEndCommandBuffer(cb),"end");VkSubmitInfo sub{VK_STRUCTURE_TYPE_SUBMIT_INFO};sub.commandBufferCount=1;sub.pCommandBuffers=&cb;vkcheck(vkQueueSubmit(queue,1,&sub,fence),"submit");vkcheck(vkWaitForFences(dev,1,&fence,VK_TRUE,10000000000ull),"wait");vkResetFences(dev,1,&fence);
    for(auto&bf:bufs)for(size_t j=0;j<256;++j)require(bf.ptr[j]==0xa5&&bf.ptr[bf.size-256+j]==0xa5,"buffer guard");for(int z=0;z<3;++z)require(!memcmp(saved[z].data(),bufs[z].ptr+256,saved[z].size()),"input unchanged");
    for(int mat=0;mat<2;++mat){auto*out=(float*)(bufs[3+mat].ptr+256);for(size_t j=0;j<nout;++j)require(std::isfinite(out[j])&&std::abs(out[j]-oracle[mat?1-order:order][j])<=.001f+.00001f*std::abs(oracle[mat?1-order:order][j]),"native matrix CPU oracle");}
    auto*ref=(float*)(bufs[5].ptr+256),*cand=(float*)(bufs[6].ptr+256);for(size_t j=0;j<nout;++j){if(memcmp(ref+j,cand+j,4)){uint32_t a,b;memcpy(&a,ref+j,4);memcpy(&b,cand+j,4);fprintf(stderr,"MISMATCH k=%u rows=%u cols=%u phase=%d order=%u j=%zu ref=%a cand=%a bits=%08x/%08x\n",k,rows,cols,phase,order,j,ref[j],cand[j],a,b);exit(2);}require(std::isfinite(cand[j]),"finite GLU output");}
    printf("PAIR_EXACT k=%u rows=%u cols=%u phase=%d order=%u groups=%u outputs=%zu\n",k,rows,cols,phase,order,rows,nout);fflush(stdout);++cases;
   }
  }
  vkDestroyDescriptorPool(dev,dp,nullptr);for(auto&bf:bufs){vkUnmapMemory(dev,bf.m);vkDestroyBuffer(dev,bf.b,nullptr);vkFreeMemory(dev,bf.m,nullptr);}
 }
 printf("PAIR_ALL_EXACT cases=%u\n",cases);vkDeviceWaitIdle(dev);for(auto pipe:pipes)vkDestroyPipeline(dev,pipe,nullptr);vkDestroyFence(dev,fence,nullptr);vkDestroyCommandPool(dev,pool,nullptr);vkDestroyPipelineLayout(dev,pl,nullptr);vkDestroyDescriptorSetLayout(dev,layout,nullptr);vkDestroyDevice(dev,nullptr);vkDestroyInstance(inst,nullptr);
}
'''
(p/'probe.cpp').write_text(s);cmd=['clang++','-std=c++17','-O2',str(p/'probe.cpp'),'-lvulkan','-o',str(p/'operator_bench')];subprocess.run(cmd,check=True)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'probe-build.json').write_text(json.dumps(dict(command=cmd,source_sha256=sha(p/'probe.cpp'),binary_sha256=sha(p/'operator_bench')),indent=2)+'\n');print('PAIR_OPERATOR_PROBE_BUILT')
