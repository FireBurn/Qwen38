from pathlib import Path
import os,json,hashlib,subprocess,signal,re,time
from native_observer_common import competition
base=Path(__file__).resolve().parent;p=base/'q3-pad112';q=p/'qualified-20261029';m=json.loads((q/'manifest.json').read_text())
mode='pad';requested=32;assert mode in ['stock','pad']and requested in [32,512]
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
config_path=p/'submission-qualified-20261029.json';config=json.loads(config_path.read_text());assert config['node_cap']==400
for name,value in config['proof_files'].items():assert sha(p/name)==value,name
for name,value in m['files'].items():assert sha(q/name)==value,name
for name,value in m['external_files'].items():assert sha(Path(name))==value,name
model=Path(m['model']['path']);st=model.stat();assert st.st_size==m['model']['size']and st.st_mtime_ns==m['model']['mtime_ns'],'Model identity guard differs'
stock=base/'production-baseline-aa8';driver=base/'mtp-sched-keep-7k/driver';host=stock/'bin'if mode=='stock'else q/'bin'
out=base/'native-gdn-reader-index'/'gpu-profile32'/time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());out.mkdir(parents=True)
env={k:v for k,v in os.environ.items()if not k.startswith(('GGML_','ACO_','RADV_','LLAMA_HEAD_BOUND_'))and k not in ['LLAMA_MTP_DRAFT_NVOCAB','MTP_LOGITS_AUDIT_OUT','PRODUCTION_TARGET_AUDIT_OUT']}
env.update(GGML_VK_MAX_NODES_PER_SUBMIT='400',GGML_VK_VISIBLE_DEVICES='1',GGML_VK_ALLOW_GRAPHICS_QUEUE='1',GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM='1',GGML_VK_SUBALLOCATION_BLOCK_SIZE='4294967296',LD_LIBRARY_PATH=str(host)+':'+str(stock/'bin')+':'+str(base/'mtp-head-bound-audit/driver-deps')+':'+str(driver),VK_DRIVER_FILES=str(driver/'icd.json'),VK_ICD_FILENAMES=str(driver/'icd.json'),EXPECTED_VK_BACKEND_PATH=str(host/'libggml-vulkan.so.0.27.0'),EXPECTED_RADV_LIBRARY_PATH=str(driver/'libvulkan_radeon.so'),EXPECTED_LLAMA_CORE_PATH=str(stock/'bin/libllama.so.0.7.0'),EXPECTED_LLAMA_COMMON_PATH=str(stock/'bin/libllama-common.so.0.7.0'),MESA_SHADER_CACHE_DIR=str(p/'model-timing-cache-pad'if mode=='pad'else p/'model-timing-cache-stock'),radv_buffer_meta_path='2',radv_enable_transfer_queue='false')
env.update(GGML_VK_PERF_LOGGER='1',GGML_VK_PERF_LOGGER_FREQUENCY='1000000')
if os.environ.get('GDN_GPU_GROUPED')=='1':env['GGML_VK_PERF_LOGGER_CONCURRENT']='1'
if mode=='pad':env.update(GGML_VK_Q3_PAD112_DIR=str(q/'shaders'),GGML_VK_Q3_PAD112_IMMUTABLE='1',GGML_VK_Q3_PAD112_ARENA='1')
prompt='The history of the Roman Empire begins with the rise of Augustus. After the death of Julius Caesar, a power struggle erupted among his heirs and generals. In this essay we will examine'
cmd=[str(base/'mtp-production-throughput/model-bench'),'-m',str(model),'--spec-type','draft-mtp','--spec-draft-n-max','1','--spec-draft-n-min','1','--spec-draft-p-min','0','--spec-draft-backend-sampling','--spec-draft-ngl','99','-ngl','99','-c','4096','-b','512','-ub','512','-fa','on','-ctk','q8_0','-ctv','q8_0','-ctkd','q8_0','-ctvd','q8_0','-t','1','-tb','1','-td','1','-tbd','1','--temp','0','--seed','1','-n',str(requested),'-p',prompt]
assert not competition(),competition();before=set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines());failure=None;log=out/'run.log'
with log.open('w')as f:
 child=subprocess.Popen(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);print('QUALIFIED_CHILD',child.pid,mode,out,flush=True);start=time.monotonic()
 try:
  while child.poll()is None:
   if time.monotonic()-start>600:raise RuntimeError('Competition or timeout')
   time.sleep(.1)
 except Exception as exc:failure=repr(exc)
 finally:
  if child.poll()is None:os.killpg(child.pid,signal.SIGTERM);child.wait(timeout=10)
bad=[l for l in subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines()if l not in before and '0000:07:00.0'in l and re.search('ring .*timeout|GPU reset|fault|MES.*failed',l,re.I)]
report={'grouped':os.environ.get('GDN_GPU_GROUPED')=='1','submission_cap':400,'submission_config_sha256':sha(config_path),'mode':mode,'requested_tokens':requested,'returncode':child.returncode,'failure':failure,'new_driver_errors':bad,'command':cmd,'snapshot_manifest_sha256':sha(q/'manifest.json'),'scope':'Intrusive GPU timestamp diagnostic,32requested tokens. Logger changes waits/submission/overlap; no throughput inference. Concurrent flag groups dependency segments; otherwise ops serialized. Includes prompt and warm generation.'}
(out/'execution.json').write_text(json.dumps(report,indent=2)+chr(10));assert child.returncode==0 and failure is None and not bad,report
text=log.read_text();assert 'BACKEND_PATH_OK '+env['EXPECTED_VK_BACKEND_PATH']in text and 'DRIVER_PATH_OK '+env['EXPECTED_RADV_LIBRARY_PATH']in text
ids=list(map(int,re.findall('ACCEPTED_TOKEN ([0-9]+)',text)));assert len(ids)>=requested and ids==m['expected_token_prefix'][:len(ids)],'Token reference differs'
match=re.search('FULL_MODEL_TIMING warm_tokens=([0-9]+) cold_generation_us=([0-9]+) steady_tokens=([0-9]+) steady_us=([0-9]+) total_generation_us=([0-9]+)',text);assert match
warm,cold,n,us,total=map(int,match.groups());report.update(generated_tokens=len(ids),all_tokens_match_reference=True,steady_tokens_per_second=n*1e6/us,cold_us=cold,total_generation_us=total)
(out/'checks.json').write_text(json.dumps(report,indent=2)+chr(10));print('QUALIFIED_SINGLE_EXACT',report['generated_tokens'],'tokens',out,flush=True)
