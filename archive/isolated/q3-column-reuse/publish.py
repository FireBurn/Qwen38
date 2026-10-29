from pathlib import Path
import json,hashlib,datetime
p=Path(__file__).resolve().parent;b=p.parent;root=b.parent;pub=root/'public/Qwen38';m=json.loads((pub/'manifest.json').read_text());entries={e['source']:e for e in m['files']}
assert list((p/'timing512').glob('*/confirmation-analysis.json')),'Preserve complete discovery before publication'
files=[f for f in p.iterdir()if f.is_file()and f.suffix in ['.py','.cpp','.md','.json','.patch']]
files += list((p/'shader').glob('*.glsl'))+list((p/'shader').glob('*.comp'))
for folder in ['operators','model32','prompts128','populated-kv64','boundary128','timing512','confirmation512','micro']:
 d=p/folder
 if d.exists():files += [f for f in d.rglob('*')if f.suffix in ['.json','.jsonl']if not any('cache'in v for v in f.relative_to(d).parts)]
files += [f for f in b.glob('run_q3_column_reuse_*.py')]
for f in sorted(set(files)):
 raw=f.read_bytes();data=raw.replace(str(root).encode(),b'${WORKSPACE}').replace(b'${CLAUDE_WORKSPACE}',b'${CLAUDE_WORKSPACE}');source='isolated/'+str(f.relative_to(b));dst=pub/'archive'/source;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
 entries[source]=dict(source=source,path='archive/'+source,source_sha256=hashlib.sha256(raw).hexdigest(),export_sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),sanitized=data!=raw)
m['files']=list(entries.values());m['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(pub/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('Exported',len(set(files)),'source/evidence files; no binaries,models,rawlogits or caches')
