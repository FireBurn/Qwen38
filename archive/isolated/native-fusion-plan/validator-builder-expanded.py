from pathlib import Path
import json,subprocess,shutil,hashlib,difflib
p=Path(__file__).resolve().parent;q=p.parent/'q3-pad112';old=q/'host-fast-guard-v2';template=q/'host-fast-guard';h=p/'validator-host';h.mkdir(exist_ok=True);(h/'bin').mkdir(exist_ok=True)
for f in old.glob('*.h'):shutil.copy2(f,h/f.name)
f=h/'ggml-vulkan-types.h';s=f.read_text().replace('struct ggml_backend_vk_context {','''struct nfp_snapshot {const ggml_tensor*tensor;std::array<uint8_t,sizeof(ggml_tensor)>raw;uintptr_t buffer_context=0,buffer_type=0,device_buffer=0;uint64_t buffer_handle=0,buffer_size=0;int usage=0;};
struct nfp_entry {std::vector<uint8_t>key;std::vector<uint64_t>plan;std::vector<const ggml_tensor*>nodes;std::vector<int32_t>uses;std::vector<nfp_snapshot>snapshots;uint64_t epoch=0;int order=0;bool disabled=false;};
struct ggml_backend_vk_context {
    std::vector<nfp_entry> nfp_entries;
''',1);f.write_text(s)
s=(old/'ggml-vulkan.cpp').read_text();a=s.index('static ggml_status ggml_backend_vk_graph_compute(')
helpers=r'''
static uint64_t nfp_cpu_ns(){timespec t;clock_gettime(CLOCK_THREAD_CPUTIME_ID,&t);return uint64_t(t.tv_sec)*1000000000ull+t.tv_nsec;}
struct nfp_key_result {std::vector<uint8_t>bytes;size_t tensors=0;bool admissible=true;std::vector<const ggml_tensor*>nodes;std::vector<int32_t>uses;std::vector<nfp_snapshot>snapshots;uint64_t epoch=0;int order=0;bool disabled=false;};
static bool nfp_fast_key(ggml_backend_vk_context*ctx,const ggml_cgraph*graph,const nfp_entry&entry){
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
    result.epoch=ctx->device->buffer_destroy_count.load(std::memory_order_acquire);result.order=graph->order;result.disabled=ctx->device->disable_fusion;add(graph->n_nodes);add(graph->order);add(result.epoch);add(result.disabled);
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
'''
s=s[:a]+helpers+s[a:]
needle='    int last_node = cgraph->n_nodes - 1;';assert s.count(needle)==1
s=s.replace(needle,'''    const bool nfp_shadow=getenv("GGML_VK_FUSION_PLAN_SHADOW")!=nullptr;
    nfp_key_result nfp_signature;std::vector<uint64_t>nfp_observed;int nfp_hit=-1,nfp_fast_hit=-1;uint64_t nfp_key_cpu=0,nfp_fast_cpu=0;
    if(nfp_shadow){const uint64_t fast_start=nfp_cpu_ns();for(size_t k=0;k<ctx->nfp_entries.size();++k)if(nfp_fast_key(ctx,cgraph,ctx->nfp_entries[k])){nfp_fast_hit=k;break;}nfp_fast_cpu=nfp_cpu_ns()-fast_start;const uint64_t start=nfp_cpu_ns();nfp_signature=nfp_key(ctx,cgraph);if(nfp_signature.admissible)for(size_t k=0;k<ctx->nfp_entries.size();++k)if(ctx->nfp_entries[k].key==nfp_signature.bytes){nfp_hit=k;break;}nfp_key_cpu=nfp_cpu_ns()-start;}
'''+needle)
needle='        ctx->gdn_state_dst = nullptr;';assert s.count(needle)==1;s=s.replace(needle,needle+'\n        int nfp_gdn_cpy=0;')
needle='                ctx->gdn_state_dst = cgraph->nodes[j_cpy]->src[1];';assert s.count(needle)==1;s=s.replace(needle,needle+'\n                nfp_gdn_cpy=j_cpy;')
needle='        // Signal the almost_ready fence when the graph is mostly complete';assert s.count(needle)==1
s=s.replace(needle,'''        if(nfp_shadow){for(uint64_t value:{uint64_t(i),uint64_t(ctx->num_additional_fused_ops),uint64_t(ctx->fused_ops_write_mask),uint64_t(ctx->fused_topk_moe_mode),uint64_t(ctx->fused_topk_moe_scale),uint64_t(ctx->fused_topk_qsa),uint64_t(ctx->fused_hc_post_gate),uint64_t(ctx->fused_rms_norm_mode),uint64_t(nfp_gdn_cpy),uint64_t(reinterpret_cast<uintptr_t>(ctx->gdn_state_dst))})nfp_observed.push_back(value);}
'''+needle)
needle='    ctx->last_total_flops = total_flops;';assert s.count(needle)==1
s=s.replace(needle,'''    if(nfp_shadow){
        const bool match=nfp_hit<0||ctx->nfp_entries[nfp_hit].plan==nfp_observed;
        fprintf(stderr,"NATIVE_FUSION_SHADOW nodes=%d tensors=%zu key_bytes=%zu admissible=%d hit=%d match=%d plan_records=%zu key_cpu_ns=%llu destroy_epoch=%llu\\n",cgraph->n_nodes,nfp_signature.tensors,nfp_signature.bytes.size(),nfp_signature.admissible,nfp_hit>=0,match,nfp_observed.size()/10,(unsigned long long)nfp_key_cpu,(unsigned long long)ctx->device->buffer_destroy_count.load());
        if(!match)fprintf(stderr,"NATIVE_FUSION_PLAN_MISMATCH\\n");
        const bool fast_agree=nfp_fast_hit<0||(nfp_hit>=0&&ctx->nfp_entries[nfp_fast_hit].key==nfp_signature.bytes);
        fprintf(stderr,"NATIVE_FUSION_FAST_KEY nodes=%d hit=%d canonical_hit=%d agree=%d cpu_ns=%llu\\n",cgraph->n_nodes,nfp_fast_hit>=0,nfp_hit>=0,fast_agree,(unsigned long long)nfp_fast_cpu);
        if(!fast_agree)fprintf(stderr,"NATIVE_FUSION_FAST_KEY_MISMATCH\\n");
        if(nfp_signature.admissible&&nfp_hit<0){if(ctx->nfp_entries.size()==8)ctx->nfp_entries.erase(ctx->nfp_entries.begin());ctx->nfp_entries.push_back({std::move(nfp_signature.bytes),std::move(nfp_observed),std::move(nfp_signature.nodes),std::move(nfp_signature.uses),std::move(nfp_signature.snapshots),nfp_signature.epoch,nfp_signature.order,nfp_signature.disabled});}
    }
'''+needle)
(h/'ggml-vulkan.cpp').write_text(s)
for name in ['ggml-vulkan-buffers.cpp','ggml-vulkan-debug.cpp']:shutil.copy2(template/name,h/name)
cmds=json.loads((template/'build-argv.json').read_text());cmds=[[v.replace(str(template),str(h))for v in c]for c in cmds];(h/'build-argv.json').write_text(json.dumps(cmds,indent=2)+'\n')
for c in cmds:subprocess.run(c,check=True,cwd=h)
lib=h/'bin/libggml-vulkan.so.0.27.0'
for n in ['libggml-vulkan.so','libggml-vulkan.so.0']:
 f=h/'bin'/n
 if not f.exists():f.symlink_to(lib.name)
(p/'validator.patch').write_text(''.join(difflib.unified_diff((old/'ggml-vulkan.cpp').read_text().splitlines(True),s.splitlines(True),fromfile='a/ggml-vulkan.cpp',tofile='b/ggml-vulkan.cpp')))
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'validator-build.json').write_text(json.dumps(dict(library_sha256=sha(lib),sources={f.name:sha(f)for f in h.iterdir()if f.suffix in ['.h','.cpp']},all_three_host_TUs_rebuilt=True,scope='Fastsnapshotvalidator comparedtocanonicalfingerprint andnativefusiondecisions shadowonly;no decisions/commands/submission/mathchangedorreused. Exactkey+planvectors,eightentriespercontext,nonVKbuffer/extra metadataexcludedfromadmission;allGPUownership remainsnative. No reuse/speedproof.'),indent=2)+'\n');print('NATIVE_FUSION_VALIDATOR_BUILT')
