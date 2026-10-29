from pathlib import Path
import subprocess,json,hashlib
p=Path(__file__).resolve().parent
old=(p.parent/'q3-pad112/prepare_confirmation_timing.py').read_text();a=old.index("s+=r'''")+len("s+=r'''");z=old.index("'''\n(p/'confirmation-timing.cpp')",a);body=old[a:z]
s=(p/'probe.cpp').read_text().split(' uint32_t rng=')[0]
s=s.replace('memset(x.ptr,0xa5,x.size);','memset(x.ptr,0xa5,256);memset(x.ptr+x.size-256,0xa5,256);')
body=body.replace('nb=cols*(k/128)*144','nb=cols*k*4').replace('blocks*110','blocks*210').replace('blocks*112','blocks*212')
a=body.index('for(size_t ib=0;ib<blocks;++ib)');z=body.index('  for(unsigned r=0;',a)
body=body[:a]+'''for(size_t ib=0;ib<blocks;++ib){for(int j=0;j<208;++j)a[ib*210+j]=rnd()&255;_Float16 d=(_Float16)((ib%2?-1.f:1.f)/512.f);memcpy(a.data()+ib*210+208,&d,2);memcpy(pad.data()+ib*212,a.data()+ib*210,210);pad[ib*212+210]=pad[ib*212+211]=0;}
'''+body[z:]
a=body.index('  std::vector<unsigned char>y(nb);');z=body.index('  VkDescriptorPoolSize',a)
body=body[:a]+'''  std::vector<unsigned char>y(nb);for(uint32_t x=0;x<cols*k;++x){float v=(int(rnd()%255)-127)/16.f;memcpy(y.data()+x*4,&v,4);}memcpy(bufs[2].ptr+256,y.data(),nb);memset(bufs[4].ptr+256,0,4);
'''+body[z:]
body=body.replace('replicas*2','replicas*3').replace('mode<2','mode<3').replace('int idx[]={int(mode),2','unsigned weight=mode==0?0:1;int idx[]={int(weight),2').replace('r*strides[mode]','r*strides[weight]').replace('sizes[mode]','sizes[weight]').replace('pipes[(cols-1)*2+mode]','pipes[(cols-1)*3+mode]').replace('(rows+cols-1)/cols','(rows+1)/2')
a=body.index('  for(unsigned block=0;');z=body.index('  for(auto&bf:bufs)',a)
body=body[:a]+'''  for(unsigned block=0;block<3;++block)for(unsigned arm=0;arm<6;++arm){unsigned seq[]={0,1,2,2,1,0};unsigned mode=(seq[arm]+block)%3;record(mode,1024,0,true);printf("ARM_BEGIN k=%u rows=%u cols=%u replicas=%u block=%u arm=%u mode=%u\\n",k,rows,cols,replicas,block,arm,mode);fflush(stdout);submit();uint64_t ticks[2];vkcheck(vkGetQueryPoolResults(dev,qp,0,2,sizeof(ticks),ticks,sizeof(uint64_t),VK_QUERY_RESULT_64_BIT|VK_QUERY_RESULT_WAIT_BIT),"timestamps");double us=double(ticks[1]-ticks[0])*props.limits.timestampPeriod/1000/1024;printf("TIMING k=%u rows=%u cols=%u replicas=%u block=%u arm=%u mode=%u dispatches=1024 us=%.9f\\n",k,rows,cols,replicas,block,arm,mode,us);fflush(stdout);require(!memcmp(reference.data(),bufs[3].ptr+256,reference.size()),"timed output bytes exact");}
'''+body[z:]
body=body.replace('Q3_PAD112','Q6_PAD212')
s+=body;(p/'timing.cpp').write_text(s)
cmd=['clang++','-std=c++17','-O2',str(p/'timing.cpp'),'-lvulkan','-o',str(p/'operator_bench_timed')];subprocess.run(cmd,check=True)
(p/'timing-build.json').write_text(json.dumps(dict(command=cmd,source_sha256=hashlib.sha256(s.encode()).hexdigest(),binary_sha256=hashlib.sha256((p/'operator_bench_timed').read_bytes()).hexdigest()),indent=2)+'\n')
