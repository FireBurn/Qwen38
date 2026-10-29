from pathlib import Path
import json,hashlib,datetime
p=Path(__file__).resolve().parent;base=p.parent;root=base.parent;pub=root/'public/Qwen38';m=json.loads((pub/'manifest.json').read_text());entries={e['source']:e for e in m['files']};files=[]
for name in ['q6-pad212','q6-native-scale']:
 d=base/name
 files += [f for f in d.iterdir()if f.is_file()and f.suffix in ['.py','.cpp','.json','.md']]
 for child in ['native','pad16','pad32','shuffle','direct']:
  if(d/child).is_dir():files += [f for f in(d/child).iterdir()if f.suffix in ['.glsl','.comp']]
 if(d/'diagnostics').exists():files += [f for f in(d/'diagnostics').iterdir()if f.name in ['checks.json','assets.json','probe.log']]
 if(d/'timing-runs').exists():files += [f for f in(d/'timing-runs').rglob('*')if f.is_file()and(f.suffix in ['.json','.jsonl']or f.name=='probe.log')]
files += [base/n for n in ['run_q6_pad212_probe.py','run_q6_pad212_timing.py','run_q6_native_scale_probe.py','run_q6_native_scale_timing.py']]
for f in files:
 source='isolated/'+str(f.relative_to(base));raw=f.read_bytes();data=raw.replace(str(root).encode(),b'${WORKSPACE}').replace(b'${CLAUDE_WORKSPACE}',b'${CLAUDE_WORKSPACE}');dst=pub/'archive'/source;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
 entries[source]=dict(source=source,path='archive/'+source,source_sha256=hashlib.sha256(raw).hexdigest(),export_sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),sanitized=data!=raw)
m['files']=list(entries.values());m['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(pub/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('Exported',len(files),'Q6 files')
