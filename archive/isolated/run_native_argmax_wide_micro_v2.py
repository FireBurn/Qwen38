from pathlib import Path
import os,json,hashlib,subprocess,re,time,threading,statistics,math
from native_observer_common import competition
from quiet_builds import build_processes
b=Path(__file__).resolve().parent;p=b/'native-argmax-review';stock=b/'production-baseline-aa8';host=p/'wide-host';driver=b/'mtp-sched-keep-7k/driver';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
checks=list((p/'wide-checks').glob('*/comparison.json'));assert len(checks)==1 and json.loads(checks[0].read_text())['all_stock_indices_identical'];assert sha(host/'bin/libggml-vulkan.so.0.27.0')==json.loads((p/'wide-build.json').read_text())['library_sha256'];assert sha(p/'native-argmax-bench')==json.loads((p/'build.json').read_text())['binary_sha256']
out=p/'wide-micro-v2'/time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());out.mkdir(parents=True);assets=[Path(__file__),p/'WIDE-MICRO-PLAN-v2.md',p/'wide-build.json',host/'bin/libggml-vulkan.so.0.27.0',p/'native-argmax-bench',p/'build.json',p/'argmax-wide.spv',driver/'libvulkan_radeon.so'];(out/'assets.json').write_text(json.dumps({str(f):sha(f)for f in assets},indent=2)+'\n');sequence=[mode for block in range(6)for mode in (['native','wide','wide','native']if block%2==0 else['wide','native','native','wide'])];(out/'protocol.json').write_text(json.dumps(dict(sequence=sequence,plan=(p/'WIDE-MICRO-PLAN-v2.md').read_text()),indent=2)+'\n');rows=[]
env={k:v for k,v in os.environ.items()if not k.startswith(('GGML_','ACO_','RADV_','LLAMA_'))};env.update(GGML_VK_VISIBLE_DEVICES='1',LD_LIBRARY_PATH=str(host/'bin')+':'+str(stock/'bin')+':'+str(b/'mtp-head-bound-audit/driver-deps')+':'+str(driver),VK_DRIVER_FILES=str(driver/'icd.json'),VK_ICD_FILENAMES=str(driver/'icd.json'),EXPECTED_VK_BACKEND_PATH=str(host/'bin/libggml-vulkan.so.0.27.0'),EXPECTED_RADV_LIBRARY_PATH=str(driver/'libvulkan_radeon.so'),radv_buffer_meta_path='2',radv_enable_transfer_queue='false',MESA_SHADER_CACHE_DIR=str(p/'wide-check-cache'))
pci=Path('/sys/bus/pci/devices/0000:07:00.0');hw=next((pci/'hwmon').glob('hwmon*'))
for index,mode in enumerate(sequence):
 assert not competition(),competition();trial=env.copy()
 if mode=='wide':trial['GGML_VK_ARGMAX_WIDE_SHADER']=str(p/'argmax-wide.spv')
 before=set(subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines());samples=[];errors=[];stop=threading.Event()
 def sample():
  previous=None;tick=0;builds=0
  while not stop.is_set():
   try:
    v=[int(x)for x in Path('/proc/stat').read_text().splitlines()[0].split()[1:9]];total=sum(v);idle=v[3]+v[4];busy=None if previous is None else 1-(idle-previous[1])/max(1,total-previous[0]);previous=(total,idle)
    if tick%10==0:builds=len(build_processes())
    data=dict(cpu=busy,builds=builds,runnable=int(Path('/proc/loadavg').read_text().split()[3].split('/')[0]),clock_mhz=None,power_w=None,gpu_sensor_error=None)
    try:
     data['clock_mhz']=int((hw/'freq1_input').read_text())/1e6;data['power_w']=int((hw/'power1_average').read_text())/1e6
    except OSError as exc:data['gpu_sensor_error']=repr(exc)
    samples.append(data);tick+=1
   except Exception as exc:errors.append(repr(exc))
   stop.wait(.05)
 worker=threading.Thread(target=sample);worker.start()
 try:r=subprocess.run([str(p/'native-argmax-bench'),'248320','16','60','1'],env=trial,capture_output=True,text=True,timeout=120)
 finally:stop.set();worker.join()
 text=r.stdout+r.stderr;(out/f'{index:02d}-{mode}.log').write_text(text);bad=[l for l in subprocess.run(['dmesg','--level=err,warn'],capture_output=True,text=True,check=True).stdout.splitlines()if l not in before and '0000:07:00.0'in l and re.search(r'ring .*timeout|GPU reset|fault|MES.*failed',l,re.I)];assert r.returncode==0 and not bad,(index,r.returncode,bad)
 assert 'ARGMAX_WIDE_SELECT'not in text and 'exact=1'in text
 if mode=='wide':assert 'ARGMAX_WIDE_MODULE'in text
 m=re.search(r'us_per_argmax=([0-9.]+)',text);assert m
 valid=[s for s in samples if s['cpu']is not None];assert valid and not errors
 row=dict(index=index,mode=mode,us_per_argmax=float(m[1]),cpu=statistics.mean(s['cpu']for s in valid),builds=statistics.mean(s['builds']for s in valid),runnable=statistics.mean(s['runnable']for s in valid),clock_mhz=statistics.mean(s['clock_mhz']for s in valid if s['clock_mhz']is not None)if any(s['clock_mhz']is not None for s in valid)else None,power_w=statistics.mean(s['power_w']for s in valid if s['power_w']is not None)if any(s['power_w']is not None for s in valid)else None,new_gpu_errors=bad,sensor_errors=errors,gpu_sensor_errors=[s['gpu_sensor_error']for s in samples if s['gpu_sensor_error']]);rows.append(row);(out/f'{index:02d}-telemetry.json').write_text(json.dumps(samples,indent=2)+'\n');(out/'results.json').write_text(json.dumps(rows,indent=2)+'\n');print(row,flush=True)
blocks=[]
for i in range(0,24,4):
 rr=rows[i:i+4];means=lambda key:{m:statistics.mean(r[key]for r in rr if r['mode']==m)for m in ['native','wide']};cpu=means('cpu');builds=means('builds');rq=means('runnable');matched=abs(cpu['native']-cpu['wide'])<=.05 and abs(builds['native']-builds['wide'])<=2 and abs(rq['native']-rq['wide'])<=max(4,.15*statistics.mean(rq.values()));effect=statistics.mean(math.log(r['us_per_argmax'])for r in rr if r['mode']=='wide')-statistics.mean(math.log(r['us_per_argmax'])for r in rr if r['mode']=='native');blocks.append(dict(block=i//4,matched=matched,log_time_effect=effect,cpu=cpu,builds=builds,runnable=rq))
def estimate(values):
 n=len(values);result=dict(blocks=n)
 if n:
  mu=statistics.mean(values);result['geometric_time_change_percent']=100*math.expm1(mu)
  if n>=4:
   half={4:3.182446305284263,5:2.776445105197799,6:2.570581835636305}[n]*statistics.stdev(values)/math.sqrt(n);result['descriptive_t95_percent']=[100*math.expm1(mu-half),100*math.expm1(mu+half)]
 return result
report=dict(blocks=blocks,all6=estimate([r['log_time_effect']for r in blocks]),matched=estimate([r['log_time_effect']for r in blocks if r['matched']]),scope='Fixed24operatorwalltime only, wholeprocessloadmatching, no model/speedup/equalclock/adoption claim.');(out/'analysis.json').write_text(json.dumps(report,indent=2)+'\n');print('WIDE_MICRO_COMPLETE',report,flush=True)
