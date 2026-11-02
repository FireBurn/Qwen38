from pathlib import Path
import os,subprocess,hashlib,json,struct,re,datetime,heapq,math
root=Path(__file__).resolve().parent/'current-server-scope'/'topk-chunk';run=root/'model-check'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');run.mkdir(parents=True);probe=root/'topk-probe';inp=root/'model-logits-5rows.bin';arms={a:root/a/'libggml-vulkan.so.0.28.0' for a in ('baseline','candidate')}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def kernel():return set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines())
def faults(before):return sorted(x for x in kernel()-before if '0000:07:00.0' in x and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',x,re.I))
env={k:v for k,v in os.environ.items() if not k.startswith(('GGML_','ACO_','RADV_','MESA_','VK_','LLAMA_','radv_','LD_LIBRARY_PATH'))};env.update(GGML_VK_VISIBLE_DEVICES='1',radv_buffer_meta_path='1',radv_enable_transfer_queue='false');raw=inp.read_bytes();assert len(raw)==5*248320*4;expected=[]
for row in range(5):
 vals=struct.unpack_from('<248320f',raw,row*248320*4);assert all(map(math.isfinite,vals));indices=heapq.nlargest(21,range(len(vals)),key=vals.__getitem__);assert vals[indices[19]]>vals[indices[20]],'ambiguous top-k cutoff';expected.append(set(indices[:20]))
report={'scope':'five historical greedy target-logit rows; not current DFlash or speed qualification','input_sha256':sha(inp),'probe_sha256':sha(probe),'backend_sha256':{a:sha(p) for a,p in arms.items()},'results':{},'passed':False};before=kernel()
try:
 for arm,p in arms.items():
  out=run/(arm+'.bin');r=subprocess.run([str(probe),str(p),'5','4',str(out),str(inp)],env=env,capture_output=True,text=True,timeout=30);(run/(arm+'.stdout')).write_text(r.stdout);(run/(arm+'.stderr')).write_text(r.stderr);errors=faults(before);assert not errors,errors;assert r.returncode==0,(arm,r.returncode);assert str(p) in r.stderr and 'vulkan_radeon' in r.stderr,(arm,'mapping missing');b=out.read_bytes();assert len(b)==400;idx=struct.unpack('<100i',b);assert all(set(idx[i*20:(i+1)*20])==expected[i] for i in range(5)),(arm,'CPU oracle mismatch');report['results'][arm]={'indices':idx,'cpu_oracle_rows_passed':5,'new_gpu_errors':errors};print(arm,'five rows oracle passed',flush=True)
 report['same_order']=report['results']['baseline']['indices']==report['results']['candidate']['indices'];assert report['same_order'],'baseline/candidate order mismatch';report['passed']=True
except BaseException as e:report['error']=repr(e);raise
finally:(run/'result.json').write_text(json.dumps(report,indent=2)+'\n');print('results',run,flush=True)
