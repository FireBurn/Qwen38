from pathlib import Path
import json
p=Path(__file__).resolve().parent;b=p.parent
s=(b/'run_q3_submission_cap_confirm.py').read_text().replace("project=base/'q3-pad112'","project=base/'native-gdn-reader-index'").replace("out=project/'submission-cap-confirm512'","out=project/'timing512'")
a=s.index("qualified=json.loads(");z=s.index("(out/'assets.json')",a)
s=s[:a]+'''for name in ['model32','prompts128','populated-kv64','boundary128']:
 check=json.loads((project/name/'comparison.json').read_text());assert check['all_requested_target_logit_bits_identical']and check['all_tokens_and_counters_identical']
 rr=json.loads((project/name/'checks.json').read_text());oracle=[v for v in rr if v.get('reader_mode')==2];assert oracle and all(v['oracle_checks']>0 and v['oracle_mismatches']==0 and v['verified_fused_decisions']>0 for v in oracle)
assert hashlib.sha256((project/'host/bin/libggml-vulkan.so.0.27.0').read_bytes()).hexdigest()==json.loads((project/'build.json').read_text())['library_sha256']
assets=[Path(__file__),project/'PLAN.md',project/'build.json',project/'host/bin/libggml-vulkan.so.0.27.0',base/'q3-pad112/qualified-20261029/manifest.json',base/'q3-pad112/qualified-20261029/shaders/pad16_subgroup_no_shmem.spv',base/'q3-pad112/qualified-20261029/shaders/repack.spv',base/'mtp-production-throughput/model-bench',base/'mtp-production-throughput/runner.cpp',stock/'bin/libllama.so.0.7.0',stock/'bin/libllama-common.so.0.7.0',driver/'libvulkan_radeon.so']
(out/'protocol.json').write_text(json.dumps(dict(plan=(project/'PLAN.md').read_text(),sequence=['legacy','indexed','indexed','legacy','indexed','legacy','legacy','indexed']*3,mode_legacy=0,mode_indexed=1,node_cap=400),indent=2)+'\\n')
'''+s[z:]
a=s.index('modes=');z=s.index('runtime_lib=',a);seq=[]
for i in range(6):seq+=['legacy','indexed','indexed','legacy']if i%2==0 else['indexed','legacy','legacy','indexed']
s=s[:a]+'modes='+repr(['legacy','indexed'])+';sequence='+repr(seq)+';rows=[]\n'+s[z:]
s=s.replace("selected_host=project/'qualified-20261029'","selected_host=project/'host'").replace("MESA_SHADER_CACHE_DIR=str(project/'model-timing-cache-pad')","MESA_SHADER_CACHE_DIR=str(base/'q3-pad112/model-timing-cache-pad')").replace("GGML_VK_MAX_NODES_PER_SUBMIT=mode[3:]","GGML_VK_MAX_NODES_PER_SUBMIT='400',GGML_VK_GDN_READER_INDEX='1'if mode=='indexed'else'0'").replace("GGML_VK_Q3_PAD112_DIR=str(selected_host/'shaders')","GGML_VK_Q3_PAD112_DIR=str(base/'q3-pad112/qualified-20261029/shaders')")
s=s.replace(' and max(clock.values())/min(clock.values())<=1.03','').replace("and all(r['clock_settled']for r in block)",'').replace("by['cap100']","by['legacy']").replace("selected_mode=modes[1]","selected_mode=modes[1]").replace('Same frozen Q3 library/shaders; only submission cap differs. Incremental versuscap100,not a direct stock contrast.','Same uninstrumented newlibrary,cap400,frozenQ3shaders;only readerindex mode0/1 differs. Incremental versusnewlegacy,not directstock or preservedfrozen contrast. Naturalclocks/power are outcomes.').replace('SUBMISSION_CAP_CONFIRMATION','GDN_READER_INDEX_CONFIRMATION')
s='\n'.join(x.rstrip()for x in s.splitlines())+'\n';(b/'run_gdn_reader_timing.py').write_text(s)
f=b/'run_private_guarded_batch.py';s=f.read_text().replace("'run_gdn_reader_model32.py'","'run_gdn_reader_model32.py','run_gdn_reader_timing.py'",1);f.write_text(s)
