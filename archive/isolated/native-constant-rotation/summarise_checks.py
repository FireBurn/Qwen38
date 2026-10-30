from pathlib import Path
import json
p=Path(__file__).resolve().parent;cases=[]
for folder in ['model32','prompts128','populated-kv64','boundary128']:
 assert json.loads((p/folder/'comparison.json').read_text())['all_requested_target_logit_bits_identical'];rr=json.loads((p/folder/'checks.json').read_text());assert all(not v['new_driver_errors']for v in rr)
 for r in rr:
  if r['constant_rotation_active']:
   assert r['rotation_caches_created']>0 and r['rotation_input_bypasses']>10
   cases.append(dict(case=r.get('case',folder),target_rows=r['target_logit_rows'],sha256=r['target_logit_audit_sha256'],created=r['rotation_caches_created'],bypasses=r['rotation_input_bypasses']))
assert sum(v['target_rows']for v in cases)==530
(p/'qualification-summary.json').write_text(json.dumps(dict(cases=cases,target_rows=530,scope='Privateinactive/activecorefullrequestedtargetbits/tokens/countersmatchnative;positivecacheactivity,noGPUerrors. Sampledcontextsnotgenerallifetime/performanceproof. Repeatedclearprofilestillrequired.'),indent=2)+'\n');print('CONST_ROT_FIVE_CASES_530_TARGET_ROWS_EXACT')
