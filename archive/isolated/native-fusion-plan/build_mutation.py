from pathlib import Path
import json,subprocess,hashlib
p=Path(__file__).resolve().parent;b=p.parent;(p/'mutation-bin').mkdir(exist_ok=True);cmd=json.loads((b/'production-native-shaders/client/build.json').read_text())['command'];cmd=[str(p/'mutation.cpp')if x.endswith('/client/operator_bench.cpp')else x for x in cmd];cmd[cmd.index('-o')+1]=str(p/'mutation-bin/operator_bench');subprocess.run(cmd,check=True)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'mutation-build.json').write_text(json.dumps(dict(command=cmd,source_sha256=sha(p/'mutation.cpp'),binary_sha256=sha(p/'mutation-bin/operator_bench')),indent=2)+'\n')
