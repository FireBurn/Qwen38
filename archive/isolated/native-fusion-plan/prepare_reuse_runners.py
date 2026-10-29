from pathlib import Path
import re
p=Path(__file__).resolve().parent;b=p.parent
for suffix,folder in [('model32','model32'),('prompts128','prompts128'),('kv64','populated-kv64'),('boundary128','boundary128')]:
 s=(b/('run_gdn_reader_'+suffix+'.py')).read_text().replace("p=base/'native-gdn-reader-index'","p=base/'native-fusion-plan'").replace("host=p/'host'","host=p/'reuse-host'").replace("out=p/'"+folder+"'","out=p/'reuse-"+folder+"'").replace("p/'build.json'","p/'reuse-build.json'")
 s=s.replace('assets=[',"assets=[p/'reuse-build.json',p/'REUSE-PLAN.md',")
 if suffix=='model32':
  s=s.replace("[('stock400',0,0),('verify400',8,2),('index400',8,1)]","[('stock400',0,0),('frozen400',8,0),('verify400',8,2),('index400',8,1)]")
  s=s.replace("selected_host=stock if mode=='stock400'else host","selected_host=stock if mode=='stock400'else base/'q3-pad112/qualified-20261029'if mode=='frozen400'else host").replace("['stock400','verify400','index400']","['stock400','frozen400','verify400','index400']").replace("'arms':3","'arms':4")
 s=s.replace('GGML_VK_GDN_READER_INDEX','GGML_VK_FUSION_PLAN_REUSE').replace("trial['GGML_VK_FUSION_PLAN_REUSE']=str(indexmode);","trial['GGML_VK_FUSION_PLAN_REUSE']=str(indexmode);trial['GGML_VK_FUSION_PLAN_AUDIT']='1';").replace("trial['GGML_VK_FUSION_PLAN_REUSE']=str(reader_mode)","trial['GGML_VK_FUSION_PLAN_REUSE']=str(reader_mode);trial['GGML_VK_FUSION_PLAN_AUDIT']='1'")
 s=s.replace('GDN_READER_VERIFY','NATIVE_FUSION_REUSE').replace('GDN_READER_MISMATCH','NATIVE_FUSION_ORACLE_MISMATCH').replace("v['fused']","v['used']")
 s=s.replace('else:assert not verification',"else:assert all(v['checks']==0 and v['mismatches']==0 for v in verification)")
 s=s.replace('else:assert not oracle',"else:assert all(v['checks']==0 and v['mismatches']==0 for v in oracle)")
 # All emitted per-graph records (including release) must report zero mismatches.
 if suffix=='prompts128':
  marker='  row=dict(case=case,';s=s.replace(marker,"  assert not re.search(r'NATIVE_FUSION_[A-Z_]*MISMATCH',text)\n  assert sum(v['used']for v in oracle)>1000\n"+marker)
 else:
  marker=' row=dict(mode=mode,';flag='indexmode'if suffix=='model32'else'reader_mode';s=s.replace(marker," assert not re.search(r'NATIVE_FUSION_[A-Z_]*MISMATCH',text)\n if "+flag+":assert sum(v['used']for v in "+('verification'if suffix=='model32'else'oracle')+")>1000\n"+marker)
 s=re.sub(r'\breader_mode=(?!=)','reuse_mode=',s).replace('verified_fused_decisions','cached_decisions')
 s=s.replace('GDNreader-index modes2oracle and1release','nativefusionplanmode2oracle/mode1reuse').replace('GDN_READER_','NATIVE_FUSION_REUSE_')
 (b/('run_native_fusion_reuse_'+suffix+'.py')).write_text(s)
f=b/'run_private_guarded_batch.py';f.write_text(f.read_text().replace('allowed={','allowed={'+','.join(repr('run_native_fusion_reuse_'+x+'.py')for x in ['model32','prompts128','kv64','boundary128'])+',',1))
