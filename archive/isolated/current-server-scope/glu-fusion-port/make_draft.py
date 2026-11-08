from pathlib import Path
p=Path(__file__).resolve().parent
s=(p/'ggml-vulkan.base.cpp').read_text();old=(p/'ggml-vulkan.old-reference.cpp').read_text();h=(p/'ggml-vulkan-types.base.h').read_text()
def once(text,a,b):
 assert text.count(a)==1,(a[:100],text.count(a));return text.replace(a,b)
quant=old[old.index('static void nq_quantize('):old.index('static void ggml_vk_mul_mat_vec_q_f16(',old.index('static void nq_quantize('))]
s=once(s,'static void ggml_vk_mul_mat_vec_q_f16(',quant+'static void ggml_vk_mul_mat_vec_q_f16(')
needle='            ggml_vk_quantize_q8_1(ctx, subctx, d_Qy, d_Y, y_ne);';assert s.count(needle)==2
s=s.replace(needle,'            if(ctx->nq_skipped.count(src1)) nq_quantize(ctx,subctx,src1,d_Qy,d_Y,uint32_t(y_ne)); else ggml_vk_quantize_q8_1(ctx, subctx, d_Qy, d_Y, y_ne);',1)
needle='''    case GGML_OP_GLU:
        switch (ggml_get_glu_op(node)) {''';replacement='''    case GGML_OP_GLU:
        if (ctx->nq_plan.count(node)) {
            ctx->nq_skipped[node]=true;
            ctx->prealloc_y_last_pipeline_used=nullptr;
            ctx->prealloc_y_last_tensor_used=nullptr;
            ctx->prealloc_y_last_k_padded=false;
            break;
        }
        switch (ggml_get_glu_op(node)) {''';s=once(s,needle,replacement)
s=once(s,'    ggml_vk_cleanup(ctx);\n\n    delete ctx;', '    ggml_vk_cleanup(ctx);\n    if(ctx->nq_pipeline){ggml_vk_destroy_pipeline(ctx->device->device,ctx->nq_pipeline);ctx->nq_pipeline.reset();}\n\n    delete ctx;')
start=old.index('static bool nq_overlap(');end=old.index('static void nq_prepare_fast(',start);planner=old[start:end]
planner=planner.replace('static void nq_prepare_legacy(', 'static void nq_prepare(').replace('qt!=GGML_TYPE_Q5_K&&qt!=GGML_TYPE_Q4_0','qt!=GGML_TYPE_Q5_K&&qt!=GGML_TYPE_Q6_K&&qt!=GGML_TYPE_Q4_0').replace('(g->ne[1]!=1&&g->ne[1]!=2)', '(g->ne[1]!=5)')
planner=planner.replace('if(!ggml_vk_should_use_mmvq(ctx->device,w->ne[1],g->ne[1],g->ne[0],w->type))continue;', 'if(!ggml_vk_src1_prec_allows_q8(m)||!ggml_vk_should_use_mmvq(ctx->device,w->ne[1],g->ne[1],g->ne[0],w->type))continue;')
planner=planner.replace('if(getenv("GGML_VK_NATIVE_GLUQ_EXPAND_VIEWS")){', 'if(false){')
s=once(s,'static ggml_status ggml_backend_vk_graph_compute(ggml_backend_t backend, ggml_cgraph * cgraph) {',planner+'static ggml_status ggml_backend_vk_graph_compute(ggml_backend_t backend, ggml_cgraph * cgraph) {')
needle='    ggml_backend_vk_context * ctx = (ggml_backend_vk_context *)backend->context;\n\n    if (getenv("GGML_VK_GLU_CONSUMER_AUDIT")) {';s=once(s,needle,'    ggml_backend_vk_context * ctx = (ggml_backend_vk_context *)backend->context;\n    nq_prepare(ctx,cgraph);\n\n    if (getenv("GGML_VK_GLU_CONSUMER_AUDIT")) {')
s=once(s,'    ctx->last_total_flops = total_flops;','    GGML_ASSERT(ctx->nq_skipped.empty());\n    if(ctx->nq_fused_count&&getenv("GGML_VK_NATIVE_GLUQ_AUDIT"))fprintf(stderr,"NATIVE_GLUQ_FUSED %u\\n",ctx->nq_fused_count);\n    ctx->last_total_flops = total_flops;')
h=once(h,'struct ggml_backend_vk_context {','struct ggml_backend_vk_context {\n    vk_pipeline nq_pipeline;\n    std::unordered_map<const ggml_tensor*,const ggml_tensor*> nq_plan;\n    std::unordered_map<const ggml_tensor*,bool> nq_skipped;\n    unsigned nq_fused_count=0;')
(p/'ggml-vulkan.draft.cpp').write_text(s);(p/'ggml-vulkan-types.draft.h').write_text(h)
