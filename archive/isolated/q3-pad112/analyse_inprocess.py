from pathlib import Path
import json,statistics,math,sys
p=Path(sys.argv[1])if len(sys.argv)>1 else sorted((Path(__file__).resolve().parent/'inprocess').iterdir())[-1];r=json.loads((p/'checks.json').read_text());rows=[a for a in r['arms']if a['arm']>=0];blocks=[];effects=[]
telemetry=[json.loads(x)for x in(p/'telemetry.jsonl').read_text().splitlines()]
for a in rows:a['active_clock_samples']=sum(t.get('arm')==a['arm']and t.get('steady_seen',False)and t.get('gpu_busy',0)>=50 and 'clock_mhz'in t for t in telemetry)
for i in range(6):
 bb=rows[i*4:i*4+4];by={m:[a for a in bb if a['mode']==m]for m in ['control','pad']};assert all(len(v)==2 for v in by.values())
 clocks={m:statistics.mean(a['clock_median_mhz']for a in v)for m,v in by.items()};cpu={m:statistics.mean(a['cpu_mean']for a in v)for m,v in by.items()};builds={m:statistics.mean(a['build_mean']for a in v)for m,v in by.items()}
 comparable=max(clocks.values())/min(clocks.values())<=1.03 and max(cpu.values())-min(cpu.values())<=.05 and max(builds.values())-min(builds.values())<=2 and all(a['active_clock_samples']>=8 and a['samples']>=8 and not a['sensor_errors']for a in bb)
 effect=statistics.mean(math.log(a['steady_tps'])for a in by['pad'])-statistics.mean(math.log(a['steady_tps'])for a in by['control']);effects.append(effect)
 blocks.append({'block':i,'arms':[a['arm']for a in bb],'clock_mode_means_mhz':clocks,'cpu_mode_means':cpu,'build_mode_means':builds,'comparable':comparable,'speed_change_percent':100*math.expm1(effect)})
mean=statistics.mean(effects);half=2.570581835636305*statistics.stdev(effects)/math.sqrt(6)
result={'means_tps':{m:statistics.mean(a['steady_tps']for a in rows if a['mode']==m)for m in ['control','pad']},'geometric_speed_change_percent':100*math.expm1(mean),'descriptive_t95_percent':[100*math.expm1(mean-half),100*math.expm1(mean+half)],'all_blocks_comparable':all(b['comparable']for b in blocks),'gain_supported':r['returncode']==0 and not r['new_driver_errors']and all(b['comparable']for b in blocks)and mean-half>0,'blocks':blocks,'all_tokens_and_counters_identical':r['all_tokens_and_counters_identical'],'new_driver_errors':r['new_driver_errors'],'scope':'Six fixed within-process symmetric blocks, df5 descriptive Student-t interval; temporal correlation and limited sample remain. Resident model private native vs padded only; no direct unmodified-stock, long-context or cold-load gain established.'}
(p/'analysis.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
