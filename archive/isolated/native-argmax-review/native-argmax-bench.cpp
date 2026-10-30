#include "llama.h"
#include "ggml-backend.h"
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
#include <fstream>
static void check(bool x,const char*m){if(!x){fprintf(stderr,"FAIL %s\n",m);exit(2);}}
int main(int argc,char**argv){
 check(argc==5,"K copies iterations gather");int k=atoi(argv[1]),copies=atoi(argv[2]),iters=atoi(argv[3]),gather=atoi(argv[4]);check(k>0&&copies>0&&copies<=32&&iters>0&&(gather==0||gather==1),"arguments");
 llama_backend_init();ggml_backend_t gpu=nullptr;
 for(size_t i=0;i<ggml_backend_dev_count();++i){auto d=ggml_backend_dev_get(i);if(ggml_backend_dev_type(d)==GGML_BACKEND_DEVICE_TYPE_GPU&&std::string(ggml_backend_dev_description(d)).find("R9700")!=std::string::npos){gpu=ggml_backend_dev_init(d,nullptr);break;}}check(gpu,"R9700 required");
 for(const char*key:{"EXPECTED_VK_BACKEND_PATH","EXPECTED_RADV_LIBRARY_PATH"}){const char*expected=getenv(key);check(expected,"expected mapping");std::ifstream maps("/proc/self/maps");std::string line;bool seen=false;while(std::getline(maps,line))if(line.find(expected)!=std::string::npos)seen=true;check(seen,"pinned library mapping missing");fprintf(stderr,"MAPPING_OK %s\n",expected);}
 ggml_init_params ip={ggml_tensor_overhead()*512+ggml_graph_overhead_custom(512,false),nullptr,true};auto ctx=ggml_init(ip);check(ctx,"context");auto graph=ggml_new_graph_custom(ctx,512,false);auto input=ggml_new_tensor_1d(ctx,GGML_TYPE_F32,k);ggml_set_input(input);std::vector<ggml_tensor*> ids,values;
 for(int i=0;i<copies;++i){auto idx=ggml_argmax(ctx,input);ids.push_back(idx);ggml_build_forward_expand(graph,idx);if(gather){auto v=ggml_get_rows(ctx,ggml_reshape_2d(ctx,input,1,k),idx);values.push_back(v);ggml_build_forward_expand(graph,v);}}
 auto buffer=ggml_backend_alloc_ctx_tensors(ctx,gpu);check(buffer,"buffer");std::vector<float> data(k);for(int i=0;i<k;++i)data[i]=float((i*17)%65521)/65521.f;int peak=k/3;data[peak]=2.f;ggml_backend_tensor_set(input,data.data(),0,data.size()*sizeof(float));
 for(int i=0;i<16;++i)check(ggml_backend_graph_compute(gpu,graph)==GGML_STATUS_SUCCESS,"warmup");ggml_backend_synchronize(gpu);auto start=std::chrono::steady_clock::now();for(int i=0;i<iters;++i)check(ggml_backend_graph_compute(gpu,graph)==GGML_STATUS_SUCCESS,"compute");ggml_backend_synchronize(gpu);auto end=std::chrono::steady_clock::now();
 for(auto t:ids){int32_t v=-1;ggml_backend_tensor_get(t,&v,0,sizeof(v));check(v==peak,"argmax identity");}for(auto t:values){float v=0;ggml_backend_tensor_get(t,&v,0,sizeof(v));check(v==2.f,"gather value");}
 printf("NATIVE_ARGMAX_BENCH k=%d copies=%d iterations=%d gather=%d us_per_graph=%.6f us_per_argmax=%.6f exact=1\n",k,copies,iters,gather,std::chrono::duration<double,std::micro>(end-start).count()/iters,std::chrono::duration<double,std::micro>(end-start).count()/iters/copies);
 ggml_backend_buffer_free(buffer);ggml_free(ctx);ggml_backend_free(gpu);llama_backend_free();
}
