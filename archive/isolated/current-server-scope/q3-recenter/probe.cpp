#include "ggml.h"
#include "ggml-backend.h"
#include <dlfcn.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <fstream>
#include <string>
#include <vector>
static void ck(bool v,const char*s){if(!v){fprintf(stderr,"FAIL %s\n",s);exit(2);}}
int main(int argc,char**argv){
 ck(argc==6,"backend output K M N");int k=atoi(argv[3]),m=atoi(argv[4]),n=atoi(argv[5]);ck(k==5120 && (m==64||m==17408) && (n==4||n==5),"bounded shapes");
 void*lib=dlopen(argv[1],RTLD_NOW|RTLD_LOCAL);if(!lib){fprintf(stderr,"dlopen %s\n",dlerror());return 2;}using regfn=ggml_backend_reg_t(*)();auto fn=(regfn)dlsym(lib,"ggml_backend_vk_reg");ck(fn,"backend registry");auto reg=fn();ggml_backend_t gpu=nullptr;for(size_t i=0;i<ggml_backend_reg_dev_count(reg);i++){auto d=ggml_backend_reg_dev_get(reg,i);if(strstr(ggml_backend_dev_description(d),"R9700")){gpu=ggml_backend_dev_init(d,nullptr);break;}}ck(gpu,"R9700");std::ifstream maps("/proc/self/maps");std::string l;bool backend=false,driver=false;while(std::getline(maps,l)){if(l.find(argv[1])!=std::string::npos){backend=true;fprintf(stderr,"BACKEND_MAP %s\n",l.c_str());}if(l.find("libvulkan_radeon")!=std::string::npos){driver=true;fprintf(stderr,"DRIVER_MAP %s\n",l.c_str());}}ck(backend&&driver,"mappings");
 ggml_init_params ip={ggml_tensor_overhead()*32+ggml_graph_overhead_custom(32,false),nullptr,true};auto ctx=ggml_init(ip);ck(ctx,"context");auto graph=ggml_new_graph_custom(ctx,32,false);auto w=ggml_new_tensor_2d(ctx,GGML_TYPE_Q3_K,k,m);auto x=ggml_new_tensor_2d(ctx,GGML_TYPE_F32,k,n);ggml_set_input(w);ggml_set_input(x);auto y=ggml_mul_mat(ctx,w,x);ggml_build_forward_expand(graph,y);auto buf=ggml_backend_alloc_ctx_tensors(ctx,gpu);ck(buf,"buffer");
 std::vector<float> full(size_t(k)*m);for(size_t i=0;i<full.size();i++){uint32_t q=uint32_t(i)*1664525u+1013904223u;full[i]=float(int((q^(q>>13))%4093)-2046)/2048.f;}
 std::vector<unsigned char> quant(ggml_nbytes(w));ggml_quantize_init(GGML_TYPE_Q3_K);size_t written=ggml_quantize_chunk(GGML_TYPE_Q3_K,full.data(),quant.data(),0,m,k,nullptr);ck(written==quant.size(),"quantization size");full.clear();full.shrink_to_fit();std::vector<float> input(size_t(k)*n);for(size_t i=0;i<input.size();i++){uint32_t q=uint32_t(i)*22695477u+1u;input[i]=float(int((q^(q>>11))%2047)-1023)/512.f;}
 ggml_backend_tensor_set(w,quant.data(),0,quant.size());ggml_backend_tensor_set(x,input.data(),0,input.size()*sizeof(float));fprintf(stderr,"Q3_CASE_BEGIN k=%d m=%d n=%d\n",k,m,n);fflush(stderr);ck(ggml_backend_graph_compute(gpu,graph)==GGML_STATUS_SUCCESS,"compute");ggml_backend_synchronize(gpu);std::vector<float> result(size_t(m)*n);ggml_backend_tensor_get(y,result.data(),0,result.size()*sizeof(float));for(float f:result)ck(std::isfinite(f),"nonfinite output");FILE*f=fopen(argv[2],"wb");ck(f,"open");ck(fwrite(result.data(),sizeof(float),result.size(),f)==result.size(),"write");ck(fclose(f)==0,"close");fprintf(stderr,"Q3_CASE_PASS k=%d m=%d n=%d\n",k,m,n);ggml_backend_buffer_free(buf);ggml_free(ctx);ggml_backend_free(gpu);return 0;
}
