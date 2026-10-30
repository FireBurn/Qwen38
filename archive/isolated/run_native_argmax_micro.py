from pathlib import Path
import os,json,hashlib,subprocess,re,time
from native_observer_common import competition
b=Path(__file__).resolve().parent;p=b/'native-argmax-review';stock=b/'production-baseline-aa8';driver=b/'mtp-sched-keep-7k/driver';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert not competition(),competition()
assert sha(p/'native-argmax-bench')==json.loads((p/'build.json').read_text())['binary_sha256']
for name,r in json.loads((driver/'manifest.json').read_text())['libraries'].items():assert sha(driver/name)==r['sha256']
for r in json.loads((stock/'manifest.json').read_text())['files']:
 if r['name'].startswith('lib'):assert sha(stock/'bin'/r['name'])==r['sha256']
out=p/'native-micro'/time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());out.mkdir(parents=True)
env={k:v for k,v in os.environ.items()if not k.startswith(('GGML_','ACO_','RADV_','LLAMA_'))};env.update(GGML_VK_VISIBLE_DEVICES='1',LD_LIBRARY_PATH=str(stock/'bin')+':'+str(b/'mtp-head-bound-audit/driver-deps')+':'+str(driver),VK_DRIVER_FILES=str(driver/'icd.json'),VK_ICD_FILENAMES=str(driver/'icd.json'),EXPECTED_VK_BACKEND_PATH=str(stock/'bin/libggml-vulkan.so.0.27.0'),EXPECTED_RADV_LIBRARY_PATH=str(driver/'libvulkan_radeon.so'),radv_buffer_meta_path='2',radv_enable_transfer_queue='false',MESA_SHADER_CACHE_DIR=str(p/'native-micro-cache'))
assets=[Path(__file__),p/'PLAN.md',p/'build.json',p/'native-argmax-bench.cpp',p/'native-argmax-bench',stock/'manifest.json',driver/'libvulkan_radeon.so'];(out/'assets.json').write_text(json.dumps({str(f):sha(f)for f in assets},indent=2)+'\n');rows=[]
for i,(k,copies,gather)in enumerate([(1,1,0),(248320,1,0),(248320,1,1),(1,16,0),(248320,16,0),(248320,16,1)]):
 assert not competition(),competition();before=set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines());cmd=[str(p/'native-argmax-bench'),str(k),str(copies),'60',str(gather)];r=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=120);(out/f'{i:02d}.log').write_text(r.stdout+r.stderr);bad=[l for l in subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines()if l not in before and '0000:07:00.0'in l and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',l,re.I)];assert r.returncode==0 and not bad,(r.returncode,bad,out)
 m=re.search(r'NATIVE_ARGMAX_BENCH (.+)',r.stdout);assert m;row={key:float(value)for key,value in re.findall(r'(\w+)=([0-9.]+)',m[1])};row.update(new_gpu_errors=bad,scope='Nativeexistingoperator synchronouswalltime underbackgroundload, warmed16graphs; no customshader, statisticalspeedcomparison or modelgainclaim.');rows.append(row);(out/'results.json').write_text(json.dumps(rows,indent=2)+'\n');print(row,flush=True)
print('NATIVE_ARGMAX_MICRO_COMPLETE',out,flush=True)
