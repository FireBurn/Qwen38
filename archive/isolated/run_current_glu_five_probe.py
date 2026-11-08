from pathlib import Path
import hashlib,json,os,re,signal,subprocess,time
from native_observer_common import competition
base=Path(__file__).resolve().parent;p=base/'current-server-scope/glu-five-probe';driver=base/'mtp-sched-keep-7k/driver';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for name,r in json.loads((driver/'manifest.json').read_text())['libraries'].items():assert sha(driver/name)==r['sha256']
assert not competition(),competition()
def kernel():return set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines())
initial=kernel();faults=lambda:[x for x in kernel()-initial if '0000:07:00.0' in x and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',x,re.I)]
env={k:v for k,v in os.environ.items() if not k.startswith(('GGML_','ACO_','RADV_','MESA_','VK_','LLAMA_','radv_','LD_'))};env.update(VK_DRIVER_FILES=str(driver/'icd.json'),VK_ICD_FILENAMES=str(driver/'icd.json'),LD_LIBRARY_PATH=str(base/'mtp-head-bound-audit/driver-deps')+':'+str(driver),EXPECTED_RADV_LIBRARY_PATH=str(driver/'libvulkan_radeon.so'),radv_buffer_meta_path='1',radv_enable_transfer_queue='false')
assets=[Path(__file__),p/'probe.cpp',p/'operator_bench',p/'glu.spv',p/'quant.spv',p/'fused.comp.spv',driver/'libvulkan_radeon.so'];(p/'assets.json').write_text(json.dumps({str(x):sha(x) for x in assets},indent=2)+'\n')
with (p/'probe.log').open('w') as f:
 child=subprocess.Popen([str(p/'operator_bench'),str(p)],env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);print('PROBE_CHILD',child.pid,flush=True);deadline=time.monotonic()+180
 try:
  while child.poll() is None:
   assert time.monotonic()<deadline,'timeout';assert not faults(),faults();assert not competition(child.pid),competition(child.pid);time.sleep(.2)
 finally:
  if child.poll() is None:os.killpg(child.pid,signal.SIGTERM);child.wait(timeout=10)
assert child.returncode==0,(child.returncode,(p/'probe.log').read_text()[-3000:]);text=(p/'probe.log').read_text();assert 'DRIVER_PATH_OK '+env['EXPECTED_RADV_LIBRARY_PATH'] in text;cases=re.findall(r'^EXACT n=87040 phase=(\d+) float_bytes=(\d+) packed_bytes=(\d+) groups=16$',text,re.M);assert len(cases)==6 and 'STANDALONE_GLU_QUANT_ALL_EXACT' in text and not faults();(p/'checks.json').write_text(json.dumps({'passed':True,'cases':cases,'new_gpu_errors':faults(),'scope':'Six synthetic patterns, flattened five-column 17408-wide input, old standalone shader controls, 16 workgroups, not current backend/model or speed qualification.'},indent=2)+'\n');print('GLU_FIVE_EXACT',cases,flush=True)
