#include "llama.h"
#include "ggml-backend.h"
#include "llama-ext.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <fstream>
static void check(bool ok,const char* s){if(!ok){fprintf(stderr,"FAIL %s\n",s);exit(2);}}
int main(int argc,char**argv){
 if(argc==2 && !strcmp(argv[1],"--help")){puts("usage: isolation-probe target.gguf draft.gguf output.bin");return 0;}
 check(argc==4,"arguments");llama_backend_init();auto dev=ggml_backend_dev_by_name("Vulkan0");check(dev,"Vulkan0");ggml_backend_dev_t devs[]={dev,nullptr};auto mp=llama_model_default_params();mp.devices=devs;mp.n_gpu_layers=999;
 auto tgt=llama_model_load_from_file(argv[1],mp);check(tgt,"target model");auto cp=llama_context_default_params();cp.n_ctx=2048;cp.n_batch=64;cp.n_ubatch=64;cp.n_seq_max=2;cp.kv_unified=false;cp.flash_attn_type=LLAMA_FLASH_ATTN_TYPE_ENABLED;cp.type_k=GGML_TYPE_Q8_0;cp.type_v=GGML_TYPE_Q8_0;auto tc=llama_init_from_model(tgt,cp);check(tc,"target context");
 auto draft=llama_model_load_from_file(argv[2],mp);check(draft,"draft model");cp.ctx_other=tc;auto dc=llama_init_from_model(draft,cp);check(dc,"draft context");llama_set_embeddings_nextn(dc,true,false);llama_set_causal_attn(dc,false);int width=llama_model_n_embd_out(draft);check(width>0 && width<=16384,"embedding width");auto mask=llama_vocab_mask(llama_model_get_vocab(draft));check(mask>=0,"mask id");auto batch=llama_batch_ext_init(dc);check(batch,"batch");FILE*f=fopen(argv[3],"wb");check(f,"output");
 for(int k=0;k<4;k++){
  llama_memory_clear(llama_get_memory(dc),true);llama_batch_ext_clear(batch);int anchors[]={100+(k==1),200+(k==2)};
  for(int seq=0;seq<2;seq++)for(int pos=0;pos<5;pos++){int idx=llama_batch_ext_add_token(batch,seq,pos==0?anchors[seq]:mask);check(idx>=0,"add token");llama_pos pp=pos;check(llama_batch_ext_set_pos(batch,idx,&pp),"set pos");}
  fprintf(stderr,"ISOLATION_CASE_BEGIN %d anchors=%d,%d\n",k,anchors[0],anchors[1]);fflush(stderr);check(llama_process(dc,LLAMA_PROCESS_TYPE_DECODE,batch)==0,"draft decode");float*p=llama_get_embeddings_nextn(dc);check(p,"lattice output");uint32_t h[]={0x49534f4cu,(uint32_t)k,10u,(uint32_t)width};check(fwrite(h,sizeof(h),1,f)==1,"write header");check(fwrite(p,sizeof(float),size_t(10)*width,f)==size_t(10)*width,"write lattice");fflush(f);fprintf(stderr,"ISOLATION_CASE_PASS %d\n",k);fflush(stderr);
 }
 check(fclose(f)==0,"close");llama_batch_ext_free(batch);llama_free(dc);llama_model_free(draft);llama_free(tc);llama_model_free(tgt);llama_backend_free();return 0;
}
