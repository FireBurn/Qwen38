from pathlib import Path
import os,json,hashlib,subprocess,time,re,signal,threading,struct,traceback
from native_observer_common import competition
b=Path(__file__).resolve().parent;q=b/'current-server-scope';root=q/'dflash-two-seq';identity=json.loads((q/'profile/20261102T102358Z/identity.json').read_text());models={k:Path(v['path']) for k,v in identity['models'].items()};reference={k:(v['bytes'],v['inode'],v['device'],v['mtime_ns']) for k,v in identity['models'].items()};sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();arms={'baseline':q/'dflash-selector-anchor/trace-baseline','candidate':root/'iswa/candidate'};probe=root/'isolation-probe';driver=Path('/usr/lib/libvulkan_radeon.so').resolve();files=[probe,driver,root/'ISWA-ISOLATION-PLAN.md',Path(__file__),*(x/'libllama.so.0.8.0' for x in arms.values()),q/'installed-build/bin/libggml-vulkan.so.0.28.0'];hashes={str(p):sha(p) for p in files};out=root/'iswa-isolation'/time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());out.mkdir(parents=True);(out/'assets.json').write_text(json.dumps(hashes,indent=2)+'\n');report={'passed':False,'scope':'four fixed empty-draft-KV synthetic two-sequence blocks, not model-server or performance qualification'}
def kernel():return set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines())
def faults(before):return sorted(x for x in kernel()-before if '0000:07:00.0' in x and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',x,re.I))
def parse(f):
 raw=f.read_bytes();records=[];off=0
 for i in range(4):
  assert off+16<=len(raw),'missing header';magic,k,n,w=struct.unpack_from('<4I',raw,off);off+=16;assert magic==0x49534f4c and k==i and n==10 and 1<=w<=16384,(magic,k,n,w);size=n*w*4;assert off+size<=len(raw),'short lattice';records.append((w,raw[off:off+size]));off+=size
 assert off==len(raw),'trailing bytes';return records
def validate(records):
 widths={x[0] for x in records};assert len(widths)==1;stride=next(iter(widths))*5*4;x=[r[1] for r in records];return {'base_repeat_exact':x[0]==x[3],'sequence1_unchanged_when_sequence0_perturbed':x[0][stride:]==x[1][stride:],'sequence0_unchanged_when_sequence1_perturbed':x[0][:stride]==x[2][:stride],'changed_sequence0':x[0][:stride]!=x[1][:stride],'changed_sequence1':x[0][stride:]!=x[2][stride:]}
try:
 captures={}
 for arm,path in arms.items():
  assert not competition(),competition();assert all(sha(p)==hashes[str(p)] for p in files),'asset changed'
  for k,p in models.items():
   st=p.stat();assert (st.st_size,st.st_ino,st.st_dev,st.st_mtime_ns)==reference[k],('model stat changed',k)
  env={k:v for k,v in os.environ.items() if not k.startswith(('GGML_','ACO_','RADV_','MESA_','VK_','LLAMA_','radv_','LD_LIBRARY_PATH','DFLASH_'))};env.update(GGML_VK_VISIBLE_DEVICES='1',radv_buffer_meta_path='1',radv_enable_transfer_queue='false',DFLASH_SELECTOR_TRACE='1',LD_LIBRARY_PATH=str(path)+':'+str(q/'installed-build/bin')+':/usr/lib64/llama.cpp');before=kernel();log=out/(arm+'.log');capture=out/(arm+'.bin');stop=threading.Event();errors=[];maps=[]
  with log.open('w') as f:
   proc=subprocess.Popen([str(probe),str(models['target']),str(models['draft']),str(capture)],env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);print('child',arm,proc.pid,flush=True)
   def watch():
    while not stop.wait(.25):
     if proc.poll() is not None:return
     try:
      bad=faults(before);other=competition(proc.pid)
      if bad or other:errors.append({'gpu_errors':bad,'competition':other});os.killpg(proc.pid,signal.SIGTERM);return
      text=Path(f'/proc/{proc.pid}/maps').read_text();maps[:]=[x for x in text.splitlines() if any(s in x for s in ('libllama.so','libggml-vulkan','libvulkan_radeon'))]
     except FileNotFoundError:return
     except Exception as e:errors.append(repr(e));os.killpg(proc.pid,signal.SIGTERM);return
   t=threading.Thread(target=watch);t.start()
   try:rc=proc.wait(timeout=300)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGTERM);proc.wait();raise
   finally:stop.set();t.join()
  (out/(arm+'-maps.txt')).write_text('\n'.join(maps)+'\n');bad=faults(before);text=log.read_text(errors='replace');assert rc==0 and not bad and not errors,(arm,'exit/fault',rc,bad,errors);assert str(path/'libllama.so.0.8.0') in '\n'.join(maps),(arm,'wrong llama mapping');assert 'libvulkan_radeon' in '\n'.join(maps),(arm,'missing RADV mapping');assert all(f'ISOLATION_CASE_PASS {i}' in text for i in range(4)),(arm,'case markers');sections=text.split('ISOLATION_CASE_BEGIN ');assert len(sections)==5,(arm,'case starts',len(sections));graphs=[re.findall(r'DFLASH_SELECTOR_TRACE blocks=(\d+) tokens=(\d+) block=(\d+)',x) for x in sections[1:]];required=('2','10','5') if arm=='candidate' else ('1','5','5');assert all(required in g for g in graphs),(arm,'graph marker missing',graphs);assert arm!='candidate' or all('DFLASH_TWOSEQ_ISWA_HIT tokens=10' in x for x in sections[1:]),(arm,'guard hit missing');records=parse(capture);checks=validate(records);report[arm]={'checks':checks,'sha256':sha(capture),'graphs':graphs,'new_gpu_errors':bad};(out/'comparison.json').write_text(json.dumps(report,indent=2)+'\n');assert all(checks.values()),(arm,'isolation checks',checks);captures[arm]=capture.read_bytes();print(arm,'isolation passed',flush=True)
 report['full_capture_exact']=captures['baseline']==captures['candidate'];assert report['full_capture_exact'],'baseline/candidate lattice differs';report['passed']=True
except BaseException:
 report['failure']=traceback.format_exc();raise
finally:
 (out/'comparison.json').write_text(json.dumps(report,indent=2)+'\n');print('ISOLATION_RESULT',out,json.dumps(report),flush=True)
