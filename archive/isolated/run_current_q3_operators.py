from pathlib import Path
import os,json,hashlib,subprocess,time,re,signal,threading,traceback
from native_observer_common import competition
base=Path(__file__).resolve().parent;root=base/'current-server-scope/q3-recenter';probe=root/'probe';arms={x:root/x/'libggml-vulkan.so.0.28.0' for x in ('baseline','candidate')};driver=Path('/usr/lib/libvulkan_radeon.so').resolve();files=[probe,driver,root/'OPERATOR-PLAN.md',Path(__file__),*arms.values()];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();hashes={str(p):sha(p) for p in files};out=root/'operators'/time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());out.mkdir(parents=True);(out/'assets.json').write_text(json.dumps(hashes,indent=2)+'\n');report={'passed':False,'cases':[],'scope':'synthetic Q3 backend output comparison, not speed or full correctness'}
def kernel():return set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines())
def faults(before):return sorted(x for x in kernel()-before if '0000:07:00.0' in x and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',x,re.I))
try:
 for m,n in ((64,4),(64,5),(17408,4),(17408,5)):
  result={}
  for arm,p in arms.items():
   assert not competition(),competition();assert all(sha(f)==hashes[str(f)] for f in files),'asset changed';env={k:v for k,v in os.environ.items() if not k.startswith(('GGML_','ACO_','RADV_','MESA_','VK_','LLAMA_','radv_','LD_LIBRARY_PATH'))};env.update(GGML_VK_VISIBLE_DEVICES='1',radv_buffer_meta_path='1',radv_enable_transfer_queue='false');before=kernel();log=out/f'm{m}-n{n}-{arm}.log';data=out/f'm{m}-n{n}-{arm}.bin';stop=threading.Event();errors=[]
   with log.open('w') as f:
    proc=subprocess.Popen([str(probe),str(p),str(data),'5120',str(m),str(n)],env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);print('child',m,n,arm,proc.pid,flush=True)
    def watch():
     while not stop.wait(.2):
      if proc.poll() is not None:return
      try:
       bad=faults(before);other=competition(proc.pid)
       if bad or other:errors.append({'faults':bad,'competition':other});os.killpg(proc.pid,signal.SIGTERM);return
      except Exception as e:errors.append(repr(e));os.killpg(proc.pid,signal.SIGTERM);return
    t=threading.Thread(target=watch);t.start()
    try:rc=proc.wait(timeout=120)
    except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGTERM);proc.wait();raise
    finally:stop.set();t.join()
   bad=faults(before);text=log.read_text(errors='replace');assert rc==0 and not bad and not errors,(m,n,arm,rc,bad,errors);assert 'BACKEND_MAP ' in text and str(p) in text and 'DRIVER_MAP ' in text,(m,n,arm,'mapping');assert f'Q3_CASE_PASS k=5120 m={m} n={n}' in text,(m,n,arm,'marker');assert data.stat().st_size==m*n*4,(m,n,arm,'length');result[arm]={'sha256':sha(data),'new_gpu_errors':bad}
  result.update(m=m,n=n,exact=(out/f'm{m}-n{n}-baseline.bin').read_bytes()==(out/f'm{m}-n{n}-candidate.bin').read_bytes());report['cases'].append(result);(out/'comparison.json').write_text(json.dumps(report,indent=2)+'\n');assert result['exact'],('output mismatch',m,n);print('case exact',m,n,flush=True)
 report['passed']=True
except BaseException:report['failure']=traceback.format_exc();raise
finally:(out/'comparison.json').write_text(json.dumps(report,indent=2)+'\n');print('Q3_OPERATOR_RESULT',out,json.dumps(report),flush=True)
