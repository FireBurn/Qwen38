from pathlib import Path
import json,sys
p=Path(__file__).resolve().parent;b=p.parent;screen=Path(sys.argv[1]);selection=json.loads((screen/'screen.json').read_text());best=selection['selected_mode'];assert best in ['fuse','quant','both']
s=(b/'run_q3_pad112_guard_v2_matched_stock.py').read_text().replace("project/'guard-v2-matched-stock512'","project/'fusion-combination-confirm512'").replace("project/'guard-v2-model32/comparison.json'","project/'fusion-options-model136/comparison.json'").replace("project/'host-fast-guard-v2/bin/","project/'host-fusion-options/bin/")
a=s.index("modes=['stock'");z=s.index('rows=[]',a)+len('rows=[]');modes=['stock','frozen','best'];sequence=[]
for i in range(6):
 abc=modes[i%3:]+modes[:i%3];sequence+=abc+abc[::-1]
s=s[:a]+"selected="+repr(best)+";modes="+repr(modes)+";sequence="+repr(sequence)+";rows=[]"+s[z:]
a=s.index("(out/'protocol.json').write_text");z=s.index("(out/'assets.json')",a);protocol={'selected_mode':best,'screen':str(screen),'screen_sha256':__import__('hashlib').sha256((screen/'screen.json').read_bytes()).hexdigest(),'sequence':sequence,'plan':json.loads((p/'fusion-combination-plan.json').read_text())};s=s[:a]+"(out/'protocol.json').write_text("+repr(json.dumps(protocol,indent=2)+chr(10))+")\n"+s[z:]
s=s.replace("selected_host=stock if mode=='stock'else project/'host-fast-guard-v2'","selected_host=stock if mode=='stock'else project/'qualified-20261029'if mode=='frozen'else project/'host-fusion-options'")
needle=" if mode=='pad':trial.update(GGML_VK_Q3_PAD112_ARENA='1',GGML_VK_Q3_PAD112_DIR=str(project),GGML_VK_Q3_PAD112_IMMUTABLE='1')";assert needle in s
s=s.replace(needle,""" if mode!='stock':trial.update(GGML_VK_Q3_PAD112_ARENA='1',GGML_VK_Q3_PAD112_DIR=str(project/'qualified-20261029/shaders'if mode=='frozen'else project),GGML_VK_Q3_PAD112_IMMUTABLE='1')
 if mode=='best'and selected in ['fuse','both']:trial.update(GGML_VK_NATIVE_GLUQ_FUSE='1',GGML_VK_NATIVE_GLUQ_SHADER=str(base/'native-swiglu-q8/shuffle8/fused.comp.spv'),GGML_VK_NATIVE_GLUQ_GROUPS='136',GGML_VK_NATIVE_GLUQ_EXPAND_VIEWS='1',GGML_VK_NATIVE_GLUQ_COALESCE='1')
 if mode=='best'and selected in ['quant','both']:trial.update(GGML_VK_NATIVE_Q8_SHUFFLE='1',GGML_VK_NATIVE_Q8_SHADER=str(base/'native-quant-shuffle/shuffle.spv'))""")
a=s.index('means={m:');s=s[:a]+'''
import math
blocks=[]
for start in range(0,len(rows),6):
 block=rows[start:start+6];by={m:[r for r in block if r['mode']==m]for m in modes};assert all(len(v)==2 for v in by.values())
 def means(key):return {m:statistics.mean(r[key]for r in v)for m,v in by.items()}
 cpu=means('phase_cpu_busy_mean');clock=means('steady_clock_median_mhz');builds=means('phase_build_process_mean');runqueue=means('phase_runnable_mean')
 comparable=max(cpu.values())-min(cpu.values())<=.05 and max(clock.values())/min(clock.values())<=1.03 and max(builds.values())-min(builds.values())<=2 and max(runqueue.values())-min(runqueue.values())<=max(4,.15*statistics.mean(runqueue.values()))and all(r['clock_settled']for r in block)
 contrasts={m:statistics.mean(math.log(r['steady_tokens_per_second'])for r in by['best'])-statistics.mean(math.log(r['steady_tokens_per_second'])for r in by[m])for m in ['frozen','stock']}
 blocks.append({'indices':[r['index']for r in block],'cpu_mode_means':cpu,'gpu_clock_mode_means':clock,'build_mode_means':builds,'runnable_mode_means':runqueue,'comparable':comparable,'log_effects':contrasts,'speed_changes_percent':{m:100*math.expm1(v)for m,v in contrasts.items()}})
def estimate(values):
 n=len(values)
 if n<4:return {'blocks':n,'qualified':False,'reason':'Fewer than4matchedblocks'}
 critical={4:3.182446305284263,5:2.776445105197799,6:2.570581835636305}[n];mean=statistics.mean(values);half=critical*statistics.stdev(values)/math.sqrt(n)
 return {'blocks':n,'geometric_speed_change_percent':100*math.expm1(mean),'descriptive_t95_percent':[100*math.expm1(mean-half),100*math.expm1(mean+half)],'lower_bound_positive':mean-half>0}
report={'selected_mode':selected,'blocks':blocks,'all6block_descriptive':{m:estimate([b['log_effects'][m]for b in blocks])for m in ['frozen','stock']},'matched_primary':{m:estimate([b['log_effects'][m]for b in blocks if b['comparable']])for m in ['frozen','stock']},'mean_steady_tps':{m:statistics.mean(r['steady_tokens_per_second']for r in rows if r['mode']==m)for m in modes},'all_tokens_and_counters_identical':True,'scope':'Fixed36fresh512token arms after fixedscreenselection. Matchedblocks selectedonlybytelemetry;>=4required. Primarygainagainstfrozen,secondaryagainststock. No samplingextension or percentageaddition; runtimeinode fixed. Limitedsample/temporalcorrelation caveats.'}
report['incremental_gain_supported']=report['matched_primary']['frozen'].get('lower_bound_positive',False);report['stock_gain_supported']=report['matched_primary']['stock'].get('lower_bound_positive',False)
(out/'confirmation-analysis.json').write_text(json.dumps(report,indent=2)+chr(10));print('FUSION_CONFIRMATION',report,flush=True)
'''
# Include the frozen baseline itself in the input fingerprint, not just its path.
s=s.replace("(out/'assets.json').write_text", "assets += [project/'qualified-20261029/manifest.json',project/'qualified-20261029/bin/libggml-vulkan.so.0.27.0']\n(out/'assets.json').write_text")
(b/'run_q3_pad112_combination_confirm.py').write_text(s)
f=b/'run_private_guarded_batch.py';s=f.read_text().replace("allowed={'run_q3_pad112_combination_screen.py'","allowed={'run_q3_pad112_combination_confirm.py','run_q3_pad112_combination_screen.py'");f.write_text(s)
print(best)
