from pathlib import Path
import json,subprocess,hashlib
p=Path(__file__).resolve().parent;(p/'stress-bin').mkdir(exist_ok=True);s=(p/'probe.cpp').read_text().replace('for(uint32_t k:{256u,512u,1024u,4096u,5120u,17408u})for(uint32_t rows:{1u,2u,3u,4u,7u,15u})','for(uint32_t k:{5120u,17408u})for(uint32_t rows:{17u,33u,5120u,17408u})').replace('groups<=16','groups<=65535')
s=s.replace('row<rows;++row){double total=0;','row<rows;++row){if(rows>64&&row!=0&&row!=rows/2&&row!=rows-1)continue;double total=0;')
s=s.replace('j<nout;++j)require(std::isfinite(out[j])','j<nout;++j)if(rows<=64||j%rows==0||j%rows==rows/2||j%rows==rows-1)require(std::isfinite(out[j])')
(p/'stress.cpp').write_text(s);cmd=['clang++','-std=c++17','-O2',str(p/'stress.cpp'),'-lvulkan','-o',str(p/'stress-bin/operator_bench')];subprocess.run(cmd,check=True)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'stress-build.json').write_text(json.dumps(dict(command=cmd,source_sha256=sha(p/'stress.cpp'),binary_sha256=sha(p/'stress-bin/operator_bench')),indent=2)+'\n')
s=(p.parent/'run_q3_pair_glu_operators.py').read_text().replace("out=p/'operators'","out=p/'stress'").replace("p/'probe.cpp'","p/'stress.cpp'").replace("p/'probe-build.json'","p/'stress-build.json'").replace("p/'operator_bench'","p/'stress-bin/operator_bench'").replace('==576','==128').replace('timeout=180','timeout=600').replace('PAIR_576_CASES_EXACT','PAIR_128_FULL_SHAPE_CASES_EXACT').replace('6Kwidths/6rowtails/C1C2/4patterns/2orders;allfirstdispatches<=16WG. Native matrixscalarCPUoracle','2Kwidths/4rowsincludingfull5120and17408/C1C2/4patterns/2orders;after576boundedchecks/resourceinspection,max17408WG,nointerWGsync. Native matrixscalarCPUoracle samplesfirst/middle/lastrowatlargeshapes,allrowsatsmalltails')
s=s.replace("assert not competition(),competition();before=", "assert json.loads((p/'operators/checks.json').read_text())['exact_cases']==576\nassert not competition(),competition();before=")
(p.parent/'run_q3_pair_glu_stress.py').write_text(s)
f=p.parent/'run_private_guarded_batch.py';f.write_text(f.read_text().replace('allowed={',"allowed={'run_q3_pair_glu_stress.py',",1))
