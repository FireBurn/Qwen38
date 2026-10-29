from pathlib import Path
import json,math,statistics
p=sorted((Path(__file__).resolve().parent/'timing').iterdir())[-1];r=json.loads((p/'checks.json').read_text());assert r['complete'] and r['returncode']==0 and not r['new_driver_errors'];samples=[json.loads(l)for l in(p/'telemetry.jsonl').read_text().splitlines()];cases=[]
for cols in [1,2]:
 for replicas in [1,8]:
  arms=[x.copy()for x in r['timing_arms']if x['cols']==cols and x['replicas']==replicas];blocks=[]
  for arm in arms:
   ss=[x for x in samples if arm['start_ns']<=x['monotonic_ns']<=arm['end_ns']];arm['telemetry_samples']=len(ss);arm['sensor_errors']=[e for x in ss for e in x['sensor_errors']]
   for key in ['cpu_busy','clock_mhz','power_w','gpu_busy','builds']:
    values=[x[key]for x in ss if key in x and x[key]is not None];arm[key+'_mean']=statistics.mean(values)if values else None
  for block in range(6):
   aa=[a for a in arms if a['block']==block];by={mode:[a for a in aa if a['mode']==mode]for mode in [0,1]};assert all(len(x)==2 for x in by.values())
   effect=statistics.mean(math.log(a['us'])for a in by[1])-statistics.mean(math.log(a['us'])for a in by[0]);blocks.append(dict(block=block,log_time_ratio=effect,time_change_percent=100*math.expm1(effect)))
  mu=statistics.mean(b['log_time_ratio']for b in blocks);half=2.570581835636305*statistics.stdev(b['log_time_ratio']for b in blocks)/math.sqrt(6)
  cases.append(dict(cols=cols,replicas=replicas,reference_us=statistics.mean(a['us']for a in arms if a['mode']==0),fused_us=statistics.mean(a['us']for a in arms if a['mode']==1),geometric_time_change_percent=100*math.expm1(mu),descriptive_t95_percent=[100*math.expm1(mu-half),100*math.expm1(mu+half)],blocks=blocks,arms=arms))
primary=next(c for c in cases if c['cols']==2 and c['replicas']==8)
report=dict(cases=cases,primary=dict(cols=2,replicas=8,time_change_percent=primary['geometric_time_change_percent'],descriptive_t95_percent=primary['descriptive_t95_percent']),screen_justifies_host_prototype=primary['descriptive_t95_percent'][1]<0,scope='Fixed96-arm operator screen,alloutputs exact;negative timechange faster. Same112weights andnativeindependentmatpairallowedoverlap;productionGLUmodule. Sixpairedlogblocks/condition,df5descriptiveintervals. Per-armtelemetrydescriptive only,noformalclock/loadgate orendtoendgainqualification. Activationquantizationexcludedboth;hostintegrationsafetyand5modelaudits+fixedA/B stillrequired. No sampleextension.')
(p/'analysis.json').write_text(json.dumps(report,indent=2)+'\n')
for c in cases:print({k:v for k,v in c.items()if k not in ['arms','blocks']})
print('HOST_PROTOTYPE_TRIGGER',report['screen_justifies_host_prototype'])
