from pathlib import Path
import re
p=Path(__file__).resolve().parent;b=p.parent
for suffix,folder in [('model32','model32'),('prompts128','prompts128'),('kv64','populated-kv64'),('boundary128','boundary128')]:
 s=(b/('run_native_submit_budget_'+suffix+'.py')).read_text().replace("p=base/'native-submit-budget'","p=base/'native-constant-rotation'").replace("host=p/'host'","host=base/'q3-pad112/qualified-20261029'")
 s=s.replace("sha(host/'bin/libggml-vulkan.so.0.27.0')==json.loads((p/'build.json').read_text())['library_sha256']","sha(p/'bin/libllama.so.0.7.0')==json.loads((p/'build.json').read_text())['library_sha256']")
 s=s.replace('assets=[',"assets=[p/'bin/libllama.so.0.7.0',")
 var='indexmode'if suffix=='model32'else'reader_mode';indent='  'if suffix=='prompts128'else' '
 core="p"if suffix=='prompts128'else"stock if mode in ['stock400','frozen400']else p"
 replacement="selected_core="+core+";trial.update(LD_LIBRARY_PATH=(str(p/'bin')+':'if selected_core==p else'')+trial['LD_LIBRARY_PATH'],EXPECTED_LLAMA_CORE_PATH=str(selected_core/'bin/libllama.so.0.7.0'),LLAMA_VK_CONST_ROT='1'if "+var+"==1 else'0',LLAMA_VK_CONST_ROT_AUDIT='1')"
 s=re.sub(r"trial\['GGML_VK_NATIVE_SUBMIT_DIVISOR'\]=.*?;trial\['GGML_VK_NATIVE_SUBMIT_AUDIT'\]='1'",replacement,s)
 a=s.index(indent+'budget_records=');z=s.index(indent+'row=dict',a)
 check=indent+"created=len(re.findall(r'LLAMA_CONST_ROT_CREATED matrices=[1-9]',text));bypasses=text.count('LLAMA_CONST_ROT_BYPASS ')\n"+indent+"if "+var+"==1:assert created>0 and bypasses>10,'Constant cache inactive'\n"+indent+"else:assert created==0 and bypasses==0\n"
 s=s[:a]+check+s[z:];s=s.replace('submit_divisor=20 if '+var+'==1 else 40,budget_records=budget_records,','constant_rotation_active='+var+'==1,rotation_caches_created=created,rotation_input_bypasses=bypasses,')
 s=s.replace('control40','private0').replace('budget20','private1').replace('nativeinitialsubmitdivisor40versus20','nativeversusprivateimmutabledeviceHadamardcache').replace('NATIVE_SUBMIT_BUDGET','NATIVE_CONST_ROT')
 if suffix=='prompts128':s=s.replace("label='divisor'+str(20 if reader_mode==1 else 40)","label='const'+str(reader_mode==1)")
 (b/('run_native_const_rot_'+suffix+'.py')).write_text(s)
f=b/'run_private_guarded_batch.py';s=f.read_text().replace('allowed={','allowed={'+','.join(repr('run_native_const_rot_'+v+'.py')for v in ['model32','prompts128','kv64','boundary128'])+',',1);f.write_text(s)
