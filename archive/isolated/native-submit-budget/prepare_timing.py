from pathlib import Path
p=Path(__file__).resolve().parent;b=p.parent;s=(b/'run_native_fusion_reuse_timing.py').read_text().replace("project=base/'native-fusion-plan'","project=base/'native-submit-budget'")
s=s.replace("project/('reuse-'+name)","project/name").replace("project/'reuse-host","project/'host").replace("project/'reuse-build.json'","project/'build.json'")
a=s.index("for folder in ['reuse-model32'");z=s.index('assets=[',a);s=s[:a]+"for folder in ['model32','prompts128','populated-kv64','boundary128']:\n rr=json.loads((project/folder/'checks.json').read_text());active=[v for v in rr if v.get('submit_divisor')==20];assert active and all(v['budget_records']for v in active)\n"+s[z:]
for f in ['sync-build.json','sync-runner.cpp','sync-bin/model-bench']:s=s.replace("project/'"+f+"'","base/'native-fusion-plan/"+f+"'")
s=s.replace("if mode=='reuse':trial['GGML_VK_FUSION_PLAN_REUSE']='1'","if mode=='budget20':trial['GGML_VK_NATIVE_SUBMIT_DIVISOR']='20'")
a=s.index(' finals=[');z=s.index(' encode_match=',a);s=s[:a]+" assert 'NATIVE_SUBMIT_BUDGET 'not in text,'Pergraph audit enabled during timing'\n"+s[z:];s=s.replace('row=dict(reuse_final=finals,','row=dict(')
s=s.replace("'reuse'","'budget20'").replace('mode_reuse=','mode_budget20=').replace('CPUfusionplanreuse','nativeinitialsubmitdivisor20').replace('CPUplanhost','nativebudgethost').replace('privateCPUplanreusehost','privatenativesubmitbudgethost').replace('NATIVE_FUSION_PLAN_MODEL_DISCOVERY','NATIVE_SUBMIT_BUDGET_MODEL_DISCOVERY')
(b/'run_native_submit_budget_timing.py').write_text(s);f=b/'run_private_guarded_batch.py';f.write_text(f.read_text().replace('allowed={',"allowed={'run_native_submit_budget_timing.py',",1))
