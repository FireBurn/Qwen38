from pathlib import Path
import json,math,statistics,sys
p=Path(__file__).resolve().parent;d=Path(sys.argv[1])if len(sys.argv)>1 else sorted((p/'timing-runs').iterdir())[-1]
r=json.loads((d/'checks.json').read_text());assert r['complete'] and len(r['timing_arms'])==144 and not r['new_driver_errors']
samples=[json.loads(x)for x in (d/'telemetry.jsonl').read_text().splitlines()];keys=['k','rows','cols','replicas','block','arm','mode'];groups={}
for s in samples:
 if 'arm'in s:groups.setdefault(tuple(s['arm'][k]for k in keys),[]).append(s)
rows=r['timing_arms'];arms=[]
for row in rows:
 ss=groups.get(tuple(row[k]for k in keys),[]);v=dict(row,samples=len(ss),sensor_errors=[s['sensor_error']for s in ss if 'sensor_error'in s]);
 for name,field in [('clock_mhz','freq1_input'),('cpu_busy','cpu_busy_fraction')]:
  vals=[float(s[field])/(1e6 if name=='clock_mhz'else 1)for s in ss if field in s];v[name]=statistics.mean(vals)if vals else None
 arms.append(v)
results=[]
for cols in [1,2]:
 for k in [5120,17408]:
  for replicas in [1,16]:
   subset=[a for a in arms if a['cols']==cols and a['k']==k and a['replicas']==replicas];blocks=[]
   for b in range(3):
    by={m:[a for a in subset if a['block']==b and a['mode']==m]for m in [0,1,2]};assert all(len(v)==2 for v in by.values())
    logs={m:statistics.mean(math.log(a['us'])for a in by[0])-statistics.mean(math.log(a['us'])for a in by[m])for m in [1,2]}
    clocks={m:statistics.mean(a['clock_mhz']for a in by[m])if all(a['clock_mhz']is not None for a in by[m])else None for m in by};cpu={m:statistics.mean(a['cpu_busy']for a in by[m])if all(a['cpu_busy']is not None for a in by[m])else None for m in by}
    valid=all(a['samples'] and not a['sensor_errors']for vv in by.values()for a in vv)and all(v is not None for v in clocks.values())and all(v is not None for v in cpu.values())
    comparable=bool(valid and max(clocks.values())/min(clocks.values())<=1.03 and max(cpu.values())-min(cpu.values())<=.05)
    blocks.append(dict(block=b,log_speed_ratios=logs,clock_mode_means=clocks,cpu_mode_means=cpu,comparable=comparable))
   estimates={}
   for m in [1,2]:
    vals=[b['log_speed_ratios'][m]for b in blocks];mu=statistics.mean(vals);half=4.302652729911275*statistics.stdev(vals)/math.sqrt(3)
    estimates[m]=dict(geometric_speed_change_percent=100*math.expm1(mu),descriptive_t95_percent=[100*math.expm1(mu-half),100*math.expm1(mu+half)])
   results.append(dict(cols=cols,k=k,replicas=replicas,mean_us={m:statistics.mean(a['us']for a in subset if a['mode']==m)for m in [0,1,2]},blocks=blocks,estimates=estimates,all_blocks_comparable=all(b['comparable']for b in blocks)))
out=dict(scope='Fixed144arm synthetic GPU timestamp experiment. Mode0 native,1 pad16,2 pad32. Positive speed changes mean faster. All3 blocks reported regardless of telemetry, df2 descriptive intervals; no model speed or additional throughput gain established.',arms=arms,results=results,total_samples=len(samples),samples_with_arm=sum('arm'in s for s in samples),sensor_errors=[s['sensor_error']for s in samples if 'sensor_error'in s]);(d/'analysis.json').write_text(json.dumps(out,indent=2)+'\n')
for v in results:print(v['cols'],v['k'],v['replicas'],v['mean_us'],v['estimates'],'comparable',v['all_blocks_comparable'])
