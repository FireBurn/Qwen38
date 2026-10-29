from pathlib import Path
import json
p=Path(__file__).resolve().parent;cases=[]
for folder in ['model32','prompts128','populated-kv64','boundary128']:
 assert json.loads((p/folder/'comparison.json').read_text())['all_requested_target_logit_bits_identical'];rows=json.loads((p/folder/'checks.json').read_text())
 names=['coding','math']if folder=='prompts128'else[folder]
 for name in names:
  group=[r for r in rows if r.get('case',folder)==name];active=next(r for r in group if r['submit_divisor']==20);control=next(r for r in group if r['submit_divisor']==40 and r['budget_records']);aa=active['budget_records'];cc=control['budget_records'];assert[(v['nodes'],v['flops'])for v in aa]==[(v['nodes'],v['flops'])for v in cc];assert all(v['batches']<=w['batches']for v,w in zip(aa,cc));assert sum(v['batches']for v in aa)<sum(v['batches']for v in cc)
  assert all(active[k]==control[k]for k in ['tokens','n_drafted','n_accept','n_predict','target_logit_audit_sha256','audit_bytes','target_logit_rows','audit_batches']);assert not active['new_driver_errors']and not control['new_driver_errors']
  cases.append(dict(case=name,target_rows=active['target_logit_rows'],sha256=active['target_logit_audit_sha256'],graphs=len(aa),control40_batches=sum(v['batches']for v in cc),budget20_batches=sum(v['batches']for v in aa),all_tokens_counters_and_target_bits_identical=True))
assert sum(v['target_rows']for v in cases)==530
(p/'qualification-summary.json').write_text(json.dumps(dict(cases=cases,target_rows=530,scope='Fivefulltargetbitcases,actualnativegraphbatchreductionwithsameorderedgraphnode/FLOPsequence;noGPUerrors. Notallcontexts,draftintermediates,orperformancespeedproof.'),indent=2)+'\n');print('NATIVE_SUBMIT_BUDGET_FIVE_CASES_EXACT_530_ROWS')
