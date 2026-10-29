from pathlib import Path
import subprocess,json,hashlib
p=Path(__file__).resolve().parent;s=(p.parent/'q3-pad112/probe.cpp').read_text()
s=s.replace('q3-pad112','q6-pad212').replace('values[]={64,3,','values[]={64,2,').replace('47u','31u').replace('blocks*110','blocks*210').replace('blocks*112','blocks*212').replace('nb=cols*(k/128)*144','nb=cols*k*4').replace('for(int phase=0;phase<4;++phase)','for(int phase=0;phase<6;++phase)')
a=s.index('   for(size_t ib=0;ib<blocks;++ib)');z=s.index('   auto savedA=',a)
s=s[:a]+r'''
   for(size_t ib=0;ib<blocks;++ib){for(int j=0;j<208;++j)a[ib*210+j]=rnd()&255;_Float16 d=phase==3&&ib%3==0?(_Float16)0:(_Float16)((ib%2?-1.f:1.f)/512.f);memcpy(a+ib*210+208,&d,2);memcpy(pad+ib*212,a+ib*210,210);pad[ib*212+210]=0;pad[ib*212+211]=0;}
   auto*fy=(float*)y;
   for(uint32_t c=0;c<cols;++c)for(uint32_t x=0;x<k;++x){int v=phase==0?0:phase==1?((x/32%2)?127:-127):phase==2?int(rnd()%255)-127:int(x%9)-4;fy[c*k+x]=v/16.f;if(phase==4)fy[c*k+x]=std::sin(float(x))*129.125f;if(phase==5)fy[c*k+x]=(x%2)?-0.f:0.f;}
'''+s[z:]
a=s.index('   std::vector<float>oracle(');z=s.index('   std::vector<unsigned char>reference;',a)
s=s[:a]+r'''
   std::vector<float>oracle(rows*cols);for(uint32_t c=0;c<cols;++c)for(uint32_t row=0;row<rows;++row){double total=0;for(uint32_t x=0;x<k;++x){const auto*w=cpu_weights+(row*(k/256)+x/256)*210;uint32_t local=x%256,half=local/128,l=local%32,section=(local%128)/32;int lo=(w[half*64+l+(section%2)*32]>>(section>=2?4:0))&15;int hi=(w[128+half*32+l]>>(section*2))&3;int q=(lo|(hi<<4))-32;int scale=int((int8_t)w[192+local/16]);_Float16 d;memcpy(&d,w+208,2);total+=double(q)*scale*double(d)*fy[c*k+x];}oracle[c*rows+row]=float(total);}
'''+s[z:]
s=s.replace('uint32_t groups=(rows+2)/3','uint32_t groups=(rows+1)/2').replace('Q3_PAD112_ALL_EXACT','Q6_PAD212_ALL_EXACT')
# max rows31 =>16WG, rm_kq2 matches RDNA4 native float path.
(p/'probe.cpp').write_text(s)
cmd=['clang++','-std=c++17','-O2',str(p/'probe.cpp'),'-lvulkan','-o',str(p/'operator_bench')];subprocess.run(cmd,check=True)
(p/'probe-build.json').write_text(json.dumps(dict(command=cmd,source_sha256=hashlib.sha256(s.encode()).hexdigest(),binary_sha256=hashlib.sha256((p/'operator_bench').read_bytes()).hexdigest(),scope='Nonpersistent native/padded Q6 float shader probe, native rm_kq2, C1/C2,16WG maximum; build only'),indent=2)+'\n')
