from pathlib import Path
import json,subprocess,shutil,hashlib,difflib
p=Path(__file__).resolve().parent;q=p.parent/'q3-pad112';old=q/'host-fast-guard-v2';template=q/'host-fast-guard';h=p/'shadow-host';h.mkdir(exist_ok=True);(h/'bin').mkdir(exist_ok=True)
for f in old.glob('*.h'):shutil.copy2(f,h/f.name)
f=h/'ggml-vulkan-types.h';s=f.read_text().replace('struct ggml_backend_vk_context {','''struct nfp_entry {std::vector<uint8_t> key;std::vector<uint64_t> plan;};
struct ggml_backend_vk_context {
    std::vector<nfp_entry> nfp_entries;
''',1);f.write_text(s)
s=(old/'ggml-vulkan.cpp').read_text();a=s.index('static ggml_status ggml_backend_vk_graph_compute(')
helpers=r'''
static uint64_t nfp_cpu_ns(){timespec t;clock_gettime(CLOCK_THREAD_CPUTIME_ID,&t);return uint64_t(t.tv_sec)*1000000000ull+t.tv_nsec;}
struct nfp_key_result {std::vector<uint8_t>bytes;size_t tensors=0;bool admissible=true;};
static nfp_key_result nfp_key(ggml_backend_vk_context*ctx,const ggml_cgraph*graph){
    nfp_key_result result;auto&key=result.bytes;key.reserve(size_t(graph->n_nodes)*512);
    auto add=[&](const auto&v){const auto*b=reinterpret_cast<const uint8_t*>(&v);key.insert(key.end(),b,b+sizeof(v));};
    auto ptr=[&](const void*v){add(reinterpret_cast<uintptr_t>(v));};
    add(graph->n_nodes);add(graph->order);add(ctx->device->buffer_destroy_count.load(std::memory_order_acquire));add(ctx->device->disable_fusion);
    std::vector<const ggml_tensor*>all;all.reserve(graph->n_nodes*2);std::unordered_set<const ggml_tensor*>seen;seen.reserve(graph->n_nodes*2);
    auto enqueue=[&](const ggml_tensor*t){if(t&&seen.insert(t).second)all.push_back(t);};
    for(int i=0;i<graph->n_nodes;++i){const auto*t=graph->nodes[i];ptr(t);add(ggml_node_get_use_count(graph,i));enqueue(t);}
    for(size_t i=0;i<all.size();++i){const auto*t=all[i];ptr(t);add(t->type);add(t->op);add(t->flags);add(t->ne);add(t->nb);add(t->op_params);ptr(t->data);ptr(t->view_src);add(t->view_offs);ptr(t->extra);if(t->extra)result.admissible=false;
        for(const auto*src:t->src){ptr(src);enqueue(src);}enqueue(t->view_src);
        const size_t name_length=strnlen(t->name,sizeof(t->name));add(name_length);key.insert(key.end(),reinterpret_cast<const uint8_t*>(t->name),reinterpret_cast<const uint8_t*>(t->name)+name_length);
        ptr(t->buffer);
        if(t->buffer){ptr(t->buffer->context);ptr(t->buffer->buft);add(ggml_backend_buffer_get_usage(t->buffer));
            const bool vk=ggml_backend_buffer_is_vk(t->buffer);add(vk);
            if(vk){const auto*bctx=static_cast<const ggml_backend_vk_buffer_context*>(t->buffer->context);ptr(bctx->dev_buffer.get());if(bctx->dev_buffer){add(bctx->dev_buffer->size);add(uint64_t(VkBuffer(bctx->dev_buffer->buffer)));}}
            else result.admissible=false;
        }
    }
    result.tensors=all.size();return result;
}
'''
s=s[:a]+helpers+s[a:]
needle='    int last_node = cgraph->n_nodes - 1;';assert s.count(needle)==1
s=s.replace(needle,'''    const bool nfp_shadow=getenv("GGML_VK_FUSION_PLAN_SHADOW")!=nullptr;
    nfp_key_result nfp_signature;std::vector<uint64_t>nfp_observed;int nfp_hit=-1;uint64_t nfp_key_cpu=0;
    if(nfp_shadow){const uint64_t start=nfp_cpu_ns();nfp_signature=nfp_key(ctx,cgraph);if(nfp_signature.admissible)for(size_t k=0;k<ctx->nfp_entries.size();++k)if(ctx->nfp_entries[k].key==nfp_signature.bytes){nfp_hit=k;break;}nfp_key_cpu=nfp_cpu_ns()-start;}
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
        if(nfp_signature.admissible&&nfp_hit<0){if(ctx->nfp_entries.size()==8)ctx->nfp_entries.erase(ctx->nfp_entries.begin());ctx->nfp_entries.push_back({std::move(nfp_signature.bytes),std::move(nfp_observed)});}
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
(p/'shadow.patch').write_text(''.join(difflib.unified_diff((old/'ggml-vulkan.cpp').read_text().splitlines(True),s.splitlines(True),fromfile='a/ggml-vulkan.cpp',tofile='b/ggml-vulkan.cpp')))
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'shadow-build.json').write_text(json.dumps(dict(library_sha256=sha(lib),sources={f.name:sha(f)for f in h.iterdir()if f.suffix in ['.h','.cpp']},all_three_host_TUs_rebuilt=True,scope='Metadata fingerprint andnativefusiondecisions shadowonly;no decisions/commands/submission/mathchangedorreused. Exactkey+planvectors,eightentriespercontext,nonVKbuffer/extra metadataexcludedfromadmission;allGPUownership remainsnative. No reuse/speedproof.'),indent=2)+'\n');print('NATIVE_FUSION_SHADOW_BUILT')
