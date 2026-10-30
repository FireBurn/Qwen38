from pathlib import Path
import ast,json
p=Path(__file__).resolve().parent;b=p.parent
build=json.loads((b/'native-default-baseline/build.json').read_text());build['scope']='Frozen Q3 padding at native default100, four legacy overrides absent. No build.';(p/'build.json').write_text(json.dumps(build,indent=2)+'\n')
for suffix in ['model32','prompts128','kv64','boundary128']:
 s=(b/f'run_native_default_{suffix}.py').read_text().replace("p=base/'native-default-baseline'","p=base/'native-default-q3-100'")
 s=s.replace("('stock400',0,0),",'').replace("('stock400',0,400),",'').replace("('stock400',400,0),",'')
 s=s.replace("('q3_400',8,400)","('q3_100',8,100)").replace("('q3_400',400,1)","('q3_100',100,1)").replace('q3_400','q3_100')
 s=s.replace("cap=100 if mode=='stock100'else 400",'cap=100')
 s=s.replace("['stock100','stock400','q3_100']","['stock100','q3_100']")
 s=s.replace("'arms':6","'arms':4").replace("'arms':3","'arms':2")
 s=s.replace('Freshstock400','Freshstock100').replace('stocknative-default100/400versusQ3default400','stocknative-default100 versusQ3default100')
 # Inject explicit experiment plan into provenance.
 s=s.replace('assets=[',"assets=[p/'PLAN.md',",1)
 ast.parse(s);(b/f'run_native_q3_100_{suffix}.py').write_text(s)
 print(suffix,'prepared')
f=b/'run_private_guarded_batch.py';s=f.read_text();names=[f'run_native_q3_100_{v}.py'for v in ['model32','prompts128','kv64','boundary128']];missing=[repr(v)for v in names if repr(v)not in s]
if missing:s=s.replace('allowed={','allowed={'+','.join(missing)+',',1)
ast.parse(s);f.write_text(s)
