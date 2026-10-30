from pathlib import Path
import os,json,hashlib,subprocess,re,time
from native_observer_common import competition
b=Path(__file__).resolve().parent;p=b/'native-argmax-review';stock=b/'production-baseline-aa8';driver=b/'mtp-sched-keep-7k/driver';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert not competition(),competition();assert sha(p/'argmax-check')==json.loads((p/'check-build.json').read_text())['binary_sha256'];wide=json.loads((b/'native-pad-wide/build.json').read_text());assert sha(b/'native-pad-wide/host/bin/libggml-vulkan.so.0.27.0')==wide['library_sha256']and sha(p/'argmax-wide.spv')==wide['shader_sha256']
for name,r in json.loads((driver/'manifest.json').read_text())['libraries'].items():assert sha(driver/name)==r['sha256']
out=b/'native-pad-wide/operators'/time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());out.mkdir(parents=True);assets=[b/'native-pad-wide/PLAN.md',Path(__file__),p/'PLAN.md',b/'native-pad-wide/build.json',p/'argmax-wide.comp',p/'argmax-wide.spv',p/'check-build.json',p/'argmax-check.cpp',p/'argmax-check',b/'native-pad-wide/host/bin/libggml-vulkan.so.0.27.0',stock/'bin/libggml-vulkan.so.0.27.0',driver/'libvulkan_radeon.so'];(out/'assets.json').write_text(json.dumps({str(f):sha(f)for f in assets},indent=2)+'\n');rows=[]
for mode in ['stock','private_off','private_wide']:
 assert not competition(),competition();host=stock if mode=='stock'else b/'native-pad-wide/host';env={k:v for k,v in os.environ.items()if not k.startswith(('GGML_','ACO_','RADV_','LLAMA_'))};env.update(GGML_VK_VISIBLE_DEVICES='1',LD_LIBRARY_PATH=str(host/'bin')+':'+str(stock/'bin')+':'+str(b/'mtp-head-bound-audit/driver-deps')+':'+str(driver),VK_DRIVER_FILES=str(driver/'icd.json'),VK_ICD_FILENAMES=str(driver/'icd.json'),EXPECTED_VK_BACKEND_PATH=str(host/'bin/libggml-vulkan.so.0.27.0'),EXPECTED_RADV_LIBRARY_PATH=str(driver/'libvulkan_radeon.so'),radv_buffer_meta_path='2',radv_enable_transfer_queue='false',MESA_SHADER_CACHE_DIR=str(p/'wide-check-cache'),GGML_VK_ARGMAX_WIDE_AUDIT='1')
 if mode=='private_wide':env['GGML_VK_ARGMAX_WIDE_SHADER']=str(p/'argmax-wide.spv')
 before=set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines());binary=out/(mode+'.bin');r=subprocess.run([str(p/'argmax-check'),str(binary)],env=env,capture_output=True,text=True,timeout=240);text=r.stdout+r.stderr;(out/(mode+'.log')).write_text(text);bad=[l for l in subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines()if l not in before and '0000:07:00.0'in l and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',l,re.I)];assert r.returncode==0 and not bad,(mode,r.returncode,bad,out)
 assert 'cases=630 rows=1680'in text
 if mode=='private_wide':assert re.search(r'ARGMAX_WIDE_SELECT native_block=(32|64) enabled=1',text)
 if mode=='private_off':assert 'enabled=1'not in text
 row=dict(mode=mode,cases=630,rows=1680,indices_sha256=sha(binary),new_gpu_errors=bad)
 if rows:assert row['indices_sha256']==rows[0]['indices_sha256'],'Native indices differ'
 rows.append(row);(out/'results.json').write_text(json.dumps(rows,indent=2)+'\n');print(row,flush=True)
(out/'comparison.json').write_text(json.dumps(dict(all_stock_indices_identical=True,cases_per_mode=630,rows_per_mode=1680,scope='Finite/ties/NaN/infinity/signedzero/subnormal/multirow/dimensionboundary indices, wideactiveandprivateoffcontrols. No model or performance qualification.'),indent=2)+'\n');print('WIDE_ARGMAX_ALL_INDICES_EXACT',out,flush=True)
