from pathlib import Path
import json,hashlib,datetime
p=Path(__file__).resolve().parent;b=p.parent;root=b.parent;pub=root/'public/Qwen38';m=json.loads((pub/'manifest.json').read_text());entries={e['source']:e for e in m['files']};files=[]
for f in p.rglob('*'):
 if not f.is_file()or f.suffix not in ['.py','.cpp','.h','.md','.json','.jsonl','.patch']:continue
 parts=f.relative_to(p).parts
 if any('cache'in x for x in parts):continue
 if parts[0]in ['model-timing512','model-confirmation512']and not(p/parts[0]/parts[1]/'confirmation-analysis.json').exists():continue
 files.append(f)
files+=list(b.glob('run_native_q3_100_*.py'))
for f in sorted(set(files)):
 raw=f.read_bytes();data=raw.replace(str(root).encode(),b'${WORKSPACE}').replace(b'${CLAUDE_WORKSPACE}',b'${CLAUDE_WORKSPACE}');source='isolated/'+str(f.relative_to(b));dst=pub/'archive'/source;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data);entries[source]=dict(source=source,path='archive/'+source,source_sha256=hashlib.sha256(raw).hexdigest(),export_sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),sanitized=data!=raw)
m['files']=list(entries.values());m['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(pub/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('Exported',len(set(files)),'completed source/evidence files; active timing/binaries/models excluded')
