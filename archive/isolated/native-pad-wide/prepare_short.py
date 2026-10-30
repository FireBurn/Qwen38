from pathlib import Path
import ast
p=Path(__file__).resolve().parent;b=p.parent
s=(b/'run_native_argmax_wide_model32.py').read_text().replace("out=base/'native-argmax-review/wide-model32'","out=base/'native-pad-wide/model32'")
s=s.replace("[('stock100',0,0),('private_off',0,0),('private_wide',0,0)]","[('stock100',0,0),('private_off',0,0),('pad',8,1),('wide',0,0),('both',8,1)]")
s=s.replace("['stock100','private_off','private_wide']","['stock100','private_off','pad','wide','both']").replace("'arms':3","'arms':5")
s=s.replace("else base/'native-argmax-review/wide-host'","else base/'native-pad-wide/host'")
s=s.replace("'1'if mode!='stock100'else'0'","'1'if mode in ['wide','both']else'0'").replace("if mode!='stock100':cmd+=","if mode in ['wide','both']:cmd+=").replace("if mode=='private_wide':","if mode in ['wide','both']:")
s=s.replace("base/'native-argmax-review/wide-build.json'","base/'native-pad-wide/build.json'").replace("base/'native-argmax-review/wide-host/bin/libggml-vulkan.so.0.27.0'","base/'native-pad-wide/host/bin/libggml-vulkan.so.0.27.0'")
s=s.replace("assets=[","assets=[base/'native-pad-wide/PLAN.md',",1)
s=s.replace("'padded_cache_dispatch_verified':True","'feature_activity_checked':True")
s=s.replace("'scope':'Productionaa8 .27/.7 Freshstock100 vsstocknative-default100 versusQ3default100 withfrozenQ3shaders.","'scope':'Combinedhost five-arm stock/privateoff/pad/wide/both;")
ast.parse(s);name='run_native_pad_wide_model32.py';(b/name).write_text(s)
f=b/'run_private_guarded_batch.py';v=f.read_text()
if repr(name)not in v:v=v.replace('allowed={','allowed={'+repr(name)+',',1)
f.write_text(v)
print('Prepared five-arm short raw-model correctness/activity check')
