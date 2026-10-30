from pathlib import Path
import json,collections,statistics,re
p=Path(__file__).resolve().parent;b=p.parent;cases=[]
for folder in ['model32','prompts128','populated-kv64','boundary128']:
 assert json.loads((p/folder/'comparison.json').read_text())['all_requested_target_logit_bits_identical'];rr=json.loads((p/folder/'checks.json').read_text());cases.extend(dict(case=v.get('case',folder),target_rows=v['target_logit_rows'],sha256=v['target_logit_audit_sha256'])for v in rr if v['mapped_vram_requested']);assert all(not v['new_driver_errors']for v in rr)
assert sum(v['target_rows']for v in cases)==530
(p/'qualification-summary.json').write_text(json.dumps(dict(cases=cases,target_rows=530,scope='Sameimmutablequalifiedcore/backend/shaders;onlychildprocessunsetsdisablehostvisibleVRAM. Allrequestedtargetbits/tokens/counters exact,noGPUerrors;notallcontexts/performanceproof.'),indent=2)+'\n')
r=sorted((b/'native-transfer-observer/mapped-metadata-runs').iterdir())[-1];ex=json.loads((r/'execution.json').read_text());assert ex['child_returncode']==0 and not ex['new_driver_errors'];assert json.loads((r/'behavior-check.json').read_text())['all_tokens_and_counters_identical'];old=b/'native-transfer-observer/metadata-runs/20261029T210122Z';arms=[]
for arm in range(4):
 meta=json.loads((r/f'metadata-{arm}.json').read_text());ref=json.loads((old/f'metadata-{arm}.json').read_text());assert meta==ref and not meta['dropped'];events=json.loads((r/f'arm-{arm}.json').read_text());events.sort(key=lambda v:(v['begin_ns'],-v['end_ns']));stack=[];q=collections.Counter();set_wall=set_cpu=0
 for e in events:
  while stack and e['begin_ns']>=stack[-1]['end_ns']:stack.pop()
  if stack:assert e['end_ns']<=stack[-1]['end_ns']
  if e['kind']==4:set_wall+=e['end_ns']-e['begin_ns'];set_cpu+=e['cpu_ns']
  if e['kind']==3:q['sync_set'if any(v['kind']==4 for v in stack)else'graph'if any(v['kind']==0 for v in stack)else'other_outside']+=1
  stack.append(e)
 assert q['sync_set']==0 and sum(q.values())==2137
 arms.append(dict(arm=arm,queues=dict(q),fence_waits=sum(v['kind']==2 for v in events),set_wall_ns=set_wall,set_cpu_ns=set_cpu,metadata_matches_unmapped=True))
(p/'profile-summary.json').write_text(json.dumps(dict(profile=str(r),arms=arms,baseline_queue_calls=4579,candidate_queue_calls=2137,baseline_sync_set_queue_calls=1850,candidate_sync_set_queue_calls=0,baseline_fence_waits=518,candidate_fence_waits=222,mean_set_wall_ms=statistics.mean(v['set_wall_ns']for v in arms)/1e6,mean_set_cpu_ms=statistics.mean(v['set_cpu_ns']for v in arms)/1e6,scope='CPUinstrumentedmechanismprofileonly,notmatchedTPScomparison. Allsixnative129tokens/74drafts/55accepts exact;fourmetadatahistogramsidentical,zerooverflow/noGPUerrors.Nativeallocationfallbackexistsbutobservedqueuesprovenactivepath.'),indent=2)+'\n');print('REBAR_530_TARGET_ROWS_EXACT_AND_2442_FEWER_QUEUE_CALLS',r)
