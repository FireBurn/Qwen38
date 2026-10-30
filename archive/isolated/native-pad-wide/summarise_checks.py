from pathlib import Path
import hashlib,json,re
p=Path(__file__).resolve().parent;modes=['stock100','private_off','pad','wide','both'];cases=[];activities=[]
for folder in ['model32','prompts128','populated-kv64','boundary128']:
 d=p/folder;c=json.loads((d/'comparison.json').read_text());assert c['all_requested_target_logit_bits_identical']and c['all_tokens_and_counters_identical']
 for f,h in json.loads((d/'assets.json').read_text()).items():assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==h,f
 rows=json.loads((d/'checks.json').read_text());names=['coding','math']if folder=='prompts128'else[folder]
 for name in names:
  rr=[r for r in rows if r.get('case',folder)==name];assert len(rr)==5 and set(r['mode']for r in rr)==set(modes)
  for r in rr:
   mode=r['mode'];assert not r['new_driver_errors']and r['cap']==100 and r['mask']==(8 if mode in ['pad','both']else 0) and all(v is None for v in r['effective_legacy_overrides'].values())
   assert all(r[k]==rr[0][k]for k in ['tokens','n_drafted','n_accept','n_predict','target_logit_audit_sha256','audit_bytes','target_logit_rows','audit_batches'])
   log=d/name/(mode+'.log')if folder=='prompts128'else d/(mode+'.log');text=log.read_text();aa=[dict((k,int(v))for k,v in re.findall(r'(\w+)=(-?\d+)',line))for line in re.findall(r'^TARGET_SAMPLING_ACTIVITY (.+)$',text,re.M)];assert len(aa)==r['target_logit_rows'];gpu=mode in ['wide','both'];pad=mode in ['pad','both']
   assert all(a['backend']==gpu and (a['sampled']>=0 if gpu else a['sampled']==-1)for a in aa)
   if gpu:assert all(a['logits']==1 and a['candidates']==1 and a['probs']<=1 for a in aa)and re.search(r'ARGMAX_WIDE_SELECT native_block=(32|64) enabled=1',text)
   if pad:assert 'Q3_PAD112_CACHE 'in text and re.search(r'Q3_PAD112_FINAL entries=[1-9]\d* bytes=\d+ calls=[1-9]\d*',text)
   activities.append(dict(case=name,mode=mode,rows=len(aa),target_backend_active=gpu,wide_selection_verified=gpu,padded_arena_verified=pad,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest()))
  cases.append(dict(case=name,target_rows_per_mode=rr[0]['target_logit_rows'],raw_audit_sha256=rr[0]['target_logit_audit_sha256']))
assert sum(c['target_rows_per_mode']for c in cases)==530
(p/'qualification-summary.json').write_text(json.dumps(dict(cases=cases,activities=activities,target_rows_per_mode=530,total_mode_row_checks=2650,all_native_raw_bits_tokens_counters_identical=True,no_new_gpu_errors=True,all_assets_unchanged=True,scope='Five restricted greedy configs, native100 defaults, sameprivatecombinedhost for allprivatearms. Q3arena/wide/backendactivity verified, rawtargetbits/tokens/counters exact. No timing/universal sampler equivalence claim.'),indent=2)+'\n');print('COMBINED_FIVE_MODES_530_ROWS_EACH_EXACT_FEATURE_ACTIVITY_VERIFIED')
