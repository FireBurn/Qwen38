from pathlib import Path
p=Path(__file__).resolve().parent;b=p.parent
s=(b/'run_q3_submission_cap_model32.py').read_text().replace('from mixed_matrix_stream_settled3_common import competition','from native_observer_common import competition').replace("p=base/'q3-pad112';out=p/'submission-cap-model32'","p=base/'native-command-observer';out=p/'model32'").replace("host=p/'qualified-20261029'","host=p/'host'")
s=s.replace('for cap in [100,200,400]:\n mask=8',"for mode,mask in [('stock400',0),('observer400',8)]:\n cap=400")
s=s.replace("label='cap'+str(cap);trial=env.copy();","label=mode;trial=env.copy();selected_host=stock if mode=='stock400'else host;trial.update(LD_LIBRARY_PATH=str(selected_host/'bin')+':'+str(stock/'bin')+':'+str(base/'mtp-head-bound-audit/driver-deps')+':'+str(driver),EXPECTED_VK_BACKEND_PATH=str(selected_host/'bin/libggml-vulkan.so.0.27.0'));")
s=s.replace(" if mask==8:trial.update", " if mask==8:\n  obs=out/'observer';obs.mkdir();trial['GGML_VK_CMD_OBSERVER_DIR']=str(obs)\n if mask==8:trial.update",1).replace("GGML_VK_Q3_PAD112_DIR=str(host/'shaders')","GGML_VK_Q3_PAD112_DIR=str(base/'q3-pad112/qualified-20261029/shaders')").replace(";assert 'NQ_PLAN_EXACT'in text",";assert 'NQ_PLAN_EXACT'in text if mask==8 else True").replace('if competition()or time.monotonic()','if competition(child.pid)or time.monotonic()')
a=s.index('assets=[');z=s.index("(out/'assets.json')",a)
s=s[:a]+'''assert sha(host/'bin/libggml-vulkan.so.0.27.0')==json.loads((p/'build.json').read_text())['library_sha256']
assets=[Path(__file__),base/'native_observer_common.py',base/'production-native-shaders/model-audit-runner',base/'production-native-shaders/model-audit-runner.cpp',host/'bin/libggml-vulkan.so.0.27.0',stock/'bin/libggml-vulkan.so.0.27.0',stock/'bin/libllama.so.0.7.0',stock/'bin/libllama-common.so.0.7.0',driver/'libvulkan_radeon.so',base/'q3-pad112/qualified-20261029/manifest.json',base/'q3-pad112/qualified-20261029/shaders/pad16_subgroup_no_shmem.spv',base/'q3-pad112/qualified-20261029/shaders/repack.spv']
'''+s[z:]
s=s.replace('row=dict(cap=cap,','row=dict(mode=mode,cap=cap,').replace("(out/'cap100.bin')","(out/'stock400.bin')").replace("'arms':3","'arms':2").replace("['cap'+str(i)+'.bin'for i in [100,200,400]]","[i+'.bin'for i in ['stock400','observer400']]").replace("for cap in [100,200,400]:(out/('cap'+str(cap)+'.bin')).unlink()","for mode in ['stock400','observer400']:(out/(mode+'.bin')).unlink()")
s=s.replace('frozen paddedQ3 immutablecache,stockactivationpolicy,nodecaps100/200/400','Freshstock400 vscommand-observer400 withfrozenQ3shaders. Exacttargetbits only;capturedtraceisnotreplayidentityor speed proof').replace('SUBMISSION_CAP_MODEL_TARGET_LOGITS_ALL_EXACT','NATIVE_COMMAND_OBSERVER_MODEL32_TARGET_BITS_EXACT')
s+='''
graphs=[json.loads(x)for x in (out/'observer/graphs.jsonl').read_text().splitlines()];assert len(graphs)>=20 and sum(x['dispatches']for x in graphs)>1000
assert all(x['io_ok']and not x['dropped']for x in graphs),'Observer storage incomplete'
assert 'NCO_IO_FAILED'not in (out/'observer400.log').read_text()
(out/'observer-checks.json').write_text(json.dumps(dict(graphs=len(graphs),dispatches=sum(x['dispatches']for x in graphs),all_io_complete=True,scope='Observer output sanity;target-bit checks separate. Program repetition isnot safe replay or performance proof.'),indent=2)+'\\n')
'''
(b/'run_native_command_observer_model32.py').write_text(s)
f=b/'run_private_guarded_batch.py';s=f.read_text().replace("'run_q3_submission_system_effect.py'","'run_q3_submission_system_effect.py','run_native_command_observer_model32.py'",1);f.write_text(s)
