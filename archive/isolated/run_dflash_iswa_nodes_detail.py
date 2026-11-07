from pathlib import Path
import os,json,hashlib,subprocess,time,re,signal,threading,struct,traceback
from native_observer_common import competition
b=Path(__file__).resolve().parent;q=b/'current-server-scope';root=q/'dflash-two-seq';identity=json.loads((q/'profile/20261102T102358Z/identity.json').read_text());models={k:Path(v['path']) for k,v in identity['models'].items()};reference={k:(v['bytes'],v['inode'],v['device'],v['mtime_ns']) for k,v in identity['models'].items()};sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();arms={'baseline':q/'dflash-selector-anchor/trace-baseline','candidate':root/'iswa/candidate'};probe=root/'nodes-detail-probe';driver=Path('/usr/lib/libvulkan_radeon.so').resolve();files=[probe,driver,root/'NODE-DETAIL-PLAN.md',Path(__file__),*(x/'libllama.so.0.8.0' for x in arms.values()),q/'installed-build/bin/libggml-vulkan.so.0.28.0'];hashes={str(p):sha(p) for p in files};out=root/'node-detail-diagnostic'/time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());out.mkdir(parents=True);(out/'assets.json').write_text(json.dumps(hashes,indent=2)+'\n');report={'passed':False,'scope':'one synthetic fixed input, intrusive intermediate captures, no timing'}
def kernel():return set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines())
def faults(before):return sorted(x for x in kernel()-before if '0000:07:00.0' in x and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',x,re.I))
try:
 for arm,path in arms.items():
  assert not competition(),competition();assert all(sha(p)==hashes[str(p)] for p in files),'asset changed'
  for k,p in models.items():
   st=p.stat();assert (st.st_size,st.st_ino,st.st_dev,st.st_mtime_ns)==reference[k],('model stat changed',k)
  env={k:v for k,v in os.environ.items() if not k.startswith(('GGML_','ACO_','RADV_','MESA_','VK_','LLAMA_','radv_','LD_LIBRARY_PATH','DFLASH_','EXPECTED_LLAMA_'))};env.update(GGML_VK_VISIBLE_DEVICES='1',radv_buffer_meta_path='1',radv_enable_transfer_queue='false',DFLASH_SELECTOR_TRACE='1',DFLASH_NODE_AUDIT=str(out/(arm+'-nodes.bin')),EXPECTED_LLAMA_PATH=str(path/'libllama.so.0.8.0'),LD_LIBRARY_PATH=str(path)+':'+str(q/'installed-build/bin')+':/usr/lib64/llama.cpp');before=kernel();log=out/(arm+'.log');capture=out/(arm+'.bin');stop=threading.Event();errors=[]
  with log.open('w') as f:
   proc=subprocess.Popen([str(probe),str(models['target']),str(models['draft']),str(capture)],env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);print('child',arm,proc.pid,flush=True)
   def watch():
    while not stop.wait(.2):
     if proc.poll() is not None:return
     try:
      bad=faults(before);other=competition(proc.pid)
      if bad or other:errors.append({'gpu_errors':bad,'competition':other});os.killpg(proc.pid,signal.SIGTERM);return
     except Exception as e:errors.append(repr(e));os.killpg(proc.pid,signal.SIGTERM);return
   t=threading.Thread(target=watch);t.start()
   try:rc=proc.wait(timeout=300)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGTERM);proc.wait();raise
   finally:stop.set();t.join()
  bad=faults(before);text=log.read_text(errors='replace');assert rc==0 and not bad and not errors,(arm,'exit/fault',rc,bad,errors);assert 'PINNED_MAP '+'' in text and str(path/'libllama.so.0.8.0') in text,(arm,'wrong mapping');assert 'DRIVER_MAP ' in text,(arm,'driver missing');assert 'ISOLATION_CASE_PASS 0' in text,(arm,'case failure');section=text.split('ISOLATION_CASE_BEGIN 0',1)[1];graph=('blocks=2 tokens=10 block=5' if arm=='candidate' else 'blocks=1 tokens=5 block=5');assert graph in section,(arm,'graph missing');assert (out/(arm+'-nodes.bin')).is_file() and (out/(arm+'-nodes.bin')).stat().st_size>0,(arm,'node data missing');report[arm]={'lattice_sha256':sha(capture),'nodes_sha256':sha(out/(arm+'-nodes.bin')),'node_bytes':(out/(arm+'-nodes.bin')).stat().st_size,'new_gpu_errors':bad};(out/'comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(arm,'capture completed',flush=True)
 report['lattice_exact']=(out/'baseline.bin').read_bytes()==(out/'candidate.bin').read_bytes();report['passed']=True
except BaseException:
 report['failure']=traceback.format_exc();raise
finally:
 (out/'comparison.json').write_text(json.dumps(report,indent=2)+'\n');print('NODE_RESULT',out,json.dumps(report),flush=True)
