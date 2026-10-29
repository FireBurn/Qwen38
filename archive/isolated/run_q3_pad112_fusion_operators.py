from pathlib import Path
import os,json,hashlib,subprocess,signal,re,time
from mixed_matrix_stream_settled3_common import competition
base=Path(__file__).resolve().parent;p=base/'q3-pad112';out=p/'fusion-options-operators';out.mkdir();host=p/'host-fusion-options';stock=base/'production-baseline-aa8';driver=base/'mtp-sched-keep-7k/driver'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
for name,r in json.loads((driver/'manifest.json').read_text())['libraries'].items():assert sha(driver/name)==r['sha256']
for f in json.loads((stock/'manifest.json').read_text())['files']:
 path=stock/'bin'/f['name']
 if path.is_file():assert sha(path)==f['sha256'],path
assert sha(host/'bin/libggml-vulkan.so.0.27.0')==json.loads((host/'build.json').read_text())['library_sha256']
assets=[Path(__file__),base/'production-native-shaders/client/operator_bench',host/'bin/libggml-vulkan.so.0.27.0',driver/'libvulkan_radeon.so',base/'native-swiglu-q8/shuffle8/fused.comp.spv',base/'native-quant-shuffle/shuffle.spv',*[base/'q3-native-correction'/('candidate-mul_mat_vec_q3_k_q8_1_f32'+suffix+'.spv')for suffix in ['','_subgroup','_subgroup_no_shmem']]]
(out/'assets.json').write_text(json.dumps({str(f):sha(f)for f in assets},indent=2)+'\n')
env={k:v for k,v in os.environ.items()if not k.startswith(('GGML_','ACO_','RADV_'))};env.update(GGML_VK_VISIBLE_DEVICES='1',GGML_VK_ALLOW_GRAPHICS_QUEUE='1',GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM='1',GGML_VK_SUBALLOCATION_BLOCK_SIZE='4294967296',LD_LIBRARY_PATH=str(host/'bin')+':'+str(stock/'bin')+':'+str(base/'mtp-head-bound-audit/driver-deps')+':'+str(driver),VK_DRIVER_FILES=str(driver/'icd.json'),VK_ICD_FILENAMES=str(driver/'icd.json'),EXPECTED_VK_BACKEND_PATH=str(host/'bin/libggml-vulkan.so.0.27.0'),EXPECTED_RADV_LIBRARY_PATH=str(driver/'libvulkan_radeon.so'),radv_buffer_meta_path='2',radv_enable_transfer_queue='false')
rows=[]
for cols in [1,2]:
 reference=None
 for mask in [0,4,7]:
  assert not competition(),competition();label=f'c{cols}-mask{mask}';trial=env.copy();trial['MESA_SHADER_CACHE_DIR']=str(out/('cache-'+label));trial.update(GGML_VK_NATIVE_GLUQ_AUDIT='1',GGML_VK_NATIVE_GLUQ_CHECK_PLAN='1')
  if mask&1:trial.update(GGML_VK_NATIVE_Q8_SHUFFLE='1',GGML_VK_NATIVE_Q8_SHADER=str(base/'native-quant-shuffle/shuffle.spv'))
  if mask&2:trial['GGML_VK_NATIVE_Q3_CORRECTION_DIR']=str(base/'q3-native-correction')
  if mask&4:trial.update(GGML_VK_NATIVE_GLUQ_FUSE='1',GGML_VK_NATIVE_GLUQ_SHADER=str(base/'native-swiglu-q8/shuffle8/fused.comp.spv'),GGML_VK_NATIVE_GLUQ_GROUPS='16',GGML_VK_NATIVE_GLUQ_EXPAND_VIEWS='1',GGML_VK_NATIVE_GLUQ_COALESCE='1',GGML_VK_PIPELINE_STATS='native_swiglu_quant')
  binary=out/(label+'.bin');log=out/(label+'.log');before=set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines())
  with log.open('w')as f:
   child=subprocess.Popen([str(base/'production-native-shaders/client/operator_bench'),'3','2','4',str(cols),str(binary)],env=trial,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);print('PRODUCTION_OPERATOR_CHILD',label,child.pid,flush=True)
   try:child.wait(timeout=120)
   finally:
    if child.poll()is None:os.killpg(child.pid,signal.SIGTERM);child.wait(timeout=10)
  bad=[l for l in subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines()if l not in before and '0000:07:00.0'in l and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',l,re.I)]
  text=log.read_text();counts={k:0 for k in ['quant_new','quant_old','q3_new','q3_old']}
  for line in re.findall(r'^NATIVE_SHADER_DISPATCH_COUNTS (.+)$',text,re.M):
   for k,v in re.findall(r'(\w+)=(\d+)',line):counts[k]+=int(v)
  row=dict(columns=cols,mask=mask,pid=child.pid,returncode=child.returncode,actual_dispatch_counts=counts,new_driver_errors=bad,scope='Productionaa8 .27fusion operator check,stockactivationpolicy,16fusedworkgroups;native,fusiononly,allthree. Planner equality and actualfusedcalls checked;not timing ormodelqualification.')
  assert child.returncode==0 and not bad,row
  assert 'BACKEND_PATH_OK '+trial['EXPECTED_VK_BACKEND_PATH']in text and 'DRIVER_PATH_OK '+trial['EXPECTED_RADV_LIBRARY_PATH']in text
  raw=binary.read_bytes();assert len(raw)==64*cols*(17408+12)*4*4
  if reference is None:reference=raw
  else:assert raw==reference,'Production operator bytes differ'
  fused=[int(v)for v in re.findall(r'NATIVE_GLUQ_FUSED (\d+)',text)];assert 'NQ_PLAN_EXACT'in text
  if mask&4:
   assert fused and all(n==64 for n in fused),fused
   stats={k:int(v)for k,v in re.findall(r'^ggml_vulkan:   ([A-Za-z -]+): (\d+)',text,re.M)};assert stats['VGPRs']==24 and stats['LDS size']==0 and stats['Scratch size']==0,stats
  else:assert not fused
  row.pop('actual_dispatch_counts');row.update(fused_graphs=len(fused),fused_calls=sum(fused),coalesced_barriers=text.count('NQ_COALESCE '),planner_comparisons=text.count('NQ_PLAN_EXACT '))
  row.update(all_outputs_exact=True,output_sha256=hashlib.sha256(raw).hexdigest());rows.append(row);(out/'checks.json').write_text(json.dumps(rows,indent=2)+'\n');binary.unlink();print(row,flush=True)
(out/'comparison.json').write_text(json.dumps({'all_six_operator_arms_exact':True,'fused_dispatch_calls_verified':True,'columns':[1,2],'masks':[0,4,7],'scope':'Productionaa8 .27host/core operator checks for native/fusion/allcombined operators. No model,performance or current-system qualification.'},indent=2)+'\n')
print('PRODUCTION_NATIVE_FUSION_OPERATOR_ALL_EXACT',flush=True)
