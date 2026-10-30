from pathlib import Path
import json,hashlib,re
p=Path(__file__).resolve().parent;b=p.parent;frozen=b/'q3-pad112/qualified-20261029';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'build.json').write_text(json.dumps(dict(library_sha256=sha(frozen/'bin/libggml-vulkan.so.0.27.0'),scope='Existingimmutablequalifiedlibrary;candidateonlyunsetsGGML_VK_DISABLE_HOST_VISIBLE_VIDMEMinchildprocess.Nohost/core/shaderbuild.'),indent=2)+'\n')
for suffix,folder in [('model32','model32'),('prompts128','prompts128'),('kv64','populated-kv64'),('boundary128','boundary128')]:
 s=(b/('run_native_submit_budget_'+suffix+'.py')).read_text().replace("p=base/'native-submit-budget'","p=base/'native-rebar-input'").replace("host=p/'host'","host=base/'q3-pad112/qualified-20261029'")
 if suffix=='model32':s=s.replace("[('stock400',0,0),('frozen400',8,0),('control40',8,0),('budget20',8,1)]","[('stock400',0,0),('frozen400',8,0),('mapped400',8,1)]").replace("['stock400','frozen400','control40','budget20']","['stock400','frozen400','mapped400']").replace("'arms':4","'arms':3")
 elif suffix=='prompts128':s=s.replace('for reader_mode in [2,1]:','for reader_mode in [0,1]:')
 else:s=s.replace("[('stock400',400,0),('control40',400,2),('budget20',400,1)]","[('stock400',400,0),('frozen400',400,0),('mapped400',400,1)]").replace("['stock400','control40','budget20']","['stock400','frozen400','mapped400']")
 indent='  'if suffix=='prompts128'else' ';var='indexmode'if suffix=='model32'else'reader_mode'
 s=re.sub(r"trial\['GGML_VK_NATIVE_SUBMIT_DIVISOR'\]=.*?;trial\['GGML_VK_NATIVE_SUBMIT_AUDIT'\]='1'", "trial.pop('GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM',None)if "+var+"==1 else None",s)
 a=s.index(indent+'budget_records=');z=s.index(indent+'row=dict',a);s=s[:a]+s[z:];s=s.replace('submit_divisor=20 if '+var+'==1 else 40,budget_records=budget_records,','mapped_vram_requested='+var+'==1,')
 s=s.replace('nativeinitialsubmitdivisor40versus20','nativeunmappedversusmappedVRAM').replace('NATIVE_SUBMIT_BUDGET','NATIVE_REBAR_INPUT').replace("label='divisor'+str(20 if reader_mode==1 else 40)","label='mapped'+str(reader_mode)")
 (b/('run_native_rebar_'+suffix+'.py')).write_text(s)
f=b/'run_private_guarded_batch.py';s=f.read_text().replace('allowed={','allowed={'+','.join(repr('run_native_rebar_'+v+'.py')for v in ['model32','prompts128','kv64','boundary128'])+',',1);f.write_text(s)
