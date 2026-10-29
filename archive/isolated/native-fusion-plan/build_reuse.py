from pathlib import Path
import json,subprocess,shutil,hashlib,difflib
p=Path(__file__).resolve().parent;old=p/'validator-host';q=p.parent/'q3-pad112';template=q/'host-fast-guard';h=p/'reuse-host';h.mkdir(exist_ok=True);(h/'bin').mkdir(exist_ok=True)
for f in old.glob('*.h'):shutil.copy2(f,h/f.name)
f=h/'ggml-vulkan-types.h';s=f.read_text().replace('uint64_t epoch=0;int order=0;bool disabled=false;};','uint64_t epoch=0;int order=0;bool disabled=false;std::vector<uint64_t>options;};')
s=s.replace('    std::vector<nfp_entry> nfp_entries;','''    std::vector<nfp_entry> nfp_entries;
    uint64_t nfp_total_hits=0,nfp_total_misses=0,nfp_total_used=0,nfp_total_checks=0,nfp_total_mismatches=0;
    bool nfp_ever_enabled=false;
''');f.write_text(s)
s=(old/'ggml-vulkan.cpp').read_text();s=s.replace('uint64_t epoch=0;int order=0;bool disabled=false;};','uint64_t epoch=0;int order=0;bool disabled=false;std::vector<uint64_t>options;};')
a=s.index('static bool nfp_fast_key(')
options=r'''static std::vector<uint64_t>nfp_options(ggml_backend_vk_context*ctx){
    const auto&d=ctx->device;std::vector<uint64_t>v={uint64_t(reinterpret_cast<uintptr_t>(d.get())),uint64_t(d->driver_id),uint64_t(d->multi_add),uint64_t(d->subgroup_arithmetic),uint64_t(d->subgroup_shuffle),uint64_t(d->subgroup_require_full_support),uint64_t(d->subgroup_size_log2),uint64_t(d->uma),uint64_t(d->properties.limits.maxPushConstantsSize),uint64_t(d->properties.limits.minStorageBufferOffsetAlignment),uint64_t(reinterpret_cast<uintptr_t>(d->pipeline_topk_radix_qsa.get()))};
    for(const auto&pl:d->pipeline_topk_f32)v.push_back(uint64_t(reinterpret_cast<uintptr_t>(pl.get())));return v;
}
static void nfp_apply(ggml_backend_vk_context*ctx,const ggml_cgraph*graph,const uint64_t*v){
    GGML_ASSERT(v[1]<13&&v[2]<8192&&v[8]<uint64_t(graph->n_nodes));
    ctx->num_additional_fused_ops=int(v[1]);ctx->fused_ops_write_mask=uint32_t(v[2]);
    ctx->fused_topk_moe_mode=decltype(ctx->fused_topk_moe_mode)(v[3]);ctx->fused_topk_moe_scale=v[4];ctx->fused_topk_qsa=v[5];ctx->fused_hc_post_gate=v[6];ctx->fused_rms_norm_mode=decltype(ctx->fused_rms_norm_mode)(v[7]);
    ctx->gdn_state_dst=nullptr;
    if(v[8]){auto*cpy=graph->nodes[v[8]];GGML_ASSERT(cpy->op==GGML_OP_CPY);ctx->gdn_state_dst=cpy->src[1];ctx->gdn_elided_cpys.insert(cpy);}
    GGML_ASSERT(uint64_t(reinterpret_cast<uintptr_t>(ctx->gdn_state_dst))==v[9]);
}
'''
s=s[:a]+options+s[a:]
s=s.replace('if(entry.nodes.size()!=size_t(graph->n_nodes)', 'if(entry.options!=nfp_options(ctx))return false;\n    if(entry.nodes.size()!=size_t(graph->n_nodes)')
s=s.replace('add(result.epoch);add(result.disabled);', 'add(result.epoch);add(result.disabled);result.options=nfp_options(ctx);for(uint64_t value:result.options)add(value);')
a=s.index('    const bool nfp_shadow=getenv(');z=s.index('    int last_node =',a)
s=s[:a]+r'''    const char*nfp_env=getenv("GGML_VK_FUSION_PLAN_REUSE");
    int nfp_mode=nfp_env&&nfp_env[0]=='1'?1:nfp_env&&nfp_env[0]=='2'?2:0;
    if(vk_perf_logger_enabled||getenv("GGML_VK_DEBUG_MARKERS")||ctx->device->uma||!ctx->nq_plan.empty())nfp_mode=0;
    const bool nfp_shadow=getenv("GGML_VK_FUSION_PLAN_SHADOW")!=nullptr||nfp_mode==2;
    const bool nfp_enabled=nfp_mode||nfp_shadow;
    const bool nfp_audit=getenv("GGML_VK_FUSION_PLAN_AUDIT")!=nullptr;
    nfp_key_result nfp_signature;std::vector<uint64_t>nfp_observed;int nfp_hit=-1,nfp_fast_hit=-1;uint64_t nfp_key_cpu=0,nfp_fast_cpu=0,nfp_cursor=0,nfp_used=0,nfp_checks=0,nfp_mismatches=0;bool nfp_key_built=false;
    if(nfp_enabled){
        const uint64_t start=nfp_cpu_ns();for(size_t k=0;k<ctx->nfp_entries.size();++k)if(nfp_fast_key(ctx,cgraph,ctx->nfp_entries[k])){nfp_fast_hit=k;break;}nfp_fast_cpu=nfp_cpu_ns()-start;
        if(nfp_shadow||nfp_fast_hit<0){const uint64_t begin=nfp_cpu_ns();nfp_signature=nfp_key(ctx,cgraph);nfp_key_built=true;if(nfp_signature.admissible)for(size_t k=0;k<ctx->nfp_entries.size();++k)if(ctx->nfp_entries[k].key==nfp_signature.bytes){nfp_hit=k;break;}nfp_key_cpu=nfp_cpu_ns()-begin;
            if(nfp_fast_hit>=0&&(nfp_hit<0||ctx->nfp_entries[nfp_fast_hit].key!=nfp_signature.bytes)){++nfp_mismatches;nfp_hit=-1;nfp_fast_hit=-1;fprintf(stderr,"NATIVE_FUSION_FAST_KEY_MISMATCH\n");}
        }else nfp_hit=nfp_fast_hit;
    }
    bool nfp_use=nfp_mode&&nfp_hit>=0;
'''+s[z:]
# Wrap the original selection/alias checks; actual native helpers/recording remain below.
a=s.index('        ctx->fused_topk_moe_mode = TOPK_MOE_COUNT;',s.index('    for (int i = 0; i < cgraph->n_nodes; i++)'))
z=s.index('        if(nfp_shadow){for(uint64_t value:',a)
native=s[a:z].replace('        const char *fusion_string {};','').replace('        int nfp_gdn_cpy=0;','')
wrap=r'''        const char*fusion_string{};int nfp_gdn_cpy=0;const uint64_t*nfp_cached=nullptr;
        if(nfp_use){const auto&plan=ctx->nfp_entries[nfp_hit].plan;if(nfp_cursor+10<=plan.size()&&plan[nfp_cursor]==uint64_t(i))nfp_cached=plan.data()+nfp_cursor;else{nfp_use=false;++nfp_mismatches;fprintf(stderr,"NATIVE_FUSION_RECORD_MISMATCH\n");}}
        if(nfp_cached&&nfp_mode==1){nfp_apply(ctx,cgraph,nfp_cached);nfp_gdn_cpy=nfp_cached[8];++nfp_used;}
        else {
'''+native+r'''        }
        if(nfp_cached&&nfp_mode==2){
            const uint64_t actual[]={uint64_t(i),uint64_t(ctx->num_additional_fused_ops),uint64_t(ctx->fused_ops_write_mask),uint64_t(ctx->fused_topk_moe_mode),uint64_t(ctx->fused_topk_moe_scale),uint64_t(ctx->fused_topk_qsa),uint64_t(ctx->fused_hc_post_gate),uint64_t(ctx->fused_rms_norm_mode),uint64_t(nfp_gdn_cpy),uint64_t(reinterpret_cast<uintptr_t>(ctx->gdn_state_dst))};
            ++nfp_checks;if(std::equal(actual,actual+10,nfp_cached)){nfp_apply(ctx,cgraph,nfp_cached);++nfp_used;}else{++nfp_mismatches;fprintf(stderr,"NATIVE_FUSION_ORACLE_MISMATCH\n");}
        }
'''
s=s[:a]+wrap+s[z:]
s=s.replace('if(nfp_shadow){for(uint64_t value:', 'if(nfp_enabled&&(nfp_shadow||nfp_hit<0)){for(uint64_t value:')
needle='        // Signal the almost_ready fence';s=s.replace(needle,'        if(nfp_enabled)nfp_cursor+=10;\n'+needle,1)
a=s.index('    if(nfp_shadow){\n        const bool match=');z=s.index('    ctx->last_total_flops',a)
s=s[:a]+r'''    if(nfp_enabled){
        if(nfp_use&&nfp_cursor!=ctx->nfp_entries[nfp_hit].plan.size()){++nfp_mismatches;fprintf(stderr,"NATIVE_FUSION_RECORD_COUNT_MISMATCH\n");}
        if(nfp_shadow&&nfp_hit>=0&&ctx->nfp_entries[nfp_hit].plan!=nfp_observed){++nfp_mismatches;fprintf(stderr,"NATIVE_FUSION_PLAN_MISMATCH\n");}
        if(nfp_key_built&&nfp_signature.admissible&&nfp_hit<0&&nfp_mismatches==0){if(ctx->nfp_entries.size()==8)ctx->nfp_entries.erase(ctx->nfp_entries.begin());ctx->nfp_entries.push_back({std::move(nfp_signature.bytes),std::move(nfp_observed),std::move(nfp_signature.nodes),std::move(nfp_signature.uses),std::move(nfp_signature.snapshots),nfp_signature.epoch,nfp_signature.order,nfp_signature.disabled,std::move(nfp_signature.options)});}
        ctx->nfp_total_hits+=nfp_hit>=0;ctx->nfp_total_misses+=nfp_hit<0;ctx->nfp_total_used+=nfp_used;ctx->nfp_total_checks+=nfp_checks;ctx->nfp_total_mismatches+=nfp_mismatches;ctx->nfp_ever_enabled|=nfp_mode!=0;
        if(nfp_audit)fprintf(stderr,"NATIVE_FUSION_REUSE mode=%d nodes=%d hit=%d used=%llu checks=%llu mismatches=%llu fast_cpu_ns=%llu key_cpu_ns=%llu\n",nfp_mode,cgraph->n_nodes,nfp_hit>=0,(unsigned long long)nfp_used,(unsigned long long)nfp_checks,(unsigned long long)nfp_mismatches,(unsigned long long)nfp_fast_cpu,(unsigned long long)nfp_key_cpu);
    }
'''+s[z:]
needle='    delete ctx;\n    delete backend;';assert s.count(needle)==1
s=s.replace(needle,r'''    if(ctx->nfp_ever_enabled)fprintf(stderr,"NATIVE_FUSION_REUSE_FINAL hits=%llu misses=%llu used=%llu checks=%llu mismatches=%llu\n",(unsigned long long)ctx->nfp_total_hits,(unsigned long long)ctx->nfp_total_misses,(unsigned long long)ctx->nfp_total_used,(unsigned long long)ctx->nfp_total_checks,(unsigned long long)ctx->nfp_total_mismatches);
'''+needle)
(h/'ggml-vulkan.cpp').write_text(s)
for name in ['ggml-vulkan-buffers.cpp','ggml-vulkan-debug.cpp']:shutil.copy2(template/name,h/name)
cmds=json.loads((template/'build-argv.json').read_text());cmds=[[v.replace(str(template),str(h))for v in c]for c in cmds];(h/'build-argv.json').write_text(json.dumps(cmds,indent=2)+'\n')
for c in cmds:subprocess.run(c,check=True,cwd=h)
lib=h/'bin/libggml-vulkan.so.0.27.0'
for n in ['libggml-vulkan.so','libggml-vulkan.so.0']:
 f=h/'bin'/n
 if not f.exists():f.symlink_to(lib.name)
(p/'reuse.patch').write_text(''.join(difflib.unified_diff((q/'host-fast-guard-v2/ggml-vulkan.cpp').read_text().splitlines(True),s.splitlines(True),fromfile='a/ggml-vulkan.cpp',tofile='b/ggml-vulkan.cpp')))
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'reuse-build.json').write_text(json.dumps(dict(library_sha256=sha(lib),sources={f.name:sha(f)for f in h.iterdir()if f.suffix in ['.h','.cpp']},all_three_host_TUs_rebuilt=True,scope='Opt-inCPUfusionplanreuse(mode1),fullnativeoracle(mode2). Strictsnapshot/deviceoptions/buffer-epoch validation,exactcanonicalkeys onmiss,8context-ownedCPUentries. Actualnormalnativehelpers/descriptors/barriers/submissions/shadersretained;noVkcommandreuse. Modelqualificationpending;no speedclaim.'),indent=2)+'\n');print('NATIVE_FUSION_REUSE_BUILT')
