from pathlib import Path
import json,hashlib
p=Path(__file__).resolve().parent;b=p.parent;screen=sorted((p/'submission-cap-screen512').iterdir())[-1];f=screen/'screen.json';selection=json.loads(f.read_text())['selected_mode'];assert selection in ['cap200','cap400']
s=(b/'run_q3_submission_cap_screen.py').read_text().replace("out=project/'submission-cap-screen512'","out=project/'submission-cap-confirm512'")
seq=[]
for i in range(6):seq += ['cap100',selection,selection,'cap100']if i%2==0 else[selection,'cap100','cap100',selection]
s=s.replace("modes=['cap100','cap200','cap400'];sequence=modes+list(reversed(modes));rows=[]",'modes='+repr(['cap100',selection])+';sequence='+repr(seq)+';rows=[]')
old="(out/'protocol.json').write_text((project/'submission-cap-plan.json').read_text())"
meta=dict(selected_mode=selection,screen=str(screen.relative_to(p)),screen_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),sequence=seq,plan=json.loads((p/'submission-cap-plan.json').read_text()))
s=s.replace(old,"(out/'protocol.json').write_text("+repr(json.dumps(meta,indent=2)+'\n')+")")
s=s.replace("assets=[Path(__file__)","assert json.loads((project/'submission-cap-prompts128/comparison.json').read_text())['all_requested_target_logit_bits_identical']\nassets=[Path(__file__)",1)
a=s.index('means={m:statistics.mean');s=s[:a]+'''
import math
blocks=[]
for start in range(0,len(rows),4):
 block=rows[start:start+4];by={m:[r for r in block if r['mode']==m]for m in modes};assert all(len(v)==2 for v in by.values())
 def means(key):return {m:statistics.mean(r[key]for r in v)for m,v in by.items()}
 cpu=means('phase_cpu_busy_mean');clock=means('steady_clock_median_mhz');builds=means('phase_build_process_mean');runqueue=means('phase_runnable_mean')
 comparable=max(cpu.values())-min(cpu.values())<=.05 and max(clock.values())/min(clock.values())<=1.03 and max(builds.values())-min(builds.values())<=2 and max(runqueue.values())-min(runqueue.values())<=max(4,.15*statistics.mean(runqueue.values()))and all(r['clock_settled']for r in block)
 effect=statistics.mean(math.log(r['steady_tokens_per_second'])for r in by[modes[1]])-statistics.mean(math.log(r['steady_tokens_per_second'])for r in by['cap100'])
 blocks.append(dict(indices=[r['index']for r in block],cpu_mode_means=cpu,gpu_clock_mode_means=clock,build_mode_means=builds,runnable_mode_means=runqueue,comparable=comparable,log_effect=effect,speed_change_percent=100*math.expm1(effect)))
def estimate(values):
 n=len(values)
 if n<4:return dict(blocks=n,qualified=False,reason='Fewer than4matched blocks')
 mu=statistics.mean(values);half={4:3.182446305284263,5:2.776445105197799,6:2.570581835636305}[n]*statistics.stdev(values)/math.sqrt(n)
 return dict(blocks=n,geometric_speed_change_percent=100*math.expm1(mu),descriptive_t95_percent=[100*math.expm1(mu-half),100*math.expm1(mu+half)],lower_bound_positive=mu-half>0)
report=dict(selected_mode=modes[1],blocks=blocks,all6block_descriptive=estimate([v['log_effect']for v in blocks]),matched_primary=estimate([v['log_effect']for v in blocks if v['comparable']]),mean_steady_tps={m:statistics.mean(r['steady_tokens_per_second']for r in rows if r['mode']==m)for m in modes},all_tokens_and_counters_identical=True,scope='Fixed24fresh512token confirmation, sixABBA/BAABblocks. Same frozen Q3 library/shaders; only submission cap differs. Incremental versuscap100,not a direct stock contrast. Matching only by preset telemetry;all results retained,no extension. Descriptive intervals,small sample/timecorrelation limitations.')
report['incremental_gain_supported']=report['matched_primary'].get('lower_bound_positive',False)
(out/'confirmation-analysis.json').write_text(json.dumps(report,indent=2)+'\\n');print('SUBMISSION_CAP_CONFIRMATION',report,flush=True)
'''
(b/'run_q3_submission_cap_confirm.py').write_text(s)
# Selected-cap coding/math audit, preserving the reference hashes and all original guards.
s=(b/'run_q3_pad112_guard_v2_prompts128.py').read_text().replace("out=p/'guard-v2-prompts128'","out=p/'submission-cap-prompts128'").replace("host=p/'host-fast-guard-v2'","host=p/'qualified-20261029'").replace('GGML_VK_Q3_PAD112_DIR=str(p)','GGML_VK_Q3_PAD112_DIR=str(host/\'shaders\')')
s=s.replace("trial.update(GGML_VK_VISIBLE_DEVICES=","trial.update(GGML_VK_MAX_NODES_PER_SUBMIT="+repr(selection[3:])+",GGML_VK_VISIBLE_DEVICES=")
(b/'run_q3_submission_cap_prompts128.py').write_text(s)
f=b/'run_private_guarded_batch.py';s=f.read_text().replace("'run_q3_submission_cap_screen.py'","'run_q3_submission_cap_screen.py','run_q3_submission_cap_confirm.py','run_q3_submission_cap_prompts128.py'",1);f.write_text(s)
print('Prepared fixed confirmation',selection)
