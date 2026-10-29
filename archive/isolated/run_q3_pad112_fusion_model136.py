from pathlib import Path
import os,json,hashlib,subprocess,signal,re,time,gzip,shutil,struct
from mixed_matrix_stream_settled3_common import competition
base=Path(__file__).resolve().parent;p=base/'q3-pad112';out=p/'fusion-options-model136';out.mkdir();host=p/'host-fusion-options';stock=base/'production-baseline-aa8';driver=base/'mtp-sched-keep-7k/driver'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
for name,r in json.loads((driver/'manifest.json').read_text())['libraries'].items():assert sha(driver/name)==r['sha256']
assert sha(base/'production-native-shaders/model-audit-runner')==json.loads((base/'production-native-shaders/model-audit-build.json').read_text())['binary_sha256']
assets=[Path(__file__),base/'production-native-shaders/model-audit-runner',base/'production-native-shaders/model-audit-runner.cpp',host/'bin/libggml-vulkan.so.0.27.0',stock/'bin/libllama.so.0.7.0',stock/'bin/libllama-common.so.0.7.0',driver/'libvulkan_radeon.so',base/'native-swiglu-q8/shuffle8/fused.comp.spv',base/'native-quant-shuffle/shuffle.spv',*[base/'q3-native-correction'/('candidate-mul_mat_vec_q3_k_q8_1_f32'+suffix+'.spv')for suffix in ['','_subgroup','_subgroup_no_shmem']]]
(out/'assets.json').write_text(json.dumps({str(f):sha(f)for f in assets},indent=2)+'\n')
env={k:v for k,v in os.environ.items()if not k.startswith(('GGML_','ACO_','RADV_'))};env.update(GGML_VK_VISIBLE_DEVICES='1',GGML_VK_ALLOW_GRAPHICS_QUEUE='1',GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM='1',GGML_VK_SUBALLOCATION_BLOCK_SIZE='4294967296',LD_LIBRARY_PATH=str(host/'bin')+':'+str(stock/'bin')+':'+str(base/'mtp-head-bound-audit/driver-deps')+':'+str(driver),VK_DRIVER_FILES=str(driver/'icd.json'),VK_ICD_FILENAMES=str(driver/'icd.json'),EXPECTED_VK_BACKEND_PATH=str(host/'bin/libggml-vulkan.so.0.27.0'),EXPECTED_RADV_LIBRARY_PATH=str(driver/'libvulkan_radeon.so'),EXPECTED_LLAMA_CORE_PATH=str(stock/'bin/libllama.so.0.7.0'),radv_buffer_meta_path='2',radv_enable_transfer_queue='false')
model='${CLAUDE_WORKSPACE}/eval/models/nerkyor/GGUF/Qwen3.8-27B-Coder390-EfficientThink-Q3LynnStyle-MTP.gguf';prompt='The history of the Roman Empire begins with the rise of Augustus. After the death of Julius Caesar, a power struggle erupted among his heirs and generals. In this essay we will examine';rows=[]
for mask in [0,8,12,13]:
 assert not competition(),competition();label='mask'+str(mask);trial=env.copy();binary=out/(label+'.bin');trial.update(GGML_VK_NATIVE_GLUQ_AUDIT='1',GGML_VK_NATIVE_GLUQ_CHECK_PLAN='1',PRODUCTION_TARGET_AUDIT_OUT=str(binary),MESA_SHADER_CACHE_DIR=str(out/('cache-'+label)))
 if mask&8:trial.update(GGML_VK_Q3_PAD112_ARENA='1',GGML_VK_Q3_PAD112_DIR=str(p),GGML_VK_Q3_PAD112_IMMUTABLE='1',GGML_VK_Q3_PAD112_AUDIT='1')
 if mask&1:trial.update(GGML_VK_NATIVE_Q8_SHUFFLE='1',GGML_VK_NATIVE_Q8_SHADER=str(base/'native-quant-shuffle/shuffle.spv'))
 if mask&2:trial['GGML_VK_NATIVE_Q3_CORRECTION_DIR']=str(base/'q3-native-correction')
 if mask&4:trial.update(GGML_VK_NATIVE_GLUQ_FUSE='1',GGML_VK_NATIVE_GLUQ_SHADER=str(base/'native-swiglu-q8/shuffle8/fused.comp.spv'),GGML_VK_NATIVE_GLUQ_GROUPS='136',GGML_VK_NATIVE_GLUQ_EXPAND_VIEWS='1',GGML_VK_NATIVE_GLUQ_COALESCE='1')
 cmd=[str(base/'production-native-shaders/model-audit-runner'),'-m',model,'--spec-type','draft-mtp','--spec-draft-n-max','1','--spec-draft-n-min','1','--spec-draft-p-min','0','--spec-draft-backend-sampling','--spec-draft-ngl','99','-ngl','99','-c','4096','-b','512','-ub','512','-fa','on','-ctk','q8_0','-ctv','q8_0','-ctkd','q8_0','-ctvd','q8_0','-t','1','-tb','1','-td','1','-tbd','1','--temp','0','--seed','1','-n','32','-p',prompt]
 before=set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines());log=out/(label+'.log')
 with log.open('w')as f:
  child=subprocess.Popen(cmd,env=trial,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);started=time.monotonic();print('PRODUCTION_MODEL_CHILD',label,child.pid,flush=True)
  try:
   while child.poll()is None:
    if competition()or time.monotonic()-started>600:raise RuntimeError('Competition or timeout')
    time.sleep(.1)
  finally:
   if child.poll()is None:os.killpg(child.pid,signal.SIGTERM);child.wait(timeout=10)
 bad=[l for l in subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines()if l not in before and '0000:07:00.0'in l and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',l,re.I)]
 text=log.read_text();assert child.returncode==0 and not bad,(child.returncode,bad,log)
 for marker,key in [('BACKEND_PATH_OK','EXPECTED_VK_BACKEND_PATH'),('DRIVER_PATH_OK','EXPECTED_RADV_LIBRARY_PATH'),('CORE_PATH_OK','EXPECTED_LLAMA_CORE_PATH')]:assert marker+' '+trial[key]in text
 counts={k:0 for k in ['quant_new','quant_old','q3_new','q3_old']}
 for line in re.findall(r'^NATIVE_SHADER_DISPATCH_COUNTS (.+)$',text,re.M):
  for k,v in re.findall(r'(\w+)=(\d+)',line):counts[k]+=int(v)
 assert not any(counts.values())
 fused=sum(int(v)for v in re.findall(r'NATIVE_GLUQ_FUSED (\d+)',text));assert 'NQ_PLAN_EXACT'in text
 assert fused>100 if mask&4 else fused==0
 if mask&8:assert 'Q3_PAD112_CACHE 'in text and re.search(r'Q3_PAD112_FINAL entries=[1-9]\d* bytes=\d+ calls=[1-9]\d*',text),'Padded path unused'
 tokens=[int(x)for x in re.findall(r'ACCEPTED_TOKEN (\d+)',text)];assert len(tokens)>=32
 fields={k:int(re.findall(r'\b'+k+r'\s*=\s*(\d+)',text)[-1])for k in ['n_drafted','n_accept','n_predict']}
 audit_rows=0;batches=0
 with binary.open('rb')as f:
  while raw:=f.read(16):
   assert len(raw)==16;magic,nt,nrows,nvocab=struct.unpack('<4I',raw);assert magic==0x51333841 and nt>0 and nrows<=nt and nvocab>100000
   for i in range(nrows):
    info=f.read(12);assert len(info)==12;idx,token,pos=struct.unpack('<3i',info);assert 0<=idx<nt and 0<=token<nvocab and pos>=0
    values=f.read(nvocab*4);assert len(values)==nvocab*4
   audit_rows+=nrows;batches+=1
 assert audit_rows>=32 and audit_rows==sum(int(x)for x in re.findall(r'TARGET_LOGIT_AUDIT batch_tokens=\d+ rows=(\d+)',text))
 row=dict(mask=mask,pid=child.pid,fused_calls=fused,coalesced_barriers=text.count("NQ_COALESCE "),planner_comparisons=text.count("NQ_PLAN_EXACT "),**fields,tokens=tokens,target_logit_audit_sha256=sha(binary),audit_bytes=binary.stat().st_size,target_logit_rows=audit_rows,audit_batches=batches,new_driver_errors=bad,scope='Productionaa8 .27/.7MTP stockactivationpolicy;every requested targetlogit row from runnerprocesscalls,tokens/counters. No targethidden/draftscorecapture or performance qualification.')
 prior=json.loads((base/'production-native-shaders/model32/checks.json').read_text())[0]
 assert all(row[k]==prior[k]for k in ['tokens','n_drafted','n_accept','n_predict','target_logit_audit_sha256','audit_bytes','target_logit_rows','audit_batches']),'Production native reference differs'
 if rows:assert all(row[k]==rows[0][k]for k in ['tokens','n_drafted','n_accept','n_predict','target_logit_audit_sha256','audit_bytes','target_logit_rows','audit_batches']),'Production model differs'
 rows.append(row);(out/'checks.json').write_text(json.dumps(rows,indent=2)+'\n');print({k:v for k,v in row.items()if k!='tokens'},flush=True)
archive=out/'canonical-target-logits.bin.gz'
with(out/'mask0.bin').open('rb')as f,gzip.GzipFile(filename=str(archive),mode='wb',compresslevel=1,mtime=0)as z:shutil.copyfileobj(f,z,4*1024*1024)
with gzip.open(archive,'rb')as f:assert hashlib.file_digest(f,'sha256').hexdigest()==rows[0]['target_logit_audit_sha256']
(out/'comparison.json').write_text(json.dumps({'all_requested_target_logit_bits_identical':True,'all_tokens_and_counters_identical':True,'padded_cache_dispatch_verified':True,'matches_prior_unmodified_stock_target_logits':True,'arms':4,'requested_tokens':32,'target_logit_rows_per_arm':rows[0]['target_logit_rows'],'target_logit_audit_sha256':rows[0]['target_logit_audit_sha256'],'scope':'Productionaa8 .27/.7 native/paddedQ3 immutablecache,stockactivationpolicy,16fusiongroups;targetlogit rows only,not hidden/draftscore,longcontext or speed qualification.'},indent=2)+'\n')
(out/'audit-archive.json').write_text(json.dumps({'archive':archive.name,'uncompressed_sha256':rows[0]['target_logit_audit_sha256'],'identical_originals':['mask'+str(i)+'.bin'for i in [0,8,12,13]]},indent=2)+'\n')
for mask in [0,8,12,13]:(out/('mask'+str(mask)+'.bin')).unlink()
print('PRODUCTION_NATIVE_FUSION_MODEL_TARGET_LOGITS_ALL_EXACT',flush=True)
