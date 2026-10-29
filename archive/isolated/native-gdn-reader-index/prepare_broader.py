from pathlib import Path
p=Path(__file__).resolve().parent;b=p.parent
s=(b/'run_native_command_observer_prompts128.py').read_text().replace("p=base/'native-command-observer'","p=base/'native-gdn-reader-index'")
s=s.replace(' for mask in [8]:',' for reader_mode in [2,1]:\n  mask=8').replace("label='mask'+str(mask)","label='reader'+str(reader_mode)")
s=s.replace("  obs=folder/'observer';obs.mkdir();trial['GGML_VK_CMD_OBSERVER_DIR']=str(obs)","  trial['GGML_VK_GDN_READER_INDEX']=str(reader_mode)")
needle='  row=dict(case=case,';assert needle in s;s=s.replace(needle,'''  oracle=[{k:int(v)for k,v in re.findall(r'(\\w+)=(\\d+)',line)}for line in re.findall(r'^GDN_READER_VERIFY (.+)$',text,re.M)]
  if reader_mode==2:assert sum(v['checks']for v in oracle)>1000 and sum(v['fused']for v in oracle)>0 and not any(v['mismatches']for v in oracle)and 'GDN_READER_MISMATCH'not in text
  else:assert not oracle
  row=dict(case=case,reader_mode=reader_mode,oracle_checks=sum(v['checks']for v in oracle),oracle_mismatches=sum(v['mismatches']for v in oracle),verified_fused_decisions=sum(v['fused']for v in oracle),''')
s=s.replace("'arms':2","'arms':4").replace('Productionaa8 .27/.7native/fusion/allthree,128requestedtokens,136fusiongroups','GDNreader-index modes2oracle and1release,128requestedtokens').replace('PRODUCTION_FUSION_TWO_PROMPTS_128_ALL_TARGET_BITS_EXACT','GDN_READER_TWO_PROMPTS128_ALL_TARGET_BITS_AND_DECISIONS_EXACT')
i=s.find('\nfor case,prompt in cases:\n obs=');assert i>0;s=s[:i];(b/'run_gdn_reader_prompts128.py').write_text(s)
for folder,source in [('populated-kv64','run_native_command_observer_kv64.py'),('boundary128','run_native_command_observer_boundary128.py')]:
 s=(b/source).read_text().replace("p=base/'native-command-observer'","p=base/'native-gdn-reader-index'").replace("for mode,cap in [('stock400',400),('observer400',400)]:","for mode,cap,reader_mode in [('stock400',400,0),('verify400',400,2),('index400',400,1)]:")
 a=s.index(" if mask==8:\n  obs=");z=s.index(' if mask==8:trial.update',a);s=s[:a]+" trial['GGML_VK_GDN_READER_INDEX']=str(reader_mode)\n"+s[z:]
 needle=' row=dict(mode=mode,';assert needle in s;s=s.replace(needle,''' oracle=[{k:int(v)for k,v in re.findall(r'(\\w+)=(\\d+)',line)}for line in re.findall(r'^GDN_READER_VERIFY (.+)$',text,re.M)]
 if reader_mode==2:assert sum(v['checks']for v in oracle)>1000 and sum(v['fused']for v in oracle)>0 and not any(v['mismatches']for v in oracle)and 'GDN_READER_MISMATCH'not in text
 else:assert not oracle
 row=dict(mode=mode,reader_mode=reader_mode,oracle_checks=sum(v['checks']for v in oracle),oracle_mismatches=sum(v['mismatches']for v in oracle),verified_fused_decisions=sum(v['fused']for v in oracle),''')
 s=s.replace("['stock400','observer400']","['stock400','verify400','index400']").replace("'arms':2","'arms':3").replace('Freshstock400 versusobserver400','Freshstock400 versusGDNreader-index modes2oracle and1release')
 a=s.find('\ngraphs=[json.loads');assert a>0;s=s[:a];(b/('run_gdn_reader_kv64.py'if folder=='populated-kv64'else'run_gdn_reader_boundary128.py')).write_text(s)
f=b/'run_private_guarded_batch.py';s=f.read_text().replace("'run_gdn_reader_model32.py'","'run_gdn_reader_model32.py','run_gdn_reader_prompts128.py','run_gdn_reader_kv64.py','run_gdn_reader_boundary128.py'",1);f.write_text(s)
