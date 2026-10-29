from pathlib import Path
import os,json,hashlib,subprocess,signal,re,time,gzip,shutil,struct
from native_observer_common import competition
base=Path(__file__).resolve().parent;p=base/'q3-pair-glu';out=p/'host-boundary128';out.mkdir();host=p/'host';stock=base/'production-baseline-aa8';driver=base/'mtp-sched-keep-7k/driver'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
for name,r in json.loads((driver/'manifest.json').read_text())['libraries'].items():assert sha(driver/name)==r['sha256']
assert sha(base/'production-native-shaders/model-audit-runner')==json.loads((base/'production-native-shaders/model-audit-build.json').read_text())['binary_sha256']
assets=[p/'host-build.json',p/'pair_subgroup_no_shmem.spv',base/'q3-pad112/qualified-20261029/bin/libggml-vulkan.so.0.27.0',stock/'bin/libggml-vulkan.so.0.27.0',Path(__file__),base/'production-native-shaders/model-audit-runner',base/'production-native-shaders/model-audit-runner.cpp',host/'bin/libggml-vulkan.so.0.27.0',stock/'bin/libllama.so.0.7.0',stock/'bin/libllama-common.so.0.7.0',driver/'libvulkan_radeon.so',base/'native-swiglu-q8/shuffle8/fused.comp.spv',base/'native-quant-shuffle/shuffle.spv',*[base/'q3-native-correction'/('candidate-mul_mat_vec_q3_k_q8_1_f32'+suffix+'.spv')for suffix in ['','_subgroup','_subgroup_no_shmem']]]
(out/'assets.json').write_text(json.dumps({str(f):sha(f)for f in assets},indent=2)+'\n')
env={k:v for k,v in os.environ.items()if not k.startswith(('GGML_','ACO_','RADV_'))};env.update(GGML_VK_VISIBLE_DEVICES='1',GGML_VK_ALLOW_GRAPHICS_QUEUE='1',GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM='1',GGML_VK_SUBALLOCATION_BLOCK_SIZE='4294967296',LD_LIBRARY_PATH=str(host/'bin')+':'+str(stock/'bin')+':'+str(base/'mtp-head-bound-audit/driver-deps')+':'+str(driver),VK_DRIVER_FILES=str(driver/'icd.json'),VK_ICD_FILENAMES=str(driver/'icd.json'),EXPECTED_VK_BACKEND_PATH=str(host/'bin/libggml-vulkan.so.0.27.0'),EXPECTED_RADV_LIBRARY_PATH=str(driver/'libvulkan_radeon.so'),EXPECTED_LLAMA_CORE_PATH=str(stock/'bin/libllama.so.0.7.0'),radv_buffer_meta_path='2',radv_enable_transfer_queue='false')
model='${CLAUDE_WORKSPACE}/eval/models/nerkyor/GGUF/Qwen3.8-27B-Coder390-EfficientThink-Q3LynnStyle-MTP.gguf';prompt='The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. \nWrite a detailed explanation with several examples of how GPU matrix multiplication and attention work together. Start by describing a memory access:';rows=[]
for mode,cap,reader_mode in [('stock400',400,0),('inactive400',400,0),('active400',400,1)]:
 mask=0 if mode=='stock400'else 8
 assert not competition(),competition();label=mode;trial=env.copy();selected_host=stock if mode=='stock400'else base/'q3-pad112/qualified-20261029' if mode=='frozen400'else host;trial.update(LD_LIBRARY_PATH=str(selected_host/'bin')+':'+str(stock/'bin')+':'+str(base/'mtp-head-bound-audit/driver-deps')+':'+str(driver),EXPECTED_VK_BACKEND_PATH=str(selected_host/'bin/libggml-vulkan.so.0.27.0'),EXPECTED_LLAMA_COMMON_PATH=str(stock/'bin/libllama-common.so.0.7.0'));trial['GGML_VK_MAX_NODES_PER_SUBMIT']=str(cap);binary=out/(label+'.bin');trial.update(GGML_VK_NATIVE_GLUQ_AUDIT='1',GGML_VK_NATIVE_GLUQ_CHECK_PLAN='1',PRODUCTION_TARGET_AUDIT_OUT=str(binary),MESA_SHADER_CACHE_DIR=str(out/('cache-'+label)))
 trial['GGML_VK_PAIR_GLU_AUDIT']='1'
 if reader_mode:trial['GGML_VK_PAIR_GLU_SHADER']=str(p/'pair_subgroup_no_shmem.spv')
 if mask==8:trial.update(GGML_VK_Q3_PAD112_ARENA='1',GGML_VK_Q3_PAD112_DIR=str(base/'q3-pad112/qualified-20261029/shaders'),GGML_VK_Q3_PAD112_IMMUTABLE='1',GGML_VK_Q3_PAD112_AUDIT='1')
 if mask&1:trial.update(GGML_VK_NATIVE_Q8_SHUFFLE='1',GGML_VK_NATIVE_Q8_SHADER=str(base/'native-quant-shuffle/shuffle.spv'))
 if mask&2:trial['GGML_VK_NATIVE_Q3_CORRECTION_DIR']=str(base/'q3-native-correction')
 if mask&4:trial.update(GGML_VK_NATIVE_GLUQ_FUSE='1',GGML_VK_NATIVE_GLUQ_SHADER=str(base/'native-swiglu-q8/shuffle8/fused.comp.spv'),GGML_VK_NATIVE_GLUQ_GROUPS='16',GGML_VK_NATIVE_GLUQ_EXPAND_VIEWS='1',GGML_VK_NATIVE_GLUQ_COALESCE='1')
 cmd=[str(base/'production-native-shaders/model-audit-runner'),'-m',model,'--spec-type','draft-mtp','--spec-draft-n-max','1','--spec-draft-n-min','1','--spec-draft-p-min','0','--spec-draft-backend-sampling','--spec-draft-ngl','99','-ngl','99','-c','4096','-b','512','-ub','512','-fa','on','-ctk','q8_0','-ctv','q8_0','-ctkd','q8_0','-ctvd','q8_0','-t','1','-tb','1','-td','1','-tbd','1','--temp','0','--seed','1','-n','128','-p',prompt]
 before=set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines());log=out/(label+'.log')
 with log.open('w')as f:
  child=subprocess.Popen(cmd,env=trial,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);started=time.monotonic();print('PRODUCTION_MODEL_CHILD',label,child.pid,flush=True)
  try:
   while child.poll()is None:
    if competition(child.pid)or time.monotonic()-started>600:raise RuntimeError('Competition or timeout')
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
 fused=sum(int(v)for v in re.findall(r'NATIVE_GLUQ_FUSED (\d+)',text));assert 'NQ_PLAN_EXACT'in text if mode!='stock400'else True
 assert fused>100 if mask&4 else fused==0
 if mask==8:assert 'Q3_PAD112_CACHE 'in text and re.search(r'Q3_PAD112_FINAL entries=[1-9]\d* bytes=\d+ calls=[1-9]\d*',text),'Padded path unused'
 tokens=[int(x)for x in re.findall(r'ACCEPTED_TOKEN (\d+)',text)];assert len(tokens)>=128
 fields={k:int(re.findall(r'\b'+k+r'\s*=\s*(\d+)',text)[-1])for k in ['n_drafted','n_accept','n_predict']}
 audit_rows=0;batches=0;positions=[]
 with binary.open('rb')as f:
  while raw:=f.read(16):
   assert len(raw)==16;magic,nt,nrows,nvocab=struct.unpack('<4I',raw);assert magic==0x51333841 and nt>0 and nrows<=nt and nvocab>100000
   for i in range(nrows):
    info=f.read(12);assert len(info)==12;idx,token,pos=struct.unpack('<3i',info);positions.append(pos);assert 0<=idx<nt and 0<=token<nvocab and pos>=0
    values=f.read(nvocab*4);assert len(values)==nvocab*4
   audit_rows+=nrows;batches+=1
 assert positions and 128<=min(positions)<=220 and 256<max(positions)<4096
 assert audit_rows>=128 and audit_rows==sum(int(x)for x in re.findall(r'TARGET_LOGIT_AUDIT batch_tokens=\d+ rows=(\d+)',text))
 oracle=[{k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',line)}for line in re.findall(r'^Q3_PAIR_GLU_VERIFY (.+)$',text,re.M)]
 if reader_mode==2:assert sum(v['checks']for v in oracle)>1000 and sum(v['fused']for v in oracle)>0 and not any(v['mismatches']for v in oracle)and 'Q3_PAIR_GLU_MISMATCH'not in text
 else:assert not oracle
 pair_calls=len(re.findall(r'^PAIR_GLU_DISPATCH ',text,re.M))
 assert pair_calls>100 if reader_mode else pair_calls==0
 row=dict(mode=mode,pair_calls=pair_calls,pair_mode=reader_mode,oracle_checks=sum(v['checks']for v in oracle),oracle_mismatches=sum(v['mismatches']for v in oracle),verified_fused_decisions=sum(v['fused']for v in oracle),prefix_min_audit_position=min(positions),max_audit_position=max(positions),cap=cap,mask=mask,pid=child.pid,fused_calls=fused,coalesced_barriers=text.count("NQ_COALESCE "),planner_comparisons=text.count("NQ_PLAN_EXACT "),**fields,tokens=tokens,target_logit_audit_sha256=sha(binary),audit_bytes=binary.stat().st_size,target_logit_rows=audit_rows,audit_batches=batches,new_driver_errors=bad,scope='Productionaa8 .27/.7MTP stockactivationpolicy;every requested targetlogit row from runnerprocesscalls,tokens/counters. No targethidden/draftscorecapture or performance qualification.')
 if rows:assert all(row[k]==rows[0][k]for k in ['tokens','n_drafted','n_accept','n_predict','target_logit_audit_sha256','audit_bytes','target_logit_rows','audit_batches']),'Production model differs'
 rows.append(row);(out/'checks.json').write_text(json.dumps(rows,indent=2)+'\n');print({k:v for k,v in row.items()if k!='tokens'},flush=True)
archive=out/'canonical-target-logits.bin.gz'
with(out/'stock400.bin').open('rb')as f,gzip.GzipFile(filename=str(archive),mode='wb',compresslevel=1,mtime=0)as z:shutil.copyfileobj(f,z,4*1024*1024)
with gzip.open(archive,'rb')as f:assert hashlib.file_digest(f,'sha256').hexdigest()==rows[0]['target_logit_audit_sha256']
(out/'comparison.json').write_text(json.dumps({'all_requested_target_logit_bits_identical':True,'all_tokens_and_counters_identical':True,'padded_cache_dispatch_verified':True,'matches_fresh_unmodified_stock_target_logits':True,'arms':3,'requested_tokens':128,'target_logit_rows_per_arm':rows[0]['target_logit_rows'],'target_logit_audit_sha256':rows[0]['target_logit_audit_sha256'],'minimum_target_audit_position':min(r['prefix_min_audit_position']for r in rows),'maximum_target_audit_position':max(r['max_audit_position']for r in rows),'scope':'Freshstock400 versusboundedQ3pairGLU inactive/active comparisons across audit positions straddling256,4kctx,128requestedtokens. Allrequested targetlogits/tokens/counters;not every internal drafttensor,allcontexts or performance qualification.'},indent=2)+'\n')
(out/'audit-archive.json').write_text(json.dumps({'archive':archive.name,'uncompressed_sha256':rows[0]['target_logit_audit_sha256'],'identical_originals':[n+'.bin'for n in ['stock400','inactive400','active400']]},indent=2)+'\n')
for mode in ['stock400','inactive400','active400']:(out/(mode+'.bin')).unlink()
print('NATIVE_COMMAND_BOUNDARY128_ALL_TARGET_BITS_EXACT',flush=True)
