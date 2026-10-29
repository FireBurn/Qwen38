from pathlib import Path
import json,collections,re
p=Path(__file__).resolve().parent;cases=[]
for name in ['host-model32','host-prompts128','host-populated-kv64','host-boundary128']:
 c=json.loads((p/name/'comparison.json').read_text());assert c['all_requested_target_logit_bits_identical']and c['all_tokens_and_counters_identical']
 for r in json.loads((p/name/'checks.json').read_text()):
  if r.get('pair_mode')!=1:continue
  assert r['pair_calls']>100 and not r['new_driver_errors']
  cases.append(dict(case=r.get('case',name),target_rows=r['target_logit_rows'],target_sha256=r['target_logit_audit_sha256'],pair_calls=r['pair_calls'],n_predict=r['n_predict'],n_drafted=r['n_drafted'],n_accept=r['n_accept']))
assert len(cases)==5
bounded=json.loads((p/'operators/checks.json').read_text());stress=json.loads((p/'stress/checks.json').read_text());assert bounded['exact_cases']==576 and stress['exact_cases']==128 and not bounded['new_driver_errors']and not stress['new_driver_errors']
micro=json.loads(sorted((p/'timing').glob('*/analysis.json'))[-1].read_text());assert micro['screen_justifies_host_prototype']
r=dict(bounded_cases=576,larger_cases=128,model_cases=cases,unique_target_rows=sum(c['target_rows']for c in cases),total_model_pair_calls=sum(c['pair_calls']for c in cases),host_library_sha256=json.loads((p/'host-build.json').read_text())['library_sha256'],pair_shader_sha256=json.loads((p/'shader-build.json').read_text())['modules']['pair_subgroup_no_shmem.spv'],operator_primary=micro['primary'],scope='Five specified fullrequestedtarget-vocabulary rows/tokens/counters exact;actualpairuse inallactivecases,inactivecontrolsinallcases andfreshstock/frozencontrolsshort. Notallinternaltensors/draftscores/arbitrarycontexts. Inheritedzerooraclefields areunused(noGDNreaderindex);copylabels mayretainnative-command/GDNtext,actualassets/paths/modesgovern. NewhostallthreeTUs rebuilt;strictaliasfallback;noendtoendthroughputconclusionfromqualification/micro.')
(p/'qualification-summary.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
