from pathlib import Path
import json,re,statistics
p=sorted((Path(__file__).resolve().parent/'host-profile-runs').iterdir())[-1];text=(p/'run.log').read_text();execution=json.loads((p/'execution.json').read_text());assert execution['child_returncode']==0 and not execution['new_driver_errors'];assert json.loads((p/'behavior-check.json').read_text())['all_tokens_and_counters_identical']
rows=[]
for part in text.split('INPROCESS_ARM_BEGIN ')[1:]:
 arm,mode=re.match('arm=(-?[0-9]+) mode=([a-z_]+)',part).groups();arm=int(arm)
 if arm<0:continue
 events={name:{'count':int(n),'wall_ns':int(w),'cpu_ns':int(c)}for _,name,n,w,c in re.findall('NP_PROFILE arm=([0-9]+) event=([a-z_]+) count=([0-9]+) wall_ns=([0-9]+) cpu_ns=([0-9]+)',part)}
 assert len(events)==8
 for e in events.values():
  if e['count']:e.update(cpu_ns_per_call=e['cpu_ns']/e['count'],wall_ns_per_call=e['wall_ns']/e['count'])
 rows.append({'arm':arm,'mode':mode,'events':events})
assert len(rows)==8
summary={}
for mode in ['control','pad']:
 rr=[r for r in rows if r['mode']==mode];total_q3=sum(r['events']['mmvq']['count']for r in rr);summary[mode]={}
 for event in rows[0]['events']:
  count=sum(r['events'][event]['count']for r in rr);cpu=sum(r['events'][event]['cpu_ns']for r in rr);wall=sum(r['events'][event]['wall_ns']for r in rr)
  summary[mode][event]={'total_count':count,'cpu_us_per_Q3_mmvq':cpu/total_q3/1000,'wall_us_per_Q3_mmvq':wall/total_q3/1000,'cpu_ns_per_event':cpu/count if count else None,'wall_ns_per_event':wall/count if count else None}
report={'arms':rows,'normalized':summary,'scope':'Intrusive nested CPU/wall scopes; metrics overlap and must not be added. Native/padded resident128token arms, ABBA BAAB, one unmeasured warmup; no throughput inference. Profile event costs include timer overhead. Graph/submit events include work outside Q3. Normalized by Q3 MMVQ calls, not an asserted GPU-time fraction.'}
(p/'analysis.json').write_text(json.dumps(report,indent=2)+chr(10));print(json.dumps(summary,indent=2))
