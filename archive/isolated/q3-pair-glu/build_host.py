from pathlib import Path
import json,subprocess,shutil,hashlib,difflib
p=Path(__file__).resolve().parent;q=p.parent/'q3-pad112';old=q/'host-fast-guard-v2';template=q/'host-fast-guard';h=p/'host';h.mkdir(exist_ok=True);(h/'bin').mkdir(exist_ok=True)
for f in old.glob('*.h'):shutil.copy2(f,h/f.name)
f=h/'ggml-vulkan-types.h';s=f.read_text().replace('struct ggml_backend_vk_context {','''struct ggml_backend_vk_context {
    vk_pipeline qpg_matrix[2];
    vk_subbuffer qpg_gate{},qpg_up{};
    bool qpg_enabled=false,qpg_active=false,qpg_audit=false;
    std::string qpg_shader;
    uint64_t qpg_calls=0;
''',1);f.write_text(s)
s=(old/'ggml-vulkan.cpp').read_text();a=s.index('static void ggml_vk_mul_mat_vec_q_f16(')
helpers=r'''
static bool qpg_pipeline(ggml_backend_vk_context*ctx,uint32_t cols){
    auto&pl=ctx->qpg_matrix[cols-1];if(pl)return true;
    std::ifstream f(ctx->qpg_shader,std::ios::binary|std::ios::ate);if(!f)return false;size_t n=f.tellg();if(n<20||n%4)return false;std::vector<uint32_t>code(n/4);f.seekg(0);f.read((char*)code.data(),n);if(!f||code[0]!=0x07230203u)return false;
    pl=std::make_shared<vk_pipeline_struct>();pl->name="q3_pair_glu";pl->parameter_count=5;pl->push_constant_size=sizeof(vk_mat_vec_push_constants);pl->wg_denoms={1,1,1};pl->align=1;pl->initialized=true;
    ggml_vk_create_pipeline_func(ctx->device,pl,n,code.data(),"main",5,{1,1,1},{64,2,cols},true,true,64);return true;
}
static void qpg_dispatch(ggml_backend_vk_context*ctx,vk_context&subctx,const ggml_cgraph*graph,int idx){
    GGML_ASSERT(ctx->qpg_active&&ctx->num_additional_fused_ops==2);
    const ggml_tensor*g=graph->nodes[idx+2],*gate=g->src[0],*x=gate->src[1];
    const uint32_t k=x->ne[0],cols=x->ne[1],rows=g->ne[0];
    vk_subbuffer d_X=ggml_vk_tensor_subbuffer(ctx,x),d_D=ggml_vk_tensor_subbuffer(ctx,g);
    const uint64_t count=uint64_t(k)*cols;
    const uint64_t packed_size=ggml_vk_align_size(count,128)*ggml_type_size(GGML_TYPE_Q8_1)/ggml_blck_size(GGML_TYPE_Q8_1);
    GGML_ASSERT(packed_size<=ctx->device->properties.limits.maxStorageBufferRange);
    if(ctx->prealloc_size_y<packed_size){ctx->prealloc_size_y=packed_size;ggml_vk_preallocate_buffers(ctx,subctx);}
    vk_subbuffer d_Y={ctx->prealloc_y,0,ctx->prealloc_y->size};
    vk_pipeline quant=ggml_vk_get_quantize_pipeline(ctx,GGML_TYPE_Q8_1);ggml_pipeline_request_descriptor_sets(ctx,quant,1);
    if(ctx->prealloc_y_last_pipeline_used!=quant.get()||ctx->prealloc_y_last_tensor_used!=x||ctx->prealloc_y_last_k_padded){
        if(ctx->prealloc_y_need_sync)ggml_vk_sync_buffers(ctx,subctx);
        ggml_vk_quantize_q8_1(ctx,subctx,d_X,d_Y,count);
        ctx->prealloc_y_last_pipeline_used=quant.get();ctx->prealloc_y_last_tensor_used=x;ctx->prealloc_y_last_k_padded=false;
    }
    vk_pipeline&pl=ctx->qpg_matrix[cols-1];ggml_pipeline_request_descriptor_sets(ctx,pl,1);
    const vk_mat_vec_push_constants pc={k,k,k,2*rows,0,k,rows,0,0,1,1,1,1};
    ggml_vk_dispatch_pipeline(ctx,subctx,pl,{ctx->qpg_gate,d_Y,d_D,ctx->qpg_up,d_D},pc,{rows,1,1});
    ctx->prealloc_y_need_sync=true;++ctx->qpg_calls;
    if(ctx->qpg_audit)fprintf(stderr,"PAIR_GLU_DISPATCH K=%u rows=%u cols=%u gate=%s up=%s output=%s\n",k,rows,cols,gate->src[0]->name,g->src[1]->src[0]->name,g->name);
}
'''
s=s[:a]+helpers+s[a:]
a=s.index('\nbool ggml_vk_can_fuse_snake',s.index('bool ggml_vk_tensors_overlap('))
elig=r'''
// Strict three-node subgraph. Built-in graph use counts avoid a new per-graph index.
static bool qpg_can_fuse(ggml_backend_vk_context*ctx,const ggml_cgraph*graph,int i){
    if(!ctx->qpg_enabled||vk_perf_logger_enabled||i+2>=graph->n_nodes)return false;
    const ggml_tensor*a=graph->nodes[i],*b=graph->nodes[i+1],*g=graph->nodes[i+2];
    if(a->op!=GGML_OP_MUL_MAT||b->op!=GGML_OP_MUL_MAT||g->op!=GGML_OP_GLU||ggml_get_glu_op(g)!=GGML_GLU_OP_SWIGLU)return false;
    if(!((g->src[0]==a&&g->src[1]==b)||(g->src[0]==b&&g->src[1]==a)))return false;
    if(!ggml_node_has_n_uses(graph,i,1)||!ggml_node_has_n_uses(graph,i+1,1))return false;
    if(!a->src[0]||!b->src[0]||!a->src[1]||a->src[1]!=b->src[1])return false;
    const ggml_tensor*wa=a->src[0],*wb=b->src[0],*x=a->src[1];
    if(wa->type!=GGML_TYPE_Q3_K||wb->type!=GGML_TYPE_Q3_K||x->type!=GGML_TYPE_F32||a->type!=GGML_TYPE_F32||b->type!=GGML_TYPE_F32||g->type!=GGML_TYPE_F32)return false;
    if(ggml_get_op_params_i32(a,0)!=GGML_PREC_DEFAULT||ggml_get_op_params_i32(b,0)!=GGML_PREC_DEFAULT)return false;
    if(!ggml_are_same_shape(wa,wb)||!ggml_are_same_shape(a,b)||!ggml_are_same_shape(a,g))return false;
    if(wa->ne[0]!=x->ne[0]||wa->ne[1]!=g->ne[0]||x->ne[1]!=g->ne[1]||x->ne[0]%256||g->ne[1]<1||g->ne[1]>2||g->ne[0]<1||g->ne[0]>ctx->device->properties.limits.maxComputeWorkGroupCount[0])return false;
    for(const ggml_tensor*t:{wa,wb,x,a,b,g}){
        if(!t->buffer||!ggml_backend_buffer_is_vk(t->buffer)||!ggml_is_contiguous(t)||t->view_src||t->ne[2]!=1||t->ne[3]!=1||get_misalign_bytes(ctx,t)!=0||((t->flags&GGML_TENSOR_FLAG_COMPUTE)==0&&t!=wa&&t!=wb&&t!=x))return false;
    }
    if(!ggml_vk_should_use_mmvq(ctx->device,g->ne[0],g->ne[1],x->ne[0],GGML_TYPE_Q3_K))return false;
    // Include constant weights and activation: no destination overlap is allowed.
    for(const ggml_tensor*t:{wa,wb,x})if(ggml_vk_tensors_overlap(t,g,false))return false;
    if(ggml_nbytes(wa)>ctx->device->properties.limits.maxStorageBufferRange||ggml_nbytes(wb)>ctx->device->properties.limits.maxStorageBufferRange)return false;
    const uint32_t cols=g->ne[1];if(!qpg_pipeline(ctx,cols))return false;
    auto subctx=ggml_vk_get_compute_ctx(ctx);vk_pipeline original;
    auto gate=ggml_vk_tensor_subbuffer(ctx,g->src[0]->src[0]);auto up=ggml_vk_tensor_subbuffer(ctx,g->src[1]->src[0]);
    if(!np_weight(ctx,subctx,g->src[0]->src[0],cols,original,gate)||!np_weight(ctx,subctx,g->src[1]->src[0],cols,original,up))return false;
    ctx->qpg_gate=gate;ctx->qpg_up=up;return true;
}
'''
s=s[:a]+elig+s[a:]
needle='    nq_prepare(ctx,cgraph);';assert s.count(needle)==1;s=s.replace(needle,needle+r'''
    const char*qpg_path=getenv("GGML_VK_PAIR_GLU_SHADER");
    ctx->qpg_enabled=ctx->np_enabled&&qpg_path&&((!ctx->qpg_matrix[0]&&!ctx->qpg_matrix[1])||ctx->qpg_shader==qpg_path);
    if(ctx->qpg_enabled)ctx->qpg_shader=qpg_path;
    ctx->qpg_audit=getenv("GGML_VK_PAIR_GLU_AUDIT")!=nullptr;
''')
needle='        ctx->fused_rms_norm_mode = RMS_NORM_COUNT;\n        const char *fusion_string {};';assert s.count(needle)==1;s=s.replace(needle,'        ctx->qpg_active=false;\n'+needle)
needle='            if (num_adds) {';assert s.count(needle)==1;s=s.replace(needle,'''            if (qpg_can_fuse(ctx,cgraph,i)) {
                ctx->qpg_active=true;ctx->num_additional_fused_ops=2;fusion_string="Q3_PAIR_GLU";
                std::fill_n(op_srcs_fused_elementwise,3,false);
            } else if (num_adds) {''')
