from pathlib import Path
import subprocess,hashlib,json
p=Path(__file__).resolve().parent;q=p.parent/'q3-pad112'
s=(q/'timing.cpp').read_text().replace('names[]={"native","pad16","native","pad16"}','names[]={"pad16","reuse","pad16","reuse"}').replace('sizes[]={blocks*110,blocks*112}','sizes[]={blocks*112,blocks*112}').replace('  for(unsigned r=0;r<replicas;++r){memcpy(bufs[0]', '  a=pad;\n  for(unsigned r=0;r<replicas;++r){memcpy(bufs[0]').replace('4096','1024')
# Original shape K5120/R17408 and K17408/R5120 contains no literal4096. Fixed1024 dispatches/arm.
(p/'timing.cpp').write_text(s);cmd=['clang++','-std=c++17','-O2',str(p/'timing.cpp'),'-lvulkan','-o',str(p/'operator_bench_timed')];subprocess.run(cmd,check=True)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
(p/'timing-build.json').write_text(json.dumps(dict(command=cmd,source_sha256=sha(p/'timing.cpp'),binary_sha256=sha(p/'operator_bench_timed')),indent=2)+'\n')
s=(p.parent/'run_q3_pad112_timing.py').read_text().replace("p=base/'q3-pad112'","p=base/'q3-column-reuse'").replace("out=p/'timing'","out=p/'micro'").replace("['native','pad16','pad32']","['pad16','reuse']").replace('production-diagnostics/checks.json','operators/checks.json')
(p.parent/'run_q3_column_reuse_micro.py').write_text(s)
f=p.parent/'run_private_guarded_batch.py';f.write_text(f.read_text().replace('allowed={',"allowed={'run_q3_column_reuse_micro.py',",1))
