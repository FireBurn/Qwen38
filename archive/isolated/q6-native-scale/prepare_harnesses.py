from pathlib import Path
import subprocess,json,hashlib
p=Path(__file__).resolve().parent;ref=p.parent/'q6-pad212'
for name,binary in [('probe.cpp','operator_bench'),('timing.cpp','operator_bench_timed')]:
 s=(ref/name).read_text().replace('"pad16"','"shuffle"').replace('"pad32"','"direct"').replace('q6-pad212','q6-native-scale').replace('Q6_PAD212','Q6_NATIVE_SCALE')
 if name=='probe.cpp':
  s=s.replace('memcpy(pad+ib*212,a+ib*210,210);pad[ib*212+210]=0;pad[ib*212+211]=0;','memcpy(pad+ib*210,a+ib*210,210);')
 else:s=s.replace('memcpy(pad.data()+ib*212,a.data()+ib*210,210);pad[ib*212+210]=pad[ib*212+211]=0;','memcpy(pad.data()+ib*210,a.data()+ib*210,210);')
 s=s.replace('blocks*212','blocks*210');assert '*212'not in s
 (p/name).write_text(s);cmd=['clang++','-std=c++17','-O2',str(p/name),'-lvulkan','-o',str(p/binary)];subprocess.run(cmd,check=True)
 (p/('probe-build.json'if name=='probe.cpp'else'timing-build.json')).write_text(json.dumps(dict(command=cmd,source_sha256=hashlib.sha256(s.encode()).hexdigest(),binary_sha256=hashlib.sha256((p/binary).read_bytes()).hexdigest()),indent=2)+'\n')
plan=json.loads((ref/'timing-plan.json').read_text());plan.update(scope='Native float Q6 scale handoff only; no padding/cache, no model speedup inference',modes=['native210','shuffle210','direct210'],limits='Synthetic streaming16replicas each over1GiB; one replica exceeds64MiB LLC. No extra cache needed in model. Same arithmetic/reduction, wave64,64WG. No full-model gain established. Earlier mega scale experiments do not establish this native performance.')
(p/'timing-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
for kind in ['probe','timing']:
 s=(p.parent/('run_q6_pad212_'+kind+'.py')).read_text().replace("p=base/'q6-pad212'","p=base/'q6-native-scale'").replace("'pad16','pad32'","'shuffle','direct'").replace('pad16_c','shuffle_c').replace('pad32_c','direct_c').replace('Q6_PAD212','Q6_NATIVE_SCALE').replace('vs212bytepaddingcontrols','vsnative210byte scale alternatives').replace('native/pad16/pad32','native/shuffle/direct')
 (p.parent/('run_q6_native_scale_'+kind+'.py')).write_text(s)
f=p.parent/'run_private_guarded_batch.py';s=f.read_text().replace("'run_q6_pad212_probe.py'","'run_q6_pad212_probe.py','run_q6_native_scale_probe.py','run_q6_native_scale_timing.py'",1);f.write_text(s)
