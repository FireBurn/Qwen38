from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parent;source=(root/'../installed-source/src/llama-kv-cache-iswa.cpp').read_text();a=source.index('            bool two_full_dflash_blocks = false;');b=source.index('            if (two_full_dflash_blocks && std::getenv',a);guard=source[a:b]
program=r'''#include <cstdint>
#include <cstdio>
#include <random>
using llama_seq_id=int32_t;const int LLM_ARCH_DFLASH=1;
struct batch_t{int n_tokens;int *n_seq_id;llama_seq_id **seq_id;};struct model_t{int arch;void*dflash_selector_hidden;};struct alloc_t{batch_t batch;int used;const batch_t&get_batch()const{return batch;}int get_n_used()const{return used;}};
bool evaluate(int n_stream,bool embd_all,model_t model,int n_ubatch,alloc_t balloc){ const bool unified=n_stream<=1;const bool dflash2_selector=model.arch==1 && model.dflash_selector_hidden;
''' + guard + r'''
return two_full_dflash_blocks;}
int main(){std::mt19937 rng(192837);int checks=0,accepted=0;for(int t=0;t<50000;t++){
 int ids[10],counts[10];int32_t *ptr[10];int seqbase=int(rng()%5);bool intended=t<1000;for(int i=0;i<10;i++){ids[i]=intended?seqbase+(i>=5):int(rng()%7);counts[i]=intended?1:int(rng()%3);ptr[i]=(t%131==0&&!intended)?nullptr:&ids[i];}
 int n=intended?10:int(rng()%14);int capacity=intended?10:int(rng()%14);int streams=intended?2:int(rng()%3);bool all=intended?true:bool(rng()%2);model_t model{intended?1:int(rng()%2),intended?(void*)1:(rng()%2?(void*)1:nullptr)};alloc_t alloc{{n,counts,ptr},intended?0:int(rng()%2)};
 bool reference=streams>1&&all&&model.arch==1&&model.dflash_selector_hidden&&capacity>=10&&alloc.used==0&&n==10;
 if(reference){for(int i=0;i<10;i++)if(counts[i]!=1||ptr[i]==nullptr)reference=false;}
 if(reference){int a=ids[0],b=ids[5];reference=a>=0&&b==a+1;for(int i=0;i<10;i++)if(ids[i]!=(i<5?a:b))reference=false;}
 bool actual=evaluate(streams,all,model,capacity,alloc);if(actual!=reference){fprintf(stderr,"mismatch %d\n",t);return 1;}checks++;accepted+=actual;}
 printf("{\"cases\":%d,\"accepted\":%d,\"result\":\"pass\"}\n",checks,accepted);}
'''
with tempfile.TemporaryDirectory() as t:
 cpp=Path(t)/'guard.cpp';exe=Path(t)/'guard';cpp.write_text(program);subprocess.run(['clang++','-std=c++17','-O2',str(cpp),'-o',str(exe)],check=True);result=json.loads(subprocess.check_output([str(exe)],text=True));result['scope']='actual extracted guard logic against independent structural oracle; not allocator, attention, cache or GPU behavior';print(json.dumps(result));(root/'iswa-guard-audit.json').write_text(json.dumps(result,indent=2)+'\n')
