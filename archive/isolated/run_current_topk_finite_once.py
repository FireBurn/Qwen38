from pathlib import Path
import os,subprocess,hashlib,json,struct,re,datetime,sys
root=Path(__file__).resolve().parent/'current-server-scope'/'topk-chunk';run=root/'finite-health'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');run.mkdir(parents=True)
probe=root/'topk-probe'; arms={a:root/a/'libggml-vulkan.so.0.28.0' for a in ('baseline','candidate')}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def kernel():return set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines())
def faults(before):return sorted(x for x in kernel()-before if '0000:07:00.0' in x and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',x,re.I))
env={k:v for k,v in os.environ.items() if not k.startswith(('GGML_','ACO_','RADV_','MESA_','VK_','LLAMA_','radv_','LD_LIBRARY_PATH'))};env.update(GGML_VK_VISIBLE_DEVICES='1',radv_buffer_meta_path='1',radv_enable_transfer_queue='false')
report={'scope':'one row unique finite only; no speed or sampling qualification','probe_sha256':sha(probe),'backend_sha256':{a:sha(p) for a,p in arms.items()},'results':{},'passed':False};before=kernel();expected={((248320-1-j)*pow(17,-1,248320))%248320 for j in range(20)}
try:
 for arm,p in arms.items():
  out=run/(arm+'.bin');r=subprocess.run([str(probe),str(p),'1','0',str(out)],env=env,capture_output=True,text=True,timeout=30);(run/(arm+'.stdout')).write_text(r.stdout);(run/(arm+'.stderr')).write_text(r.stderr);errors=faults(before);assert not errors,errors;assert r.returncode==0,(arm,r.returncode);assert str(p) in r.stderr and 'vulkan_radeon' in r.stderr,(arm,'mapping missing');raw=out.read_bytes();assert len(raw)==80;idx=struct.unpack('<20i',raw);assert set(idx)==expected and len(set(idx))==20,(arm,'oracle mismatch',idx);report['results'][arm]={'indices':idx,'oracle_match':True,'new_gpu_errors':errors};print(arm,'oracle passed',flush=True)
 report['same_order']=report['results']['baseline']['indices']==report['results']['candidate']['indices'];assert report['same_order'],'baseline/candidate index order differs';report['passed']=True
except BaseException as e:
 report['error']=repr(e);raise
finally:(run/'result.json').write_text(json.dumps(report,indent=2)+'\n');print('results',run,flush=True)
