from pathlib import Path
p=Path(__file__).resolve().parent;b=p.parent
s=(b/'run_q3_submission_cap_prompts128.py').read_text().replace('from mixed_matrix_stream_settled3_common import competition','from native_observer_common import competition').replace("p=base/'q3-pad112';out=p/'submission-cap-prompts128'","p=base/'native-command-observer';out=p/'prompts128'").replace("host=p/'qualified-20261029'","host=p/'host'").replace("GGML_VK_Q3_PAD112_DIR=str(host/'shaders')","GGML_VK_Q3_PAD112_DIR=str(base/'q3-pad112/qualified-20261029/shaders')").replace('if competition()or time.monotonic()','if competition(child.pid)or time.monotonic()')
needle='  if mask==8:trial.update';assert needle in s;s=s.replace(needle,"  obs=folder/'observer';obs.mkdir();trial['GGML_VK_CMD_OBSERVER_DIR']=str(obs)\n"+needle,1)
s+='''
for case,prompt in cases:
 obs=out/case/'observer';graphs=[json.loads(x)for x in(obs/'graphs.jsonl').read_text().splitlines()];assert len(graphs)>=20 and all(x['io_ok']and not x['dropped']for x in graphs)
(out/'observer-checks.json').write_text(json.dumps(dict(all_observer_io_complete=True,cases=[x[0]for x in cases],scope='No replay or performance claim'),indent=2)+'\\n')
'''
(b/'run_native_command_observer_prompts128.py').write_text(s)
s=(b/'run_q3_submission_populated_kv64.py').read_text().replace('from mixed_matrix_stream_settled3_common import competition','from native_observer_common import competition').replace("p=base/'q3-pad112';out=p/'submission-populated-kv64'","p=base/'native-command-observer';out=p/'populated-kv64'").replace("host=p/'qualified-20261029'","host=p/'host'").replace("for mode,cap in [('stock100',100),('frozen100',100),('frozen400',400)]:","for mode,cap in [('stock400',400),('observer400',400)]:").replace("mode=='stock100'","mode=='stock400'").replace("mode!='stock100'","mode!='stock400'").replace('if competition()or time.monotonic()','if competition(child.pid)or time.monotonic()').replace("GGML_VK_Q3_PAD112_DIR=str(host/'shaders')","GGML_VK_Q3_PAD112_DIR=str(base/'q3-pad112/qualified-20261029/shaders')")
needle=' if mask==8:trial.update';assert needle in s;s=s.replace(needle," if mask==8:\n  obs=out/'observer';obs.mkdir();trial['GGML_VK_CMD_OBSERVER_DIR']=str(obs)\n"+needle,1)
s=s.replace('stock100.bin','stock400.bin').replace("['stock100','frozen100','frozen400']","['stock400','observer400']").replace("'arms':3","'arms':2").replace('Fresh stock100/frozen100/frozen400 reference comparisons','Freshstock400 versusobserver400 comparisons')
s+='''
graphs=[json.loads(x)for x in(out/'observer/graphs.jsonl').read_text().splitlines()];assert len(graphs)>=20 and all(x['io_ok']and not x['dropped']for x in graphs)
(out/'observer-checks.json').write_text(json.dumps(dict(graphs=len(graphs),all_observer_io_complete=True,scope='No replay or performance claim'),indent=2)+'\\n')
'''
(b/'run_native_command_observer_kv64.py').write_text(s)
s=s.replace("out=p/'populated-kv64'","out=p/'boundary128'")
a=s.index(";prompt='");z=s.index(';rows=[]',a);prompt='The quick brown fox jumps over the lazy dog. '*15+'\nWrite a detailed explanation with several examples of how GPU matrix multiplication and attention work together. Start by describing a memory access:';s=s[:a]+';prompt='+repr(prompt)+s[z:]
s=s.replace("'-n','64'","'-n','128'").replace("'-b','4096'","'-b','512'").replace('len(tokens)>=64','len(tokens)>=128').replace('audit_rows>=64','audit_rows>=128').replace('min(positions)>=2048 and max(positions)<4096','128<=min(positions)<=220 and 256<max(positions)<4096').replace("'requested_tokens':64","'requested_tokens':128").replace('after >=2048 populated KV positions','across audit positions straddling256').replace('64requestedtokens','128requestedtokens').replace('SUBMISSION_POPULATED_KV64','NATIVE_COMMAND_BOUNDARY128')
(b/'run_native_command_observer_boundary128.py').write_text(s)
f=b/'run_private_guarded_batch.py';s=f.read_text().replace("'run_native_command_observer_model32.py'","'run_native_command_observer_model32.py','run_native_command_observer_prompts128.py','run_native_command_observer_kv64.py','run_native_command_observer_boundary128.py'",1);f.write_text(s)
