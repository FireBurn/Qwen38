from pathlib import Path
p=Path(__file__).resolve().parent;b=p.parent
s=(b/'run_native_planning_profile_model32.py').read_text().replace("p=base/'native-host-planning-profile'","p=base/'native-gdn-reader-index'").replace("json.loads((host/'build.json')","json.loads((p/'build.json')")
s=s.replace("for mode,mask in [('stock400',0),('profile400',8)]:","for mode,mask,indexmode in [('stock400',0,0),('verify400',8,2),('index400',8,1)]:")
s=s.replace("trial['GGML_VK_MAX_NODES_PER_SUBMIT']=str(cap);","trial['GGML_VK_MAX_NODES_PER_SUBMIT']=str(cap);trial['GGML_VK_GDN_READER_INDEX']=str(indexmode);")
needle=' row=dict(mode=mode,cap=cap,';assert needle in s
extra=''' verification=[{k:int(v)for k,v in re.findall(r'(\\w+)=(\\d+)',line)}for line in re.findall(r'^GDN_READER_VERIFY (.+)$',text,re.M)]
 if indexmode==2:assert verification and sum(v['checks']for v in verification)>1000 and sum(v['fused']for v in verification)>0 and not any(v['mismatches']for v in verification)and 'GDN_READER_MISMATCH'not in text
 else:assert not verification
'''
s=s.replace(needle,extra+' row=dict(mode=mode,reader_mode=indexmode,oracle_checks=sum(v[\'checks\']for v in verification),oracle_mismatches=sum(v[\'mismatches\']for v in verification),verified_fused_decisions=sum(v[\'fused\']for v in verification),cap=cap,')
s=s.replace("['stock400','profile400']","['stock400','verify400','index400']").replace("'arms':2","'arms':3").replace('planning-profile400','GDNreader-index modes2oracle and1release').replace('NATIVE_COMMAND_OBSERVER_MODEL32_TARGET_BITS_EXACT','GDN_READER_MODEL32_ALL_TARGET_BITS_AND_DECISIONS_EXACT')
(b/'run_gdn_reader_model32.py').write_text(s)
f=b/'run_private_guarded_batch.py';s=f.read_text().replace("'run_native_command_observer_model32.py'","'run_native_command_observer_model32.py','run_gdn_reader_model32.py'",1);f.write_text(s)
