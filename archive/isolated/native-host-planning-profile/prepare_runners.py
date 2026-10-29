from pathlib import Path
p=Path(__file__).resolve().parent;b=p.parent
s=(b/'run_native_command_observer_model32.py').read_text().replace("p=base/'native-command-observer'","p=base/'native-host-planning-profile'").replace("json.loads((p/'build.json')","json.loads((host/'build.json')").replace("'observer400'","'profile400'").replace('command-observer400','planning-profile400')
a=s.index(" if mask==8:\n  obs=");z=s.index(' if mask==8:trial.update',a);s=s[:a]+s[z:]
a=s.index('\ngraphs=[json.loads');s=s[:a]
(b/'run_native_planning_profile_model32.py').write_text(s)
s=(b/'run_q3_host_profile_cap400.py').read_text().replace('from mixed_matrix_stream_settled3_common import competition','from native_observer_common import competition')
s=s.replace("p=base/'q3-pad112';out=p/'host-profile-v2-cap400-runs'","p=base/'native-host-planning-profile';q=base/'q3-pad112';out=p/'runs'").replace("host=p/'host-profile-v2'","host=p/'host'")
for name in ['arena-inprocess/20261028T232836Z/checks.json','arena-model32/comparison.json','inprocess-plan.json','inprocess-shader-cache','pad16_subgroup_no_shmem.spv','profile-model-bench','profile-runner-build.json','profile-runner.cpp','repack.spv']:
 s=s.replace("p/"+repr(name),"q/"+repr(name))
s=s.replace('GGML_VK_Q3_PAD112_DIR=str(p)','GGML_VK_Q3_PAD112_DIR=str(q/\'qualified-20261029/shaders\')').replace("text.count('NP_PROFILE arm=')==120","text.count('NP_PROFILE arm=')==160")
(b/'run_native_planning_profile.py').write_text(s)
f=b/'run_private_guarded_batch.py';s=f.read_text().replace("'run_native_command_observer_model32.py'","'run_native_command_observer_model32.py','run_native_planning_profile_model32.py','run_native_planning_profile.py'",1);f.write_text(s)
