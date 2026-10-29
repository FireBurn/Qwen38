from pathlib import Path
import os,json,subprocess,hashlib,re,signal
from native_observer_common import competition
base=Path(__file__).resolve().parent;p=base/'q3-pair-glu';out=p/'eligibility';out.mkdir();driver=base/'mtp-sched-keep-7k/driver';stock=base/'production-baseline-aa8';frozen=base/'q3-pad112/qualified-20261029';host=p/'host'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
assert sha(p/'eligibility-bin/operator_bench')==json.loads((p/'eligibility-build.json').read_text())['binary_sha256']
for n,v in json.loads((driver/'manifest.json').read_text())['libraries'].items():assert sha(driver/n)==v['sha256']
assets=[Path(__file__),p/'ELIGIBILITY-PLAN.md',p/'eligibility.cpp',p/'eligibility-build.json',p/'eligibility-bin/operator_bench',p/'host-build.json',host/'bin/libggml-vulkan.so.0.27.0',frozen/'bin/libggml-vulkan.so.0.27.0',p/'pair_subgroup_no_shmem.spv',driver/'libvulkan_radeon.so'];(out/'assets.json').write_text(json.dumps({str(f):sha(f)for f in assets},indent=2)+'\n');rows=[]
for mode,disabled in [('frozen',False),('inactive',False),('active',False),('frozen',True),('active',True)]:
 selected=frozen if mode=='frozen'else host;label=mode+('-disabled'if disabled else'');log=out/(label+'.log');binary=out/(label+'.bin')
 env={k:v for k,v in os.environ.items()if not k.startswith(('GGML_','ACO_','RADV_'))};env.update(GGML_VK_VISIBLE_DEVICES='1',GGML_VK_ALLOW_GRAPHICS_QUEUE='1',GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM='1',GGML_VK_SUBALLOCATION_BLOCK_SIZE='4294967296',GGML_VK_MAX_NODES_PER_SUBMIT='400',GGML_VK_Q3_PAD112_DIR=str(frozen/'shaders'),GGML_VK_Q3_PAD112_IMMUTABLE='1',GGML_VK_Q3_PAD112_ARENA='1',GGML_VK_PAIR_GLU_AUDIT='1',VK_DRIVER_FILES=str(driver/'icd.json'),VK_ICD_FILENAMES=str(driver/'icd.json'),LD_LIBRARY_PATH=str(selected/'bin')+':'+str(stock/'bin')+':'+str(base/'mtp-head-bound-audit/driver-deps')+':'+str(driver),EXPECTED_VK_BACKEND_PATH=str(selected/'bin/libggml-vulkan.so.0.27.0'),EXPECTED_RADV_LIBRARY_PATH=str(driver/'libvulkan_radeon.so'),MESA_SHADER_CACHE_DIR=str(out/'cache'),radv_enable_transfer_queue='false',radv_buffer_meta_path='2')
 if mode=='active':env['GGML_VK_PAIR_GLU_SHADER']=str(p/'pair_subgroup_no_shmem.spv')
 if disabled:env['GGML_VK_DISABLE_FUSION']='1'
 assert not competition(),competition();before=set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines());failure=None
 with log.open('w')as f:
  child=subprocess.Popen([str(p/'eligibility-bin/operator_bench'),'disabled'if disabled else'normal',str(binary)],env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);print('PAIR_ELIGIBILITY_CHILD',label,child.pid,flush=True)
  try:child.wait(timeout=300)
  except Exception as exc:failure=repr(exc)
  finally:
   if child.poll()is None:os.killpg(child.pid,signal.SIGTERM);child.wait(timeout=10)
 text=log.read_text();bad=[l for l in subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines()if l not in before and '0000:07:00.0'in l and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',l,re.I)];execution=dict(returncode=child.returncode,failure=failure,new_driver_errors=bad);(out/(label+'-execution.json')).write_text(json.dumps(execution,indent=2)+'\n');assert child.returncode==0 and failure is None and not bad,execution
 assert 'WITNESS_PATH_OK '+env['EXPECTED_VK_BACKEND_PATH']in text and 'WITNESS_PATH_OK '+env['EXPECTED_RADV_LIBRARY_PATH']in text
 cases=[]
 for part in text.split('ELIGIBILITY_BEGIN ')[1:]:
  name=re.match(r'case=(\w+)',part)[1];cols=int(re.search(r' C=(\d+)',part)[1]);calls=len(re.findall(r'^PAIR_GLU_DISPATCH ',part,re.M));expected=4 if mode=='active'and not disabled and name in ['valid','reverse']else 0;assert calls==expected,(label,name,cols,calls,expected);cases.append(dict(case=name,columns=cols,pair_calls=calls,expected_pair_calls=expected))
 assert len(cases)==(2 if disabled else 25)and'ELIGIBILITY_ALL_DONE'in text
 row=dict(mode=mode,disabled=disabled,cases=cases,output_bytes=binary.stat().st_size,sha256=sha(binary),**execution);rows.append(row);(out/'checks.json').write_text(json.dumps(rows,indent=2)+'\n')
 ref=next(x for x in rows if x['disabled']==disabled);assert row['sha256']==ref['sha256']and row['output_bytes']==ref['output_bytes'],'Eligibility outputs differ'
(out/'comparison.json').write_text(json.dumps(dict(all_output_and_preserved_intermediate_bytes_identical=True,all_positive_and_negative_fusion_counts_expected=True,arms=5,cases_per_normal_arm=25,cases_per_disabled_arm=2,scope='Dedicatedhosteligibilitywitnesses;25casesx4patterns=100graphspernormalarm,8graphsperdisabledarm. Valid/reversedQ3pairs fuse;all specifiednegativecasesfallback. Allcontexts/buffersretaineduntilGPUdone. No throughput/generaldeploymentproof.'),indent=2)+'\n');print('PAIR_ELIGIBILITY_ALL_EXACT',flush=True)
