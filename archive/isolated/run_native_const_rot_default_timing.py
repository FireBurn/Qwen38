from pathlib import Path
import os,json,time,subprocess,signal,re,hashlib,threading,statistics
base=Path(__file__).resolve().parent
from native_observer_common import competition
project=base/'native-constant-rotation-default';stock=base/'production-baseline-aa8';core=stock
modes=['stock100','private_off','cache'];orders=[tuple((i+j)%3 for j in range(3)) for i in range(3)];sequence=[modes[i] for block in range(12) for i in (*orders[block%3],*reversed(orders[block%3]))];assert len(sequence)==72
quant=base/'native-quant-shuffle';q3=base/'q3-native-correction'
env={k:v for k,v in os.environ.items()if not k.startswith(('GGML_','ACO_','RADV_','LLAMA_HEAD_BOUND_'))and k not in ['LLAMA_MTP_DRAFT_NVOCAB','MTP_LOGITS_AUDIT_OUT','PRODUCTION_TARGET_AUDIT_OUT']}
env.update(GGML_VK_VISIBLE_DEVICES='1')
from quiet_builds import build_processes
def cpu_stat():
 v=[int(x)for x in Path('/proc/stat').read_text().splitlines()[0].split()[1:9]];return sum(v),v[3]+v[4]
print('Authorized under-load A/B: CPU/build load recorded, no quiet wait; original quiet queues unchanged',flush=True)
qualification=json.loads((project/'qualification-summary.json').read_text());assert qualification['private_modes_raw_target_rows']==530 and qualification['six_repeated_clear_generations']
out=project/'model-timing512'/time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());out.mkdir(parents=True)
driver=base/'mtp-sched-keep-7k/driver';env.update(VK_DRIVER_FILES=str(driver/'icd.json'),VK_ICD_FILENAMES=str(driver/'icd.json'),EXPECTED_RADV_LIBRARY_PATH=str(driver/'libvulkan_radeon.so'))
env['radv_buffer_meta_path']='2'
manifest=json.loads((driver/'manifest.json').read_text());assert all(hashlib.sha256((driver/name).read_bytes()).hexdigest()==r['sha256']for name,r in manifest['libraries'].items())
native_reference=base/'native-default-baseline/model-timing512/20261030T061854Z/results.json'
fm={'expected_token_prefix':json.loads(native_reference.read_text())[0]['tokens']}
stock_manifest=json.loads((stock/'manifest.json').read_text());stock_libraries=[stock/'bin'/r['name']for r in stock_manifest['files']if r['name'].startswith('lib')]
for r in stock_manifest['files']:
 if r['name'].startswith('lib'):assert hashlib.sha256((stock/'bin'/r['name']).read_bytes()).hexdigest()==r['sha256']
