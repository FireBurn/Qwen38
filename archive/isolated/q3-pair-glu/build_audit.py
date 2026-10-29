from pathlib import Path
import json,subprocess,shutil,difflib,hashlib
p=Path(__file__).resolve().parent;q=p.parent/'q3-pad112';old=q/'host-fast-guard-v2';h=p/'audit-host';h.mkdir(exist_ok=True);(h/'bin').mkdir(exist_ok=True)
for f in old.glob('*.h'):shutil.copy2(f,h/f.name)
s=(old/'ggml-vulkan.cpp').read_text();a=s.index('static ggml_status ggml_backend_vk_graph_compute(')
helper=r'''
// Read-only graph metadata diagnostic; no recording/planning changes.
static void qpg_graph_audit(const ggml_cgraph*graph){
    if(!getenv("GGML_VK_PAIR_AUDIT"))return;
    std::unordered_map<const ggml_tensor*,int>indices,uses;
    for(int i=0;i<graph->n_nodes;++i){indices[graph->nodes[i]]=i;for(int k=0;k<GGML_MAX_SRC;++k)if(graph->nodes[i]->src[k])++uses[graph->nodes[i]->src[k]];}
    int pairs=0,eligible=0;
    for(int i=0;i<graph->n_nodes;++i){
        const ggml_tensor*g=graph->nodes[i];if(g->op!=GGML_OP_GLU||ggml_get_glu_op(g)!=GGML_GLU_OP_SWIGLU||!g->src[0]||!g->src[1])continue;
        const ggml_tensor*a=g->src[0],*b=g->src[1];if(a->op!=GGML_OP_MUL_MAT||b->op!=GGML_OP_MUL_MAT||!a->src[0]||!a->src[1]||!b->src[0]||!b->src[1])continue;
        ++pairs;const ggml_tensor*wa=a->src[0],*wb=b->src[0];int ia=indices.count(a)?indices[a]:-1,ib=indices.count(b)?indices[b]:-1;
        const bool shared=a->src[1]==b->src[1];
        const bool contiguous=ggml_is_contiguous(wa)&&ggml_is_contiguous(wb)&&ggml_is_contiguous(a->src[1])&&ggml_is_contiguous(a)&&ggml_is_contiguous(b)&&ggml_is_contiguous(g);
        const bool no_views=!wa->view_src&&!wb->view_src&&!a->view_src&&!b->view_src&&!g->view_src;
        const bool same_shape=ggml_are_same_shape(wa,wb)&&ggml_are_same_shape(a,b)&&ggml_are_same_shape(a,g);
        const bool small=a->ne[1]>=1&&a->ne[1]<=2&&a->ne[2]==1&&a->ne[3]==1&&wa->ne[2]==1&&wa->ne[3]==1;
        const bool unique=uses[a]==1&&uses[b]==1&&!(a->flags&GGML_TENSOR_FLAG_OUTPUT)&&!(b->flags&GGML_TENSOR_FLAG_OUTPUT);
        const bool adjacent=ia>=0&&ib>=0&&std::max(ia,ib)==i-1&&std::min(ia,ib)==i-2;
        const bool ok=shared&&contiguous&&no_views&&same_shape&&small&&unique&&adjacent&&wa->type==GGML_TYPE_Q3_K&&wb->type==GGML_TYPE_Q3_K;
        eligible+=ok;
        fprintf(stderr,"PAIR_GRAPH glu=%d a=%d b=%d type_a=%s type_b=%s K=%lld R=%lld C=%lld shared=%d contiguous=%d no_views=%d same_shape=%d small=%d uses_a=%d uses_b=%d unique=%d adjacent=%d eligible=%d name=%s\n",i,ia,ib,ggml_type_name(wa->type),ggml_type_name(wb->type),(long long)wa->ne[0],(long long)wa->ne[1],(long long)a->ne[1],shared,contiguous,no_views,same_shape,small,uses[a],uses[b],unique,adjacent,ok,g->name);
    }
    fprintf(stderr,"PAIR_GRAPH_SUMMARY nodes=%d pairs=%d eligible=%d\n",graph->n_nodes,pairs,eligible);
}
'''
s=s[:a]+helper+s[a:];needle='    np_prepare_options(ctx);';s=s.replace(needle,'    qpg_graph_audit(cgraph);\n'+needle,1);(h/'ggml-vulkan.cpp').write_text(s)
cmds=json.loads((old/'build-argv.json').read_text());cmds=[[v.replace(str(old),str(h))for v in c]for c in cmds];(h/'build-argv.json').write_text(json.dumps(cmds,indent=2)+'\n')
for c in cmds:subprocess.run(c,check=True,cwd=h)
lib=h/'bin/libggml-vulkan.so.0.27.0'
for n in ['libggml-vulkan.so','libggml-vulkan.so.0']:
 f=h/'bin'/n
 if not f.exists():f.symlink_to(lib.name)
(p/'audit-host.patch').write_text(''.join(difflib.unified_diff((old/'ggml-vulkan.cpp').read_text().splitlines(True),s.splitlines(True),fromfile='a/ggml-vulkan.cpp',tofile='b/ggml-vulkan.cpp')))
(p/'audit-build.json').write_text(json.dumps(dict(library_sha256=hashlib.sha256(lib.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(s.encode()).hexdigest(),context_layout_unchanged=True,scope='Read-only graph metadata,mainTU rebuild withmatchingotherobjects/shaders. No numerical/recording/submission change;diagnostic only.'),indent=2)+'\n');print('PAIR_AUDIT_BUILT')
