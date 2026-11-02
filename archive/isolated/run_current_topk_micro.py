from pathlib import Path
import os,json,hashlib,subprocess,re,time,threading,statistics,math
from native_observer_common import competition
from quiet_builds import build_processes
b=Path(__file__).resolve().parent;root=b/'current-server-scope/topk-chunk';probe=root/'topk-probe';inp=root/'model-logits-1row.bin';ref=root/'model-check/20261102T103328Z/baseline.bin';arms={x:root/x/'libggml-vulkan.so.0.28.0' for x in ('baseline','candidate')};driver=Path('/usr/lib/libvulkan_radeon.so').resolve();files=[probe,inp,ref,driver,*arms.values(),root/'MICRO-PLAN.md',Path(__file__)];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();hashes={str(p):sha(p) for p in files};out=root/'micro'/time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());out.mkdir(parents=True);(out/'assets.json').write_text(json.dumps(hashes,indent=2)+'\n');sequence=[a for i in range(4) for a in (['baseline','candidate','candidate','baseline'] if i%2==0 else ['candidate','baseline','baseline','candidate'])];(out/'protocol.json').write_text(json.dumps({'sequence':sequence,'plan':(root/'MICRO-PLAN.md').read_text()},indent=2)+'\n');env={k:v for k,v in os.environ.items() if not k.startswith(('GGML_','ACO_','RADV_','MESA_','VK_','LLAMA_','radv_','LD_LIBRARY_PATH','TOPK_PROBE_'))};env.update(GGML_VK_VISIBLE_DEVICES='1',radv_buffer_meta_path='1',radv_enable_transfer_queue='false',TOPK_PROBE_ITERS='60');rows=[]
def kernel():return set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines())
for i,arm in enumerate(sequence):
 assert not competition(),competition();assert all(sha(p)==hashes[str(p)] for p in files),'asset changed';before=kernel();samples=[];errors=[];stop=threading.Event()
 def sample():
  prev=None;tick=0;builds=0
  while not stop.is_set():
   try:
    v=[int(x) for x in Path('/proc/stat').read_text().splitlines()[0].split()[1:9]];total=sum(v);idle=v[3]+v[4];busy=None if prev is None else 1-(idle-prev[1])/max(1,total-prev[0]);prev=(total,idle)
    if tick%10==0:builds=len(build_processes())
    samples.append({'cpu':busy,'builds':builds,'runnable':int(Path('/proc/loadavg').read_text().split()[3].split('/')[0])});tick+=1
   except Exception as e:errors.append(repr(e))
   stop.wait(.05)
 worker=threading.Thread(target=sample);worker.start();result=out/f'{i:02d}-{arm}.bin'
 try:r=subprocess.run([str(probe),str(arms[arm]),'1','4',str(result),str(inp)],env=env,capture_output=True,text=True,timeout=30)
 finally:stop.set();worker.join()
 text=r.stdout+r.stderr;(out/f'{i:02d}-{arm}.log').write_text(text);bad=[x for x in kernel()-before if '0000:07:00.0' in x and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',x,re.I)];assert r.returncode==0 and not bad,(i,r.returncode,bad);assert str(arms[arm]) in text and 'vulkan_radeon' in text;assert result.read_bytes()==ref.read_bytes()[:80];m=re.search(r'us_per_graph=([0-9.]+) iters=60',text);assert m;valid=[s for s in samples if s['cpu'] is not None];assert valid and not errors,(samples,errors)
 row={'index':i,'arm':arm,'us_per_graph':float(m[1]),**{k:statistics.mean(s[k] for s in valid) for k in ('cpu','builds','runnable')},'new_gpu_errors':bad};rows.append(row);(out/f'{i:02d}-telemetry.json').write_text(json.dumps(samples,indent=2)+'\n');(out/'results.json').write_text(json.dumps(rows,indent=2)+'\n');print(row,flush=True)
blocks=[]
for i in range(0,16,4):
 rr=rows[i:i+4];means=lambda key:{a:statistics.mean(r[key] for r in rr if r['arm']==a) for a in arms};cpu=means('cpu');builds=means('builds');rq=means('runnable');matched=abs(cpu['baseline']-cpu['candidate'])<=.05 and abs(builds['baseline']-builds['candidate'])<=2 and abs(rq['baseline']-rq['candidate'])<=max(4,.15*statistics.mean(rq.values()));effect=statistics.mean(math.log(r['us_per_graph']) for r in rr if r['arm']=='candidate')-statistics.mean(math.log(r['us_per_graph']) for r in rr if r['arm']=='baseline');blocks.append({'block':i//4,'matched':matched,'log_time_effect':effect,'cpu':cpu,'builds':builds,'runnable':rq})
def estimate(values):
 n=len(values);out={'blocks':n}
 if n:
  mu=statistics.mean(values);out['geometric_time_change_percent']=100*math.expm1(mu)
  if n==4:
   half=3.182446305284263*statistics.stdev(values)/math.sqrt(n);out['descriptive_t95_percent']=[100*math.expm1(mu-half),100*math.expm1(mu+half)]
 return out
report={'blocks':blocks,'all4':estimate([r['log_time_effect'] for r in blocks]),'matched':estimate([r['log_time_effect'] for r in blocks if r['matched']]),'scope':'Operator wall time only, not model or server throughput'};(out/'analysis.json').write_text(json.dumps(report,indent=2)+'\n');print('TOPK_MICRO_COMPLETE',json.dumps(report),flush=True)
