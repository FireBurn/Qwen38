#include "llama.h"
#include "ggml-backend.h"
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <vector>
#include <string>
#include <chrono>
#include <cstring>
#include <fstream>
static void check(bool ok,const char *m){if(!ok){fprintf(stderr,"FAIL %s\n",m);exit(2);}}
int main(int argc,char **argv){
 check(argc==6,"R iterations cases columns output");const int K=17408,R=atoi(argv[1]),iters=atoi(argv[2]),cases=atoi(argv[3]),cols=atoi(argv[4]);check(R>0&&iters>0&&cases>0&&cases<=16&&(cols==5),"shape");
 llama_backend_init();ggml_backend_t gpu=nullptr;
 for(size_t i=0;i<ggml_backend_dev_count();++i){auto d=ggml_backend_dev_get(i);if(ggml_backend_dev_type(d)==GGML_BACKEND_DEVICE_TYPE_GPU&&std::string(ggml_backend_dev_name(d)).find("Vulkan")==0&&std::string(ggml_backend_dev_description(d)).find("R9700")!=std::string::npos){fprintf(stderr,"SELECTED_BACKEND %s\n",ggml_backend_dev_name(d));gpu=ggml_backend_dev_init(d,nullptr);break;}}
 check(gpu,"R9700 required");
 if (const char *expected = getenv("EXPECTED_VK_BACKEND_PATH")) {
  std::ifstream maps("/proc/self/maps");std::string line;bool seen=false;
  while(std::getline(maps,line)) if(line.find("libggml-vulkan.so")!=std::string::npos){check(line.find(expected)!=std::string::npos,"unexpected Vulkan backend mapping");seen=true;}
  check(seen,"Vulkan backend mapping missing");fprintf(stderr,"BACKEND_PATH_OK %s\n",expected);
 }
if(const char*expected=getenv("EXPECTED_RADV_LIBRARY_PATH")){std::ifstream maps("/proc/self/maps");std::string line;bool seen=false;while(std::getline(maps,line))if(line.find("libvulkan_radeon.so")!=std::string::npos){check(line.find(expected)!=std::string::npos,"unexpected driver");seen=true;}check(seen,"driver missing");fprintf(stderr,"DRIVER_PATH_OK %s\n",expected);}
const ggml_type base_types[]={GGML_TYPE_Q3_K,GGML_TYPE_Q4_K,GGML_TYPE_Q5_K,GGML_TYPE_Q6_K}; ggml_type types[4]; int order=getenv("GLU_FIRST_TYPE")?atoi(getenv("GLU_FIRST_TYPE")):0; check(order>=0&&order<4,"type order"); for(int t=0;t<4;++t)types[t]=base_types[(t+order)%4]; fprintf(stderr,"FIRST_WEIGHT %s\n",ggml_type_name(types[0]));
 ggml_init_params ip={ggml_tensor_overhead()*512+ggml_graph_overhead_custom(512,false),nullptr,true};auto c=ggml_init(ip);check(c,"context");
 constexpr int copies=4;
 auto gate=ggml_new_tensor_2d(c,GGML_TYPE_F32,K,cols);auto up=ggml_new_tensor_2d(c,GGML_TYPE_F32,K,cols);ggml_tensor *w[4],*x[copies],*y[copies][4];auto g=ggml_new_graph_custom(c,512,false);
 for(int t=0;t<4;++t)w[t]=ggml_new_tensor_2d(c,types[t],K,R);
 for(int copy=0;copy<copies;++copy){x[copy]=ggml_swiglu_split(c,gate,up);for(int t=0;t<4;++t){y[copy][t]=ggml_mul_mat(c,w[t],x[copy]);ggml_build_forward_expand(g,y[copy][t]);}}
 auto buf=ggml_backend_alloc_ctx_tensors(c,gpu);check(buf,"buffer");std::vector<float> weights(size_t(K)*R),input(K);std::vector<ggml_fp16_t> half(K);
 for(int t=0;t<4;++t){for(size_t i=0;i<weights.size();++i)weights[i]=float(((i*17+t*23)%257)-128.0)/128.f;std::vector<unsigned char> q(ggml_nbytes(w[t]));auto n=ggml_quantize_chunk(types[t],weights.data(),q.data(),0,R,K,nullptr);check(n==q.size(),"quantization size");ggml_backend_tensor_set(w[t],q.data(),0,q.size());}
 std::vector<float> gate_data(K*cols),up_data(K*cols),all;
 for(int phase=0;phase<cases;++phase){
  for(int i=0;i<K*cols;++i){gate_data[i]=phase==0?0.f:float(int((i*13+phase*17)%257)-128)/float(phase==1?1:16);up_data[i]=float(int((i*29+phase*11)%251)-125)/32.f;}
  ggml_backend_tensor_set(gate,gate_data.data(),0,K*cols*sizeof(float));ggml_backend_tensor_set(up,up_data.data(),0,K*cols*sizeof(float));
  for(int i=0;i<16;++i)check(ggml_backend_graph_compute(gpu,g)==GGML_STATUS_SUCCESS,"warmup");ggml_backend_synchronize(gpu);
  auto warm_start=std::chrono::steady_clock::now();do {check(ggml_backend_graph_compute(gpu,g)==GGML_STATUS_SUCCESS,"settle");ggml_backend_synchronize(gpu);}while(std::chrono::duration<double>(std::chrono::steady_clock::now()-warm_start).count()<0.1);
  auto start=std::chrono::steady_clock::now();for(int i=0;i<iters;++i)check(ggml_backend_graph_compute(gpu,g)==GGML_STATUS_SUCCESS,"compute");ggml_backend_synchronize(gpu);auto stop=std::chrono::steady_clock::now();
  std::vector<float> out(copies*cols*(K+R*4));for(int copy=0;copy<copies;++copy){auto dst=out.data()+copy*cols*(K+R*4);ggml_backend_tensor_get(x[copy],dst,0,K*cols*sizeof(float));for(int t=0;t<4;++t)ggml_backend_tensor_get(y[copy][t],dst+cols*(K+t*R),0,R*cols*sizeof(float));}for(float a:out)check(std::isfinite(a),"finite output");all.insert(all.end(),out.begin(),out.end());
  printf("phase %d us_per_graph %.6f\n",phase,std::chrono::duration<double,std::micro>(stop-start).count()/iters);
 }
 FILE*f=fopen(argv[5],"wb");check(f,"open");check(fwrite(all.data(),sizeof(float),all.size(),f)==all.size(),"write");fclose(f);
 ggml_backend_buffer_free(buf);ggml_free(c);ggml_backend_free(gpu);llama_backend_free();
}
