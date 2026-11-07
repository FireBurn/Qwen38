from pathlib import Path
import hashlib,json,os,re,signal,socket,subprocess,sys,threading,time,urllib.request
from concurrent.futures import ThreadPoolExecutor
from native_observer_common import competition
from quiet_builds import build_processes
base=Path(__file__).resolve().parent;q=base/'current-server-scope';hub=Path('${HF_CACHE}')
repos={'target':'models--nerkyor--Qwen3.8-27B-Coder390-EfficientThink-Opus5.5-GPT6Astra-Grok4.7-DSV4Pro-K3-SFT-RLOO-MTP-DFlash2','draft':'models--incoai--Qwen3.8-27B-DFlash2-GGUF'}
files={'target':'GGUF/Qwen3.8-27B-Coder390-EfficientThink-Q3LynnStyle-MTP.gguf','draft':'Qwen3.8-27B-DFlash2-Q4_K_M.gguf'}
models={}
for key,repo in repos.items():
 d=hub/repo;revision=(d/'refs/main').read_text().strip();f=(d/'snapshots'/revision/files[key]).resolve(strict=True);st=f.stat();models[key]={'path':str(f),'revision':revision,'bytes':st.st_size,'inode':st.st_ino,'device':st.st_dev,'mtime_ns':st.st_mtime_ns}
server=Path('/usr/bin/llama-server');ver=subprocess.run([str(server),'--version'],capture_output=True,text=True,check=True);version=(ver.stdout+ver.stderr).strip();server_hash=hashlib.sha256(server.read_bytes()).hexdigest()
if sys.argv[1:]==['--preflight']:
 print(json.dumps({'version':version,'server_sha256':server_hash,'models':models,'scope':'CPU-only preflight; no GPU or server start.'},indent=2));sys.exit(0)
assert len(sys.argv)==3 and sys.argv[1] in ('trace-baseline','trace-candidate') and not competition(),competition();arm=sys.argv[1];out=Path(sys.argv[2])/arm;out.mkdir(parents=True)
with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
cmd=[str(server),'-m',models['target']['path'],'--device','Vulkan0','--n-gpu-layers','all','--ctx-size','327680','--rope-scaling','yarn','--rope-scale','1.25','--yarn-orig-ctx','262144','--no-mmproj','--parallel','2','--flash-attn','on','--cache-type-k','q8_0','--cache-type-v','q8_0','--batch-size','2048','--ubatch-size','1024','--spec-draft-model',models['draft']['path'],'--spec-draft-ngl','all','--spec-draft-device','Vulkan0','--spec-type','ngram-mod,draft-dflash','--spec-ngram-mod-n-max','63','--spec-ngram-mod-n-min','16','--spec-draft-n-max','4','--backend-sampling','--spec-draft-type-k','q8_0','--spec-draft-type-v','q8_0','--ctx-checkpoints','16','--jinja','--reasoning','on','--reasoning-effort','xhigh','--reasoning-preserve','--temp','0.6','--top-p','0.95','--top-k','20','--min-p','0','--repeat-penalty','1.0','--presence-penalty','0','--cache-reuse','256','--fit','off','--poll','0','--host','127.0.0.1','--port',str(port)]
env={k:v for k,v in os.environ.items() if not k.startswith(('GGML_','ACO_','RADV_','MESA_','VK_','LLAMA_','radv_','LD_LIBRARY_PATH'))};env.update(GGML_VK_VISIBLE_DEVICES='1',radv_buffer_meta_path='1',radv_enable_transfer_queue='false',LD_LIBRARY_PATH=str(q/'dflash-selector-anchor'/arm)+':'+str(q/'installed-build/bin')+':/usr/lib64/llama.cpp',DFLASH_LATTICE_AUDIT=str(out/'lattice.bin'),DFLASH_SELECTOR_TRACE='1')
identity={'server_version':version,'server_sha256':server_hash,'models':models,'args':cmd,'child_overrides':{'GGML_VK_VISIBLE_DEVICES':'1','radv_buffer_meta_path':'1','radv_enable_transfer_queue':'false','audit':'private lattice capture','arm':arm}};(out/'identity.json').write_text(json.dumps(identity,indent=2)+'\n')
def http(path,payload=None,timeout=3):
 data=json.dumps(payload).encode() if payload is not None else None;req=urllib.request.Request(f'http://127.0.0.1:{port}'+path,data=data,headers={'Content-Type':'application/json'});return json.loads(urllib.request.urlopen(req,timeout=timeout).read())
def other_server(exclude=None):
 for p in Path('/proc').glob('[0-9]*'):
  try:
   if int(p.name)==exclude:continue
   args=(p/'cmdline').read_bytes().split(b'\0');name=Path(os.fsdecode(args[0])).name
   if name=='llama' and b'server' in args[1:]:return {'pid':int(p.name),'command':'llama server'}
  except (OSError,ValueError):continue
 return None
