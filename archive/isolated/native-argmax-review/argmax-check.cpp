#include "llama.h"
#include "ggml-backend.h"
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
#include <fstream>
#include <cmath>
#include <limits>
static void check(bool x,const char*m){if(!x){fprintf(stderr,"FAIL %s\n",m);exit(2);}}
int main(int argc,char**argv){
 check(argc==2,"output binary");
 llama_backend_init();ggml_backend_t gpu=nullptr;
 for(size_t i=0;i<ggml_backend_dev_count();++i){auto d=ggml_backend_dev_get(i);if(ggml_backend_dev_type(d)==GGML_BACKEND_DEVICE_TYPE_GPU&&std::string(ggml_backend_dev_description(d)).find("R9700")!=std::string::npos){gpu=ggml_backend_dev_init(d,nullptr);break;}}check(gpu,"R9700 required");
 for(const char*key:{"EXPECTED_VK_BACKEND_PATH","EXPECTED_RADV_LIBRARY_PATH"}){const char*expected=getenv(key);check(expected,"expected mapping");std::ifstream maps("/proc/self/maps");std::string line;bool seen=false;while(std::getline(maps,line))if(line.find(expected)!=std::string::npos)seen=true;check(seen,"pinned library mapping missing");fprintf(stderr,"MAPPING_OK %s\n",expected);}

 FILE *file=fopen(argv[1],"wb");check(file,"output");int cases=0;
 for(int k:{1,2,3,31,32,33,63,64,65,127,255,256,257,1025,248320})for(int rows:{1,2,5})for(int pattern=0;pattern<14;++pattern){
  ggml_init_params ip={ggml_tensor_overhead()*32+ggml_graph_overhead_custom(32,false),nullptr,true};auto ctx=ggml_init(ip);auto graph=ggml_new_graph_custom(ctx,32,false);auto input=ggml_new_tensor_2d(ctx,GGML_TYPE_F32,k,rows);ggml_set_input(input);auto result=ggml_argmax(ctx,input);ggml_build_forward_expand(graph,result);auto buffer=ggml_backend_alloc_ctx_tensors(ctx,gpu);check(buffer,"case buffer");std::vector<float> data(size_t(k)*rows);
  for(int row=0;row<rows;++row){auto v=data.data()+size_t(row)*k;for(int i=0;i<k;++i)v[i]=float((i*17+row*13)%1009)/1009.f;
   if(pattern==0)v[(k/3+row)%k]=2.f;
   if(pattern==1)for(int i=0;i<k;++i)v[i]=0.f;
   if(pattern==2){v[1%k]=2.f;v[2%k]=2.f;}
   if(pattern==3){v[k/2]=2.f;v[k-1]=2.f;}
   if(pattern==4)for(int i=0;i<k;++i)v[i]=-INFINITY;
   if(pattern==5)for(int i=0;i<k;++i)v[i]=INFINITY;
   if(pattern==6)v[0]=NAN;
   if(pattern==7)v[k-1]=NAN;
   if(pattern==8)v[k/2]=NAN;
   if(pattern==9)for(int i=0;i<k;++i)v[i]=NAN;
   if(pattern==10)for(int i=0;i<k;++i)v[i]=i%2?0.f:-0.f;
   if(pattern==11)for(int i=0;i<k;++i)v[i]=(i%2?1.f:-1.f)*std::numeric_limits<float>::denorm_min();
   if(pattern==12)for(int i=0;i<k;++i)v[i]=-std::numeric_limits<float>::max();
   if(pattern==13){for(int i=0;i<k;++i)v[i]=float((i+row)%8);v[k/2]=INFINITY;v[k-1]=NAN;}
  }
  ggml_backend_tensor_set(input,data.data(),0,data.size()*sizeof(float));check(ggml_backend_graph_compute(gpu,graph)==GGML_STATUS_SUCCESS,"case compute");ggml_backend_synchronize(gpu);std::vector<int32_t> indices(rows);ggml_backend_tensor_get(result,indices.data(),0,rows*sizeof(int32_t));for(auto index:indices)check(index>=0&&index<k,"index bounds");uint32_t header[]={0x4152474du,uint32_t(k),uint32_t(rows),uint32_t(pattern)};check(fwrite(header,sizeof(header),1,file)==1,"header write");check(fwrite(indices.data(),sizeof(int32_t),rows,file)==size_t(rows),"indices write");++cases;ggml_backend_buffer_free(buffer);ggml_free(ctx);
 }
 check(fclose(file)==0,"close");printf("ARGMAX_CASES_EXACT_CAPTURE cases=%d rows=%d\n",cases,15*14*8);ggml_backend_free(gpu);llama_backend_free();
}
