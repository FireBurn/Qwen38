from pathlib import Path
import os,json,hashlib,subprocess,signal,re,time,gzip,shutil,struct,threading,statistics
from native_observer_common import competition
base=Path(__file__).resolve().parent;p=base/'native-transfer-observer';q=base/'q3-pad112';out=base/'native-constant-rotation-default/clear-profile'/time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());out.mkdir(parents=True);host=p/'metadata-host';stock=base/'production-baseline-aa8';driver=base/'mtp-sched-keep-7k/driver'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
for name,r in json.loads((driver/'manifest.json').read_text())['libraries'].items():assert sha(driver/name)==r['sha256']
assert sha(base/'production-native-shaders/model-audit-runner')==json.loads((base/'production-native-shaders/model-audit-build.json').read_text())['binary_sha256']
env={k:v for k,v in os.environ.items()if not k.startswith(('GGML_','ACO_','RADV_'))};env.update(GGML_VK_VISIBLE_DEVICES='1',LD_LIBRARY_PATH=str(host/'bin')+':'+str(stock/'bin')+':'+str(base/'mtp-head-bound-audit/driver-deps')+':'+str(driver),VK_DRIVER_FILES=str(driver/'icd.json'),VK_ICD_FILENAMES=str(driver/'icd.json'),EXPECTED_VK_BACKEND_PATH=str(host/'bin/libggml-vulkan.so.0.27.0'),EXPECTED_RADV_LIBRARY_PATH=str(driver/'libvulkan_radeon.so'),EXPECTED_LLAMA_CORE_PATH=str(stock/'bin/libllama.so.0.7.0'),radv_buffer_meta_path='2',radv_enable_transfer_queue='false')
model='${CLAUDE_WORKSPACE}/eval/models/nerkyor/GGUF/Qwen3.8-27B-Coder390-EfficientThink-Q3LynnStyle-MTP.gguf';prompt='The history of the Roman Empire begins with the rise of Augustus. After the death of Julius Caesar, a power struggle erupted among his heirs and generals. In this essay we will examine';rows=[]

from quiet_builds import build_processes
assert json.loads((q/'arena-model32/comparison.json').read_text())['all_requested_target_logit_bits_identical']
assert sha(p/'bin/model-bench')==json.loads((p/'metadata-build.json').read_text())['binary_sha256']
assets=[base/'native-constant-rotation/build.json',base/'native-constant-rotation/bin/libllama.so.0.7.0',base/'native-constant-rotation/CLEAR-PROFILE-PLAN.md',Path(__file__),p/'metadata-build.json',p/'bin/model-bench',p/'runner.cpp',p/'METADATA-PLAN.md',host/'bin/libggml-vulkan.so.0.27.0',q/'pad16_subgroup_no_shmem.spv',q/'repack.spv',stock/'bin/libllama.so.0.7.0',stock/'bin/libllama-common.so.0.7.0',driver/'libvulkan_radeon.so']
(out/'assets.json').write_text(json.dumps({str(f):sha(f)for f in assets},indent=2)+'\n')
env.update(EXPECTED_LLAMA_COMMON_PATH=str(stock/'bin/libllama-common.so.0.7.0'),MESA_SHADER_CACHE_DIR=str(q/'inprocess-shader-cache'))
env['GGML_VK_Q3_PAD112_DIR']=str(q/'qualified-20261029/shaders') # runner requires this variable but does not use it
env['GGML_VK_FUSION_PLAN_REUSE']='0'
env.pop('GGML_VK_Q3_PAD112_AUDIT',None)
assert sha(host/'bin/libggml-vulkan.so.0.27.0')==json.loads((p/'metadata-build.json').read_text())['library_sha256']
runtime_lib=Path('/usr/lib/libc.so.1').resolve();runtime_inode=runtime_lib.stat().st_ino
(out/'runtime-baseline.json').write_text(json.dumps(dict(path=str(runtime_lib),inode=runtime_inode,sha256=sha(runtime_lib)),indent=2)+'\n')
runtime_mapped=set()
env.update(LD_LIBRARY_PATH=str(base/'native-constant-rotation/bin')+':'+env['LD_LIBRARY_PATH'],EXPECTED_LLAMA_CORE_PATH=str(base/'native-constant-rotation/bin/libllama.so.0.7.0'),LLAMA_VK_CONST_ROT='1',LLAMA_VK_CONST_ROT_AUDIT='1')
env['NFP_TIMELINE_DIR']=str(out)
mode='native'
cmd=[str(p/'bin/model-bench'),'-m',model,'--spec-type','draft-mtp','--spec-draft-n-max','1','--spec-draft-n-min','1','--spec-draft-p-min','0','--no-spec-draft-backend-sampling'if mode=='native_cpu'else'--spec-draft-backend-sampling','--spec-draft-ngl','99','-ngl','99','-c','4096','-b','512','-ub','512','-fa','on','-ctk','q8_0','-ctv','q8_0','-ctkd','q8_0','-ctvd','q8_0','-t','1','-tb','1','-td','1','-tbd','1','--temp','0','--seed','1','-n','128','-p',prompt]

