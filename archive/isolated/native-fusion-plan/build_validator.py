from pathlib import Path
p=Path(__file__).resolve().parent
s=(p/'build_shadow.py').read_text().replace("h=p/'shadow-host'","h=p/'validator-host'").replace("p/'shadow.patch'","p/'validator.patch'").replace("p/'shadow-build.json'","p/'validator-build.json'").replace('NATIVE_FUSION_SHADOW_BUILT','NATIVE_FUSION_VALIDATOR_BUILT')
s=s.replace('struct nfp_entry {std::vector<uint8_t> key;std::vector<uint64_t> plan;};','''struct nfp_snapshot {const ggml_tensor*tensor;std::array<uint8_t,sizeof(ggml_tensor)>raw;uintptr_t buffer_context=0,buffer_type=0,device_buffer=0;uint64_t buffer_handle=0,buffer_size=0;int usage=0;};
struct nfp_entry {std::vector<uint8_t>key;std::vector<uint64_t>plan;std::vector<const ggml_tensor*>nodes;std::vector<int32_t>uses;std::vector<nfp_snapshot>snapshots;uint64_t epoch=0;int order=0;bool disabled=false;};''')
s=s.replace('struct nfp_key_result {std::vector<uint8_t>bytes;size_t tensors=0;bool admissible=true;};','struct nfp_key_result {std::vector<uint8_t>bytes;size_t tensors=0;bool admissible=true;std::vector<const ggml_tensor*>nodes;std::vector<int32_t>uses;std::vector<nfp_snapshot>snapshots;uint64_t epoch=0;int order=0;bool disabled=false;};')
s=s.replace('add(graph->n_nodes);add(graph->order);add(ctx->device->buffer_destroy_count.load(std::memory_order_acquire));add(ctx->device->disable_fusion);','result.epoch=ctx->device->buffer_destroy_count.load(std::memory_order_acquire);result.order=graph->order;result.disabled=ctx->device->disable_fusion;add(graph->n_nodes);add(graph->order);add(result.epoch);add(result.disabled);')
s=s.replace('ptr(t);add(ggml_node_get_use_count(graph,i));enqueue(t);','ptr(t);const int32_t uses=ggml_node_get_use_count(graph,i);add(uses);result.nodes.push_back(t);result.uses.push_back(uses);enqueue(t);')
s=s.replace('    for(size_t i=0;i<all.size();++i){','    if(all.size()!=size_t(graph->n_nodes))result.admissible=false;\n    for(size_t i=0;i<all.size();++i){')
s=s.replace('const auto*t=all[i];ptr(t);','const auto*t=all[i];nfp_snapshot snapshot{};snapshot.tensor=t;std::memcpy(snapshot.raw.data(),t,sizeof(*t));ptr(t);')
s=s.replace('ptr(t->buffer->context);ptr(t->buffer->buft);add(ggml_backend_buffer_get_usage(t->buffer));','snapshot.buffer_context=reinterpret_cast<uintptr_t>(t->buffer->context);snapshot.buffer_type=reinterpret_cast<uintptr_t>(t->buffer->buft);snapshot.usage=ggml_backend_buffer_get_usage(t->buffer);ptr(t->buffer->context);ptr(t->buffer->buft);add(snapshot.usage);')
s=s.replace('ptr(bctx->dev_buffer.get());if(bctx->dev_buffer){add(bctx->dev_buffer->size);add(uint64_t(VkBuffer(bctx->dev_buffer->buffer)));}','snapshot.device_buffer=reinterpret_cast<uintptr_t>(bctx->dev_buffer.get());ptr(bctx->dev_buffer.get());if(bctx->dev_buffer){snapshot.buffer_size=bctx->dev_buffer->size;snapshot.buffer_handle=uint64_t(VkBuffer(bctx->dev_buffer->buffer));add(snapshot.buffer_size);add(snapshot.buffer_handle);}')
s=s.replace('    result.tensors=all.size();return result;','        result.snapshots.push_back(snapshot);\n    result.tensors=all.size();return result;') if False else s
# Append the snapshot inside the closure loop, after buffer admission checks.
s=s.replace('            else result.admissible=false;\n        }\n    }\n    result.tensors=', '            else result.admissible=false;\n        }\n        result.snapshots.push_back(snapshot);\n    }\n    result.tensors=')
needle='static nfp_key_result nfp_key('
fast=r'''static bool nfp_fast_key(ggml_backend_vk_context*ctx,const ggml_cgraph*graph,const nfp_entry&entry){
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
'''
s=s.replace(needle,fast+needle)
s=s.replace('int nfp_hit=-1;uint64_t nfp_key_cpu=0;', 'int nfp_hit=-1,nfp_fast_hit=-1;uint64_t nfp_key_cpu=0,nfp_fast_cpu=0;')
s=s.replace('if(nfp_shadow){const uint64_t start=nfp_cpu_ns();nfp_signature=', 'if(nfp_shadow){const uint64_t fast_start=nfp_cpu_ns();for(size_t k=0;k<ctx->nfp_entries.size();++k)if(nfp_fast_key(ctx,cgraph,ctx->nfp_entries[k])){nfp_fast_hit=k;break;}nfp_fast_cpu=nfp_cpu_ns()-fast_start;const uint64_t start=nfp_cpu_ns();nfp_signature=')
needle='        if(nfp_signature.admissible&&nfp_hit<0)'
assert needle in s
s=s.replace(needle,r'''        const bool fast_agree=nfp_fast_hit<0||(nfp_hit>=0&&ctx->nfp_entries[nfp_fast_hit].key==nfp_signature.bytes);
        fprintf(stderr,"NATIVE_FUSION_FAST_KEY nodes=%d hit=%d canonical_hit=%d agree=%d cpu_ns=%llu\\n",cgraph->n_nodes,nfp_fast_hit>=0,nfp_hit>=0,fast_agree,(unsigned long long)nfp_fast_cpu);
        if(!fast_agree)fprintf(stderr,"NATIVE_FUSION_FAST_KEY_MISMATCH\\n");
'''+needle)
s=s.replace('ctx->nfp_entries.push_back({std::move(nfp_signature.bytes),std::move(nfp_observed)});','ctx->nfp_entries.push_back({std::move(nfp_signature.bytes),std::move(nfp_observed),std::move(nfp_signature.nodes),std::move(nfp_signature.uses),std::move(nfp_signature.snapshots),nfp_signature.epoch,nfp_signature.order,nfp_signature.disabled});')
s=s.replace('Metadata fingerprint andnativefusiondecisions shadowonly;', 'Fastsnapshotvalidator comparedtocanonicalfingerprint andnativefusiondecisions shadowonly;')
(p/'validator-builder-expanded.py').write_text(s)
exec(compile(s,str(p/'validator-builder-expanded.py'),'exec'),{'__file__':str(p/'build_validator.py')})
