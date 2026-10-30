from pathlib import Path
import ast
p=Path(__file__).resolve().parent;b=p.parent
s=(b/'run_native_default_timing.py').read_text().replace("project=base/'native-default-baseline'","project=base/'native-default-q3-100'")
start=s.index("modes=['stock100'");end=s.index('\nquant=',start)
s=s[:start]+"modes=['stock100','q3_100'];sequence=[mode for block in range(12)for mode in (['stock100','q3_100','q3_100','stock100']if block%2==0 else ['q3_100','stock100','stock100','q3_100'])];assert len(sequence)==48"+s[end:]
s=s.replace("if mode=='stock100':trial.pop('GGML_VK_MAX_NODES_PER_SUBMIT',None)","trial.pop('GGML_VK_MAX_NODES_PER_SUBMIT',None)")
s=s.replace('q3_400','q3_100').replace('assert len(rows)==72','assert len(rows)==48')
s=s.replace("[('combined','stock100','q3_100'),('submission','stock100','stock400'),('padding','stock400','q3_100')]","[('combined','stock100','q3_100')]")
s=s.replace('range(0,len(rows),6)','range(0,len(rows),4)').replace('rows[start:start+6]','rows[start:start+4]').replace('block=start//6','block=start//4')
s=s.replace("secondary=['stock400 versus stock100','q3_100 versus stock400']","secondary=[]")
s=s.replace('Fixed72','Fixed48').replace('12symmetric6armblocks','12alternatingABBA/BAABblocks').replace('Unmodifiedstock100/stock400/frozenQ3cap400','Unmodifiedstock100/frozenQ3cap100').replace('specifiedGPU/shaderpaths','native100capunsetBothModes,specifiedGPU/shaderpaths').replace('PrimaryQ3default400vsstock100,secondarycap/paddingdescriptivepair-specificmatchedsubsets.','PrimaryQ3default100vsstock100.').replace('nodecapunsetforstock100','nodecapunsetBothModes')
s=s.replace("print('NATIVE_DEFAULT_BASELINE_DISCOVERY'","print('NATIVE_DEFAULT_Q3_100_DISCOVERY'")
s=s.replace("env.update(GGML_VK_VISIBLE_DEVICES='1',GGML_VK_ALLOW_GRAPHICS_QUEUE='1',GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM='1',GGML_VK_SUBALLOCATION_BLOCK_SIZE='4294967296')", "env.update(GGML_VK_VISIBLE_DEVICES='1')")
s=s.replace(",GGML_VK_MAX_NODES_PER_SUBMIT='400')", ")")
s=s.replace("trial.pop('GGML_VK_MAX_NODES_PER_SUBMIT',None)", "trial.pop('GGML_VK_MAX_NODES_PER_SUBMIT',None);assert all(trial.get(k)is None for k in ['GGML_VK_MAX_NODES_PER_SUBMIT','GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM','GGML_VK_PREFER_HOST_MEMORY','GGML_VK_ALLOW_GRAPHICS_QUEUE','GGML_VK_SUBALLOCATION_BLOCK_SIZE'])")
ast.parse(s);(b/'run_native_q3_100_timing.py').write_text(s)
f=b/'run_private_guarded_batch.py';v=f.read_text();name='run_native_q3_100_timing.py'
if repr(name)not in v:v=v.replace('allowed={','allowed={'+repr(name)+',',1)
ast.parse(v);f.write_text(v)
