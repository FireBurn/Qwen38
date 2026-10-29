from pathlib import Path
import json,re,math,statistics,sys
p=Path(sys.argv[1])if len(sys.argv)>1 else sorted((Path(__file__).resolve().parent/'micro').iterdir())[-1]
r=json.loads((p/'checks.json').read_text());groups={}
for a in r['timing_arms']:groups.setdefault((a['k'],a['rows'],a['cols'],a['replicas']),[]).append(a)
summary=[]
for key,aa in groups.items():
 ratios=[];blocks=[]
 for b in range(3):
  means=[statistics.mean(a['us']for a in aa if a['block']==b and a['mode']==m)for m in range(2)]
  ratio=means[1]/means[0];ratios.append(math.log(ratio));blocks.append({'block':b,'frozen_us':means[0],'reuse_us':means[1],'time_change_percent':100*(ratio-1)})
 mean=statistics.mean(ratios);err=4.302652729911275*statistics.stdev(ratios)/math.sqrt(3)
 summary.append(dict(zip(['k','rows','cols','replicas'],key),frozen_us=statistics.mean(a['us']for a in aa if a['mode']==0),reuse_us=statistics.mean(a['us']for a in aa if a['mode']==1),geometric_time_change_percent=100*math.expm1(mean),descriptive_t95_percent=[100*math.expm1(mean-err),100*math.expm1(mean+err)],blocks=blocks))
result={'complete':r['complete'],'arms':len(r['timing_arms']),'new_driver_errors':r['new_driver_errors'],'cases':summary,'interpretation':'GPU operator timing only. Negative time change is faster. Descriptive t intervals use three symmetric blocks (df2), temporal correlation and GPU workload differences limit generalization. No full-model performance established. Same112byteweightlayout,shaderonlycomparison;separate fromfailedfixed24modeldiscovery. Process-widesensors do notestablishper-armclock/loadmatching.'}
(p/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
for a in summary:print({k:v for k,v in a.items()if k!='blocks'})
