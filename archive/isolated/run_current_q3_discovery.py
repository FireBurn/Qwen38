from pathlib import Path
import hashlib,json,math,os,re,signal,socket,statistics,subprocess,sys,threading,time,urllib.request
from native_observer_common import competition
from quiet_builds import build_processes
base=Path(__file__).resolve().parent;q=base/'current-server-scope';hub=Path('${HF_CACHE}');server=Path('/usr/bin/llama-server');sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
repos={'target':'models--nerkyor--Qwen3.8-27B-Coder390-EfficientThink-Opus5.5-GPT6Astra-Grok4.7-DSV4Pro-K3-SFT-RLOO-MTP-DFlash2','draft':'models--incoai--Qwen3.8-27B-DFlash2-GGUF'};names={'target':'GGUF/Qwen3.8-27B-Coder390-EfficientThink-Q3LynnStyle-MTP.gguf','draft':'Qwen3.8-27B-DFlash2-Q4_K_M.gguf'}
models={}
for key,repo in repos.items():
 d=hub/repo;revision=(d/'refs/main').read_text().strip();f=(d/'snapshots'/revision/names[key]).resolve(strict=True);st=f.stat();models[key]={'path':str(f),'revision':revision,'bytes':st.st_size,'inode':st.st_ino,'device':st.st_dev,'mtime_ns':st.st_mtime_ns}
shared_paths=[(q/'dflash-selector-anchor/baseline/libllama.so.0').resolve(),(q/'installed-build/bin/libggml-base.so.0').resolve(),(q/'installed-build/bin/libggml-cpu.so.0').resolve(),(q/'installed-build/bin/libggml.so.0').resolve(),(q/'installed-build/bin/libllama-common.so.0').resolve(),Path('/usr/lib64/llama.cpp/libllama-server-impl.so').resolve(),Path('/usr/lib64/libvulkan_radeon.so').resolve(),Path('/usr/lib64/libc.so.1').resolve()];arm_paths={n:(q/'q3-recenter'/n/'libggml-vulkan.so.0.28.0').resolve() for n in ('baseline','candidate')};library_paths=shared_paths+list(arm_paths.values())
lib_hashes={str(f):sha(f) for f in library_paths};lib_stats={str(f):(f.stat().st_dev,f.stat().st_ino,f.stat().st_size,f.stat().st_mtime_ns) for f in library_paths}
def same_libraries():
 for path,identity in lib_stats.items():
  st=Path(path).stat()
  if (st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns)!=identity:return False
 return True
ver=subprocess.run([str(server),'--version'],capture_output=True,text=True,check=True);version=(ver.stdout+ver.stderr).strip();server_hash=sha(server);prompt='Explain how memory bandwidth and cache locality affect a GPU matrix multiplication, with a concise example.'
sequence=[x for b in range(4) for x in (['baseline','candidate','candidate','baseline'] if b%2==0 else ['candidate','baseline','baseline','candidate'])];assert len(sequence)==16
if sys.argv[1:]==['--preflight']:
 print(json.dumps({'version':version,'sequence':sequence,'models':models,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'scope':'CPU-only; no GPU initialized.'},indent=2));sys.exit(0)
assert not sys.argv[1:] and not competition(),competition();out=q/'q3-recenter/discovery'/time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());out.mkdir(parents=True)
identity={'server_version':version,'server_sha256':server_hash,'library_sha256':lib_hashes,'models':models,'plan_sha256':sha(q/'q3-recenter/DISCOVERY-PLAN.md'),'runner_sha256':sha(Path(__file__)),'sequence':sequence,'prompt':prompt,'child_overrides':{'GGML_VK_VISIBLE_DEVICES':'1','radv_buffer_meta_path':'1','radv_enable_transfer_queue':'false'}};(out/'protocol.json').write_text(json.dumps(identity,indent=2)+'\n')
def kernel():return set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines())
def other_server(exclude=None):
 for p in Path('/proc').glob('[0-9]*'):
  try:
   if int(p.name)==exclude:continue
   args=(p/'cmdline').read_bytes().split(b'\0');name=Path(os.fsdecode(args[0])).name
   if name=='llama' and b'server' in args[1:]:return {'pid':int(p.name),'command':'llama server'}
  except (OSError,ValueError):continue
 return None
def same_models():
 for v in models.values():
  st=Path(v['path']).stat()
  if (st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns)!=(v['device'],v['inode'],v['bytes'],v['mtime_ns']):return False
 return True
