from pathlib import Path
import os,json,subprocess,hashlib,re,signal,time,threading,datetime
base=Path(__file__).resolve().parent;p=base/'q6-pad212';out=p/'timing-runs'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');out.mkdir(parents=True);driver=base/'mtp-sched-keep-7k/driver'
for name,r in json.loads((driver/'manifest.json').read_text())['libraries'].items():assert hashlib.sha256((driver/name).read_bytes()).hexdigest()==r['sha256']
build=json.loads((p/'timing-build.json').read_text());assert hashlib.sha256((p/'operator_bench_timed').read_bytes()).hexdigest()==build['binary_sha256']
assets=[Path(__file__),p/'timing.cpp',p/'operator_bench_timed',*[p/(name+'_subgroup_no_shmem.spv')for name in ['native','pad16','pad32']],driver/'libvulkan_radeon.so'];(out/'assets.json').write_text(json.dumps({str(f):hashlib.sha256(f.read_bytes()).hexdigest()for f in assets},indent=2)+'\n')
env={k:v for k,v in os.environ.items()if not k.startswith(('GGML_','ACO_','RADV_'))};env.update(VK_DRIVER_FILES=str(driver/'icd.json'),VK_ICD_FILENAMES=str(driver/'icd.json'),LD_LIBRARY_PATH=str(base/'mtp-head-bound-audit/driver-deps')+':'+str(driver),EXPECTED_RADV_LIBRARY_PATH=str(driver/'libvulkan_radeon.so'),MESA_SHADER_CACHE_DIR=str(out/'cache'),radv_enable_transfer_queue='false',radv_buffer_meta_path='2')
assert json.loads((p/'diagnostics/checks.json').read_text())['exact_dispatch_cases']==1080
stop=threading.Event()
def monitor():
 previous=None
 with (out/'telemetry.jsonl').open('w')as f:
  while not stop.is_set():
   rec={'time':time.time(),'monotonic':time.monotonic(),'loadavg':os.getloadavg()}
   try:
    lp=out/'probe.log'
    if lp.exists():
     tail=lp.read_text(errors='replace')[-8192:];markers=list(re.finditer(r'^(ARM_BEGIN|TIMING) (.+)$',tail,re.M))
     if markers and markers[-1][1]=='ARM_BEGIN':rec['arm']={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',markers[-1][2])}
    fields=list(map(int,Path('/proc/stat').read_text().splitlines()[0].split()[1:]));total=sum(fields[:8]);idle=fields[3]+fields[4]
    if previous and total>previous[0]:rec['cpu_busy_fraction']=1-(idle-previous[1])/(total-previous[0])
    previous=(total,idle)
    hw=next(Path('/sys/bus/pci/devices/0000:07:00.0/hwmon').glob('hwmon*'))
    for name in ['freq1_input','freq2_input','temp1_input','power1_average']:rec[name]=(hw/name).read_text().strip()
    for name in ['gpu_busy_percent','mem_busy_percent','mem_info_vram_used']:rec[name]=(Path('/sys/bus/pci/devices/0000:07:00.0')/name).read_text().strip()
   except Exception as exc:rec['sensor_error']=str(exc)
   f.write(json.dumps(rec)+'\n');f.flush();stop.wait(.05)
thread=threading.Thread(target=monitor);thread.start()
before=set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines());log=out/'probe.log'
with log.open('w')as f:
 child=subprocess.Popen([str(p/'operator_bench_timed'),str(p),'64'],env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);print('Q6_PAD212_CHILD',child.pid,flush=True)
 failure=None
 try:child.wait(timeout=900)
 except Exception as exc:failure={"type":type(exc).__name__,"message":str(exc)}
 finally:
  if child.poll()is None:os.killpg(child.pid,signal.SIGTERM);child.wait(timeout=10)
stop.set();thread.join()
bad=[l for l in subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines()if l not in before and '0000:07:00.0'in l and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',l,re.I)]
text=log.read_text()
rows=[{k:(float(v)if k=='us'else int(v))for k,v in re.findall(r'(\w+)=(\S+)',line)}for line in text.splitlines()if line.startswith('TIMING ')]
report={'pid':child.pid,'returncode':child.returncode,'harness_failure':failure,'validated_shapes':text.count('VALIDATED '),'timing_arms':rows,'new_driver_errors':bad,'complete':'Q6_PAD212_TIMING_COMPLETE'in text,'scope':'Synthetic Q6 float operator GPU timestamps, native rm_kq2, fixed 3 ABC-CBA rotated blocks each, native/pad16/pad32, cached and 16-replica streamed weights. Under CPU/build load; no full model speed claim.'}
(out/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
assert child.returncode==0 and len(rows)==144 and report['validated_shapes']==8 and report['complete']and not bad and failure is None,report
print('Q6_PAD212_TIMING_144_ARMS_COMPLETE',out,flush=True)
