from pathlib import Path
import re
p=Path(__file__).resolve().parent;b=p.parent;s=(b/'run_native_rebar_timing.py').read_text().replace("project=base/'native-rebar-input'","project=base/'native-default-baseline'")
s=s.replace("v.get('mapped_vram_requested')","v.get('candidate_q3')")
s=s.replace(" selected_host=frozen if mode=='frozen'else frozen"," selected_host=stock if mode.startswith('stock')else frozen")
s=s.replace(" trial.update(GGML_VK_Q3_PAD112_ARENA='1'", " if mode=='q3_400':trial.update(GGML_VK_Q3_PAD112_ARENA='1'",1)
s=s.replace(" if mode=='mapped':trial.pop('GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM',None)"," [trial.pop(k,None)for k in ['GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM','GGML_VK_PREFER_HOST_MEMORY','GGML_VK_ALLOW_GRAPHICS_QUEUE','GGML_VK_SUBALLOCATION_BLOCK_SIZE']]\n if mode=='stock100':trial.pop('GGML_VK_MAX_NODES_PER_SUBMIT',None)")
start=s.index("(out/'protocol.json').write_text");end=s.index("assert hashlib.sha256",start)
s=s[:start]+"(out/'protocol.json').write_text(json.dumps(dict(plan=(project/'MODEL-TIMING-PLAN.md').read_text(),sequence=sequence,modes=modes,primary='q3_400 versus stock100',secondary=['stock400 versus stock100','q3_400 versus stock400'],allocation_queue_suballocation_defaults=True),indent=2)+'\\n')\n"+s[end:]
# Declare balanced sequence before assets/protocol are captured.
a=s.index("project=base/'native-default-baseline'");z=s.index('\n',a)
s=s[:z]+"\nmodes=['stock100','stock400','q3_400'];permutations=[(0,1,2),(1,2,0),(2,0,1),(0,2,1),(2,1,0),(1,0,2)]*2;sequence=[modes[i]for order in permutations for i in (*order,*reversed(order))];assert len(sequence)==72"+s[z:]
s=re.sub(r"modes=\['frozen', 'mapped'\];sequence=.*?;rows=\[\]",'rows=[]',s)
s=s.replace('assert len(rows)==48','assert len(rows)==72').replace('Fixed48','Fixed72').replace('twelveABBA/BAABblocks','twelvesymmetricABC/CBAblocks')
# Per-arm fields identify the actual runtime recipe.
s=s.replace('row=dict(index=index,','row=dict(effective_legacy_overrides={k:trial.get(k)for k in [\'GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM\',\'GGML_VK_PREFER_HOST_MEMORY\',\'GGML_VK_ALLOW_GRAPHICS_QUEUE\',\'GGML_VK_SUBALLOCATION_BLOCK_SIZE\']},index=index,')
a=s.index('import math\nblocks=[]');s=s[:a]+'''import math
critical={4:3.182446305284263,5:2.776445105197799,6:2.570581835636305,7:2.44691185114497,8:2.3646242515927844,9:2.306004135204166,10:2.2621571628540993,11:2.2281388519649385,12:2.200985160082949}
def estimate(values):
 n=len(values)
 if n<4:return dict(blocks=n,qualified=False,reason='Fewer than4matched blocks')
 mu=statistics.mean(values);half=critical[n]*statistics.stdev(values)/math.sqrt(n)
 return dict(blocks=n,geometric_speed_change_percent=100*math.expm1(mu),descriptive_t95_percent=[100*math.expm1(mu-half),100*math.expm1(mu+half)],lower_bound_positive=mu-half>0)
contrasts={}
for name,baseline,candidate in [('combined','stock100','q3_400'),('submission','stock100','stock400'),('padding','stock400','q3_400')]:
 blocks=[]
 for start in range(0,len(rows),6):
  aa=rows[start:start+6];by={m:[r for r in aa if r['mode']==m]for m in [baseline,candidate]};assert all(len(v)==2 for v in by.values())
  means=lambda key:{m:statistics.mean(r[key]for r in v)for m,v in by.items()}
  cpu=means('phase_cpu_busy_mean');builds=means('phase_build_process_mean');runqueue=means('phase_runnable_mean');clocks=means('steady_clock_median_mhz')
  comparable=all(r['under_load_measurement_valid']for v in by.values()for r in v)and max(cpu.values())-min(cpu.values())<=.05 and max(builds.values())-min(builds.values())<=2 and max(runqueue.values())-min(runqueue.values())<=max(4,.15*statistics.mean(runqueue.values()))
  effect=statistics.mean(math.log(r['steady_tokens_per_second'])for r in by[candidate])-statistics.mean(math.log(r['steady_tokens_per_second'])for r in by[baseline])
  blocks.append(dict(block=start//6,indices=[r['index']for v in by.values()for r in v],cpu_mode_means=cpu,build_mode_means=builds,runnable_mode_means=runqueue,gpu_clock_mode_means=clocks,comparable=comparable,log_effect=effect,speed_change_percent=100*math.expm1(effect)))
 contrasts[name]=dict(baseline=baseline,candidate=candidate,blocks=blocks,all12block_descriptive=estimate([v['log_effect']for v in blocks]),matched=estimate([v['log_effect']for v in blocks if v['comparable']]))
report=dict(contrasts=contrasts,primary=contrasts['combined'],mean_steady_tps={m:statistics.mean(r['steady_tokens_per_second']for r in rows if r['mode']==m)for m in modes},all_tokens_and_counters_identical=True,scope='Fixed72fresh512token directnative-defaultattribution,12symmetric6armblocks. PrimaryQ3default400vsstock100,secondarycap/paddingdescriptivepair-specificmatchedsubsets. No legacyallocation/queue/suballocationoverrides;nodecapunsetforstock100. Samepinnedstack/MTP/driver,synchronizedtiming,naturalclocks/poweroutcomes. Noextensions/retries/pooling/quietgate. Notmega/equalclock/generaldeploymentproof.')
report['incremental_gain_supported']=report['primary']['matched'].get('lower_bound_positive',False)
(out/'confirmation-analysis.json').write_text(json.dumps(report,indent=2)+'\\n');print('NATIVE_DEFAULT_BASELINE_DISCOVERY',report,flush=True)
'''
s=s.replace('privatesamefrozenhostMappedVRAM','specifiednative-defaultconfiguration').replace('nativeMappedVRAM','native-defaultconfigs')
s=s.replace('assets=[',"stock_manifest=json.loads((stock/'manifest.json').read_text());stock_libraries=[stock/'bin'/r['name']for r in stock_manifest['files']if r['name'].startswith('lib')]\nfor r in stock_manifest['files']:\n if r['name'].startswith('lib'):assert hashlib.sha256((stock/'bin'/r['name']).read_bytes()).hexdigest()==r['sha256']\nassets=[*stock_libraries,",1)
s=s.replace('Fixed72frozen-versus-native-defaultconfigs512token underload A/B. Preservedqualifiedhost/cap400 versusspecifiednative-defaultconfiguration,samefrozenpaddedQ3shaders/cap400;noadditionalshaders.', 'Fixed72native-defaultattribution512token underload comparison. Unmodifiedstock100/stock400/frozenQ3cap400,nativeallocation/queue/suballocationdefaults;specifiedGPU/shaderpaths,pinnedstockcore.')
(b/'run_native_default_timing.py').write_text(s);f=b/'run_private_guarded_batch.py';f.write_text(f.read_text().replace('allowed={',"allowed={'run_native_default_timing.py',",1))