cache_core=base/'native-constant-rotation/bin/libllama.so.0.7.0';assert hashlib.sha256(cache_core.read_bytes()).hexdigest()==json.loads((base/'native-constant-rotation/build.json').read_text())['library_sha256']
assets=[*stock_libraries,cache_core,Path(__file__),project/'MODEL-TIMING-PLAN.md',project/'qualification-summary.json',base/'native-fusion-plan/sync-build.json',base/'native-fusion-plan/sync-runner.cpp',base/'native-fusion-plan/sync-bin/model-bench',native_reference,driver/'libvulkan_radeon.so']
(out/'protocol.json').write_text(json.dumps(dict(plan=(project/'MODEL-TIMING-PLAN.md').read_text(),sequence=sequence,primary='cache versus private_off'),indent=2)+'\n')
assert hashlib.sha256((base/'native-fusion-plan/sync-bin/model-bench').read_bytes()).hexdigest()==json.loads((base/'native-fusion-plan/sync-build.json').read_text())['binary_sha256']
(out/'assets.json').write_text(json.dumps({str(x):hashlib.sha256(x.read_bytes()).hexdigest()for x in assets},indent=2)+'\n')
model='${CLAUDE_WORKSPACE}/eval/models/nerkyor/GGUF/Qwen3.8-27B-Coder390-EfficientThink-Q3LynnStyle-MTP.gguf'
prompt='The history of the Roman Empire begins with the rise of Augustus. After the death of Julius Caesar, a power struggle erupted among his heirs and generals. In this essay we will examine'
pci=Path('/sys/bus/pci/devices/0000:07:00.0');freq=next((pci/'hwmon').glob('hwmon*/freq1_input'))
from quiet_builds import build_processes
def build_count():return len(build_processes())
rows=[]
runtime_lib=Path('/usr/lib64/libc.so.1').resolve();runtime_inode=runtime_lib.stat().st_ino
(out/'runtime-baseline.json').write_text(json.dumps({'path':str(runtime_lib),'inode':runtime_inode,'sha256':hashlib.sha256(runtime_lib.read_bytes()).hexdigest()},indent=2)+chr(10))
for index,mode in enumerate(sequence):
 assert runtime_lib.stat().st_ino==runtime_inode,'Runtime replaced during test'
 assert not competition(),competition();trial=env.copy();bounded=False
 for key in ['GGML_VK_TAPE','GGML_VK_PIPELINE_STATS','MTP_LOGITS_AUDIT_OUT','LLAMA_HEAD_BOUND_CACHE','ACO_DEBUG','RADV_DEBUG','MESA_SHADER_CACHE_DISABLE','GGML_VK_NATIVE_GLUQ_FUSE','GGML_VK_NATIVE_GLUQ_EXPAND_VIEWS','GGML_VK_NATIVE_GLUQ_AUDIT','GGML_VK_SYNC_LOGGER','GGML_VK_NATIVE_GLUQ_CHECK_PLAN','GGML_VK_NATIVE_GLUQ_COALESCE','GGML_VK_NATIVE_GLUQ_SUBGROUP32']:trial.pop(key,None)
 for key in list(trial):
  if key.startswith('GGML_VK_NATIVE_'):trial.pop(key)
 selected_host=stock
 trial.update(LD_LIBRARY_PATH=str(selected_host/'bin')+':'+str(stock/'bin')+':'+str(base/'mtp-head-bound-audit/driver-deps')+':'+str(driver),EXPECTED_VK_BACKEND_PATH=str(selected_host/'bin/libggml-vulkan.so.0.27.0'),EXPECTED_LLAMA_CORE_PATH=str(stock/'bin/libllama.so.0.7.0'),EXPECTED_LLAMA_COMMON_PATH=str(stock/'bin/libllama-common.so.0.7.0'),MESA_SHADER_CACHE_DIR=str(base/'q3-pad112/model-timing-cache-pad'),radv_enable_transfer_queue='false')
 [trial.pop(k,None)for k in ['GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM','GGML_VK_PREFER_HOST_MEMORY','GGML_VK_ALLOW_GRAPHICS_QUEUE','GGML_VK_SUBALLOCATION_BLOCK_SIZE']]
 trial.pop('GGML_VK_MAX_NODES_PER_SUBMIT',None);assert all(trial.get(k)is None for k in ['GGML_VK_MAX_NODES_PER_SUBMIT','GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM','GGML_VK_PREFER_HOST_MEMORY','GGML_VK_ALLOW_GRAPHICS_QUEUE','GGML_VK_SUBALLOCATION_BLOCK_SIZE'])
 trial.pop('LLAMA_VK_CONST_ROT_AUDIT',None);trial['LLAMA_VK_CONST_ROT']='1' if mode=='cache' else '0'
 if mode!='stock100':trial.update(LD_LIBRARY_PATH=str(cache_core.parent)+':'+trial['LD_LIBRARY_PATH'],EXPECTED_LLAMA_CORE_PATH=str(cache_core))
 before_driver=set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines())
 label=f'{index:02d}-{mode}';log=out/(label+'.log');samples=[];runtime=[];child=None;stop=threading.Event();telemetry_errors=[];monitor_fatal=[]
 def sample():
  tick=0;builds=0;previous=None
  while not stop.is_set():
   text=""
   try:
    if tick%10==0:builds=build_count()
    v=[int(x)for x in Path('/proc/stat').read_text().splitlines()[0].split()[1:9]];total=sum(v);idle=v[3]+v[4];busy=None if previous is None else 1-(idle-previous[1])/max(1,total-previous[0]);previous=(total,idle)
    text=log.read_text()if log.exists()else''
    if child is not None and not runtime and 'FULL_MODEL_WARM 'in text:
     maps=(Path('/proc')/str(child.pid)/'maps').read_text().splitlines()
     mapped=[{'inode':int(v.split(None,5)[4]),'path':v.split(None,5)[5]}for v in maps if len(v.split(None,5))==6 and v.split(None,5)[5].removesuffix(' (deleted)').endswith('/libc.so.1')]
     if mapped:runtime.extend(mapped)
    samples.append(dict(runnable_threads=int(Path('/proc/loadavg').read_text().split()[3].split('/')[0]),monotonic_ns=time.monotonic_ns(),clock_mhz=int(freq.read_text())/1e6,power_w=int(next((pci/'hwmon').glob('hwmon*/power1_average')).read_text())/1e6,gpu_busy=int((pci/'gpu_busy_percent').read_text()),cpu_busy=busy,background_build_processes=builds,vram_bytes=int((pci/'mem_info_vram_used').read_text()),process_rss_bytes=int((Path('/proc')/str(child.pid)/'statm').read_text().split()[1])*os.sysconf('SC_PAGE_SIZE')if child is not None else None,generation_seen='ACCEPTED_TOKEN 'in text,steady_seen='FULL_MODEL_WARM 'in text and'FULL_MODEL_TIMING 'not in text));tick+=1
   except OSError as exc:telemetry_errors.append(dict(errno=exc.errno,message=str(exc),steady_seen='FULL_MODEL_WARM 'in text and 'FULL_MODEL_TIMING 'not in text))
   except Exception as exc:monitor_fatal.append(repr(exc));return
   stop.wait(.1)
 cmd=[str(base/'native-fusion-plan/sync-bin/model-bench'),'-m',model,'--spec-type','draft-mtp','--spec-draft-n-max','1','--spec-draft-n-min','1','--spec-draft-p-min','0','--no-spec-draft-backend-sampling'if mode=='native_cpu'else'--spec-draft-backend-sampling','--spec-draft-ngl','99','-ngl','99','-c','4096','-b','512','-ub','512','-fa','on','-ctk','q8_0','-ctv','q8_0','-ctkd','q8_0','-ctvd','q8_0','-t','1','-tb','1','-td','1','-tbd','1','--temp','0','--seed','1','-n','512','-p',prompt]
 worker=threading.Thread(target=sample);worker.start();started=time.monotonic()
 try:
  with log.open('w')as f:
   child=subprocess.Popen(cmd,env=trial,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
   try:
    while child.poll()is None:
     if monitor_fatal or competition(child.pid)or time.monotonic()-started>600:raise RuntimeError('Competition or timeout')
     time.sleep(.25)
   finally:
    if child.poll()is None:os.killpg(child.pid,signal.SIGTERM);child.wait(timeout=10)
  assert child.returncode==0,(label,child.returncode,log)
 finally:stop.set();worker.join()
 (out/(label+'-telemetry.json')).write_text(json.dumps({'samples':samples,'sensor_errors':telemetry_errors,'monitor_fatal':monitor_fatal},indent=2)+'\n');text=log.read_text();assert 'BACKEND_PATH_OK '+trial['EXPECTED_VK_BACKEND_PATH']in text and 'DRIVER_PATH_OK '+trial['EXPECTED_RADV_LIBRARY_PATH']in text
 new_driver_errors=[l for l in subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines()if l not in before_driver and '0000:07:00.0'in l and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',l,re.I)]
 assert not new_driver_errors,new_driver_errors
 if bounded:assert 'HEAD_BOUND_CACHE_READY'in text and 'HEAD_BOUND_FALLBACK'not in text
 if mode=='cache':assert 'LLAMA_CONST_ROT_FALLBACK' not in text,'Cache fallback'
 assert 'NATIVE_SUBMIT_BUDGET 'not in text,'Pergraph audit enabled during timing'
 encode_match=re.search(r'encoded\s+(\d+) tokens in\s+([0-9.]+) seconds',text)
 match=re.search(r'FULL_MODEL_TIMING warm_tokens=(\d+) cold_generation_us=(\d+) steady_tokens=(\d+) steady_us=(\d+) total_generation_us=(\d+)',text);assert match,label
 warm,cold,steady,us,total=map(int,match.groups());tokens=[int(x)for x in re.findall(r'ACCEPTED_TOKEN (\d+)',text)];assert len(tokens)>=512
 fields={k:int(re.findall(r'\b'+k+r'\s*=\s*(\d+)',text)[-1])for k in ['n_drafted','n_accept','n_predict']};active=[x for x in samples if x['steady_seen']and x['gpu_busy']>=50]
 row=dict(rotation_cache_requested=mode=='cache',effective_legacy_overrides={k:trial.get(k)for k in ['GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM','GGML_VK_PREFER_HOST_MEMORY','GGML_VK_ALLOW_GRAPHICS_QUEUE','GGML_VK_SUBALLOCATION_BLOCK_SIZE']},index=index,mode=mode,encode_seconds=float(encode_match[2])if encode_match else None,tokens=tokens,**fields,warm_tokens=warm,steady_tokens=steady,steady_tokens_per_second=steady*1e6/us,steady_seconds=us/1e6,cold_first_window_seconds=cold/1e6,total_generation_seconds=total/1e6,total_generation_tokens_per_second=fields['n_predict']*1e6/total,process_wall_seconds=time.monotonic()-started,steady_clock_median_mhz=statistics.median(x['clock_mhz']for x in active)if active else None,steady_cpu_busy_mean=statistics.mean(x['cpu_busy']for x in active if x['cpu_busy']is not None)if any(x['cpu_busy']is not None for x in active)else None,steady_background_build_process_range=[min(x['background_build_processes']for x in active),max(x['background_build_processes']for x in active)]if active else None,scope='Native default stock, private off and rotation cache; fixed72 matched-load discovery. Natural clocks and power; no independent confirmation.')
 assert tokens==fm['expected_token_prefix'][:len(tokens)] and len(tokens)==513,'Qualified token reference differs'
 if rows:assert row['tokens']==rows[0]['tokens']and all(row[k]==rows[0][k]for k in ['n_drafted','n_accept','n_predict','warm_tokens','steady_tokens']),'Model behavior differs'
 phase=[x for x in samples if x['steady_seen']];clocks=sorted(x['clock_mhz']for x in active);p10=clocks[len(clocks)//10]if clocks else None;p90=clocks[min(len(clocks)-1,9*len(clocks)//10)]if clocks else None;settled=len(clocks)>=8 and p90/p10<=1.15 and statistics.mean(x['clock_mhz']for x in active[:max(1,len(active)//3)])/statistics.mean(x['clock_mhz']for x in active[-max(1,len(active)//3):])>=.90
 row['phase_power_w_mean']=statistics.mean(x['power_w']for x in phase)
 row['phase_vram_bytes_mean']=statistics.mean(x['vram_bytes']for x in phase)
 row['clock_p10_mhz']=p10;row['clock_p90_mhz']=p90;row['clock_settled']=settled;row['phase_build_process_max']=max((x['background_build_processes']for x in phase),default=-1)
 row['steady_sensor_errors']=[e for e in telemetry_errors if e['steady_seen']];row['monitor_fatal']=monitor_fatal
 row['quiet_environment_valid']=not monitor_fatal and not row['steady_sensor_errors']and bool(phase)and all(x['background_build_processes']==0 for x in phase)and statistics.mean(x['cpu_busy']for x in phase if x['cpu_busy']is not None)<.35 and settled
 row['under_load_measurement_valid']=not monitor_fatal and not row['steady_sensor_errors']and len(clocks)>=8 and bool(phase)
 row['new_driver_errors']=new_driver_errors
 row['phase_runnable_mean']=statistics.mean(x['runnable_threads']for x in phase)
 row['libc_mappings']=runtime
 row['phase_cpu_busy_mean']=statistics.mean(x['cpu_busy']for x in phase if x['cpu_busy']is not None)
 row['phase_build_process_mean']=statistics.mean(x['background_build_processes']for x in phase)
 assert runtime and all(v['inode']==runtime_inode for v in runtime),'Mapped libc changed or not observed'
 rows.append(row);(out/'results.json').write_text(json.dumps(rows,indent=2)+'\n');print({k:v for k,v in row.items()if k!='tokens'},flush=True)
 assert row['under_load_measurement_valid'],'Missing/failed timed telemetry; stop rather than claim a result'

assert len(rows)==72
import math
critical={4:3.182446305284263,5:2.776445105197799,6:2.570581835636305,7:2.44691185114497,8:2.3646242515927844,9:2.306004135204166,10:2.2621571628540993,11:2.2281388519649385,12:2.200985160082949}
def estimate(values):
 n=len(values)
 if n<4:return dict(blocks=n,qualified=False,reason='Fewer than4matched blocks')
 mu=statistics.mean(values);half=critical[n]*statistics.stdev(values)/math.sqrt(n)
 return dict(blocks=n,geometric_speed_change_percent=100*math.expm1(mu),descriptive_t95_percent=[100*math.expm1(mu-half),100*math.expm1(mu+half)],lower_bound_positive=mu-half>0)
contrasts={}
for name,baseline,candidate in [('cache_effect','private_off','cache'),('cache_vs_stock','stock100','cache'),('private_control','stock100','private_off')]:
 blocks=[]
 for start in range(0,len(rows),6):
  aa=rows[start:start+6];by={m:[r for r in aa if r['mode']==m] for m in [baseline,candidate]};assert all(len(v)==2 for v in by.values())
  means=lambda k:{m:statistics.mean(r[k] for r in v) for m,v in by.items()}
  cpu=means('phase_cpu_busy_mean');build=means('phase_build_process_mean');rq=means('phase_runnable_mean')
  valid=all(r['under_load_measurement_valid'] for v in by.values() for r in v) and max(cpu.values())-min(cpu.values())<=.05 and max(build.values())-min(build.values())<=2 and max(rq.values())-min(rq.values())<=max(4,.15*statistics.mean(rq.values()))
  effect=statistics.mean(math.log(r['steady_tokens_per_second']) for r in by[candidate])-statistics.mean(math.log(r['steady_tokens_per_second']) for r in by[baseline])
  blocks.append(dict(block=start//6,indices=[r['index'] for v in by.values() for r in v],comparable=valid,log_effect=effect,cpu=cpu,build=build,runnable=rq))
 contrasts[name]=dict(baseline=baseline,candidate=candidate,blocks=blocks,all12=estimate([x['log_effect'] for x in blocks]),matched=estimate([x['log_effect'] for x in blocks if x['comparable']]))
report=dict(contrasts=contrasts,primary=contrasts['cache_effect'],confirmation_eligible=contrasts['cache_effect']['matched'].get('lower_bound_positive',False),scope='Native default cache discovery only; no independent confirmation, no equal-clock claim.')
(out/'confirmation-analysis.json').write_text(json.dumps(report,indent=2)+'\n')
