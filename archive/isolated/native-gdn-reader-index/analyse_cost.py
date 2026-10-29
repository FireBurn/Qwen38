from pathlib import Path
import json,re,statistics
p=sorted((Path(__file__).resolve().parent/'cost-runs').iterdir())[-1]
assert json.loads((p/'behavior-check.json').read_text())['all_tokens_and_counters_identical']
rows=[]
for part in (p/'run.log').read_text().split('INPROCESS_ARM_BEGIN ')[1:]:
 arm,mode=re.match(r'arm=(-?\d+) mode=([a-z_]+)',part).groups()
 if int(arm)<0:continue
 events={name:dict(count=int(n),wall_ns=int(w),cpu_ns=int(c)) for _,name,n,w,c in re.findall(r'NP_PROFILE arm=(\d+) event=([a-z_]+) count=(\d+) wall_ns=(\d+) cpu_ns=(\d+)',part)}
 assert len(events)==5
 rows.append(dict(arm=int(arm),mode=mode,events=events))
assert len(rows)==8
summary={mode:{e:dict(mean_cpu_ms=statistics.mean(r['events'][e]['cpu_ns']/1e6 for r in rows if r['mode']==mode),mean_wall_ms=statistics.mean(r['events'][e]['wall_ns']/1e6 for r in rows if r['mode']==mode)) for e in rows[0]['events']}for mode in ['legacy','indexed']}
report=dict(arms=rows,per_generation=summary,scope='Intrusive nested CPU scopes, four resident128token generations per mode after warmup. Do not add scopes or infer GPU time or throughput. Includes timer overhead. Index build is nested inside graph. Fixed discovery timing failed qualification; this diagnostic does not override it.')
(p/'analysis.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(summary,indent=2))
