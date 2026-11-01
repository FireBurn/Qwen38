from pathlib import Path
import hashlib,json,os,re,struct,subprocess,time
from native_observer_common import competition
b=Path(__file__).resolve().parent;q=b/'native-argmax-hierarchical';p=b/'native-argmax-review';stock=b/'production-baseline-aa8';driver=b/'mtp-sched-keep-7k/driver'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
probe=q/'boundary-probe';assert sha(probe)==json.loads((q/'boundary-probe-build.json').read_text())['binary_sha256']
for x in json.loads((stock/'manifest.json').read_text())['files']:
 if x['name']=='libggml-vulkan.so.0.27.0':assert sha(stock/'bin'/x['name'])==x['sha256']
for name,v in json.loads((driver/'manifest.json').read_text())['libraries'].items():assert sha(driver/name)==v['sha256']
assert not competition(),competition()
raw=(q/'checks/20261101T185614Z/stock.bin').read_bytes();off=0;reference=None
while off<len(raw):
 header=struct.unpack_from('<4I',raw,off);magic,k,rows,pattern=header;size=16+4*rows;data=raw[off:off+size];assert magic==0x4152474d and len(data)==size
 if (k,rows,pattern)==(1025,1,0):reference=data
 off+=size
assert reference is not None
out=q/'health-check'/time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());out.mkdir(parents=True)
assets=[Path(__file__),q/'HEALTH-PLAN.md',probe,q/'boundary-probe-build.json',stock/'bin/libggml-vulkan.so.0.27.0',driver/'libvulkan_radeon.so',q/'checks/20261101T185614Z/stock.bin'];(out/'assets.json').write_text(json.dumps({str(f):sha(f)for f in assets},indent=2)+'\n')
env={k:v for k,v in os.environ.items() if not k.startswith(('GGML_','ACO_','RADV_','LLAMA_'))};env.update(GGML_VK_VISIBLE_DEVICES='1',LD_LIBRARY_PATH=str(stock/'bin')+':'+str(b/'mtp-head-bound-audit/driver-deps')+':'+str(driver),VK_DRIVER_FILES=str(driver/'icd.json'),VK_ICD_FILENAMES=str(driver/'icd.json'),EXPECTED_VK_BACKEND_PATH=str(stock/'bin/libggml-vulkan.so.0.27.0'),EXPECTED_RADV_LIBRARY_PATH=str(driver/'libvulkan_radeon.so'),radv_buffer_meta_path='1',radv_enable_transfer_queue='false',MESA_SHADER_CACHE_DIR=str(out/'cache'))
before=set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines());cmd=[str(probe),str(out/'stock.bin'),'1025','1','0']
try:r=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=60);log=r.stdout+r.stderr;rc=r.returncode
except subprocess.TimeoutExpired as ex:log=str(ex);rc=None
(out/'stock.log').write_text(log);after=subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines();bad=[l for l in after if l not in before and '0000:07:00.0' in l and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',l,re.I)];actual=(out/'stock.bin').read_bytes() if (out/'stock.bin').exists() else b''
passed=rc==0 and not bad and actual==reference and 'CASE_BEGIN k=1025 rows=1 pattern=0' in log and 'CASE_PASS k=1025 rows=1 pattern=0' in log and all('MAPPING_OK '+env[x] in log for x in ('EXPECTED_VK_BACKEND_PATH','EXPECTED_RADV_LIBRARY_PATH'))
report={'passed':passed,'returncode':rc,'new_gpu_errors':bad,'case':{'k':1025,'rows':1,'pattern':0},'exact_reference':actual==reference,'copy_dwords':1,'scope':'Single stock operator case only; not GPU stability, model correctness, fault cause or performance proof.'};(out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True);assert passed,'Health check failed; hold remains in place'
