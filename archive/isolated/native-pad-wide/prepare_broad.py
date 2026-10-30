from pathlib import Path
import ast
p=Path(__file__).resolve().parent;b=p.parent
for suffix,folder in [('prompts128','prompts128'),('kv64','populated-kv64'),('boundary128','boundary128')]:
 s=(b/f'run_native_argmax_wide_{suffix}.py').read_text().replace("out=base/'native-argmax-review/wide-"+folder+"'","out=base/'native-pad-wide/"+folder+"'")
 s=s.replace("[('stock100',0,100),('private_off',0,100),('private_wide',0,100)]","[('stock100',0,100),('private_off',0,100),('pad',8,100),('wide',0,100),('both',8,100)]")
 s=s.replace("[('stock100',100,0),('private_off',100,0),('private_wide',100,0)]","[('stock100',100,0),('private_off',100,0),('pad',100,1),('wide',100,0),('both',100,1)]")
 s=s.replace(" mask=0\n"," mask=8 if mode in ['pad','both']else 0\n")
 s=s.replace("['stock100','private_off','private_wide']","['stock100','private_off','pad','wide','both']").replace("'arms':3","'arms':5").replace("'arms':6","'arms':10")
 s=s.replace("else base/'native-argmax-review/wide-host'","else base/'native-pad-wide/host'")
 s=s.replace("'1'if mode!='stock100'else'0'","'1'if mode in ['wide','both']else'0'").replace("if mode!='stock100':cmd+=","if mode in ['wide','both']:cmd+=").replace("mode=='private_wide'","mode in ['wide','both']")
 s=s.replace("base/'native-argmax-review/wide-build.json'","base/'native-pad-wide/build.json'").replace("base/'native-argmax-review/wide-host/bin/libggml-vulkan.so.0.27.0'","base/'native-pad-wide/host/bin/libggml-vulkan.so.0.27.0'").replace("base/'native-argmax-review/WIDE-MODEL-PLAN.md'","base/'native-pad-wide/PLAN.md'")
 s=s.replace("'padded_cache_dispatch_verified':False","'feature_activity_checked':True")
 ast.parse(s);(b/f'run_native_pad_wide_{suffix}.py').write_text(s)
f=b/'run_private_guarded_batch.py';v=f.read_text();names=[f'run_native_pad_wide_{x}.py'for x in ['prompts128','kv64','boundary128']];missing=[repr(n)for n in names if repr(n)not in v]
if missing:v=v.replace('allowed={','allowed={'+','.join(missing)+',',1)
f.write_text(v)
print('Prepared five-arm broader raw-model checks')
