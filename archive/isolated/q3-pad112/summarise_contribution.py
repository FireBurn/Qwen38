from pathlib import Path
import json,statistics,math,sys
p=Path(__file__).resolve().parent;d=Path(sys.argv[1])if len(sys.argv)>1 else sorted((p/'contribution512').iterdir())[-1]
a=json.loads((d/'confirmation-analysis.json').read_text());r=json.loads((d/'results.json').read_text());assert len(r)==36 and a['all_tokens_and_counters_identical']and all(not v['new_driver_errors']and v['under_load_measurement_valid']for v in r)
modes=['stock100','stock400','frozen400'];out={}
for m in modes:
 rr=[v for v in r if v['mode']==m];samples=[];optional_errors=[]
 for v in rr:
  t=json.loads((d/(f"{v['index']:02d}-{m}-telemetry.json")).read_text());samples += [x for x in t['samples']if x['steady_seen']and x['gpu_busy']>=50]
  optional_errors += [e for x in t['samples']for e in x.get('optional_sensor_errors',[])]
 outcomes={}
 for name in ['clock_mhz','memory_clock_mhz','power_watts','temperature_c','gpu_busy','cpu_busy','vram_bytes']:
  vals=sorted(float(x[name])for x in samples if x.get(name)is not None)
  outcomes[name]=dict(samples=len(vals),mean=statistics.mean(vals),p10=vals[len(vals)//10],median=statistics.median(vals),p90=vals[min(len(vals)-1,9*len(vals)//10)])if vals else dict(samples=0)
 out[m]=dict(arms=len(rr),means={k:statistics.mean(v[k]for v in rr)for k in ['steady_tokens_per_second','total_generation_tokens_per_second','encode_seconds','cold_first_window_seconds','total_generation_seconds','process_wall_seconds']},clock_settled_arms=sum(v['clock_settled']for v in rr),outcomes=outcomes,optional_sensor_errors=optional_errors)
def estimate(vals):
 n=len(vals)
 if n<4:return dict(blocks=n,qualified=False)
 mu=statistics.mean(vals);half={4:3.182446305284263,5:2.776445105197799,6:2.570581835636305}[n]*statistics.stdev(vals)/math.sqrt(n)
 return dict(blocks=n,geometric_speed_change_percent=100*math.expm1(mu),descriptive_t95_percent=[100*math.expm1(mu-half),100*math.expm1(mu+half)])
contrasts={}
for field in ['steady_tokens_per_second','total_generation_tokens_per_second']:
 contrasts[field]={}
 for name,treatment,control in [('cap_only','stock400','stock100'),('cache_incremental','frozen400','stock400'),('combo_vs_stock','frozen400','stock100')]:
  vals=[]
  for b in a['blocks']:
   if not b['comparable']:continue
   block=[r[i]for i in b['indices']];effect=statistics.mean(math.log(v[field])for v in block if v['mode']==treatment)-statistics.mean(math.log(v[field])for v in block if v['mode']==control);vals.append(effect)
  contrasts[field][name]=estimate(vals)
report=dict(modes=out,matched_contrasts=contrasts,all_tokens_and_counters_identical=True,new_driver_errors=[],scope='Supplement to predeclared contribution experiment. Clock/power/temperature are outcomes; optional sensor errors retained and do not alter mandatory external matching. Pooled mode means include all arms. Full-generation TPS contrast is descriptive secondary,not another primary test. Sensor mean power is not integrated energy or controlled-clock causality. No new samples or matching-rule changes.')
(d/'outcomes-summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(matched_contrasts=contrasts,means={m:v['means']for m,v in out.items()},power={m:v['outcomes']['power_watts']for m,v in out.items()},vram={m:v['outcomes']['vram_bytes']for m,v in out.items()}),indent=2))
