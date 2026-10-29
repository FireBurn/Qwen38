from pathlib import Path
import os,json,hashlib,subprocess
from native_observer_common import competition
b=Path(__file__).resolve().parent;p=b/'native-command-observer';driver=b/'mtp-sched-keep-7k/driver'
assert not competition(),competition()
for name,v in json.loads((driver/'manifest.json').read_text())['libraries'].items():assert hashlib.sha256((driver/name).read_bytes()).hexdigest()==v['sha256']
e={k:v for k,v in os.environ.items()if not k.startswith(('GGML_','ACO_','RADV_'))};e.update(VK_DRIVER_FILES=str(driver/'icd.json'),VK_ICD_FILENAMES=str(driver/'icd.json'),LD_LIBRARY_PATH=str(b/'mtp-head-bound-audit/driver-deps')+':'+str(driver),EXPECTED_RADV_LIBRARY_PATH=str(driver/'libvulkan_radeon.so'),radv_buffer_meta_path='2',radv_enable_transfer_queue='false')
r=subprocess.run([str(p/'capabilities')],env=e,text=True,capture_output=True,timeout=30);(p/'capabilities-run.log').write_text(r.stderr);assert r.returncode==0,(r.returncode,r.stderr)
a=json.loads(r.stdout);a['assets']={str(f):hashlib.sha256(f.read_bytes()).hexdigest()for f in [Path(__file__),p/'capabilities.cpp',p/'capabilities',driver/'libvulkan_radeon.so']};a['scope']='Read-only physical-device feature query,instance only,no VkDevice or GPU commands; pinned private driver. Extension availability isnot a performance or compatibility proof.';(p/'capabilities.json').write_text(json.dumps(a,indent=2)+'\n');print(json.dumps({k:v for k,v in a.items()if k!='assets'},indent=2))
