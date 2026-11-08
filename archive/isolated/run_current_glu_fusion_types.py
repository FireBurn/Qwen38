from pathlib import Path
import hashlib,json,os,re,signal,subprocess,time
from native_observer_common import competition
base=Path(__file__).resolve().parent;q=base/'current-server-scope';p=q/'glu-fusion-port';lib=p/'lib/libggml-vulkan.so.0.28.0';frozen=q/'frozen-installed/lib';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();assets=[Path(__file__),p/'operator.cpp',p/'operator_bench',lib,p/'fused.comp.spv'];hashes={str(f):sha(f) for f in assets};(p/'operator-assets.json').write_text(json.dumps(hashes,indent=2)+'\n')
def kernel():return set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines())
initial=kernel();faults=lambda:[x for x in kernel()-initial if '0000:07:00.0' in x and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',x,re.I)];rows=[]
for order in range(4):
 ref=None
 for mode in ('baseline','fusion'):
  assert not competition(),competition();assert all(sha(f)==hashes[str(f)] for f in assets)
  env={k:v for k,v in os.environ.items() if not k.startswith(('GGML_','ACO_','RADV_','MESA_','VK_','LLAMA_','radv_','LD_'))};env.update(GLU_FIRST_TYPE=str(order),LD_LIBRARY_PATH=str(p/'lib')+':'+str(frozen),GGML_VK_VISIBLE_DEVICES='1',radv_buffer_meta_path='1',radv_enable_transfer_queue='false',EXPECTED_VK_BACKEND_PATH=str(lib))
  if mode=='fusion':env.update(GGML_VK_NATIVE_GLUQ_FUSE='1',GGML_VK_NATIVE_GLUQ_SHADER=str(p/'fused.comp.spv'),GGML_VK_NATIVE_GLUQ_GROUPS='16',GGML_VK_NATIVE_GLUQ_AUDIT='1')
  log=p/('operator-type'+str(order)+'-'+mode+'.log');output=p/('operator-type'+str(order)+'-'+mode+'.bin')
  with log.open('w') as f:
   child=subprocess.Popen([str(p/'operator_bench'),'3','1','4','5',str(output)],env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);print('OPERATOR_CHILD',mode,child.pid,flush=True);deadline=time.monotonic()+300
   try:
    while child.poll() is None:
     assert time.monotonic()<deadline,'timeout';assert not faults(),faults();assert not competition(child.pid),competition(child.pid);time.sleep(.2)
   finally:
    if child.poll() is None:os.killpg(child.pid,signal.SIGTERM);child.wait(timeout=10)
  assert child.returncode==0,(mode,child.returncode,log.read_text()[-3000:]);text=log.read_text();assert 'BACKEND_PATH_OK '+str(lib) in text and 'SELECTED_BACKEND Vulkan' in text and 'FIRST_WEIGHT '+['q3_K','q4_K','q5_K','q6_K'][order] in text;assert not faults(),faults();raw=output.read_bytes();counts=[int(x) for x in re.findall(r'NATIVE_GLUQ_FUSED (\d+)',text)]
  if mode=='baseline':ref=raw;assert not counts
  else:assert counts and sum(counts)>0,'fusion did not execute';assert raw==ref,'floating or downstream result mismatch'
  rows.append({'order':order,'mode':mode,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'fused_calls':sum(counts),'new_gpu_errors':faults()})
(p/'operator-type-checks.json').write_text(json.dumps({'passed':True,'arms':rows,'scope':'4 first-weight orders, 4 synthetic patterns, width 5, 4 GLUs and Q3_K/Q4_K/Q5_K/Q6_K consumers; same candidate backend default-off vs on; no model/speed qualification'},indent=2)+'\n');print('GLU_OPERATOR_EXACT',json.dumps(rows),flush=True)
