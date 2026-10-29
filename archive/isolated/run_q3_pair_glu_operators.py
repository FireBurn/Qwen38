from pathlib import Path
import os,json,subprocess,hashlib,re,signal
from native_observer_common import competition
base=Path(__file__).resolve().parent;p=base/'q3-pair-glu';out=p/'operators';out.mkdir();driver=base/'mtp-sched-keep-7k/driver'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
for name,r in json.loads((driver/'manifest.json').read_text())['libraries'].items():assert sha(driver/name)==r['sha256']
assert sha(p/'operator_bench')==json.loads((p/'probe-build.json').read_text())['binary_sha256']
for name,value in json.loads((p/'shader-build.json').read_text())['modules'].items():assert sha(p/name)==value
assets=[Path(__file__),p/'PLAN.md',p/'probe.cpp',p/'probe-build.json',p/'shader-build.json',p/'operator_bench',p/'pad16_subgroup_no_shmem.spv',p/'pair_subgroup_no_shmem.spv',p/'swiglu_ref.spv',driver/'libvulkan_radeon.so'];(out/'assets.json').write_text(json.dumps({str(f):sha(f)for f in assets},indent=2)+'\n')
env={k:v for k,v in os.environ.items()if not k.startswith(('GGML_','ACO_','RADV_'))};env.update(VK_DRIVER_FILES=str(driver/'icd.json'),VK_ICD_FILENAMES=str(driver/'icd.json'),LD_LIBRARY_PATH=str(base/'mtp-head-bound-audit/driver-deps')+':'+str(driver),EXPECTED_RADV_LIBRARY_PATH=str(driver/'libvulkan_radeon.so'),RADV_DEBUG='shaders',ACO_DEBUG='validateir,validatera',MESA_SHADER_CACHE_DIR=str(out/'cache'),radv_enable_transfer_queue='false',radv_buffer_meta_path='2')
assert not competition(),competition();before=set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines());log=out/'probe.log'
with log.open('w')as f:
 child=subprocess.Popen([str(p/'operator_bench'),str(p),'64'],env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);print('PAIR_OPERATOR_CHILD',child.pid,flush=True);failure=None
 try:child.wait(timeout=180)
 except Exception as exc:failure=repr(exc)
 finally:
  if child.poll()is None:os.killpg(child.pid,signal.SIGTERM);child.wait(timeout=10)
bad=[l for l in subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines()if l not in before and '0000:07:00.0'in l and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',l,re.I)]
text=log.read_text();stats={name:{k:int(v)for k,v in re.findall(r'^STAT '+name+r' (.+) (\d+)$',text,re.M)}for name in ['pad16_c1','pair_c1','pad16_c2','pair_c2','swiglu_ref_c3']}
r=dict(pid=child.pid,returncode=child.returncode,harness_failure=failure,exact_cases=text.count('PAIR_EXACT '),stats=stats,new_driver_errors=bad,scope='Two exact frozenpaddedQ3matmuls plus extractedproductionGLU versus onepairQ3GLUkernel.6Kwidths/6rowtails/C1C2/4patterns/2orders;allfirstdispatches<=16WG. Native matrixscalarCPUoracle,fullGLUbytes,inputimmutability/guards. No modelintegration/performancequalification.')
(out/'checks.json').write_text(json.dumps(r,indent=2)+'\n');assert child.returncode==0 and r['exact_cases']==576 and not bad and failure is None,r
assert 'DRIVER_PATH_OK '+env['EXPECTED_RADV_LIBRARY_PATH']in text and all(stats.values());print('PAIR_576_CASES_EXACT',flush=True)
for name,v in stats.items():print(name,{k:v[k]for k in ['VGPRs','Spilled SGPRs','Spilled VGPRs','Code size','Instructions','VMEM','LDS size','Scratch size']if k in v},flush=True)