pci=Path('/sys/bus/pci/devices/0000:07:00.0');rows=[]
for index,width in enumerate(sequence):
 assert sha(server)==server_hash and same_models() and same_libraries() and not competition() and not other_server()
 with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
 cmd=[str(server),'-m',models['target']['path'],'--device','Vulkan0','--n-gpu-layers','all','--ctx-size','327680','--rope-scaling','yarn','--rope-scale','1.25','--yarn-orig-ctx','262144','--no-mmproj','--parallel','1','--flash-attn','on','--cache-type-k','q8_0','--cache-type-v','q8_0','--batch-size','2048','--ubatch-size','1024','--spec-draft-model',models['draft']['path'],'--spec-draft-ngl','all','--spec-draft-device','Vulkan0','--spec-type','ngram-mod,draft-dflash','--spec-ngram-mod-n-max','63','--spec-ngram-mod-n-min','16','--spec-draft-n-max','4','--backend-sampling','--spec-draft-type-k','q8_0','--spec-draft-type-v','q8_0','--ctx-checkpoints','16','--jinja','--reasoning','on','--reasoning-effort','xhigh','--reasoning-preserve','--temp','0.6','--top-p','0.95','--top-k','20','--min-p','0','--repeat-penalty','1.0','--presence-penalty','0','--cache-reuse','256','--fit','off','--poll','0','--host','127.0.0.1','--port',str(port)]
 env={k:v for k,v in os.environ.items() if not k.startswith(('GGML_','ACO_','RADV_','MESA_','VK_','LLAMA_','radv_','LD_LIBRARY_PATH','DFLASH_','Q3_TARGET_'))};env.update(GGML_VK_VISIBLE_DEVICES='1',radv_buffer_meta_path='1',radv_enable_transfer_queue='false',LD_LIBRARY_PATH=str(q/'dflash-selector-anchor/baseline')+':'+str(arm_paths[width].parent)+':'+str(q/'installed-build/bin')+':/usr/lib64/llama.cpp')
 def http(path,payload=None,timeout=3):
  data=json.dumps(payload).encode() if payload is not None else None;req=urllib.request.Request(f'http://127.0.0.1:{port}'+path,data=data,headers={'Content-Type':'application/json'});return json.loads(urllib.request.urlopen(req,timeout=timeout).read())
 initial=kernel();faults=lambda:[x for x in kernel()-initial if '0000:07:00.0' in x and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',x,re.I)]
 phase='startup';stop=threading.Event();samples=[];errors=[];gpu_errors=[];proc=None
 def monitor():
  old=None;tick=0;builds=0
  while not stop.is_set():
   try:
    v=[int(x) for x in Path('/proc/stat').read_text().splitlines()[0].split()[1:9]];total=sum(v);idle=v[3]+v[4];busy=None if old is None else 1-(idle-old[1])/max(1,total-old[0]);old=(total,idle)
    if tick%5==0:
     builds=len(build_processes())
     if proc is not None and proc.poll() is None:
      bad=faults();other=competition(proc.pid) or other_server(proc.pid)
      if bad or other:errors.append(repr({'faults':bad,'competition':other}));os.killpg(proc.pid,signal.SIGTERM);return
    sample={'time_ns':time.monotonic_ns(),'phase':phase,'cpu_busy':busy,'builds':builds,'runnable':int(Path('/proc/loadavg').read_text().split()[3].split('/')[0]),'gpu_busy':None,'vram':None}
    try:sample.update(gpu_busy=int((pci/'gpu_busy_percent').read_text()),vram=int((pci/'mem_info_vram_used').read_text()))
    except OSError as e:gpu_errors.append({'phase':phase,'time_ns':time.monotonic_ns(),'error':repr(e)})
    samples.append(sample);tick+=1
   except Exception as e:errors.append(repr(e));return
   stop.wait(.2)
 thread=threading.Thread(target=monitor);thread.start();report={'index':index,'width':width,'passed':False};log=out/f'{index:02d}-n{width}.log';started=time.monotonic()
 try:
  with log.open('w') as f:
   proc=subprocess.Popen(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);print('DFLASH_CHILD',index,width,proc.pid,flush=True);deadline=time.monotonic()+600
   while time.monotonic()<deadline:
    assert proc.poll() is None and not errors and not faults(),(proc.returncode,errors,faults())
    try:
     if http('/health').get('status')=='ok':break
    except Exception:pass
    time.sleep(.5)
   else:raise TimeoutError('server readiness')
   maps=(Path('/proc')/str(proc.pid)/'maps').read_text().splitlines();mapped={str(Path(line.split(None,5)[5].removesuffix(' (deleted)')).resolve()) for line in maps if len(line.split(None,5))==6 and line.split(None,5)[5].startswith('/')};required=shared_paths+[arm_paths[width]];assert all(str(f) in mapped for f in required),{'missing_mappings':[str(f) for f in required if str(f) not in mapped]};assert str(arm_paths['candidate' if width=='baseline' else 'baseline']) not in mapped,'wrong arm also mapped'
   text=log.read_text();assert 'radv_buffer_meta_path overridden' in text and "adding speculative implementation 'draft-dflash'" in text and 'n_max=4,' in text
   def request(p,n):
    payload={'messages':[{'role':'user','content':p}],'max_tokens':n,'seed':1234,'temperature':0.6,'top_p':0.95,'top_k':20,'min_p':0.0,'cache_prompt':False,'ignore_eos':True,'stream':False};t=time.monotonic();a=http('/v1/chat/completions',payload,timeout=600);return {'elapsed_seconds':time.monotonic()-t,'timings':a.get('timings',{}),'usage':a.get('usage',{}),'choices':len(a.get('choices',[])),'output_sha256':hashlib.sha256(json.dumps(a.get('choices',[]),sort_keys=True).encode()).hexdigest()}
   phase='warmup';warm=request('Say hello.',16);assert proc.poll() is None and not errors and not faults(),(errors,faults());phase='measured';result=request(prompt,512);phase='after';assert proc.poll() is None and not errors and not faults(),(errors,faults());t=result['timings'];assert result['choices']>0 and t.get('predicted_n')==512 and t.get('draft_n',0)>0 and t.get('predicted_per_second',0)>0,(index,t)
   active=[x for x in samples if x['phase']=='measured' and x['cpu_busy'] is not None];assert len(active)>=5,'missing measured CPU telemetry'
   report.update(passed=True,pid=proc.pid,verified_mappings=sorted(str(f) for f in required),request=result,phase_cpu=statistics.mean(x['cpu_busy'] for x in active),phase_builds=statistics.mean(x['builds'] for x in active),phase_runnable=statistics.mean(x['runnable'] for x in active),gpu_samples=sum(x['gpu_busy'] is not None for x in active),gpu_busy=statistics.mean(x['gpu_busy'] for x in active if x['gpu_busy'] is not None) if any(x['gpu_busy'] is not None for x in active) else None,vram_peak=max((x['vram'] for x in active if x['vram'] is not None),default=None),new_gpu_errors=faults())
 finally:
  if proc is not None and proc.poll() is None:
   os.killpg(proc.pid,signal.SIGTERM)
   try:proc.wait(timeout=20)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
  stop.set();thread.join();report.update(monitor_errors=errors,gpu_sensor_errors=gpu_errors,wall_seconds=time.monotonic()-started,new_gpu_errors=faults());(out/f'{index:02d}-telemetry.json').write_text(json.dumps(samples,indent=2)+'\n');(out/f'{index:02d}-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
 assert report['passed'] and not errors and not report['new_gpu_errors'];
 if rows:
  assert report['request']['output_sha256']==rows[0]['request']['output_sha256'],'response hash mismatch'
  assert all(report['request']['timings'].get(k)==rows[0]['request']['timings'].get(k) for k in ('draft_n','draft_n_accepted')),'draft counters mismatch'
 rows.append(report);(out/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
assert same_models() and same_libraries() and all(sha(Path(path))==digest for path,digest in lib_hashes.items()),'Pinned model/library identity changed'
assert len({x['request']['output_sha256'] for x in rows})==1,'response hash mismatch'
assert len({(x['request']['timings'].get('draft_n'),x['request']['timings'].get('draft_n_accepted')) for x in rows})==1,'draft counters mismatch'
blocks=[]
for i in range(0,16,4):
 rr=rows[i:i+4];means=lambda key:{n:statistics.mean(x[key] for x in rr if x['width']==n) for n in ('baseline','candidate')};cpu=means('phase_cpu');builds=means('phase_builds');runq=means('phase_runnable');matched=abs(cpu['candidate']-cpu['baseline'])<=.05 and abs(builds['candidate']-builds['baseline'])<=2 and abs(runq['candidate']-runq['baseline'])<=max(4,.15*statistics.mean(runq.values()));effect=statistics.mean(math.log(x['request']['timings']['predicted_per_second'])for x in rr if x['width']=='candidate')-statistics.mean(math.log(x['request']['timings']['predicted_per_second'])for x in rr if x['width']=='baseline');blocks.append({'block':i//4,'matched':matched,'log_effect':effect,'cpu':cpu,'builds':builds,'runnable':runq})
def estimate(values):
 n=len(values);o={'blocks':n}
 if n>=4:
  c={4:3.182446305284263,5:2.776445105197799,6:2.570581835636305}[n];mu=statistics.mean(values);half=c*statistics.stdev(values)/math.sqrt(n);o.update(geometric_speed_change_percent=100*math.expm1(mu),descriptive_t95_percent=[100*math.expm1(mu-half),100*math.expm1(mu+half)],lower_bound_positive=mu-half>0)
 return o
report={'blocks':blocks,'all4':estimate([x['log_effect']for x in blocks]),'matched':estimate([x['log_effect']for x in blocks if x['matched']]),'scope':'One short stochastic prompt; Q3 recenter candidate vs private baseline discovery, no quality, long-context or deployment claim.'};report['confirmation_eligible']=report['matched'].get('lower_bound_positive',False);(out/'analysis.json').write_text(json.dumps(report,indent=2)+'\n');print('DFLASH_WIDTH_DISCOVERY',json.dumps(report),flush=True)
