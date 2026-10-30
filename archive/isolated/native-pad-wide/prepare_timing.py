from pathlib import Path
import ast,hashlib,json
p=Path(__file__).resolve().parent;b=p.parent;parent=b/'run_native_argmax_wide_timing.py';s=parent.read_text().replace("project=base/'native-argmax-review'","project=base/'native-pad-wide'")
a=s.index("modes=['stock100'");z=s.index('\nquant=',a)
s=s[:a]+"modes=['stock100','private_off','pad','wide','both'];cyclic=[tuple((i+j)%5 for j in range(5))for i in range(5)];permutations=cyclic+[tuple(reversed(o))for o in cyclic];sequence=[modes[i]for order in permutations for i in (*order,*reversed(order))];assert len(sequence)==100"+s[z:]
s=s.replace('wide-model-qualification.json','qualification-summary.json').replace('wide-model32','model32').replace('wide-prompts128','prompts128').replace('wide-populated-kv64','populated-kv64').replace('wide-boundary128','boundary128')
s=s.replace("project/'wide-build.json',project/'wide-host/bin/libggml-vulkan.so.0.27.0',project/'argmax-wide.spv'","project/'build.json',project/'host/bin/libggml-vulkan.so.0.27.0',base/'native-argmax-review/argmax-wide.spv',base/'q3-pad112/qualified-20261029/manifest.json',base/'q3-pad112/qualified-20261029/shaders/pad16_subgroup_no_shmem.spv',base/'q3-pad112/qualified-20261029/shaders/repack.spv'")
needle='assets=[*stock_libraries';s=s.replace(needle,"frozen=base/'q3-pad112/qualified-20261029';frozen_manifest=json.loads((frozen/'manifest.json').read_text());assert all(hashlib.sha256((frozen/name).read_bytes()).hexdigest()==value for name,value in frozen_manifest['files'].items())\ncombined_build=json.loads((project/'build.json').read_text());assert hashlib.sha256((project/'host/bin/libggml-vulkan.so.0.27.0').read_bytes()).hexdigest()==combined_build['library_sha256'];assert hashlib.sha256((base/'native-argmax-review/argmax-wide.spv').read_bytes()).hexdigest()==combined_build['shader_sha256']\n"+needle)
s=s.replace("selected_host=stock if mode=='stock100'else project/'wide-host'","selected_host=stock if mode=='stock100'else project/'host'")
s=s.replace("if mode=='private_wide':trial['GGML_VK_ARGMAX_WIDE_SHADER']=str(project/'argmax-wide.spv')","if mode in ['pad','both']:trial.update(GGML_VK_Q3_PAD112_ARENA='1',GGML_VK_Q3_PAD112_DIR=str(frozen/'shaders'),GGML_VK_Q3_PAD112_IMMUTABLE='1')\n if mode in ['wide','both']:trial['GGML_VK_ARGMAX_WIDE_SHADER']=str(base/'native-argmax-review/argmax-wide.spv')")
s=s.replace("if mode!='stock100':cmd+=","if mode in ['wide','both']:cmd+=")
s=s.replace("wide_argmax_requested=mode=='private_wide'","wide_argmax_requested=mode in ['wide','both'],q3_padding_requested=mode in ['pad','both']")
s=s.replace("primary='private_wide versus stock100',secondary=['private_off versus stock100','private_wide versus private_off']","primary='both versus stock100',secondary=['both versus wide','both versus pad','private_off versus stock100','pad versus private_off','wide versus private_off']")
s=s.replace('Fixed72wide-argmax','Fixed100pad-wide-factorial').replace('StockCPU/privatebackendnative/privatebackendwideargmax,native100allmodes','Stock/privateoff/pad/wide/both,native100allmodes')
s=s.replace("if mode in ['pad','both']:trial.update(GGML_VK_Q3_PAD112_ARENA='1',GGML_VK_Q3_PAD112_DIR=str(frozen/'shaders'),GGML_VK_Q3_PAD112_IMMUTABLE='1')", "if mode in ['pad','both']:trial.update(GGML_VK_Q3_PAD112_ARENA='1',GGML_VK_Q3_PAD112_DIR=str(frozen/'shaders'),GGML_VK_Q3_PAD112_IMMUTABLE='1',GGML_VK_Q3_PAD112_AUDIT='1')")
marker=" assert 'NATIVE_SUBMIT_BUDGET 'not in text"
assert marker in s
s=s.replace(marker," if mode in ['pad','both']:\n  finals=[tuple(map(int,x))for x in re.findall(r'Q3_PAD112_FINAL entries=(\\d+) bytes=(\\d+) calls=(\\d+)',text)];assert any(entries==78 and size==3041525760 and calls>0 for entries,size,calls in finals)and 'Q3_PAD112_BUDGET_FALLBACK'not in text,('Q3arena inactive or budgetfallback',mode,finals)\n if mode in ['wide','both']:assert 'ARGMAX_WIDE_MODULE words='in text,'Wide module not loaded'\n"+marker)
a=s.index('assert len(rows)==72');prefix=s[:a]
tail=r'''assert len(rows)==100
import math
critical={4:3.182446305284263,5:2.776445105197799,6:2.570581835636305,7:2.44691185114497,8:2.3646242515927844,9:2.306004135204166,10:2.2621571628540993}
def estimate(values):
 n=len(values)
 if n<4:return dict(blocks=n,qualified=False,reason='Fewer than4matched blocks')
 mu=statistics.mean(values);half=critical[n]*statistics.stdev(values)/math.sqrt(n)
 return dict(blocks=n,geometric_speed_change_percent=100*math.expm1(mu),descriptive_t95_percent=[100*math.expm1(mu-half),100*math.expm1(mu+half)],lower_bound_positive=mu-half>0)
contrasts={}
for name,baseline,candidate in [('combined','stock100','both'),('incremental_pad','wide','both'),('incremental_wide','pad','both'),('private_control','stock100','private_off'),('pad_component','private_off','pad'),('wide_component','private_off','wide')]:
 blocks=[]
 for start in range(0,len(rows),10):
  aa=rows[start:start+10];by={m:[r for r in aa if r['mode']==m]for m in [baseline,candidate]};assert all(len(v)==2 for v in by.values())
  means=lambda key:{m:statistics.mean(r[key]for r in v)for m,v in by.items()}
  cpu=means('phase_cpu_busy_mean');builds=means('phase_build_process_mean');rq=means('phase_runnable_mean');clocks=means('steady_clock_median_mhz')
  comparable=all(r['under_load_measurement_valid']for v in by.values()for r in v)and max(cpu.values())-min(cpu.values())<=.05 and max(builds.values())-min(builds.values())<=2 and max(rq.values())-min(rq.values())<=max(4,.15*statistics.mean(rq.values()))
  effect=statistics.mean(math.log(r['steady_tokens_per_second'])for r in by[candidate])-statistics.mean(math.log(r['steady_tokens_per_second'])for r in by[baseline])
  blocks.append(dict(block=start//10,indices=[r['index']for v in by.values()for r in v],cpu_mode_means=cpu,build_mode_means=builds,runnable_mode_means=rq,gpu_clock_mode_means=clocks,comparable=comparable,log_effect=effect,speed_change_percent=100*math.expm1(effect)))
 contrasts[name]=dict(baseline=baseline,candidate=candidate,blocks=blocks,all10block_descriptive=estimate([v['log_effect']for v in blocks]),matched=estimate([v['log_effect']for v in blocks if v['comparable']]))
interaction=[]
for start in range(0,len(rows),10):
 aa=rows[start:start+10];by={m:[r for r in aa if r['mode']==m]for m in ['private_off','pad','wide','both']};assert all(len(v)==2 for v in by.values())
 means=lambda key:{m:statistics.mean(r[key]for r in v)for m,v in by.items()}
 cpu=means('phase_cpu_busy_mean');builds=means('phase_build_process_mean');rq=means('phase_runnable_mean');effect=sum(sign*statistics.mean(math.log(r['steady_tokens_per_second'])for r in by[m])for m,sign in [('both',1),('private_off',1),('pad',-1),('wide',-1)])
 comparable=all(r['under_load_measurement_valid']for v in by.values()for r in v)and max(cpu.values())-min(cpu.values())<=.05 and max(builds.values())-min(builds.values())<=2 and max(rq.values())-min(rq.values())<=max(4,.15*statistics.mean(rq.values()))
 interaction.append(dict(block=start//10,indices=[r['index']for v in by.values()for r in v],cpu_mode_means=cpu,build_mode_means=builds,runnable_mode_means=rq,comparable=comparable,log_effect=effect,interaction_percent=100*math.expm1(effect)))
report=dict(contrasts=contrasts,primary=contrasts['combined'],interaction=dict(blocks=interaction,all10_descriptive=estimate([v['log_effect']for v in interaction]),matched=estimate([v['log_effect']for v in interaction if v['comparable']])),mean_steady_tps={m:statistics.mean(r['steady_tokens_per_second']for r in rows if r['mode']==m)for m in modes},all_tokens_and_counters_identical=True,scope='Fixed100fresh512token five-mode private2x2+stock factorial,10symmetric10armblocks,primarybothvsstock,predeclaredincremental gates;pair-specific externalmatching and four-mode interactionmatching. Naturalclocks/power; no retry/extension/pooling/quietgate, no mega/equalclock/generaldeployment claim.')
report['confirmation_eligible']=all(contrasts[n]['matched'].get('lower_bound_positive',False)for n in ['combined','incremental_pad','incremental_wide'])
(out/'confirmation-analysis.json').write_text(json.dumps(report,indent=2)+'\n');print('PAD_WIDE_FACTORIAL_DISCOVERY',report,flush=True)
'''
s=(prefix+tail).replace("+'"+chr(92)*2+"n'","+chr(10)");ast.parse(s);(b/'run_native_pad_wide_timing.py').write_text(s)
# The independent two-arm confirmation is gated by all three discovery contrasts.
c=prefix;a=c.index("modes=['stock100'");z=c.index('\nquant=',a);c=c[:a]+"modes=['stock100','both'];sequence=[mode for block in range(12)for mode in (['stock100','both','both','stock100']if block%2==0 else ['both','stock100','stock100','both'])];assert len(sequence)==48"+c[z:]
c=c.replace("out=project/'model-timing512'","discovery=sorted((project/'model-timing512').glob('*/confirmation-analysis.json'));assert len(discovery)==1 and json.loads(discovery[0].read_text())['confirmation_eligible']\nout=project/'model-confirmation512'",1).replace("assert set(v['mode']for v in rr)==set(modes)","assert set(v['mode']for v in rr)=={'stock100','private_off','pad','wide','both'}")
ct=tail.replace('assert len(rows)==100','assert len(rows)==48').replace('10:2.2621571628540993}', '10:2.2621571628540993,11:2.2281388519649385,12:2.200985160082949}').replace("[('combined','stock100','both'),('incremental_pad','wide','both'),('incremental_wide','pad','both'),('private_control','stock100','private_off'),('pad_component','private_off','pad'),('wide_component','private_off','wide')]","[('combined','stock100','both')]").replace('range(0,len(rows),10)','range(0,len(rows),4)').replace('rows[start:start+10]','rows[start:start+4]').replace('block=start//10','block=start//4').replace('all10block_descriptive','all12block_descriptive')
a=ct.index('interaction=[]');ct=ct[:a]+'''report=dict(contrasts=contrasts,primary=contrasts['combined'],mean_steady_tps={m:statistics.mean(r['steady_tokens_per_second']for r in rows if r['mode']==m)for m in modes},all_tokens_and_counters_identical=True,scope='Independent fixed48stock versusboth,12ABBA/BAABblocks, same settings/loadmatching. No pooling/retry/extension/quietgate; notmega/equalclock/generaldeploymentproof.')
report['incremental_gain_supported']=report['primary']['matched'].get('lower_bound_positive',False)
(out/'confirmation-analysis.json').write_text(json.dumps(report,indent=2)+'\\n');print('PAD_WIDE_CONFIRMATION',report,flush=True)
'''
c=(c+ct).replace("+'"+chr(92)*2+"n'","+chr(10)");c=c.replace("secondary=['both versus wide','both versus pad','private_off versus stock100','pad versus private_off','wide versus private_off']","secondary=[]");ast.parse(c);(b/'run_native_pad_wide_confirm.py').write_text(c)
f=b/'run_private_guarded_batch.py';v=f.read_text();names=['run_native_pad_wide_timing.py','run_native_pad_wide_confirm.py'];missing=[repr(n)for n in names if repr(n)not in v]
if missing:v=v.replace('allowed={','allowed={'+','.join(missing)+',',1)
f.write_text(v)
ns={};exec(next(line for line in s.splitlines()if line.startswith('modes=')),{},ns);assert len(ns['sequence'])==100 and all(ns['sequence'].count(m)==20 for m in ns['modes'])
(p/'timing-preflight.json').write_text(json.dumps(dict(script_sha256=hashlib.sha256((b/'run_native_pad_wide_timing.py').read_bytes()).hexdigest(),sequence=ns['sequence'],scope='Static recipe/schedule only, no throughput data.'),indent=2)+'\n');print('Prepared fixed100 factorial and gated independent48 recipes')
