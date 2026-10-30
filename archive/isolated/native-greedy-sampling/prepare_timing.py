from pathlib import Path
import ast
p=Path(__file__).resolve().parent;b=p.parent
s=(b/'run_native_default_timing.py').read_text().replace("project=base/'native-default-baseline'","project=base/'native-greedy-sampling'")
s=s.replace('stock400','temp_cpu').replace('q3_400','temp_gpu')
s=s.replace("env.update(GGML_VK_VISIBLE_DEVICES='1',GGML_VK_ALLOW_GRAPHICS_QUEUE='1',GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM='1',GGML_VK_SUBALLOCATION_BLOCK_SIZE='4294967296')","env.update(GGML_VK_VISIBLE_DEVICES='1')")
s=s.replace("out=project/'model-timing512'","qualification=json.loads((project/'sampling-qualification-summary.json').read_text());assert qualification['target_rows_per_mode']==530 and qualification['all_native_raw_bits_tokens_counters_identical']\nout=project/'model-timing512'",1)
s=s.replace("['model32','prompts128','populated-kv64','boundary128']","['sampling-model32','sampling-prompts128','sampling-populated-kv64','sampling-boundary128']")
a=s.index("frozen=base/");z=s.index('for folder in',a)
s=s[:a]+"native_reference=base/'native-default-baseline/model-timing512/20261030T061854Z/results.json'\nfm={'expected_token_prefix':json.loads(native_reference.read_text())[0]['tokens']}\n"+s[z:]
s=s.replace("active=[v for v in rr if v.get('candidate_q3')];assert active and all(not v['new_driver_errors']for v in active)","assert set(v['mode']for v in rr)==set(modes)and all(not v['new_driver_errors']for v in rr)")
a=s.index('assets=[');z=s.index('\n(out/',a)
s=s[:a]+"assets=[*stock_libraries,Path(__file__),project/'MODEL-TIMING-PLAN.md',project/'sampling-qualification-summary.json',project/'sampling-build.json',project/'sampling-audit-runner.cpp',base/'native-fusion-plan/sync-build.json',base/'native-fusion-plan/sync-runner.cpp',base/'native-fusion-plan/sync-bin/model-bench',native_reference,driver/'libvulkan_radeon.so']"+s[z:]
s=s.replace("selected_host=stock if mode.startswith('stock')else frozen","selected_host=stock")
s=s.replace(",GGML_VK_MAX_NODES_PER_SUBMIT='400')",")")
s='\n'.join(line for line in s.splitlines()if "if mode=='temp_gpu':trial.update(GGML_VK_Q3_PAD112"not in line)+'\n'
s=s.replace("if mode=='stock100':trial.pop('GGML_VK_MAX_NODES_PER_SUBMIT',None)","trial.pop('GGML_VK_MAX_NODES_PER_SUBMIT',None);assert all(trial.get(k)is None for k in ['GGML_VK_MAX_NODES_PER_SUBMIT','GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM','GGML_VK_PREFER_HOST_MEMORY','GGML_VK_ALLOW_GRAPHICS_QUEUE','GGML_VK_SUBALLOCATION_BLOCK_SIZE'])")
needle=' worker=threading.Thread(target=sample)';assert needle in s
s=s.replace(needle," if mode.startswith('temp_'):cmd+=['--samplers','temperature']\n if mode=='temp_gpu':cmd+=['--backend-sampling']\n"+needle)
s=s.replace("('submission','stock100','temp_cpu')","('cpu_chain','stock100','temp_cpu')").replace("('padding','temp_cpu','temp_gpu')","('backend_offload','temp_cpu','temp_gpu')")
s=s.replace('Unmodifiedstock100/stock400/frozenQ3cap400','DefaultCPUchain/temperatureCPU/temperatureGPU,stock100allmodes').replace('Unmodifiedstock100/temp_cpu/frozenQ3cap400','DefaultCPUchain/temperatureCPU/temperatureGPU,stock100allmodes')
s=s.replace('Fixed72native-defaultattribution','Fixed72restricted-target-sampling').replace('PrimaryQ3default400vsstock100,secondarycap/paddingdescriptivepair-specificmatchedsubsets.','PrimaryGPUtemperaturevsdefaultCPUchain,secondaryCPUchain/backendoffloaddescriptive.').replace('nodecapunsetforstock100','nodecapunsetforallmodes')
s=s.replace("'NATIVE_DEFAULT_BASELINE_DISCOVERY'","'NATIVE_SAMPLING_DISCOVERY'")
assert 'frozen'not in s and 'Q3_PAD'not in s
ast.parse(s);(b/'run_native_sampling_timing.py').write_text(s)
f=b/'run_private_guarded_batch.py';v=f.read_text();name='run_native_sampling_timing.py'
if repr(name)not in v:v=v.replace('allowed={','allowed={'+repr(name)+',',1)
ast.parse(v);f.write_text(v)
print('Prepared fixed72 sampling timing; stocklibraries/native100 defaults; no callback or profiler')
