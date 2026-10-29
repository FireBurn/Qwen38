from pathlib import Path
import re
p=Path(__file__).resolve().parent;b=p.parent;q=b/'q3-pad112'
s=(q/'build_profile_v2.py').read_text().replace("p=Path(__file__).resolve().parent;old=p/'host-fast-guard-v2';h=p/'host-profile-v2'","p=Path(__file__).resolve().parent;q=p.parent/'q3-pad112';old=q/'host-fast-guard-v2';h=p/'host'").replace("template=p/'host-fast-guard'","template=q/'host-fast-guard'")
s=s.replace('NP_NODE,NP_EVENTS','NP_NODE,NP_FUSION,NP_ALIAS,NP_DEPENDENCY,NP_GDN_SCAN,NP_EMPTY,NP_EVENTS').replace('"synchronize","build_node"','"synchronize","build_node","fusion_select","fusion_alias","dependency_check","gdn_state_scan","empty_scope"')
old='~np_scope(){if(active){auto we=np_clock(CLOCK_MONOTONIC),ce=np_clock(CLOCK_THREAD_CPUTIME_ID);np_profile_record(event,we-w,ce-c);}}'
new='void stop(){if(active){active=false;auto we=np_clock(CLOCK_MONOTONIC),ce=np_clock(CLOCK_THREAD_CPUTIME_ID);np_profile_record(event,we-w,ce-c);}}~np_scope(){stop();}'
assert old in s;s=s.replace(old,new)
needle="(h/'ggml-vulkan.cpp').write_text(s)"
code='''signature='static int ggml_vk_find_gdn_state_cpy(const struct ggml_cgraph * cgraph, int node_idx) {';assert s.count(signature)==1;s=s.replace(signature,signature+'\\n    np_scope np_gdn_scan(NP_GDN_SCAN);')
needle='        bool op_srcs_fused_elementwise[13];';assert s.count(needle)==1;s=s.replace(needle,'        {np_scope np_empty(NP_EMPTY); }\\n        np_scope np_fusion(NP_FUSION);\\n'+needle)
a=s.index('        // Check whether fusion would overwrite src operands');z=s.index('        // Signal the almost_ready fence',a)
part=s[a:z];assert part.count('        if (ctx->num_additional_fused_ops) {')==1;part=part.replace('        if (ctx->num_additional_fused_ops) {','        if (ctx->num_additional_fused_ops) {\\n            np_scope np_alias(NP_ALIAS);');s=s[:a]+part+'        np_fusion.stop();\\n'+s[z:]
needle='        auto const &overlaps_unsynced =';assert s.count(needle)==1;s=s.replace(needle,'        np_scope np_dependency(NP_DEPENDENCY);\\n'+needle)
needle='        const ggml_tensor*nq_g=node->op==GGML_OP_MUL_MAT?node->src[1]:nullptr;';assert s.count(needle)==1;s=s.replace(needle,'        np_dependency.stop();\\n'+needle)
'''
assert needle not in s or True
s=s.replace("(h/'ggml-vulkan.cpp').write_text(s)",code+"(h/'ggml-vulkan.cpp').write_text(s)")
(p/'build.py').write_text(s)
