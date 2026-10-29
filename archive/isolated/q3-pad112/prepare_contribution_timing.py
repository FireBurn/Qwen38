from pathlib import Path
p=Path(__file__).resolve().parent;b=p.parent
s=(b/'run_q3_submission_system_effect.py').read_text().replace("out=project/'submission-system-effect512'","out=project/'contribution512'").replace("project/'submission-system-effect-plan.json'","project/'contribution-plan.json'")
a=s.index('modes=');z=s.index('runtime_lib=',a);modes=['stock100','stock400','frozen400'];seq=[]
for i in range(6):abc=modes[i%3:]+modes[:i%3];seq+=abc+list(reversed(abc))
s=s[:a]+'modes='+repr(modes)+';sequence='+repr(seq)+';rows=[]\n'+s[z:]
s=s.replace("selected_host=stock if mode=='stock100'else", "selected_host=stock if mode.startswith('stock')else").replace("'model-timing-cache-stock'if mode=='stock100'else", "'model-timing-cache-stock'if mode.startswith('stock')else").replace("'400'if mode=='frozen400'else'100'", "'100'if mode=='stock100'else'400'").replace("if mode!='stock100':trial.update", "if mode=='frozen400':trial.update")
needle='assets=[stock';assert needle in s
s=s.replace(needle,"assert json.loads((project/'contribution-stock400-model32/comparison.json').read_text())['all_requested_target_logit_bits_identical']\nassert json.loads((project/'contribution-stock400-populated-kv64/comparison.json').read_text())['all_requested_target_logit_bits_identical']\n"+needle,1)
a=s.index('\nimport math\nblocks=[]');s=s[:a]+'''
import math
blocks=[]
contrast_names=['cap_only','cache_incremental','combo_vs_stock']
for start in range(0,len(rows),6):
 block=rows[start:start+6];by={m:[r for r in block if r['mode']==m]for m in modes};assert all(len(v)==2 for v in by.values())
 def means(key):return {m:statistics.mean(r[key]for r in v)for m,v in by.items()}
 cpu=means('phase_cpu_busy_mean');clock=means('steady_clock_median_mhz');builds=means('phase_build_process_mean');runqueue=means('phase_runnable_mean')
 comparable=max(cpu.values())-min(cpu.values())<=.05 and max(builds.values())-min(builds.values())<=2 and max(runqueue.values())-min(runqueue.values())<=max(4,.15*statistics.mean(runqueue.values()))
 logs={m:statistics.mean(math.log(r['steady_tokens_per_second'])for r in v)for m,v in by.items()}
 contrasts=dict(cap_only=logs['stock400']-logs['stock100'],cache_incremental=logs['frozen400']-logs['stock400'],combo_vs_stock=logs['frozen400']-logs['stock100'])
 blocks.append(dict(indices=[r['index']for r in block],cpu_mode_means=cpu,gpu_clock_mode_means=clock,build_mode_means=builds,runnable_mode_means=runqueue,comparable=comparable,log_effects=contrasts,speed_changes_percent={m:100*math.expm1(v)for m,v in contrasts.items()}))
def estimate(values):
 n=len(values)
 if n<4:return dict(blocks=n,qualified=False,reason='Fewer than4matchedblocks')
 mu=statistics.mean(values);half={4:3.182446305284263,5:2.776445105197799,6:2.570581835636305}[n]*statistics.stdev(values)/math.sqrt(n)
 return dict(blocks=n,geometric_speed_change_percent=100*math.expm1(mu),descriptive_t95_percent=[100*math.expm1(mu-half),100*math.expm1(mu+half)],lower_bound_positive=mu-half>0)
matched=[b for b in blocks if b['comparable']]
ni=estimate([-b['log_effects']['cache_incremental']for b in matched]);ni['margin_percent']=-1.;ni['within_1percent_slower_supported']=bool(ni.get('descriptive_t95_percent',[-100])[0]>-1)
report=dict(blocks=blocks,all6block_descriptive={m:estimate([b['log_effects'][m]for b in blocks])for m in contrast_names},matched={m:estimate([b['log_effects'][m]for b in matched])for m in contrast_names},stock400_vs_frozen400_noninferiority=ni,mean_steady_tps={m:statistics.mean(r['steady_tokens_per_second']for r in rows if r['mode']==m)for m in modes},all_tokens_and_counters_identical=True,scope='Fixed36arm contribution experiment. Primary stock400vsstock100,secondary frozen400vsstock400;combo_vsstock descriptive. NaturalDVFS whole-configuration effects with preset externalCPU/build/runqueue matching,>=4blocks. Noninferiority margin1% predeclared;not equivalence. Allresults retained,no sampleextension,small sample/timecorrelation limits.')
report['stock400_gain_supported']=report['matched']['cap_only'].get('lower_bound_positive',False);report['cache_incremental_gain_supported']=report['matched']['cache_incremental'].get('lower_bound_positive',False)
(out/'confirmation-analysis.json').write_text(json.dumps(report,indent=2)+'\\n');print('CONTRIBUTION_CONFIRMATION',report,flush=True)
'''
(b/'run_q3_contribution_timing.py').write_text(s)
f=b/'run_private_guarded_batch.py';s=f.read_text().replace("'run_q3_submission_system_effect.py'","'run_q3_submission_system_effect.py','run_q3_contribution_timing.py'",1);f.write_text(s)