def kernel():return set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines())
initial=kernel();faults=lambda:[x for x in kernel()-initial if '0000:07:00.0' in x and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',x,re.I)]
stop=threading.Event();samples=[];errors=[];sensor_gaps=[];proc=None;pci=Path('/sys/bus/pci/devices/0000:07:00.0')
def monitor():
 old=None;tick=0;builds=0
 while not stop.is_set():
  try:
   v=[int(x) for x in Path('/proc/stat').read_text().splitlines()[0].split()[1:9]];t=sum(v);idle=v[3]+v[4];busy=None if old is None else 1-(idle-old[1])/max(1,t-old[0]);old=(t,idle)
   if tick%5==0:
    builds=len(build_processes())
    if proc is not None and proc.poll() is None:
     bad=faults();other=competition(proc.pid) or other_server(proc.pid)
     if bad or other:
      errors.append(repr({'new_gpu_errors':bad,'competition':other}));os.killpg(proc.pid,signal.SIGTERM);return
   samples.append({'time_ns':time.monotonic_ns(),'cpu_busy':busy,'builds':builds,'runnable':int(Path('/proc/loadavg').read_text().split()[3].split('/')[0]),'gpu_busy':int((pci/'gpu_busy_percent').read_text()),'vram':int((pci/'mem_info_vram_used').read_text())});tick+=1
  except OSError as e:
   if e.errno==16:sensor_gaps.append({'time_ns':time.monotonic_ns(),'error':repr(e)})
   else:errors.append(repr(e))
  except Exception as e:errors.append(repr(e))
  stop.wait(.2)
thread=threading.Thread(target=monitor);thread.start();report={'passed':False}
try:
 with (out/'server.log').open('w') as f:
  proc=subprocess.Popen(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);print('SERVER_CHILD',proc.pid,'output',out,flush=True);deadline=time.monotonic()+600
  while time.monotonic()<deadline:
   assert proc.poll() is None,('server exited',proc.returncode);assert not competition(proc.pid) and not other_server(proc.pid),(competition(proc.pid),other_server(proc.pid));assert not faults(),faults()
   try:
    if http('/health').get('status')=='ok':break
   except Exception:pass
   time.sleep(.5)
  else:raise TimeoutError('server readiness')
  assert 'radv_buffer_meta_path overridden' in (out/'server.log').read_text(),'1DW driver override was not observed'
  maps=Path(f'/proc/{proc.pid}/maps').read_text(); (out/'maps.txt').write_text(maps); assert str(q/'dflash-selector-anchor'/arm/'libllama.so.0.8.0') in maps,'wrong libllama'; assert str(q/'installed-build/bin/libllama-common.so') in maps,'wrong common library'; assert str(q/'installed-build/bin/libggml-vulkan.so') in maps,'wrong Vulkan backend'; assert 'vulkan_radeon' in maps,'missing RADV'
  def request(prompt,n):
   payload={'messages':[{'role':'user','content':prompt}],'max_tokens':n,'seed':1234,'temperature':0.6,'top_p':0.95,'top_k':20,'min_p':0.0,'cache_prompt':False,'ignore_eos':True,'stream':False};start=time.monotonic();answer=http('/v1/chat/completions',payload,timeout=600);elapsed=time.monotonic()-start;return {'elapsed_seconds':elapsed,'timings':answer.get('timings',{}),'usage':answer.get('usage',{}),'response_sha256':hashlib.sha256(json.dumps(answer.get('choices',[]),sort_keys=True).encode()).hexdigest(),'choice_count':len(answer.get('choices',[]))}
  warm=request('Say hello.',16);assert proc.poll() is None and not faults(),faults();barrier=threading.Barrier(2)
  def concurrent_request():
   barrier.wait(timeout=10);return request('Explain how a GPU matrix multiplication uses caches and registers, then give a short example.',128)
  with ThreadPoolExecutor(max_workers=2) as pool:
   fs=[pool.submit(concurrent_request) for _ in range(2)]; results=[f.result() for f in fs]
  assert proc.poll() is None and not faults(),faults();assert all(x['choice_count']>0 for x in results)
  report={'passed':True,'warmup':warm,'requests':results,'new_gpu_errors':[],'scope':'Instrumented two-slot lattice capture, not a speed result.'}
finally:
 if proc is not None and proc.poll() is None:
  os.killpg(proc.pid,signal.SIGTERM)
  try:proc.wait(timeout=20)
  except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
 stop.set();thread.join();report['monitor_errors']=errors;report['sensor_gaps']=sensor_gaps;report['new_gpu_errors']=faults();(out/'result.json').write_text(json.dumps(report,indent=2)+'\n');(out/'telemetry.json').write_text(json.dumps(samples,indent=2)+'\n');print(json.dumps(report),flush=True)
assert report['passed'] and not report['new_gpu_errors'] and not errors; assert (out/'lattice.bin').is_file() and (out/'lattice.bin').stat().st_size > 0,'missing lattice capture'
