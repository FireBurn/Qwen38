from pathlib import Path
import re
p=Path(__file__).resolve().parent;b=p.parent
for suffix,folder in [('model32','model32'),('prompts128','prompts128'),('kv64','populated-kv64'),('boundary128','boundary128')]:
 s=(b/('run_native_fusion_reuse_'+suffix+'.py')).read_text().replace("p=base/'native-fusion-plan'","p=base/'native-submit-budget'").replace("host=p/'reuse-host'","host=p/'host'").replace("out=p/'reuse-"+folder+"'","out=p/'"+folder+"'").replace("p/'reuse-build.json'","p/'build.json'").replace("p/'REUSE-PLAN.md'","p/'PLAN.md'")
 s=s.replace("GGML_VK_FUSION_PLAN_REUSE']=str(indexmode);trial['GGML_VK_FUSION_PLAN_AUDIT']='1'","GGML_VK_NATIVE_SUBMIT_DIVISOR']='20'if indexmode==1 else'40';trial['GGML_VK_NATIVE_SUBMIT_AUDIT']='1'")
 s=s.replace("GGML_VK_FUSION_PLAN_REUSE']=str(reader_mode);trial['GGML_VK_FUSION_PLAN_AUDIT']='1'","GGML_VK_NATIVE_SUBMIT_DIVISOR']='20'if reader_mode==1 else'40';trial['GGML_VK_NATIVE_SUBMIT_AUDIT']='1'")
 indent='  'if suffix=='prompts128'else' ';var='indexmode'if suffix=='model32'else'reader_mode';a=s.index(indent+('verification='if suffix=='model32'else'oracle='));z=s.index(indent+'row=dict',a)
 audit=indent+"budget_records=[{k:int(v)for k,v in re.findall(r'(\\w+)=(\\d+)',line)}for line in re.findall(r'^NATIVE_SUBMIT_BUDGET (.+)$',text,re.M)]\n"
 if suffix=='prompts128':audit+=indent+"assert budget_records and all(v['divisor']==(20 if reader_mode==1 else40)for v in budget_records)\n"
 else:audit+=indent+"if mode not in ['stock400','frozen400']:assert budget_records and all(v['divisor']==(20 if "+var+"==1 else40)for v in budget_records)\n"
 s=s[:a]+audit+s[z:];s=re.sub(r'reuse_mode='+var+r',oracle_checks=.*?cached_decisions=sum\(v\[\'used\'\]for v in (?:oracle|verification)\),',"submit_divisor=20 if "+var+"==1 else40,budget_records=budget_records,",s)
 s=s.replace("('verify400',8,2)","('verify400',8,0)")if suffix=='model32'else s
 s=s.replace("verify400","control40").replace('index400','budget20').replace("label='reader'+str(reader_mode)","label='divisor'+str(20 if reader_mode==1 else40)")
 s=s.replace('nativefusionplanmode2oracle/mode1reuse','nativeinitialsubmitdivisor40versus20').replace('NATIVE_FUSION_REUSE','NATIVE_SUBMIT_BUDGET').replace('ALL_TARGET_BITS_AND_DECISIONS_EXACT','ALL_TARGET_BITS_EXACT')
 s=s.replace('else40','else 40')
 (b/('run_native_submit_budget_'+suffix+'.py')).write_text(s)
f=b/'run_private_guarded_batch.py';s=f.read_text().replace('allowed={','allowed={'+','.join(repr('run_native_submit_budget_'+x+'.py')for x in ['model32','prompts128','kv64','boundary128'])+',',1);f.write_text(s)
