from pathlib import Path
import os,json,subprocess,hashlib,re,signal
base=Path(__file__).resolve().parent;p=base/'q6-pad212';out=p/'diagnostics';out.mkdir();driver=base/'mtp-sched-keep-7k/driver'
for name,r in json.loads((driver/'manifest.json').read_text())['libraries'].items():assert hashlib.sha256((driver/name).read_bytes()).hexdigest()==r['sha256']
build=json.loads((p/'probe-build.json').read_text());assert hashlib.sha256((p/'operator_bench').read_bytes()).hexdigest()==build['binary_sha256']
assets=[Path(__file__),p/'probe.cpp',p/'operator_bench',*[p/(name+'_subgroup_no_shmem.spv')for name in ['native','pad16','pad32']],driver/'libvulkan_radeon.so'];(out/'assets.json').write_text(json.dumps({str(f):hashlib.sha256(f.read_bytes()).hexdigest()for f in assets},indent=2)+'\n')
env={k:v for k,v in os.environ.items()if not k.startswith(('GGML_','ACO_','RADV_'))};env.update(VK_DRIVER_FILES=str(driver/'icd.json'),VK_ICD_FILENAMES=str(driver/'icd.json'),LD_LIBRARY_PATH=str(base/'mtp-head-bound-audit/driver-deps')+':'+str(driver),EXPECTED_RADV_LIBRARY_PATH=str(driver/'libvulkan_radeon.so'),RADV_DEBUG='shaders',ACO_DEBUG='validateir,validatera',MESA_SHADER_CACHE_DIR=str(out/'cache'),radv_enable_transfer_queue='false',radv_buffer_meta_path='2')
before=set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines());log=out/'probe.log'
with log.open('w')as f:
 child=subprocess.Popen([str(p/'operator_bench'),str(p),'64'],env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);print('Q6_PAD212_CHILD',child.pid,flush=True)
 failure=None
 try:child.wait(timeout=180)
 except Exception as exc:failure={"type":type(exc).__name__,"message":str(exc)}
 finally:
  if child.poll()is None:os.killpg(child.pid,signal.SIGTERM);child.wait(timeout=10)
bad=[l for l in subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines()if l not in before and '0000:07:00.0'in l and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',l,re.I)]
text=log.read_text();stats={}
for name in ['native_c1','pad16_c1','pad32_c1','native_c2','pad16_c2','pad32_c2']:stats[name]={k:int(v)for k,v in re.findall(r'^STAT '+name+r' (.+) (\d+)$',text,re.M)}
report={'pid':child.pid,'returncode':child.returncode,'harness_failure':failure,'exact_dispatch_cases':text.count('EXACT k='),'stats':stats,'new_driver_errors':bad,'scope':'ActualnativeQ6floatmatrix vs212bytepaddingcontrols.C1/C2,5Kshapes,6rowshapes,6patterns,each3variants,atmost16WGs. ScalarCPUoracle,byteparity,inputimmutabilityand256byteguards. No model integration or speed claim.'}
(out/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
assert child.returncode==0 and report['exact_dispatch_cases']==1080 and not bad and failure is None,report
assert 'DRIVER_PATH_OK '+env['EXPECTED_RADV_LIBRARY_PATH']in text
assert all(stats[name]for name in stats)
print('Q6_PAD212_PROBE_ALL_1080_EXACT',flush=True)
for name,v in stats.items():print(name,{k:v[k]for k in ['VGPRs','Code size','Instructions','VMEM','LDS size','Scratch size']if k in v},flush=True)
