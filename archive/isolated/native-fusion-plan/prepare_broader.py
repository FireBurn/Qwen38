from pathlib import Path
p=Path(__file__).resolve().parent;b=p.parent
helper='''def assert_shadow(text):
 assert 'NATIVE_FUSION_SHADOW 'in text and 'NATIVE_FUSION_FAST_KEY 'in text
 assert 'NATIVE_FUSION_PLAN_MISMATCH'not in text and 'NATIVE_FUSION_FAST_KEY_MISMATCH'not in text
 assert not re.search(r'NATIVE_FUSION_SHADOW .*match=0|NATIVE_FUSION_FAST_KEY .*agree=0',text)
'''
for suffix,folder in [('prompts128','prompts128'),('kv64','populated-kv64'),('boundary128','boundary128')]:
 s=(b/('run_gdn_reader_'+suffix+'.py')).read_text().replace("p=base/'native-gdn-reader-index'","p=base/'native-fusion-plan'").replace("host=p/'host'","host=p/'validator-host'").replace("out=p/'"+folder+"'","out=p/'validator-"+folder+"'")
 needle="def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()";s=s.replace(needle,needle+'\n'+helper)
 s=s.replace('assets=[',"assets=[p/'validator-build.json',p/'VALIDATOR-PLAN.md',")
 if suffix=='prompts128':
  s=s.replace(' for reader_mode in [2,1]:',' for reader_mode in [0]:').replace("  trial['GGML_VK_GDN_READER_INDEX']=str(reader_mode)","  trial['GGML_VK_FUSION_PLAN_SHADOW']='1'")
  needle="  text=log.read_text();assert child.returncode==0 and not bad,(case,mask,child.returncode,bad)"
  if needle in s:s=s.replace(needle,needle+'\n  assert_shadow(text)')
  else:
   marker="  row=dict(case=case,";assert marker in s;s=s.replace(marker,'  assert_shadow(text)\n'+marker)
  s=s.replace("'arms':4","'arms':2")
 else:
  s=s.replace("[('stock400',400,0),('verify400',400,2),('index400',400,1)]","[('stock400',400,0),('verify400',400,0)]").replace("['stock400','verify400','index400']","['stock400','verify400']").replace("'arms':3","'arms':2")
  s=s.replace(" trial['GGML_VK_GDN_READER_INDEX']=str(reader_mode)"," trial['GGML_VK_FUSION_PLAN_SHADOW']='1'")
  marker=' row=dict(mode=mode,';assert marker in s;s=s.replace(marker," if mask==8:assert_shadow(text)\n"+marker)
 s=s.replace('GDNreader-index modes2oracle and1release','nativefusionshadowvalidator').replace('GDN_READER_','NATIVE_FUSION_VALIDATOR_').replace('verify400','audit400')
 name='run_native_fusion_validator_'+suffix+'.py';(b/name).write_text(s)
f=b/'run_private_guarded_batch.py';f.write_text(f.read_text().replace('allowed={',"allowed={'run_native_fusion_validator_prompts128.py','run_native_fusion_validator_kv64.py','run_native_fusion_validator_boundary128.py',",1))
