from pathlib import Path
import json,re,statistics,sys
out=Path(sys.argv[1]);text=(out/'run.log').read_text();assert text.count('INPROCESS_ARM_END ')==25,'Run incomplete'
telemetry=[json.loads(x)for x in(out/'telemetry.jsonl').read_text().splitlines()];rows=[];ref=None
for part in text.split('INPROCESS_ARM_BEGIN ')[1:]:
 arm,mode,start=re.match(r'arm=(-?[0-9]+) mode=([a-z_]+) time_us=([0-9]+)',part).groups();arm=int(arm)
 mt=re.search(r'FULL_MODEL_TIMING warm_tokens=([0-9]+) cold_generation_us=([0-9]+) steady_tokens=([0-9]+) steady_us=([0-9]+) total_generation_us=([0-9]+)',part);assert mt
 warm,cold,n,us,total=map(int,mt.groups());tokens=list(map(int,re.findall(r'ACCEPTED_TOKEN ([0-9]+)',part)))
 fields={k:int(re.findall(k+r'[ ]*=[ ]*([0-9]+)',part)[-1])for k in ['n_drafted','n_accept','n_predict']}
 behavior={'tokens':tokens,**fields,'warm':warm,'steady_tokens':n};assert len(tokens)>=128
 if ref is None:ref=behavior
 assert behavior==ref,('Reset/mode behavior differs',arm)
 samples=[r for r in telemetry if r.get('arm')==arm and r.get('steady_seen')];active=[r for r in samples if r.get('gpu_busy',0)>=50 and 'clock_mhz'in r]
 rows.append({'arm':arm,'mode':mode,'steady_tps':n*1e6/us,'steady_us':us,'cold_us':cold,'total_us':total,**behavior,'samples':len(samples),'active_clock_samples':len(active),'clock_median_mhz':statistics.median(r['clock_mhz']for r in active)if active else None,'cpu_mean':statistics.mean(r['cpu_busy']for r in samples if'cpu_busy'in r)if samples else None,'build_mean':statistics.mean(r['builds']for r in samples if'builds'in r)if samples else None,'sensor_errors':[r['sensor_error']for r in samples if'sensor_error'in r]})
execution=json.loads((out/'execution.json').read_text())if(out/'execution.json').exists()else{'child_returncode':None,'failure':'Original harness failed to persist child code before report-parser error','new_driver_errors':None}
report={'returncode':execution['child_returncode'],'failure':execution['failure'],'new_driver_errors':execution['new_driver_errors'],'arms':rows,'all_tokens_and_counters_identical':True,'scope':'CPU-only corrected parsing of unchanged completed GPU log. One warmup plus24fixed128token resident-model arms. Native/padded private host; no stock/cold-start comparison. Unknown child exit status prevents full qualification of first attempt.'}
assert len(rows)==25
(out/'checks.json').write_text(json.dumps(report,indent=2)+chr(10));print('PARSED_25_IDENTICAL_GENERATIONS',out,'child_returncode',report['returncode'])
