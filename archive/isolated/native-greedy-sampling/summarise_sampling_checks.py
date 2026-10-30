from pathlib import Path
import hashlib,json,re
p=Path(__file__).resolve().parent;modes=['stock100','temp_cpu','temp_gpu'];cases=[];activities=[]
for folder in ['sampling-model32','sampling-prompts128','sampling-populated-kv64','sampling-boundary128']:
 d=p/folder;c=json.loads((d/'comparison.json').read_text());assert c['all_requested_target_logit_bits_identical']and c['all_tokens_and_counters_identical']
 for f,h in json.loads((d/'assets.json').read_text()).items():assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==h,f
 rows=json.loads((d/'checks.json').read_text());names=['coding','math']if folder=='sampling-prompts128'else[folder]
 for name in names:
  rr=[r for r in rows if r.get('case',folder)==name];assert len(rr)==3 and set(r['mode']for r in rr)==set(modes)
  for r in rr:
   assert not r['new_driver_errors']and r['cap']==100 and all(v is None for v in r['effective_legacy_overrides'].values())
   assert all(r[k]==rr[0][k]for k in ['tokens','n_drafted','n_accept','n_predict','target_logit_audit_sha256','audit_bytes','target_logit_rows','audit_batches'])
   log=d/name/(r['mode']+'.log')if folder=='sampling-prompts128'else d/(r['mode']+'.log');text=log.read_text();aa=[dict((k,int(v))for k,v in re.findall(r'(\w+)=(-?\d+)',line))for line in re.findall(r'^TARGET_SAMPLING_ACTIVITY (.+)$',text,re.M)];assert len(aa)==r['target_logit_rows'];gpu=r['mode']=='temp_gpu'
   assert all(a['backend']==gpu and (a['sampled']>=0 if gpu else a['sampled']==-1)for a in aa)
   if gpu:assert all(a['logits']==1 and a['candidates']==1 and a['probs']<=1 for a in aa)
   activities.append(dict(case=name,mode=r['mode'],rows=len(aa),target_backend_active=gpu,scalar_output_assertions_pass=gpu,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest()))
  cases.append(dict(case=name,target_rows_per_mode=rr[0]['target_logit_rows'],raw_audit_sha256=rr[0]['target_logit_audit_sha256']))
assert sum(c['target_rows_per_mode']for c in cases)==530
(p/'sampling-qualification-summary.json').write_text(json.dumps(dict(cases=cases,activities=activities,target_rows_per_mode=530,total_mode_row_checks=1590,all_native_raw_bits_tokens_counters_identical=True,no_new_gpu_errors=True,all_assets_unchanged=True,scope='Restricted greedy CLI controls, native100stocklibraries/MTP1/driver. GPU sampled-token/scalar-array activity verified. Fullrawcallback audit only; no timing/general tie equivalence claim.'),indent=2)+'\n');print('SAMPLING_THREE_MODES_530_ROWS_EACH_EXACT_GPU_ACTIVITY_VERIFIED')
