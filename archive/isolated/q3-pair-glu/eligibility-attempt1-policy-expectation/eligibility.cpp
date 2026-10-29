#include "llama.h"
#include "ggml-backend.h"
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <vector>
#include <string>
#include <cstring>
#include <fstream>
static void check(bool ok,const char*m){if(!ok){fprintf(stderr,"FAIL %s\n",m);exit(2);}}
int main(int argc,char**argv){
 check(argc==3,"mode output");bool disabled=std::string(argv[1])=="disabled";
 llama_backend_init();ggml_backend_t gpu=nullptr;
 for(size_t i=0;i<ggml_backend_dev_count();++i){auto d=ggml_backend_dev_get(i);if(ggml_backend_dev_type(d)==GGML_BACKEND_DEVICE_TYPE_GPU&&std::string(ggml_backend_dev_description(d)).find("R9700")!=std::string::npos){gpu=ggml_backend_dev_init(d,nullptr);break;}}
 check(gpu,"R9700");
 for(auto item:{std::pair<const char*,const char*>{"EXPECTED_VK_BACKEND_PATH","libggml-vulkan.so"},{"EXPECTED_RADV_LIBRARY_PATH","libvulkan_radeon.so"}}){const char*expected=getenv(item.first);check(expected,"expected mapping env");std::ifstream maps("/proc/self/maps");std::string line;bool found=false;while(std::getline(maps,line))if(line.find(item.second)!=std::string::npos){check(line.find(expected)!=std::string::npos,"unexpected mapping");found=true;}check(found,"mapping missing");fprintf(stderr,"WITNESS_PATH_OK %s\n",expected);}
 const char*names[]={"valid","reverse","different_input","extra_consumer","output_intermediate","weight_view","input_view","other_quant","mixed_quant","precision","unmarked_weights","activation_alias","cols3"};
 std::vector<float>all;std::vector<ggml_context*>contexts;std::vector<ggml_backend_buffer_t>buffers;unsigned cases=0;
 for(const char*name:names)for(int column:{1,2}){
  std::string kind=name;if(disabled&&kind!="valid")continue;if(kind=="cols3"&&column==2)continue;
  const int K=256,R=kind=="activation_alias"?256:15,C=kind=="cols3"?3:column;
  ggml_init_params ip={ggml_tensor_overhead()*128+ggml_graph_overhead_custom(128,false),nullptr,true};auto c=ggml_init(ip);check(c,"context");
  ggml_type ta=kind=="other_quant"?GGML_TYPE_Q4_K:GGML_TYPE_Q3_K,tb=(kind=="other_quant"||kind=="mixed_quant")?GGML_TYPE_Q4_K:GGML_TYPE_Q3_K;
  auto wa0=ggml_new_tensor_2d(c,ta,K,R),wb=ggml_new_tensor_2d(c,tb,K,R);auto wa=kind=="weight_view"?ggml_view_2d(c,wa0,K,R,wa0->nb[1],0):wa0;
  auto xbase=ggml_new_tensor_1d(c,GGML_TYPE_F32,K*C+64);auto x=kind=="input_view"?ggml_view_2d(c,xbase,K,C,K*sizeof(float),256):ggml_new_tensor_2d(c,GGML_TYPE_F32,K,C);auto x2=ggml_new_tensor_2d(c,GGML_TYPE_F32,K,C);
  auto a=ggml_mul_mat(c,wa,x),b=ggml_mul_mat(c,wb,kind=="different_input"?x2:x);ggml_set_name(a,"witness_gate");ggml_set_name(b,"witness_up");
  if(kind=="precision")ggml_mul_mat_set_prec(a,GGML_PREC_F32);
  if(kind=="output_intermediate")ggml_set_output(a);
  auto out=kind=="reverse"?ggml_swiglu_split(c,b,a):ggml_swiglu_split(c,a,b);ggml_set_name(out,"witness_glu");ggml_set_output(out);
  auto graph=ggml_new_graph_custom(c,128,false);ggml_build_forward_expand(graph,out);
  ggml_tensor*extra=nullptr;if(kind=="extra_consumer"){extra=ggml_scale(c,a,.5f);ggml_set_output(extra);ggml_build_forward_expand(graph,extra);}
  a->flags|=GGML_TENSOR_FLAG_COMPUTE;b->flags|=GGML_TENSOR_FLAG_COMPUTE;out->flags|=GGML_TENSOR_FLAG_COMPUTE;if(extra)extra->flags|=GGML_TENSOR_FLAG_COMPUTE;
  auto buf=ggml_backend_alloc_ctx_tensors(c,gpu);check(buf,"buffer");if(kind!="unmarked_weights")ggml_backend_buffer_set_usage(buf,GGML_BACKEND_BUFFER_USAGE_WEIGHTS);
  if(kind=="activation_alias"){out->data=x->data;out->buffer=x->buffer;}
  for(auto w:{wa0,wb}){std::vector<float>f(K*R);for(size_t j=0;j<f.size();++j)f[j]=float(int((j*17+(w==wa0?19:37))%257)-128)/128.f;std::vector<unsigned char>q(ggml_nbytes(w));check(ggml_quantize_chunk(w->type,f.data(),q.data(),0,R,K,nullptr)==q.size(),"quantization");ggml_backend_tensor_set(w,q.data(),0,q.size());}
  fprintf(stderr,"ELIGIBILITY_BEGIN case=%s C=%d K=%d R=%d disabled=%d\n",name,C,K,R,disabled);
  for(int phase=0;phase<4;++phase){std::vector<float>input(K*C);for(size_t j=0;j<input.size();++j)input[j]=phase==0?0.f:float(int((j*13+phase*11)%251)-125)/float(phase==1?1:16);ggml_backend_tensor_set(x,input.data(),0,input.size()*4);for(auto&v:input)v=v*.75f+.125f;ggml_backend_tensor_set(x2,input.data(),0,input.size()*4);
   check(ggml_backend_graph_compute(gpu,graph)==GGML_STATUS_SUCCESS,"compute");ggml_backend_synchronize(gpu);std::vector<float>result(R*C);ggml_backend_tensor_get(out,result.data(),0,result.size()*4);for(float v:result)check(std::isfinite(v),"finite");all.insert(all.end(),result.begin(),result.end());
   if(extra||kind=="output_intermediate"){auto t=extra?extra:a;ggml_backend_tensor_get(t,result.data(),0,result.size()*4);for(float v:result)check(std::isfinite(v),"finite intermediate");all.insert(all.end(),result.begin(),result.end());}
  }
  fprintf(stderr,"ELIGIBILITY_END case=%s C=%d\n",name,C);++cases;buffers.push_back(buf);contexts.push_back(c);
 }
 FILE*f=fopen(argv[2],"wb");check(f,"output");check(fwrite(all.data(),sizeof(float),all.size(),f)==all.size(),"write");fclose(f);ggml_backend_synchronize(gpu);for(auto buf:buffers)ggml_backend_buffer_free(buf);for(auto ctx:contexts)ggml_free(ctx);ggml_backend_free(gpu);llama_backend_free();fprintf(stderr,"ELIGIBILITY_ALL_DONE cases=%u floats=%zu\n",cases,all.size());
}