needle='                fusion_string = nullptr;';assert s.count(needle)==1;s=s.replace(needle,'                ctx->qpg_active=false;\n'+needle)
needle='    case GGML_OP_MUL_MAT:\n        ggml_vk_mul_mat(ctx, compute_ctx, cgraph, node_idx);';assert s.count(needle)==1;s=s.replace(needle,'''    case GGML_OP_MUL_MAT:
        if(ctx->qpg_active)qpg_dispatch(ctx,compute_ctx,cgraph,node_idx);
        else ggml_vk_mul_mat(ctx, compute_ctx, cgraph, node_idx);''')
needle='    for(auto&pl:ctx->np_matrix)';idx=s.index(needle);s=s[:idx]+'''    if(ctx->qpg_audit)fprintf(stderr,"PAIR_GLU_FINAL calls=%llu\\n",(unsigned long long)ctx->qpg_calls);
    ctx->qpg_gate.buffer.reset();ctx->qpg_up.buffer.reset();
    for(auto&pl:ctx->qpg_matrix)if(pl){ggml_vk_destroy_pipeline(ctx->device->device,pl);pl.reset();}
'''+s[idx:]
needle='        // Signal the almost_ready fence when the graph is mostly complete'
assert s.count(needle)==1
s=s.replace(needle,'''        if(ctx->qpg_active){for(int j=1;j<=2;++j){const auto extra=ggml_vk_get_node_flops(cgraph->nodes[i+j]);total_flops+=extra;batch_flops+=extra;}}
'''+needle)
(h/'ggml-vulkan.cpp').write_text(s)
for name in ['ggml-vulkan-buffers.cpp','ggml-vulkan-debug.cpp']:shutil.copy2(template/name,h/name)
cmds=json.loads((template/'build-argv.json').read_text());cmds=[[v.replace(str(template),str(h))for v in c]for c in cmds];(h/'build-argv.json').write_text(json.dumps(cmds,indent=2)+'\n')
for c in cmds:subprocess.run(c,check=True,cwd=h)
lib=h/'bin/libggml-vulkan.so.0.27.0'
for n in ['libggml-vulkan.so','libggml-vulkan.so.0']:
 f=h/'bin'/n
 if not f.exists():f.symlink_to(lib.name)
(p/'host.patch').write_text(''.join(difflib.unified_diff((old/'ggml-vulkan.cpp').read_text().splitlines(True),s.splitlines(True),fromfile='a/ggml-vulkan.cpp',tofile='b/ggml-vulkan.cpp')))
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
(p/'host-build.json').write_text(json.dumps(dict(library_sha256=sha(lib),sources={f.name:sha(f)for f in h.iterdir()if f.suffix in ['.cpp','.h']},context_layout_changed=True,all_three_host_TUs_rebuilt=True,scope='Opt-in boundedQ3gate/up/GLU fusion. Builtinusecounts/strictmetadataandmemoryoverlapeligibility,nativequantizer,paddedimmutablecache,reject/fallbackoneligibility/budgetfailure. Privatecontext-ownedpipelinesreleasedaftersynchronize. Numericalmodelqualification pending;no throughputclaim.'),indent=2)+'\n');print('PAIR_HOST_BUILT')
