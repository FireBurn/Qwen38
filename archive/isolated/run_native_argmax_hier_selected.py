from pathlib import Path
import hashlib,json,os,re,struct,subprocess,time
from native_observer_common import competition
b=Path(__file__).resolve().parent;q=b/'native-argmax-hierarchical';stock=b/'production-baseline-aa8';driver=b/'mtp-sched-keep-7k/driver';host=q/'host-safe-bounds';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert not competition(),competition();probe=q/'boundary-probe';assert sha(probe)==json.loads((q/'boundary-probe-build.json').read_text())['binary_sha256'];assert sha(host/'bin/libggml-vulkan.so.0.27.0')==json.loads((host/'build.json').read_text())['library_sha256']
for name,v in json.loads((driver/'manifest.json').read_text())['libraries'].items():assert sha(driver/name)==v['sha256']
for v in json.loads((stock/'manifest.json').read_text())['files']:
 if v['name']=='libggml-vulkan.so.0.27.0':assert sha(stock/'bin'/v['name'])==v['sha256']
out=q/'selected-check'/time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());out.mkdir(parents=True);assets=[Path(__file__),q/'SELECTED-PLAN.md',probe,q/'boundary-probe-build.json',stock/'bin/libggml-vulkan.so.0.27.0',host/'bin/libggml-vulkan.so.0.27.0',host/'build.json',q/'partial.spv',q/'final.spv',driver/'libvulkan_radeon.so',q/'checks/20261101T185614Z/stock.bin'];(out/'assets.json').write_text(json.dumps({str(f):sha(f)for f in assets},indent=2)+'\n');reports=[]
cases=[(2047,1,0),(2048,1,6),(2049,2,2),(4095,5,9),(4096,1,13),(4097,5,0),(248320,5,3)]
for case in cases:
 reference=None
 for mode in ('stock','hier'):
  assert not competition(),competition();selected=stock if mode=='stock'else host;env={k:v for k,v in os.environ.items() if not k.startswith(('GGML_','ACO_','RADV_','LLAMA_'))};env.update(GGML_VK_VISIBLE_DEVICES='1',LD_LIBRARY_PATH=str(selected/'bin')+':'+str(stock/'bin')+':'+str(b/'mtp-head-bound-audit/driver-deps')+':'+str(driver),VK_DRIVER_FILES=str(driver/'icd.json'),VK_ICD_FILENAMES=str(driver/'icd.json'),EXPECTED_VK_BACKEND_PATH=str(selected/'bin/libggml-vulkan.so.0.27.0'),EXPECTED_RADV_LIBRARY_PATH=str(driver/'libvulkan_radeon.so'),radv_buffer_meta_path='1',radv_enable_transfer_queue='false',MESA_SHADER_CACHE_DIR=str(out/'cache'))
  if mode=='hier':env.update(GGML_VK_HIER_ARGMAX_DIR=str(q),GGML_VK_HIER_ARGMAX_AUDIT='1')
  before=set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines());cmd=[str(probe),str(out/(f'{case[0]}-{case[1]}-{case[2]}-'+mode+'.bin')),str(case[0]),str(case[1]),str(case[2])]
  try:r=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=60);log=r.stdout+r.stderr;rc=r.returncode
  except subprocess.TimeoutExpired as ex:log=str(ex);rc=None
  (out/(f'{case[0]}-{case[1]}-{case[2]}-'+mode+'.log')).write_text(log);after=subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines();bad=[l for l in after if l not in before and '0000:07:00.0' in l and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',l,re.I)];f=out/(f'{case[0]}-{case[1]}-{case[2]}-'+mode+'.bin');actual=f.read_bytes() if f.exists() else b''
  passed=rc==0 and not bad and (mode=='stock' or actual==reference) and f'CASE_BEGIN k={case[0]} rows={case[1]} pattern={case[2]}' in log and f'CASE_PASS k={case[0]} rows={case[1]} pattern={case[2]}' in log and all('MAPPING_OK '+env[x] in log for x in ('EXPECTED_VK_BACKEND_PATH','EXPECTED_RADV_LIBRARY_PATH')) and (mode!='hier' or (('HIER_ARGMAX_DISPATCH ' in log)==(case[0]>=2048)))
  if mode=='stock' and rc==0 and not bad:reference=actual
  row={'case':case,'mode':mode,'passed':passed,'returncode':rc,'new_gpu_errors':bad,'exact_reference':actual==reference};reports.append(row);(out/'results.json').write_text(json.dumps(reports,indent=2)+'\n');print(json.dumps(row),flush=True);assert passed,'Bounded check failed; hold remains active'
(out/'comparison.json').write_text(json.dumps({'all_pass':True,'scope':'Seven selected stock/hardened-hier operator cases only; no model or performance proof.'},indent=2)+'\n')
