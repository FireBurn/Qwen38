from pathlib import Path
import json,hashlib,subprocess
p=Path(__file__).resolve().parent;(p/'eligibility-bin').mkdir(exist_ok=True);b=p.parent
cmd=json.loads((b/'production-native-shaders/client/build.json').read_text())['command'];cmd=[str(p/'eligibility.cpp')if x.endswith('/client/operator_bench.cpp')else x for x in cmd];cmd[cmd.index('-o')+1]=str(p/'eligibility-bin/operator_bench');subprocess.run(cmd,check=True)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'eligibility-build.json').write_text(json.dumps(dict(command=cmd,source_sha256=sha(p/'eligibility.cpp'),binary_sha256=sha(p/'eligibility-bin/operator_bench')),indent=2)+'\n')