assert not competition(),competition()
before=set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines());log=out/'run.log';stop=threading.Event();child=None
pci=Path('/sys/bus/pci/devices/0000:07:00.0');freq=next((pci/'hwmon').glob('hwmon*/freq1_input'))
def monitor():
 previous=None;tick=0;builds=0
 with(out/'telemetry.jsonl').open('w')as f:
  while not stop.is_set():
   rec={'monotonic_ns':time.monotonic_ns(),'time':time.time()}
   try:
    if tick%10==0:builds=len(build_processes())
    tick+=1
    v=list(map(int,Path('/proc/stat').read_text().splitlines()[0].split()[1:9]));total=sum(v);idle=v[3]+v[4]
    if previous:rec['cpu_busy']=1-(idle-previous[1])/max(1,total-previous[0])
    previous=(total,idle)
    rec.update(clock_mhz=int(freq.read_text())/1e6,gpu_busy=int((pci/'gpu_busy_percent').read_text()),vram_bytes=int((pci/'mem_info_vram_used').read_text()),power_w=int(next((pci/'hwmon').glob('hwmon*/power1_average')).read_text())/1e6,builds=builds,loadavg=Path('/proc/loadavg').read_text().strip())
    text=log.read_text()if log.exists()else'';parts=text.split('INPROCESS_ARM_BEGIN ')
    if len(parts)>1:
     part=parts[-1];rec['arm']=int(re.match(r'arm=(-?\d+)',part)[1]);rec['steady_seen']='FULL_MODEL_WARM 'in part and 'FULL_MODEL_TIMING 'not in part;rec['decode_seen']='RESIDENT_DEC_BEGIN 'in part and 'FULL_MODEL_TIMING 'not in part
    if child is not None:
     for line in (Path('/proc')/str(child.pid)/'maps').read_text().splitlines():
      if line.endswith('/libc.so.1'):runtime_mapped.add(int(line.split(None,5)[4]))
   except Exception as exc:rec['sensor_error']=repr(exc)
   f.write(json.dumps(rec)+'\n');f.flush();stop.wait(.1)
worker=threading.Thread(target=monitor);worker.start();failure=None
try:
 with log.open('w')as f:
  child=subprocess.Popen(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);print('INPROCESS_CHILD',child.pid,out,flush=True)
  try:child.wait(timeout=900)
  except Exception as exc:failure=repr(exc)
  finally:
   if child.poll()is None:os.killpg(child.pid,signal.SIGTERM);child.wait(timeout=10)
finally:stop.set();worker.join()
bad=[l for l in subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines()if l not in before and '0000:07:00.0'in l and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',l,re.I)]
(out/'execution.json').write_text(json.dumps({'child_returncode':child.returncode,'failure':failure,'new_driver_errors':bad},indent=2)+chr(10))
(out/'execution.json').write_text(json.dumps({'child_returncode':child.returncode,'failure':failure,'new_driver_errors':bad},indent=2)+chr(10))
assert child.returncode==0 and not bad and failure is None
assert runtime_lib.stat().st_ino==runtime_inode and runtime_mapped=={runtime_inode},runtime_mapped
text=log.read_text();assert text.count('INPROCESS_ARM_END ')==6 and text.count('NFP_TIMELINE arm=')==4 and not re.search(r'NATIVE_FUSION_\w*MISMATCH',text)
parts=text.split('INPROCESS_ARM_BEGIN ')[1:];behavior=[]
for part in parts:
 tokens=list(map(int,re.findall('ACCEPTED_TOKEN ([0-9]+)',part)));fields={k:int(re.findall(k+'[ ]*=[ ]*([0-9]+)',part)[-1])for k in ['n_drafted','n_accept','n_predict']};behavior.append(dict(tokens=tokens,**fields))
assert len(behavior)==6 and all(v==behavior[0]for v in behavior)
prior=json.loads((q/'arena-inprocess/20261028T232836Z/checks.json').read_text())['arms'][0]
assert all(behavior[0][k]==prior[k]for k in ['tokens','n_drafted','n_accept','n_predict'])
(out/'behavior-check.json').write_text(json.dumps({'generations':6,'all_tokens_and_counters_identical':True,'matches_prior_native_prefix':True,'scope':'Privateimmutable-rotationcoreresidentclearwitness, newhostinactiveversusactive only;notpreservedfrozenbinarycomparison'},indent=2)+chr(10))
print('NATIVE_CONST_ROT_CLEAR_PROFILE_4_ARMS_EXACT',out,flush=True)
