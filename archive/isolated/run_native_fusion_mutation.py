from pathlib import Path
import os,json,hashlib,subprocess,re,signal
from native_observer_common import competition
base=Path(__file__).resolve().parent;p=base/'native-fusion-plan';out=p/'mutation';out.mkdir();stock=base/'production-baseline-aa8';frozen=base/'q3-pad112/qualified-20261029';driver=base/'mtp-sched-keep-7k/driver'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
assert sha(p/'mutation-bin/operator_bench')==json.loads((p/'mutation-build.json').read_text())['binary_sha256']
assets=[Path(__file__),p/'MUTATION-PLAN.md',p/'mutation.cpp',p/'mutation-build.json',p/'mutation-bin/operator_bench',p/'reuse-build.json',p/'reuse-host/bin/libggml-vulkan.so.0.27.0',frozen/'bin/libggml-vulkan.so.0.27.0',driver/'libvulkan_radeon.so'];(out/'assets.json').write_text(json.dumps({str(f):sha(f)for f in assets},indent=2)+'\n');rows=[]
for name,mode in [('frozen',0),('oracle',2),('reuse',1)]:
 selected=frozen if not mode else p/'reuse-host';env={k:v for k,v in os.environ.items()if not k.startswith(('GGML_','ACO_','RADV_'))};env.update(GGML_VK_VISIBLE_DEVICES='1',GGML_VK_ALLOW_GRAPHICS_QUEUE='1',GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM='1',GGML_VK_MAX_NODES_PER_SUBMIT='400',LD_LIBRARY_PATH=str(selected/'bin')+':'+str(stock/'bin')+':'+str(base/'mtp-head-bound-audit/driver-deps')+':'+str(driver),VK_DRIVER_FILES=str(driver/'icd.json'),VK_ICD_FILENAMES=str(driver/'icd.json'),EXPECTED_VK_BACKEND_PATH=str(selected/'bin/libggml-vulkan.so.0.27.0'),EXPECTED_RADV_LIBRARY_PATH=str(driver/'libvulkan_radeon.so'),MESA_SHADER_CACHE_DIR=str(out/'cache'),radv_buffer_meta_path='2',radv_enable_transfer_queue='false')
 if mode:env.update(GGML_VK_FUSION_PLAN_REUSE=str(mode),GGML_VK_FUSION_PLAN_AUDIT='1')
 assert not competition(),competition();before=set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines());log=out/(name+'.log');binary=out/(name+'.bin');failure=None
 with log.open('w')as f:
  child=subprocess.Popen([str(p/'mutation-bin/operator_bench'),str(binary)],env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);print('NATIVE_FUSION_MUTATION_CHILD',name,child.pid,flush=True)
  try:child.wait(timeout=300)
  except Exception as exc:failure=repr(exc)
  finally:
   if child.poll()is None:os.killpg(child.pid,signal.SIGTERM);child.wait(timeout=10)
 text=log.read_text();bad=[l for l in subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines()if l not in before and '0000:07:00.0'in l and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',l,re.I)];r=dict(mode=mode,returncode=child.returncode,failure=failure,new_driver_errors=bad);(out/(name+'-execution.json')).write_text(json.dumps(r,indent=2)+'\n');assert child.returncode==0 and not bad and failure is None,r
 assert 'MUTATION_PATH_OK '+env['EXPECTED_VK_BACKEND_PATH']in text and 'MUTATION_PATH_OK '+env['EXPECTED_RADV_LIBRARY_PATH']in text
 assert text.count('MUTATION_END ')==16 and'MUTATION_DONE generations=16'in text
 records=[{k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',l)}for l in re.findall(r'^NATIVE_FUSION_REUSE (.+)$',text,re.M)]
 if mode:
  assert len(records)==16 and sum(x['hit']for x in records)>0 and sum(x['used']for x in records)>0 and not any(x['mismatches']for x in records)and not re.search(r'NATIVE_FUSION_[A-Z_]*MISMATCH',text)
  if mode==2:assert sum(x['checks']for x in records)>0
 else:assert not records
 r.update(sha256=sha(binary),bytes=binary.stat().st_size,records=records,metadata_mutation_generations=16);rows.append(r);(out/'checks.json').write_text(json.dumps(rows,indent=2)+'\n')
 assert all(x['sha256']==rows[0]['sha256']and x['bytes']==rows[0]['bytes']for x in rows),'Output/RMS intermediates differ'
(out/'comparison.json').write_text(json.dumps(dict(all_final_and_requested_RMS_bytes_identical=True,all_requested_RMS_sentinels_overwritten=True,oracle_mismatches=0,arms=3,generations_per_arm=16,scope='SamegraphnodesC1C2/8phases:OUTPUTflagandRMS epsilon mutationsbetweencomputations. Exactfrozen/oracle/reuseoutputsplusrequestedRMSmaterialization. Cachehit/missrecordsretained;noGPUerrors/newshaders/timingclaim.'),indent=2)+'\n');print('NATIVE_FUSION_MUTATION_ALL_EXACT',flush=True)
