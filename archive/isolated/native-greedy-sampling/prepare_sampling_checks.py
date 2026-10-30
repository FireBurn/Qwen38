from pathlib import Path
import ast
p=Path(__file__).resolve().parent;b=p.parent
for suffix in ['prompts128','kv64','boundary128']:
 s=(b/f'run_native_callback_{suffix}.py').read_text()
 for folder in ['prompts128','populated-kv64','boundary128']:s=s.replace("out=p/'callback-"+folder+"'","out=p/'sampling-"+folder+"'")
 s=s.replace("[('stock100',0,100)]","[('stock100',0,100),('temp_cpu',0,100),('temp_gpu',0,100)]").replace("[('stock100',100,0)]","[('stock100',100,0),('temp_cpu',100,0),('temp_gpu',100,0)]")
 s=s.replace("mask=0 if mode in ['stock100','stock400']else 8","mask=0")
 s=s.replace("['stock100']","['stock100','temp_cpu','temp_gpu']").replace("'arms':1","'arms':3").replace("'arms':2","'arms':6")
 s=s.replace("p/'callback-audit-runner.cpp'","p/'sampling-audit-runner.cpp'").replace("p/'callback-audit-runner'","p/'sampling-audit-runner'").replace("p/'callback-build.json'","p/'sampling-build.json'")
 if suffix=='prompts128':needle="  before=set(subprocess.run(['dmesg'";indent='  '
 else:needle=" before=set(subprocess.run(['dmesg'";indent=' '
 assert needle in s
 s=s.replace(needle,indent+"trial['EXPECT_TARGET_BACKEND_SAMPLING']='1'if mode=='temp_gpu'else'0'\n"+indent+"if mode.startswith('temp_'):cmd+=['--samplers','temperature']\n"+indent+"if mode=='temp_gpu':cmd+=['--backend-sampling']\n"+needle)
 ast.parse(s);(b/f'run_native_sampling_{suffix}.py').write_text(s)
f=b/'run_private_guarded_batch.py';s=f.read_text();names=[f'run_native_sampling_{x}.py'for x in ['prompts128','kv64','boundary128']];missing=[repr(x)for x in names if repr(x)not in s]
if missing:s=s.replace('allowed={','allowed={'+','.join(missing)+',',1)
ast.parse(s);f.write_text(s)
print('Prepared three-mode broader sampling controls; native100, no Q3 padding')
