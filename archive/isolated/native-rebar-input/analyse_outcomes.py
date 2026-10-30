from pathlib import Path
import json,statistics,math,sys
p=Path(sys.argv[1]);d=json.loads((p/'confirmation-analysis.json').read_text());rows=json.loads((p/'results.json').read_text());assert len(rows)==48;selected=d['selected_mode'];matched=[b for b in d['blocks']if b['comparable']]
def calc(blocks,key):
 effects=[]
 for b in blocks:
  r=[rows[i]for i in b['indices']];effects.append(statistics.mean(math.log(v[key])for v in r if v['mode']==selected)-statistics.mean(math.log(v[key])for v in r if v['mode']=='frozen'))
 if not effects:return None
 n=len(effects);mu=statistics.mean(effects);out=dict(blocks=n,geometric_change_percent=100*math.expm1(mu))
 if n>=4:
  half={4:3.182446305284263,5:2.776445105197799,6:2.570581835636305,7:2.44691185114497,8:2.3646242515927844,9:2.306004135204166,10:2.2621571628540993,11:2.2281388519649385,12:2.200985160082949}[n]*statistics.stdev(effects)/math.sqrt(n);out['descriptive_t95_percent']=[100*math.expm1(mu-half),100*math.expm1(mu+half)]
 return out
out={}
for label,blocks in [('all12',d['blocks']),('matched',matched)]:
 ids=[i for b in blocks for i in b['indices']];r=[rows[i]for i in ids];out[label]=dict(full_generation_speed=calc(blocks,'total_generation_tokens_per_second'),steady_speed=calc(blocks,'steady_tokens_per_second'),mode_means={m:{k:statistics.mean(v[k]for v in r if v['mode']==m)for k in ['steady_tokens_per_second','total_generation_tokens_per_second','total_generation_seconds','encode_seconds','process_wall_seconds','phase_cpu_busy_mean','phase_build_process_mean','phase_runnable_mean','steady_clock_median_mhz','phase_power_w_mean','phase_vram_bytes_mean']}for m in ['frozen',selected]})if ids else None
out['scope']='Secondarydescriptiveoutcomesonly;notnewmatchingrulesorindependentconfirmation,notpooledwithanyotherexperiment. Naturalclocks/powerandCPUloadreportedasobserved. Fullgenerationspeedincludeswarmwindow;processincludesload/encoding. Noequalclock/generalizationclaim.'
(p/'outcomes-summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
