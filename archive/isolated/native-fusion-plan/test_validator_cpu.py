from pathlib import Path
import subprocess,json,hashlib
p=Path(__file__).resolve().parent;src=(p/'reuse-host/ggml-vulkan.cpp').read_text();header=(p/'reuse-host/ggml-vulkan-types.h').read_text();d=p/'cpu-validator';d.mkdir(exist_ok=True)
def function(start):
 a=src.index(start);b=src.index('{',a);depth=0
 for i in range(b,len(src)):
  if src[i]=='{':depth+=1
  elif src[i]=='}':
   depth-=1
   if depth==0:return src[a:i+1]+'\n'
 raise AssertionError(start)
functions=''.join(function(n)for n in ['static std::vector<uint64_t>nfp_options(','static bool nfp_fast_key(','static nfp_key_result nfp_key('])
types='\n'.join(next(l for l in header.splitlines()if l.startswith(n))for n in ['struct nfp_snapshot','struct nfp_entry'])+'\n'+next(l for l in src.splitlines()if l.startswith('struct nfp_key_result'))+'\n'
base=r'''
#include "ggml.h"
#include <vector>
#include <array>
#include <memory>
#include <unordered_set>
#include <atomic>
#include <cstdint>
#include <cstring>
#include <cstdio>
#include <cstdlib>
#include <sys/mman.h>
#include <unistd.h>
using VkBuffer=uint64_t;
struct fake_buffer {uint64_t size=4096,buffer=17;};
struct ggml_backend_vk_buffer_context {std::shared_ptr<fake_buffer>dev_buffer=std::make_shared<fake_buffer>();};
struct ggml_backend_buffer {void*context=nullptr;void*buft=nullptr;int usage=1;bool vk=true;};
static int ggml_backend_buffer_get_usage(const ggml_backend_buffer*b){return b->usage;}
static bool ggml_backend_buffer_is_vk(const ggml_backend_buffer*b){return b->vk;}
struct fake_device {
 std::atomic<uint64_t>buffer_destroy_count{0};bool disable_fusion=false,multi_add=true,subgroup_arithmetic=true,subgroup_shuffle=true,subgroup_require_full_support=true,uma=false;unsigned subgroup_size_log2=6;int driver_id=3;
 struct {struct {uint32_t maxPushConstantsSize=128;uint64_t minStorageBufferOffsetAlignment=256;}limits;}properties;
 std::shared_ptr<int>pipeline_topk_radix_qsa=std::make_shared<int>(1);std::array<std::shared_ptr<int>,8>pipeline_topk_f32{};
};
struct ggml_backend_vk_context {std::shared_ptr<fake_device>device=std::make_shared<fake_device>();};
struct ggml_cgraph {int n_nodes=0,order=0;ggml_tensor**nodes=nullptr;std::vector<int32_t>uses;};
static int32_t ggml_node_get_use_count(const ggml_cgraph*g,int i){return g->uses.at(i);}
static unsigned tests=0;
static void check(bool b,const char*name){if(!b){fprintf(stderr,"FAIL %s\n",name);exit(2);}++tests;}
'''
main=r'''
int main(){
 ggml_backend_vk_context ctx;ggml_backend_vk_buffer_context bc;int bt=1;ggml_backend_buffer buffer{&bc,&bt,1,true};
 ggml_tensor root{},other{},replacement{};root.type=other.type=replacement.type=GGML_TYPE_F32;root.buffer=other.buffer=replacement.buffer=&buffer;root.ne[0]=other.ne[0]=replacement.ne[0]=256;
 const size_t page=sysconf(_SC_PAGESIZE);auto*leaf=(ggml_tensor*)mmap(nullptr,page,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);auto*grand=(ggml_tensor*)mmap(nullptr,page,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);check(leaf!=MAP_FAILED&&grand!=MAP_FAILED,"mmap");memset(leaf,0,sizeof(*leaf));memset(grand,0,sizeof(*grand));leaf->type=grand->type=GGML_TYPE_F32;leaf->buffer=grand->buffer=&buffer;root.src[0]=leaf;leaf->view_src=grand;
 ggml_tensor*nodes[]={&root,&other};ggml_cgraph graph{2,0,nodes,{1,1}};
 auto capture=[&](){auto k=nfp_key(&ctx,&graph);check(k.admissible,"admission");return nfp_entry{std::move(k.bytes),{},std::move(k.nodes),std::move(k.uses),std::move(k.snapshots),k.epoch,k.order,k.disabled,std::move(k.options)};};
 auto entry=capture();check(nfp_fast_key(&ctx,&graph,entry),"baseline");
 for(ggml_tensor*t:{&root,&other,leaf,grand})for(size_t i=0;i<sizeof(*t);++i){auto*b=(unsigned char*)t;const auto old=b[i];b[i]^=1;check(!nfp_fast_key(&ctx,&graph,entry),"every tensor representation byte invalidates conservatively");b[i]=old;}
 check(nfp_fast_key(&ctx,&graph,entry),"restored metadata");
 graph.uses[0]++;check(!nfp_fast_key(&ctx,&graph,entry),"use count");graph.uses[0]--;graph.order++;check(!nfp_fast_key(&ctx,&graph,entry),"graph order");graph.order--;graph.n_nodes--;check(!nfp_fast_key(&ctx,&graph,entry),"node count");graph.n_nodes++;
 std::swap(nodes[0],nodes[1]);check(!nfp_fast_key(&ctx,&graph,entry),"node order");std::swap(nodes[0],nodes[1]);
 ctx.device->buffer_destroy_count++;check(!nfp_fast_key(&ctx,&graph,entry),"destroy epoch");ctx.device->buffer_destroy_count--;
 ctx.device->disable_fusion=true;check(!nfp_fast_key(&ctx,&graph,entry),"fusion disabled");ctx.device->disable_fusion=false;
 ctx.device->multi_add=false;check(!nfp_fast_key(&ctx,&graph,entry),"multiadd option");ctx.device->multi_add=true;
 ctx.device->properties.limits.maxPushConstantsSize++;check(!nfp_fast_key(&ctx,&graph,entry),"push limit");ctx.device->properties.limits.maxPushConstantsSize--;
 ctx.device->properties.limits.minStorageBufferOffsetAlignment*=2;check(!nfp_fast_key(&ctx,&graph,entry),"alignment option");ctx.device->properties.limits.minStorageBufferOffsetAlignment/=2;
 ctx.device->pipeline_topk_f32[0]=std::make_shared<int>(3);check(!nfp_fast_key(&ctx,&graph,entry),"pipeline availability");ctx.device->pipeline_topk_f32[0].reset();
 buffer.usage++;check(!nfp_fast_key(&ctx,&graph,entry),"buffer usage");buffer.usage--;buffer.vk=false;check(!nfp_fast_key(&ctx,&graph,entry),"nonVK admission");check(!nfp_key(&ctx,&graph).admissible,"canonical nonVK rejection");buffer.vk=true;
 bc.dev_buffer->size++;check(!nfp_fast_key(&ctx,&graph,entry),"buffer size");bc.dev_buffer->size--;bc.dev_buffer->buffer++;check(!nfp_fast_key(&ctx,&graph,entry),"buffer handle");bc.dev_buffer->buffer--;
 root.extra=&bt;check(!nfp_key(&ctx,&graph).admissible,"unknown extra rejection");root.extra=nullptr;
 // Stale cached leaf: live parent changes its edge before the old leaf is unmapped.
 check(mprotect(leaf,page,PROT_NONE)==0,"guard leaf");root.src[0]=&replacement;check(!nfp_fast_key(&ctx,&graph,entry),"reject changed parent before dereferencing stale leaf");root.src[0]=leaf;check(mprotect(leaf,page,PROT_READ|PROT_WRITE)==0,"unguard leaf");
 check(mprotect(grand,page,PROT_NONE)==0,"guard grandchild");leaf->view_src=&replacement;check(!nfp_fast_key(&ctx,&graph,entry),"reject changed ancestor before stale grandchild");leaf->view_src=grand;check(mprotect(grand,page,PROT_READ|PROT_WRITE)==0,"unguard grandchild");
 void*old_context=buffer.context;check(mprotect(grand,page,PROT_NONE)==0,"guard context target");buffer.context=grand;check(!nfp_fast_key(&ctx,&graph,entry),"reject context identity before dereferencing invalid replacement");buffer.context=old_context;check(mprotect(grand,page,PROT_READ|PROT_WRITE)==0,"unguard context target");
 auto*old_root=(ggml_tensor*)mmap(nullptr,page,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);check(old_root!=MAP_FAILED,"root mmap");memcpy(old_root,&root,sizeof(root));nodes[0]=old_root;auto old_entry=capture();check(mprotect(old_root,page,PROT_NONE)==0,"guard stale root");nodes[0]=&root;check(!nfp_fast_key(&ctx,&graph,old_entry),"node identity checked before stale root dereference");check(munmap(old_root,page)==0,"unmap old root");
 check(nfp_fast_key(&ctx,&graph,entry),"final baseline");munmap(leaf,page);munmap(grand,page);printf("CPU_VALIDATOR_PASS tests=%u tensor_bytes=%zu\n",tests,sizeof(ggml_tensor));
}
'''
code=base+types+functions+main;(d/'test.cpp').write_text(code);cmd=['clang++','-std=c++17','-O2','-I'+str(p.parent/'production-baseline-aa8/ggml-include'),str(d/'test.cpp'),'-o',str(d/'test')];subprocess.run(cmd,check=True);result=subprocess.run([str(d/'test')],check=True,capture_output=True,text=True);sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();r=dict(command=cmd,stdout=result.stdout,source_sha256=sha(d/'test.cpp'),binary_sha256=sha(d/'test'),extracted_function_sha256=hashlib.sha256(functions.encode()).hexdigest(),origin_reuse_library_sha256=json.loads((p/'reuse-build.json').read_text())['library_sha256'],scope='CPUonly exactextractedkey/validatorfunctions withrealggml_tensorlayout andmockdevice/buffer/graph APIs. Exhaustivetensor-byteinvalidations/options/identities andPROT_NONEstaleroot/leaf/grandchild/context ordering witnesses. NoGPUdevice/commands,nottotalVulkanlifetimeproof. CurrentliveGGMLgraphmustremainvalidduringbackendcall. Benchmarklibraryunchanged.');(d/'checks.json').write_text(json.dumps(r,indent=2)+'\n');print(result.stdout,end='')
