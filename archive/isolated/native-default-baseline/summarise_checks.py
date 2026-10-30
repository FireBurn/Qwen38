from pathlib import Path
import json
p=Path(__file__).resolve().parent;cases=[];modes=['stock100','stock400','q3_400']
for folder in ['model32','prompts128','populated-kv64','boundary128']:
 comp=json.loads((p/folder/'comparison.json').read_text());assert comp['all_requested_target_logit_bits_identical']and comp['all_tokens_and_counters_identical'];rows=json.loads((p/folder/'checks.json').read_text());names=['coding','math']if folder=='prompts128'else[folder]
 for name in names:
  aa=[r for r in rows if r.get('case',folder)==name];assert len(aa)==3 and set(r['mode']for r in aa)==set(modes)
  for r in aa:
   assert not r['new_driver_errors'];assert r['effective_legacy_overrides']and all(v is None for v in r['effective_legacy_overrides'].values());assert r['cap']==(100 if r['mode']=='stock100'else 400);assert r['candidate_q3']==(r['mode']=='q3_400')
   assert all(r[k]==aa[0][k]for k in ['tokens','n_drafted','n_accept','n_predict','target_logit_audit_sha256','audit_bytes','target_logit_rows','audit_batches'])
  cases.append(dict(case=name,target_rows_per_mode=aa[0]['target_logit_rows'],sha256=aa[0]['target_logit_audit_sha256'],modes=modes,all_native_tokens_counters_and_target_bits_identical=True,all_four_legacy_overrides_absent=True))
assert sum(r['target_rows_per_mode']for r in cases)==530
(p/'qualification-summary.json').write_text(json.dumps(dict(cases=cases,target_rows_per_mode=530,mode_row_checks=1590,scope='Directnativeallocation/queue/suballocationdefaultsunderpinnedstack/MTPpolicy;unmodifiedstock100(defaultcapunset),stock400,Q3default400.Fivecasebits/tokens/countersmatchnative,noGPUerrors.No performance/equalclock/generalclaim.'),indent=2)+'\n');print('DEFAULT_BASELINE_THREE_MODES_530_ROWS_EACH_EXACT')
