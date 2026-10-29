from pathlib import Path
import json,hashlib,datetime
p=Path(__file__).resolve().parent;b=p.parent;root=b.parent;pub=root/'public/Qwen38';m=json.loads((pub/'manifest.json').read_text());entries={e['source']:e for e in m['files']}
assert list((p/'model-timing512').glob('*/confirmation-analysis.json')),'Only publish completed discovery'
files=[f for f in p.iterdir()if f.is_file()and f.suffix in ['.py','.cpp','.md','.json','.patch']]
files += [f for f in(p/'shader').iterdir()if f.suffix in ['.glsl','.comp']]
for name in ['host','audit-host']:
 files += [f for f in(p/name).iterdir()if f.is_file()and f.suffix in ['.json','.h']]
files += [p/'host/ggml-vulkan.cpp']
for folder in ['model32','operators','stress','timing','host-model32','host-prompts128','host-populated-kv64','host-boundary128','model-timing512','model-confirmation512','eligibility','eligibility-attempt1-policy-expectation']:
 d=p/folder
 if d.exists():files += [f for f in d.rglob('*')if f.is_file()and f.suffix in ['.json','.jsonl','.cpp','.py','.md']and not any('cache'in x for x in f.relative_to(d).parts)]
files += list(b.glob('run_q3_pair_glu_*.py'))+[b/'run_q3_pair_graph_audit.py']
for f in sorted(set(files)):
 raw=f.read_bytes();data=raw.replace(str(root).encode(),b'${WORKSPACE}').replace(b'${CLAUDE_WORKSPACE}',b'${CLAUDE_WORKSPACE}');source='isolated/'+str(f.relative_to(b));dst=pub/'archive'/source;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
 entries[source]=dict(source=source,path='archive/'+source,source_sha256=hashlib.sha256(raw).hexdigest(),export_sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),sanitized=data!=raw)
m['files']=list(entries.values());m['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(pub/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('Exported',len(set(files)),'source/evidence files, no binaries/models/raw logit tapes')
