from pathlib import Path
import json,subprocess,shutil,difflib,hashlib
p=Path(__file__).resolve().parent;q=p.parent/'q3-pad112';old=q/'host-fast-guard-v2';h=p/'host';h.mkdir(exist_ok=True);(h/'bin').mkdir(exist_ok=True)
for f in old.glob('*.h'):shutil.copy2(f,h/f.name)
s=(old/'ggml-vulkan.cpp').read_text();a=s.index('static int ggml_vk_find_gdn_state_cpy(');z=s.index('\nbool ggml_vk_can_fuse_snake',a);legacy=s[a:z];indexed=legacy.replace('ggml_vk_find_gdn_state_cpy(', 'ggml_vk_find_gdn_state_cpy_indexed(').replace('int node_idx) {','int node_idx, const gdn_reader_index& readers) {',1)
i=indexed.index('    for (int k = node_idx + 1; k < cgraph->n_nodes; ++k) {');j=indexed.index('    // the cache is now written',i)
indexed=indexed[:i]+'''    auto found=readers.find(gdn);
    if(found!=readers.end())for(const auto&ref:found->second){
        if(ref.node_idx<=node_idx||ref.node_idx==j)continue;
        const ggml_tensor*t=ref.tensor;
        if(t&&t!=src&&(t==gdn||t->view_src==gdn)&&t->view_offs>=tail_off)return 0;
    }
'''+indexed[j:]
defs='''// Per-graph metadata only: no cross-graph cache or Vulkan resource ownership.
struct gdn_reader_ref {int node_idx;const ggml_tensor*tensor;};
using gdn_reader_index=std::unordered_map<const ggml_tensor*,std::vector<gdn_reader_ref>>;
static gdn_reader_index ggml_vk_gdn_readers(const ggml_cgraph*graph){
    gdn_reader_index result;
    for(int i=0;i<graph->n_nodes;++i)for(int k=0;k<GGML_MAX_SRC;++k){
        const ggml_tensor*t=graph->nodes[i]->src[k];if(!t)continue;
        if(t->op==GGML_OP_GATED_DELTA_NET)result[t].push_back({i,t});
        if(t->view_src&&t->view_src->op==GGML_OP_GATED_DELTA_NET)result[t->view_src].push_back({i,t});
    }
    return result;
}
'''
s=s[:a]+defs+legacy+'\n'+indexed+s[z:]
a=s.index('static ggml_status ggml_backend_vk_graph_compute(');i=s.index('    int last_node =',a)
s=s[:i]+'''    // 0=legacy, 1=indexed release, 2=indexed with complete legacy decision oracle.
    const char*reader_option=getenv("GGML_VK_GDN_READER_INDEX");
    const int reader_mode=reader_option&&reader_option[0]=='1'?1:reader_option&&reader_option[0]=='2'?2:0;
    const gdn_reader_index gdn_readers=reader_mode?ggml_vk_gdn_readers(cgraph):gdn_reader_index{};
    uint64_t reader_checks=0,reader_mismatches=0,reader_calls=0,reader_fused=0;
'''+s[i:]
needle='            if (const int j_cpy = ggml_vk_find_gdn_state_cpy(cgraph, i); j_cpy > 0) {';assert s.count(needle)==1
s=s.replace(needle,'''            ++reader_calls;
            int j_cpy=reader_mode?ggml_vk_find_gdn_state_cpy_indexed(cgraph,i,gdn_readers):ggml_vk_find_gdn_state_cpy(cgraph,i);
            if(reader_mode==2){++reader_checks;const int reference=ggml_vk_find_gdn_state_cpy(cgraph,i);if(j_cpy!=reference){++reader_mismatches;fprintf(stderr,"GDN_READER_MISMATCH node=%d indexed=%d legacy=%d\\n",i,j_cpy,reference);j_cpy=reference;}}
            if (j_cpy > 0) {
                ++reader_fused;''')
needle='    ctx->last_total_flops = total_flops;';assert s.count(needle)==1;s=s.replace(needle,'''    if(reader_mode==2)fprintf(stderr,"GDN_READER_VERIFY nodes=%d roots=%zu calls=%llu fused=%llu checks=%llu mismatches=%llu\\n",cgraph->n_nodes,gdn_readers.size(),(unsigned long long)reader_calls,(unsigned long long)reader_fused,(unsigned long long)reader_checks,(unsigned long long)reader_mismatches);
'''+needle)
(h/'ggml-vulkan.cpp').write_text(s);cmds=json.loads((old/'build-argv.json').read_text());cmds=[[v.replace(str(old),str(h))for v in c]for c in cmds]
(h/'build-argv.json').write_text(json.dumps(cmds,indent=2)+'\n')
for c in cmds:subprocess.run(c,check=True,cwd=h)
lib=h/'bin/libggml-vulkan.so.0.27.0'
for n in ['libggml-vulkan.so','libggml-vulkan.so.0']:
 f=h/'bin'/n
 if not f.exists():f.symlink_to(lib.name)
(p/'reader-index.patch').write_text(''.join(difflib.unified_diff((old/'ggml-vulkan.cpp').read_text().splitlines(True),s.splitlines(True),fromfile='a/ggml-vulkan.cpp',tofile='b/ggml-vulkan.cpp')))
(p/'build.json').write_text(json.dumps(dict(library_sha256=hashlib.sha256(lib.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(s.encode()).hexdigest(),context_layout_unchanged=True,main_tu_rebuilt=True,other_host_objects='Reused exact guard-v2 matching buffer/debug objects;noheaderchange',scope='Per-graph reader index replacing repeated GDN tail scan;allother safety tests/helpers/shaderobjects unchanged. Mode2 compares every decision tolegacy,fallback onmismatch;release mode1 no oracle. Qualification pending.'),indent=2)+'\n');print('GDN_READER_INDEX_BUILT')
