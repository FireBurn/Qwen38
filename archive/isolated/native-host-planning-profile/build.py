from pathlib import Path
import json,subprocess,shutil,hashlib
p=Path(__file__).resolve().parent;q=p.parent/'q3-pad112';old=q/'host-fast-guard-v2';h=p/'host';h.mkdir(exist_ok=True);(h/'bin').mkdir(exist_ok=True)
for f in old.glob('*.h'):shutil.copy2(f,h/f.name)
(h/'np-profile.h').write_text('''#pragma once
#include <cstdint>
#include <ctime>
#include <string>
enum np_event {NP_GATE,NP_MMVQ,NP_REQUEST,NP_DISPATCH,NP_DESC_WRITE,NP_COMMANDS,NP_SUBMIT,NP_GRAPH,NP_ALL_REQUEST,NP_ALL_DISPATCH,NP_ALL_DESC_WRITE,NP_ALL_COMMANDS,NP_WAIT,NP_SYNC,NP_NODE,NP_FUSION,NP_ALIAS,NP_DEPENDENCY,NP_GDN_SCAN,NP_EMPTY,NP_EVENTS};
extern bool np_profile_active();
extern void np_profile_record(unsigned,uint64_t,uint64_t);
inline uint64_t np_clock(clockid_t id){timespec t;clock_gettime(id,&t);return uint64_t(t.tv_sec)*1000000000+uint64_t(t.tv_nsec);}
struct np_scope {unsigned event;bool active;uint64_t w=0,c=0;np_scope(unsigned e,bool eligible=true):event(e),active(eligible&&np_profile_active()){if(active){c=np_clock(CLOCK_THREAD_CPUTIME_ID);w=np_clock(CLOCK_MONOTONIC);}}void stop(){if(active){active=false;auto we=np_clock(CLOCK_MONOTONIC),ce=np_clock(CLOCK_THREAD_CPUTIME_ID);np_profile_record(event,we-w,ce-c);}}~np_scope(){stop();}};
inline bool np_q3_name(const std::string&n){return n=="q3_pad112_matrix"||n=="mul_mat_vec_q3_k_q8_1_f32";}
''')
(h/'np-profile.cpp').write_text('''#include "np-profile.h"
#include <atomic>
#include <cstdio>
struct alignas(64) metric {std::atomic<uint64_t> count{0},wall{0},cpu{0};};
static metric values[NP_EVENTS];static std::atomic<bool> enabled{false};
bool np_profile_active(){return enabled.load(std::memory_order_relaxed);}
void np_profile_record(unsigned e,uint64_t wall,uint64_t cpu){values[e].count.fetch_add(1,std::memory_order_relaxed);values[e].wall.fetch_add(wall,std::memory_order_relaxed);values[e].cpu.fetch_add(cpu,std::memory_order_relaxed);}
extern "C" __attribute__((visibility("default"))) void np_profile_select(int arm){enabled.store(false);for(auto&v:values){v.count=0;v.wall=0;v.cpu=0;}enabled.store(arm>=0);}
extern "C" __attribute__((visibility("default"))) void np_profile_dump(int arm){enabled.store(false);const char*names[]={"gate","mmvq","request","dispatch","descriptor_write","commands","submit_nonempty","graph","all_request","all_dispatch","all_descriptor_write","all_commands","wait_fence","synchronize","build_node","fusion_select","fusion_alias","dependency_check","gdn_state_scan","empty_scope"};for(unsigned i=0;i<NP_EVENTS;++i){fprintf(stderr,"NP_PROFILE arm=%d event=%s count=%llu wall_ns=%llu cpu_ns=%llu",arm,names[i],(unsigned long long)values[i].count.load(),(unsigned long long)values[i].wall.load(),(unsigned long long)values[i].cpu.load());fputc(10,stderr);}}
''')
s=(old/'ggml-vulkan.cpp').read_text();s='#include "np-profile.h"\n'+s
needle='static bool np_weight(ggml_backend_vk_context*ctx,vk_context&subctx,const ggml_tensor*w,uint32_t cols,vk_pipeline&pipeline,vk_subbuffer&weights){';assert s.count(needle)==1;s=s.replace(needle,needle+'\n    np_scope np_measure(NP_GATE,w->type==GGML_TYPE_Q3_K&&cols<=2);')
a=s.index('static void ggml_vk_mul_mat_vec_q_f16(');i=s.index('    VK_LOG_DEBUG(',a);s=s[:i]+'    np_scope np_mmvq_measure(NP_MMVQ,src0->type==GGML_TYPE_Q3_K&&src1->ne[1]<=2);\n'+s[i:]
needle='void ggml_pipeline_request_descriptor_sets(ggml_backend_vk_context *ctx, vk_pipeline& pipeline, uint32_t n) {';assert s.count(needle)==1;s=s.replace(needle,needle+'\n    np_scope np_all_request_measure(NP_ALL_REQUEST);\n    np_scope np_request_measure(NP_REQUEST,np_q3_name(pipeline->name));')
needle='void ggml_vk_submit(vk_context& ctx, vk::Fence fence) {';assert s.count(needle)==1;s=s.replace(needle,needle+'\n    np_scope np_submit_measure(NP_SUBMIT,!ctx->seqs.empty());')
needle='static ggml_status ggml_backend_vk_graph_compute(ggml_backend_t backend, ggml_cgraph * cgraph) {';assert s.count(needle)==1;s=s.replace(needle,needle+'\n    np_scope np_graph_measure(NP_GRAPH);')
for signature,event in [('void ggml_vk_wait_for_fence(ggml_backend_vk_context * ctx) {','NP_WAIT'),('void ggml_vk_synchronize(ggml_backend_vk_context * ctx) {','NP_SYNC'),('bool ggml_vk_build_graph(ggml_backend_vk_context * ctx, ggml_cgraph * cgraph, int node_idx, ggml_tensor *node_begin, int node_idx_begin, bool last_node, bool almost_ready, bool submit){','NP_NODE')]:
 assert s.count(signature)==1
 s=s.replace(signature,signature+'\n    np_scope np_extra_measure('+event+');')
