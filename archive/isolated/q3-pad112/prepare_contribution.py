from pathlib import Path
p=Path(__file__).resolve().parent;b=p.parent
s=(b/'run_q3_submission_cap_model32.py').read_text().replace("out=p/'submission-cap-model32'","out=p/'contribution-stock400-model32'").replace("host=p/'qualified-20261029'","host=base/'production-baseline-aa8'")
s=s.replace('for cap in [100,200,400]:\n mask=8','for cap in [400]:\n mask=0').replace(";assert 'NQ_PLAN_EXACT'in text",'')
s=s.replace("(out/'cap100.bin')","(out/'cap400.bin')").replace("'arms':3","'arms':1").replace("'padded_cache_dispatch_verified':True","'padded_cache_enabled':False").replace("['cap'+str(i)+'.bin'for i in [100,200,400]]","['cap400.bin']").replace("for cap in [100,200,400]:(out/('cap'+str(cap)+'.bin')).unlink()","(out/'cap400.bin').unlink()")
s=s.replace('frozen paddedQ3 immutablecache,stockactivationpolicy,nodecaps100/200/400','unmodifiedstock,stockactivationpolicy,nodecap400').replace('SUBMISSION_CAP_MODEL_TARGET_LOGITS_ALL_EXACT','STOCK400_MODEL32_TARGET_BITS_EXACT')
(b/'run_q3_contribution_stock400_model32.py').write_text(s)
s=(b/'run_q3_submission_populated_kv64.py').read_text().replace("out=p/'submission-populated-kv64'","out=p/'contribution-stock400-populated-kv64'").replace("for mode,cap in [('stock100',100),('frozen100',100),('frozen400',400)]:","for mode,cap in [('stock400',400)]:")
s=s.replace("mode=='stock100'","mode=='stock400'").replace("mode!='stock100'","mode!='stock400'").replace('stock100.bin','stock400.bin').replace("['stock100','frozen100','frozen400']","['stock400']").replace("'arms':3","'arms':1").replace("'padded_cache_dispatch_verified':True","'padded_cache_enabled':False")
needle=' if rows:assert';i=s.index(needle);s=s[:i]+" prior=json.loads((p/'submission-populated-kv64/checks.json').read_text())[0]\n assert all(row[k]==prior[k]for k in ['tokens','n_drafted','n_accept','n_predict','target_logit_audit_sha256','audit_bytes','target_logit_rows','audit_batches']),'Populated stock reference differs'\n"+s[i:]
s=s.replace('Fresh stock100/frozen100/frozen400 reference comparisons','Stock400 versus prior fresh stock100 reference').replace('SUBMISSION_POPULATED_KV64_ALL_TARGET_BITS_EXACT','STOCK400_POPULATED_KV64_ALL_TARGET_BITS_EXACT')
(b/'run_q3_contribution_stock400_kv64.py').write_text(s)
f=b/'run_private_guarded_batch.py';s=f.read_text().replace("'run_q3_submission_system_effect.py'","'run_q3_submission_system_effect.py','run_q3_contribution_stock400_model32.py','run_q3_contribution_stock400_kv64.py'",1);f.write_text(s)
