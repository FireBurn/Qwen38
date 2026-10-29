from pathlib import Path
import json
p=Path(__file__).resolve().parent
ops=json.loads((p/'operators/checks.json').read_text());assert ops['exact_dispatch_cases']==864 and ops['returncode']==0 and not ops['new_driver_errors']
cases=[]
for name in ['model32','prompts128','populated-kv64','boundary128']:
 assert json.loads((p/name/'comparison.json').read_text())['all_requested_target_logit_bits_identical']
 for r in json.loads((p/name/'checks.json').read_text()):
  if name=='prompts128'or r['mode']=='reuse400':cases.append(dict(case=r.get('case',name),target_rows=r['target_logit_rows'],target_sha256=r['target_logit_audit_sha256'],n_predict=r['n_predict'],n_drafted=r['n_drafted'],n_accept=r['n_accept'],new_driver_errors=r['new_driver_errors']))
assert len(cases)==5 and all(not r['new_driver_errors']for r in cases)
a=ops['stats']['pad16_c2'];z=ops['stats']['reuse_c2'];resources={k:dict(frozen=a[k],reuse=z[k],change_percent=100*(z[k]/a[k]-1)if a[k]else None)for k in ['Instructions','VMEM','Code size','VGPRs','LDS size','Scratch size']}
report=dict(exact_operator_dispatches=864,model_cases=cases,unique_target_rows=sum(r['target_rows']for r in cases),c2_resources=resources,scope='Full requested target-vocabulary bit parity, tokens and acceptance counters for five specified cases; not every internal draft tensor, all contexts or throughput proof. Frozen .27 host unchanged; only private paddedQ3shader differs. Inherited reader_mode/oracle fields are zero and unused, no reader index is present. Some copied textual labels refer to earlier native-command/GDN/frozen-shader experiments; actual shader paths and hashes are pinned in assets and runner source. Candidate is explicit column reuse, not command replay or a combined pair kernel.')
(p/'qualification-summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
