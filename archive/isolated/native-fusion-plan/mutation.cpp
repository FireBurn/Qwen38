#include "llama.h"
#include "ggml-backend.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <vector>
#include <string>
#include <fstream>
static void check(bool b,const char*m){if(!b){fprintf(stderr,"FAIL %s\n",m);exit(2);}}
int main(int argc,char**argv){check(argc==2,"output");llama_backend_init();ggml_backend_t gpu=nullptr;for(size_t i=0;i<ggml_backend_dev_count();++i){auto d=ggml_backend_dev_get(i);if(ggml_backend_dev_type(d)==GGML_BACKEND_DEVICE_TYPE_GPU&&std::string(ggml_backend_dev_description(d)).find("R9700")!=std::string::npos){gpu=ggml_backend_dev_init(d,nullptr);break;}}check(gpu,"GPU");
 for(auto item:{std::pair<const char*,const char*>{"EXPECTED_VK_BACKEND_PATH","libggml-vulkan.so"},{"EXPECTED_RADV_LIBRARY_PATH","libvulkan_radeon.so"}}){auto expected=getenv(item.first);check(expected,"expected path");std::ifstream f("/proc/self/maps");std::string line;bool seen=false;while(std::getline(f,line))if(line.find(item.second)!=std::string::npos){check(line.find(expected)!=std::string::npos,"wrong mapping");seen=true;}check(seen,"mapping missing");fprintf(stderr,"MUTATION_PATH_OK %s\n",expected);}
 std::vector<float>all;std::vector<ggml_context*>contexts;std::vector<ggml_backend_buffer_t>buffers;
 for(int C:{1,2}){const int K=512;ggml_init_params ip={ggml_tensor_overhead()*64+ggml_graph_overhead_custom(64,false),nullptr,true};auto ctx=ggml_init(ip);check(ctx,"context");auto x=ggml_new_tensor_2d(ctx,GGML_TYPE_F32,K,C),gain=ggml_new_tensor_1d(ctx,GGML_TYPE_F32,K);auto rms=ggml_rms_norm(ctx,x,1e-5f),scaled=ggml_mul(ctx,rms,gain),out=ggml_dup(ctx,scaled);ggml_set_name(rms,"mutable_rms");ggml_set_name(scaled,"mutable_scaled");ggml_set_output(out);auto graph=ggml_new_graph_custom(ctx,64,false);ggml_build_forward_expand(graph,out);rms->flags|=GGML_TENSOR_FLAG_COMPUTE;scaled->flags|=GGML_TENSOR_FLAG_COMPUTE;out->flags|=GGML_TENSOR_FLAG_COMPUTE;auto buffer=ggml_backend_alloc_ctx_tensors(ctx,gpu);check(buffer,"buffer");
  const bool output_flags[]={false,false,true,true,false,true,false,false};
  for(int phase=0;phase<8;++phase){ggml_backend_synchronize(gpu);if(output_flags[phase])rms->flags|=GGML_TENSOR_FLAG_OUTPUT;else rms->flags&=~GGML_TENSOR_FLAG_OUTPUT;const float eps=phase<4?1e-5f:1e-4f;memcpy(rms->op_params,&eps,sizeof(eps));
   std::vector<float>input(K*C),weights(K),sentinel(K*C,NAN);for(size_t i=0;i<input.size();++i)input[i]=float(int((i*17+phase*23)%251)-125)/32.f;for(int i=0;i<K;++i)weights[i]=float(int((i*29+7)%127)-63)/64.f;ggml_backend_tensor_set(x,input.data(),0,input.size()*4);ggml_backend_tensor_set(gain,weights.data(),0,weights.size()*4);ggml_backend_tensor_set(rms,sentinel.data(),0,sentinel.size()*4);
   fprintf(stderr,"MUTATION_BEGIN C=%d phase=%d output=%d eps=%g\n",C,phase,int(output_flags[phase]),eps);check(ggml_backend_graph_compute(gpu,graph)==GGML_STATUS_SUCCESS,"compute");ggml_backend_synchronize(gpu);std::vector<float>result(K*C);ggml_backend_tensor_get(out,result.data(),0,result.size()*4);for(float v:result)check(std::isfinite(v),"finite final");all.insert(all.end(),result.begin(),result.end());
   if(output_flags[phase]){ggml_backend_tensor_get(rms,result.data(),0,result.size()*4);for(float v:result)check(std::isfinite(v),"requested RMS materialized, sentinel overwritten");all.insert(all.end(),result.begin(),result.end());}fprintf(stderr,"MUTATION_END C=%d phase=%d\n",C,phase);
  }contexts.push_back(ctx);buffers.push_back(buffer);
 }
 FILE*f=fopen(argv[1],"wb");check(f,"file");check(fwrite(all.data(),4,all.size(),f)==all.size(),"write");fclose(f);ggml_backend_synchronize(gpu);for(auto b:buffers)ggml_backend_buffer_free(b);for(auto c:contexts)ggml_free(c);ggml_backend_free(gpu);llama_backend_free();fprintf(stderr,"MUTATION_DONE generations=16 floats=%zu\n",all.size());
}