signature='static int ggml_vk_find_gdn_state_cpy(const struct ggml_cgraph * cgraph, int node_idx) {';assert s.count(signature)==1;s=s.replace(signature,signature+'\n    np_scope np_gdn_scan(NP_GDN_SCAN);')
needle='        bool op_srcs_fused_elementwise[13];';assert s.count(needle)==1;s=s.replace(needle,'        {np_scope np_empty(NP_EMPTY); }\n        np_scope np_fusion(NP_FUSION);\n'+needle)
a=s.index('        // Check whether fusion would overwrite src operands');z=s.index('        // Signal the almost_ready fence',a)
part=s[a:z];assert part.count('        if (ctx->num_additional_fused_ops) {')==1;part=part.replace('        if (ctx->num_additional_fused_ops) {','        if (ctx->num_additional_fused_ops) {\n            np_scope np_alias(NP_ALIAS);');s=s[:a]+part+'        np_fusion.stop();\n'+s[z:]
needle='        auto const &overlaps_unsynced =';assert s.count(needle)==1;s=s.replace(needle,'        np_scope np_dependency(NP_DEPENDENCY);\n'+needle)
needle='        const ggml_tensor*nq_g=node->op==GGML_OP_MUL_MAT?node->src[1]:nullptr;';assert s.count(needle)==1;s=s.replace(needle,'        np_dependency.stop();\n'+needle)
(h/'ggml-vulkan.cpp').write_text(s)
f=h/'ggml-vulkan-common.h';s=f.read_text();s='#include "np-profile.h"\n'+s
needle='    const uint32_t wg0 = CEIL_DIV(elements[0], pipeline->wg_denoms[0]);';assert s.count(needle)==1;s=s.replace(needle,'    np_scope np_all_dispatch_measure(NP_ALL_DISPATCH);\n    np_scope np_dispatch_measure(NP_DISPATCH,np_q3_name(pipeline->name));\n'+needle)
needle='    if (!same) {';assert s.count(needle)==1;s=s.replace(needle,needle+'\n        np_scope np_all_write_measure(NP_ALL_DESC_WRITE);\n        np_scope np_write_measure(NP_DESC_WRITE,np_q3_name(pipeline->name));')
needle='    subctx->s->buffer->buf.pushConstants(';assert s.count(needle)==1;s=s.replace(needle,'    np_scope np_all_commands_measure(NP_ALL_COMMANDS);\n    np_scope np_commands_measure(NP_COMMANDS,np_q3_name(pipeline->name));\n'+needle)
f.write_text(s)
template=q/'host-fast-guard';cmds=json.loads((template/'build-argv.json').read_text());cmds=[[v.replace(str(template),str(h))for v in c]for c in cmds]
for name in ['ggml-vulkan-buffers.cpp','ggml-vulkan-debug.cpp']:shutil.copy2(template/name,h/name)
extra=[cmds[0][0],'-std=c++17','-stdlib=libc++','-O3','-fPIC','-fvisibility=hidden','-c',str(h/'np-profile.cpp'),'-o',str(h/'np-profile.cpp.o')];cmds.insert(3,extra);cmds[-1].insert(cmds[-1].index('-lvulkan'),str(h/'np-profile.cpp.o'))
(h/'build-argv.json').write_text(json.dumps(cmds,indent=2)+chr(10))
for cmd in cmds:subprocess.run(cmd,check=True,cwd=str(h))
lib=h/'bin/libggml-vulkan.so.0.27.0'
for name in ['libggml-vulkan.so','libggml-vulkan.so.0']:
 f=h/'bin'/name
 if not f.exists():f.symlink_to(lib.name)
(h/'build.json').write_text(json.dumps({'library_sha256':hashlib.sha256(lib.read_bytes()).hexdigest(),'sources':{f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in h.glob('*')if f.suffix in ['.h','.cpp']},'scope':'Opt-in scoped host CPU/wall counters for triage only. Timers are intrusive; not a throughput candidate. Same shader/cache semantics as qualified guard-v2; all host TUs rebuilt. Nested events overlap and include clock overhead; submit_nonempty excludes early returns. No throughput inference.'},indent=2)+chr(10))
