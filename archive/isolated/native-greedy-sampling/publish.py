"""Archive prepared research with explicit untested status; omit build trees/binaries."""
from pathlib import Path
import datetime,hashlib,json
p=Path(__file__).resolve().parent;b=p.parent;root=b.parent;pub=root/'public/Qwen38'
m=json.loads((pub/'manifest.json').read_text());entries={e['source']:e for e in m['files']};files=[]
for folder in [p,b/'native-mapped-plan-reuse']:
 for f in folder.rglob('*'):
  if not f.is_file()or f.suffix not in ['.py','.cpp','.h','.md','.json','.comp']:continue
  if 'build-inputs'in f.relative_to(folder).parts:continue
  files.append(f)
files+=list(b.glob('run_native_mapped_reuse_*.py'))
files+=list(b.glob('run_native_callback_*.py'))
for f in sorted(set(files)):
 raw=f.read_bytes();data=raw.replace(str(root).encode(),b'${WORKSPACE}').replace(b'${CLAUDE_WORKSPACE}',b'${CLAUDE_WORKSPACE}');source='isolated/'+str(f.relative_to(b));dst=pub/'archive'/source;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data);entries[source]=dict(source=source,path='archive/'+source,source_sha256=hashlib.sha256(raw).hexdigest(),export_sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),sanitized=data!=raw)
m['files']=list(entries.values());m['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(pub/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('Exported',len(set(files)),'prepared research files; build snapshots/binaries omitted')
