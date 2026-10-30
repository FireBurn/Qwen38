"""Build private correctness runner only after fixed timing is terminal."""
from pathlib import Path
import hashlib,json,subprocess
p=Path(__file__).resolve().parent;b=p.parent
active=[d for d in (b/'native-default-q3-100/model-timing512').glob('*')if d.is_dir()and not(d/'confirmation-analysis.json').exists()]
active += [d for d in (b/'native-default-q3-100/model-confirmation512').glob('*')if d.is_dir()and not(d/'confirmation-analysis.json').exists()]
assert not active,('Timing incomplete; do not compile',active)
for proc in Path('/proc').glob('[0-9]*'):
 try:cmd=(proc/'cmdline').read_bytes().split(b'\0');name=Path(cmd[0].decode()).name
 except (OSError,UnicodeError):continue
 assert name not in ['model-bench','llama-bench','llama-server','callback-audit-runner','sampling-audit-runner'],('Competing GPU executable',proc,name)
stock=b/'production-baseline-aa8';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
inputs=json.loads((p/'build-inputs.json').read_text())
for f,h in inputs['files'].items():assert sha(p/'build-inputs'/f)==h,f
prepared=json.loads((p/'sampling-preparation.json').read_text());source=p/'sampling-audit-runner.cpp';assert sha(source)==prepared['source_sha256']
command=['/usr/lib/llvm/23/bin/clang++','-O2','-std=c++17','-stdlib=libc++','-I'+str(p/'build-inputs/common'),'-I'+str(stock/'include'),'-I'+str(stock/'ggml-include'),str(source),'-L'+str(stock/'bin'),'-Wl,-rpath,'+str(stock/'bin'),'-lllama-common','-lllama','-lggml','-lggml-base','-pthread','-o',str(p/'sampling-audit-runner')]
subprocess.run(command,check=True)
(p/'sampling-build.json').write_text(json.dumps(dict(command=command,source_sha256=sha(source),binary_sha256=sha(p/'sampling-audit-runner'),scope='Correctness-only raw target graph callback. No GPU qualification or throughput proof.'),indent=2)+'\n')
