from pathlib import Path
p=Path(__file__).resolve().parent
s=(p/'build_profile_host.py').read_text().replace("old=p/'host-arena';h=p/'host-profile'","old=p/'host-fast-guard-v2';h=p/'host-profile-v2'")
s=s.replace('NP_GRAPH,NP_EVENTS','NP_GRAPH,NP_ALL_REQUEST,NP_ALL_DISPATCH,NP_ALL_DESC_WRITE,NP_ALL_COMMANDS,NP_WAIT,NP_SYNC,NP_NODE,NP_EVENTS')
s=s.replace('"submit","graph"','"submit_nonempty","graph","all_request","all_dispatch","all_descriptor_write","all_commands","wait_fence","synchronize","build_node"')
s=s.replace('np_scope np_submit_measure(NP_SUBMIT);','np_scope np_submit_measure(NP_SUBMIT,!ctx->seqs.empty());')
s=s.replace('np_scope np_request_measure(NP_REQUEST,np_q3_name(pipeline->name));','np_scope np_all_request_measure(NP_ALL_REQUEST);\\n    np_scope np_request_measure(NP_REQUEST,np_q3_name(pipeline->name));')
s=s.replace('np_scope np_dispatch_measure(NP_DISPATCH,np_q3_name(pipeline->name));','np_scope np_all_dispatch_measure(NP_ALL_DISPATCH);\\n    np_scope np_dispatch_measure(NP_DISPATCH,np_q3_name(pipeline->name));')
s=s.replace('np_scope np_write_measure(NP_DESC_WRITE,np_q3_name(pipeline->name));','np_scope np_all_write_measure(NP_ALL_DESC_WRITE);\\n        np_scope np_write_measure(NP_DESC_WRITE,np_q3_name(pipeline->name));')
s=s.replace('np_scope np_commands_measure(NP_COMMANDS,np_q3_name(pipeline->name));','np_scope np_all_commands_measure(NP_ALL_COMMANDS);\\n    np_scope np_commands_measure(NP_COMMANDS,np_q3_name(pipeline->name));')
needle="(h/'ggml-vulkan.cpp').write_text(s)"
insert='''for signature,event in [('void ggml_vk_wait_for_fence(ggml_backend_vk_context * ctx) {','NP_WAIT'),('void ggml_vk_synchronize(ggml_backend_vk_context * ctx) {','NP_SYNC'),('bool ggml_vk_build_graph(ggml_backend_vk_context * ctx, ggml_cgraph * cgraph, int node_idx, ggml_tensor *node_begin, int node_idx_begin, bool last_node, bool almost_ready, bool submit){','NP_NODE')]:
 assert s.count(signature)==1
 s=s.replace(signature,signature+'\\n    np_scope np_extra_measure('+event+');')
'''
s=s.replace(needle,insert+needle)
s=s.replace("cmds=json.loads((old/'build-argv.json').read_text());cmds=[[v.replace(str(old),str(h))for v in c]for c in cmds]","template=p/'host-fast-guard';cmds=json.loads((template/'build-argv.json').read_text());cmds=[[v.replace(str(template),str(h))for v in c]for c in cmds]")
s=s.replace('shutil.copy2(old/name,h/name)','shutil.copy2(template/name,h/name)')
s=s.replace("cwd='${CLAUDE_WORKSPACE}/prodtree/build'","cwd=str(h)")
s=s.replace('Same shader and immutable-cache semantics as qualified arena host.','Same shader/cache semantics as qualified guard-v2; all host TUs rebuilt. Nested events overlap and include clock overhead; submit_nonempty excludes early returns. No throughput inference.')
(p/'build_profile_v2.py').write_text(s)
