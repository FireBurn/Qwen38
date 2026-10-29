from pathlib import Path
import json,hashlib,datetime
p=Path(__file__).resolve().parent;b=p.parent;root=b.parent;pub=root/'public/Qwen38';m=json.loads((pub/'manifest.json').read_text());entries={e['source']:e for e in m['files']}
files=[f for f in p.iterdir()if f.is_file()and f.suffix in ['.py','.cpp','.h','.json','.md','.patch']]
for name in ['model32','prompts128','populated-kv64','boundary128']:
 files += [f for f in(p/name).rglob('*')if f.is_file()and f.suffix in ['.json','.jsonl']]
files += [b/n for n in ['native_observer_common.py','run_native_command_observer_model32.py','run_native_command_observer_prompts128.py','run_native_command_observer_kv64.py','run_native_command_observer_boundary128.py','run_native_command_capabilities.py']]
for f in files:
 raw=f.read_bytes();data=raw.replace(str(root).encode(),b'${WORKSPACE}').replace(b'${CLAUDE_WORKSPACE}',b'${CLAUDE_WORKSPACE}');source='isolated/'+str(f.relative_to(b));dst=pub/'archive'/source;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
 entries[source]=dict(source=source,path='archive/'+source,source_sha256=hashlib.sha256(raw).hexdigest(),export_sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),sanitized=data!=raw)
m['files']=list(entries.values());m['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(pub/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('Exported',len(files),'native command observer files;raw metadata traces remain local')
