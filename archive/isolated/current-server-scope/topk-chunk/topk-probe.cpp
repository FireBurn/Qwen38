#include "ggml.h"
#include "ggml-backend.h"
#include <dlfcn.h>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <cmath>
#include <limits>
#include <cstring>
#include <fstream>
#include <string>
static void require(bool b,const char* msg){if(!b){fprintf(stderr,"FAIL %s\n",msg);exit(2);}}
int main(int argc,char**argv){
 require(argc==5,"backend path, rows, pattern, output"); int rows=atoi(argv[2]),pattern=atoi(argv[3]);require(rows>=1&&rows<=5&&pattern>=0&&pattern<=3,"bounded arguments");
 void *lib=dlopen(argv[1],RTLD_NOW|RTLD_LOCAL);if(!lib){fprintf(stderr,"dlopen: %s\n",dlerror());return 2;}using reg_fn=ggml_backend_reg_t(*)();auto fn=(reg_fn)dlsym(lib,"ggml_backend_vk_reg");require(fn,"backend entry");auto reg=fn();ggml_backend_t gpu=nullptr;for(size_t i=0;i<ggml_backend_reg_dev_count(reg);++i){auto d=ggml_backend_reg_dev_get(reg,i);if(strstr(ggml_backend_dev_description(d),"R9700")){gpu=ggml_backend_dev_init(d,nullptr);break;}}require(gpu,"R9700");std::ifstream maps("/proc/self/maps");std::string line;while(std::getline(maps,line))if(line.find("vulkan_radeon")!=std::string::npos||line.find("libggml-vulkan")!=std::string::npos)fprintf(stderr,"MAP %s\n",line.c_str());
 const int n=248320,k=20;ggml_init_params ip={ggml_tensor_overhead()*32+ggml_graph_overhead_custom(32,false),nullptr,true};auto ctx=ggml_init(ip);require(ctx,"context");auto g=ggml_new_graph_custom(ctx,32,false);auto in=ggml_new_tensor_2d(ctx,GGML_TYPE_F32,n,rows);ggml_set_input(in);auto out=ggml_top_k(ctx,in,k);ggml_build_forward_expand(g,out);auto buf=ggml_backend_alloc_ctx_tensors(ctx,gpu);require(buf,"buffer");
 std::vector<float> data(size_t(n)*rows);for(int r=0;r<rows;r++)for(int i=0;i<n;i++){int rank=(i*17+r*113)%n;float v=float(rank);if(pattern==1)v=float(rank%31);if(pattern==2)v=(i%127==0?INFINITY:(i%251==0?-INFINITY:v));if(pattern==3)v=(i%137==0?NAN:(i%2?0.f:-0.f));data[size_t(r)*n+i]=v;}
 ggml_backend_tensor_set(in,data.data(),0,data.size()*sizeof(float));require(ggml_backend_graph_compute(gpu,g)==GGML_STATUS_SUCCESS,"compute");ggml_backend_synchronize(gpu);std::vector<int32_t> indices(rows*k);ggml_backend_tensor_get(out,indices.data(),0,indices.size()*sizeof(int32_t));for(auto i:indices)require(i>=0&&i<n,"index bounds");FILE*f=fopen(argv[4],"wb");require(f,"output");require(fwrite(indices.data(),sizeof(int32_t),indices.size(),f)==indices.size(),"write");require(fclose(f)==0,"close");printf("rows=%d pattern=%d count=%zu\n",rows,pattern,indices.size());ggml_backend_buffer_free(buf);ggml_free(ctx);ggml_backend_free(gpu);return 0;
}
