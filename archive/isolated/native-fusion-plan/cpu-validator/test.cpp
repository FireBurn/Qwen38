
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
struct nfp_snapshot {const ggml_tensor*tensor;std::array<uint8_t,sizeof(ggml_tensor)>raw;uintptr_t buffer_context=0,buffer_type=0,device_buffer=0;uint64_t buffer_handle=0,buffer_size=0;int usage=0;};
struct nfp_entry {std::vector<uint8_t>key;std::vector<uint64_t>plan;std::vector<const ggml_tensor*>nodes;std::vector<int32_t>uses;std::vector<nfp_snapshot>snapshots;uint64_t epoch=0;int order=0;bool disabled=false;std::vector<uint64_t>options;};
struct nfp_key_result {std::vector<uint8_t>bytes;size_t tensors=0;bool admissible=true;std::vector<const ggml_tensor*>nodes;std::vector<int32_t>uses;std::vector<nfp_snapshot>snapshots;uint64_t epoch=0;int order=0;bool disabled=false;std::vector<uint64_t>options;};
static std::vector<uint64_t>nfp_options(ggml_backend_vk_context*ctx){
    const auto&d=ctx->device;std::vector<uint64_t>v={uint64_t(reinterpret_cast<uintptr_t>(d.get())),uint64_t(d->driver_id),uint64_t(d->multi_add),uint64_t(d->subgroup_arithmetic),uint64_t(d->subgroup_shuffle),uint64_t(d->subgroup_require_full_support),uint64_t(d->subgroup_size_log2),uint64_t(d->uma),uint64_t(d->properties.limits.maxPushConstantsSize),uint64_t(d->properties.limits.minStorageBufferOffsetAlignment),uint64_t(reinterpret_cast<uintptr_t>(d->pipeline_topk_radix_qsa.get()))};
    for(const auto&pl:d->pipeline_topk_f32)v.push_back(uint64_t(reinterpret_cast<uintptr_t>(pl.get())));return v;
}
static bool nfp_fast_key(ggml_backend_vk_context*ctx,const ggml_cgraph*graph,const nfp_entry&entry){
    if(entry.options!=nfp_options(ctx))return false;
    if(entry.nodes.size()!=size_t(graph->n_nodes)||entry.order!=int(graph->order)||entry.disabled!=ctx->device->disable_fusion||entry.epoch!=ctx->device->buffer_destroy_count.load(std::memory_order_acquire))return false;
    for(int i=0;i<graph->n_nodes;++i)if(entry.nodes[i]!=graph->nodes[i]||entry.uses[i]!=ggml_node_get_use_count(graph,i))return false;
    // Initial graph nodes are live. Later closure nodes are reached by source/view
    // pointers in an earlier snapshot whose complete object representation matched.
    // Stop on the first mismatch, before dereferencing unvalidated descendants.
    for(const auto&snap:entry.snapshots){
        const ggml_tensor*t=snap.tensor;if(std::memcmp(snap.raw.data(),t,sizeof(*t)))return false;
        if(t->buffer){
            if(snap.buffer_context!=reinterpret_cast<uintptr_t>(t->buffer->context)||snap.buffer_type!=reinterpret_cast<uintptr_t>(t->buffer->buft)||snap.usage!=int(ggml_backend_buffer_get_usage(t->buffer))||!ggml_backend_buffer_is_vk(t->buffer))return false;
            const auto*bc=static_cast<const ggml_backend_vk_buffer_context*>(t->buffer->context);
            if(snap.device_buffer!=reinterpret_cast<uintptr_t>(bc->dev_buffer.get()))return false;
            if(bc->dev_buffer&&(snap.buffer_size!=bc->dev_buffer->size||snap.buffer_handle!=uint64_t(VkBuffer(bc->dev_buffer->buffer))))return false;
        }
    }
    return entry.epoch==ctx->device->buffer_destroy_count.load(std::memory_order_acquire);
}
static nfp_key_result nfp_key(ggml_backend_vk_context*ctx,const ggml_cgraph*graph){
    nfp_key_result result;auto&key=result.bytes;key.reserve(size_t(graph->n_nodes)*512);
    auto add=[&](const auto&v){const auto*b=reinterpret_cast<const uint8_t*>(&v);key.insert(key.end(),b,b+sizeof(v));};
    auto ptr=[&](const void*v){add(reinterpret_cast<uintptr_t>(v));};
    result.epoch=ctx->device->buffer_destroy_count.load(std::memory_order_acquire);result.order=graph->order;result.disabled=ctx->device->disable_fusion;add(graph->n_nodes);add(graph->order);add(result.epoch);add(result.disabled);result.options=nfp_options(ctx);for(uint64_t value:result.options)add(value);
    std::vector<const ggml_tensor*>all;all.reserve(graph->n_nodes*2);std::unordered_set<const ggml_tensor*>seen;seen.reserve(graph->n_nodes*2);
    auto enqueue=[&](const ggml_tensor*t){if(t&&seen.insert(t).second)all.push_back(t);};
    for(int i=0;i<graph->n_nodes;++i){const auto*t=graph->nodes[i];ptr(t);const int32_t uses=ggml_node_get_use_count(graph,i);add(uses);result.nodes.push_back(t);result.uses.push_back(uses);enqueue(t);}
    if(all.size()!=size_t(graph->n_nodes))result.admissible=false;
    for(size_t i=0;i<all.size();++i){const auto*t=all[i];nfp_snapshot snapshot{};snapshot.tensor=t;std::memcpy(snapshot.raw.data(),t,sizeof(*t));ptr(t);add(t->type);add(t->op);add(t->flags);add(t->ne);add(t->nb);add(t->op_params);ptr(t->data);ptr(t->view_src);add(t->view_offs);ptr(t->extra);if(t->extra)result.admissible=false;
        for(const auto*src:t->src){ptr(src);enqueue(src);}enqueue(t->view_src);
        const size_t name_length=strnlen(t->name,sizeof(t->name));add(name_length);key.insert(key.end(),reinterpret_cast<const uint8_t*>(t->name),reinterpret_cast<const uint8_t*>(t->name)+name_length);
        ptr(t->buffer);
        if(t->buffer){snapshot.buffer_context=reinterpret_cast<uintptr_t>(t->buffer->context);snapshot.buffer_type=reinterpret_cast<uintptr_t>(t->buffer->buft);snapshot.usage=ggml_backend_buffer_get_usage(t->buffer);ptr(t->buffer->context);ptr(t->buffer->buft);add(snapshot.usage);
            const bool vk=ggml_backend_buffer_is_vk(t->buffer);add(vk);
            if(vk){const auto*bctx=static_cast<const ggml_backend_vk_buffer_context*>(t->buffer->context);snapshot.device_buffer=reinterpret_cast<uintptr_t>(bctx->dev_buffer.get());ptr(bctx->dev_buffer.get());if(bctx->dev_buffer){snapshot.buffer_size=bctx->dev_buffer->size;snapshot.buffer_handle=uint64_t(VkBuffer(bctx->dev_buffer->buffer));add(snapshot.buffer_size);add(snapshot.buffer_handle);}}
            else result.admissible=false;
        }
        result.snapshots.push_back(snapshot);
    }
    result.tensors=all.size();return result;
}

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
