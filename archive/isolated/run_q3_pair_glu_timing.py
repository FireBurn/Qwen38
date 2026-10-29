from pathlib import Path
import os,json,subprocess,hashlib,re,signal,time,threading
from native_observer_common import competition
from quiet_builds import build_processes
base=Path(__file__).resolve().parent;p=base/'q3-pair-glu';out=p/'timing'/time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());out.mkdir(parents=True);driver=base/'mtp-sched-keep-7k/driver'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
for folder,n in [('operators',576),('stress',128)]:
 r=json.loads((p/folder/'checks.json').read_text());assert r['exact_cases']==n and r['returncode']==0 and not r['new_driver_errors']
for name,r in json.loads((driver/'manifest.json').read_text())['libraries'].items():assert sha(driver/name)==r['sha256']
assert sha(p/'timing-bin/operator_bench_timed')==json.loads((p/'timing-build.json').read_text())['binary_sha256']
for name,value in json.loads((p/'shader-build.json').read_text())['modules'].items():assert sha(p/name)==value
assets=[Path(__file__),base/'native_observer_common.py',p/'TIMING-PLAN.md',p/'timing.cpp',p/'timing-build.json',p/'shader-build.json',p/'timing-bin/operator_bench_timed',p/'pad16_subgroup_no_shmem.spv',p/'pair_subgroup_no_shmem.spv',p/'swiglu_ref.spv',driver/'libvulkan_radeon.so'];(out/'assets.json').write_text(json.dumps({str(f):sha(f)for f in assets},indent=2)+'\n')
env={k:v for k,v in os.environ.items()if not k.startswith(('GGML_','ACO_','RADV_'))};env.update(VK_DRIVER_FILES=str(driver/'icd.json'),VK_ICD_FILENAMES=str(driver/'icd.json'),LD_LIBRARY_PATH=str(base/'mtp-head-bound-audit/driver-deps')+':'+str(driver),EXPECTED_RADV_LIBRARY_PATH=str(driver/'libvulkan_radeon.so'),MESA_SHADER_CACHE_DIR=str(out/'cache'),radv_enable_transfer_queue='false',radv_buffer_meta_path='2')
assert not competition(),competition();before=set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines());log=out/'probe.log';stop=threading.Event();pci=Path('/sys/bus/pci/devices/0000:07:00.0');hw=next((pci/'hwmon').glob('hwmon*'))
def monitor():
 previous=None;tick=0;builds=None
 with(out/'telemetry.jsonl').open('w')as f:
  while not stop.is_set():
   rec=dict(monotonic_ns=time.monotonic_ns(),time=time.time(),sensor_errors=[])
   try:
    if tick%25==0:builds=len(build_processes())
    tick+=1;rec['builds']=builds;rec['loadavg']=Path('/proc/loadavg').read_text().strip();v=list(map(int,Path('/proc/stat').read_text().splitlines()[0].split()[1:9]));total=sum(v);idle=v[3]+v[4]
    if previous:rec['cpu_busy']=1-(idle-previous[1])/max(1,total-previous[0])
    previous=(total,idle)
   except Exception as exc:rec['sensor_errors'].append(dict(sensor='cpu_build_load',error=repr(exc)))
   for name,source,scale in [('clock_mhz',hw/'freq1_input',1e6),('power_w',hw/'power1_average',1e6),('gpu_busy',pci/'gpu_busy_percent',1),('vram_bytes',pci/'mem_info_vram_used',1)]:
    try:rec[name]=int(source.read_text())/scale
    except Exception as exc:rec['sensor_errors'].append(dict(sensor=name,error=repr(exc)))
   f.write(json.dumps(rec)+'\n');f.flush();stop.wait(.02)
worker=threading.Thread(target=monitor);worker.start();child=None;failure=None
try:
 with log.open('w')as f:
  child=subprocess.Popen([str(p/'timing-bin/operator_bench_timed'),str(p),'64'],env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);print('PAIR_TIMING_CHILD',child.pid,out,flush=True);start=time.monotonic()
  try:
   while child.poll()is None:
    if competition(child.pid)or time.monotonic()-start>900:raise RuntimeError('Competition or timeout')
    time.sleep(.25)
  except Exception as exc:failure=repr(exc)
  finally:
   if child.poll()is None:os.killpg(child.pid,signal.SIGTERM);child.wait(timeout=10)
finally:stop.set();worker.join()
bad=[l for l in subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines()if l not in before and '0000:07:00.0'in l and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',l,re.I)]
text=log.read_text();rows=[{k:float(v)if k=='us'else int(v)for k,v in re.findall(r'(\w+)=(\S+)',l)}for l in text.splitlines()if l.startswith('PAIR_TIMING ')]
r=dict(pid=child.pid,returncode=child.returncode,harness_failure=failure,validated_conditions=text.count('PAIR_VALIDATED '),timing_arms=rows,new_driver_errors=bad,complete='PAIR_TIMING_COMPLETE'in text,scope='Fixed96-arm pairedoperatorGPUtimestamp screen;nativeindependentgate/upcanoverlap,thenproductionGLU;candidateonepairkernel. Same112weightbuffers.C1C2/1or8replicas,K5120/R17408,sixABBAblocks,1024repeats. Alloutputs/guards/inputs checked;telemetrydescriptive,nomodel/equalclockgainclaim.')
(out/'checks.json').write_text(json.dumps(r,indent=2)+'\n');assert child.returncode==0 and len(rows)==96 and r['validated_conditions']==4 and r['complete']and not bad and failure is None,r
assert 'DRIVER_PATH_OK '+env['EXPECTED_RADV_LIBRARY_PATH']in text;print('PAIR_96_TIMING_ARMS_EXACT',out,flush=True)
