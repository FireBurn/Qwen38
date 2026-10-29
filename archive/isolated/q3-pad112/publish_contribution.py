from pathlib import Path
import json,hashlib,datetime
p=Path(__file__).resolve().parent;b=p.parent;root=b.parent;pub=root/'public/Qwen38';m=json.loads((pub/'manifest.json').read_text());entries={e['source']:e for e in m['files']};files=[]
files += [p/n for n in ['contribution-plan.json','prepare_contribution.py','prepare_contribution_timing.py','publish_contribution.py','summarise_contribution.py','stock400-qualified-20261029.json','prepare_stock400_qualified.py']]
for name in ['contribution-stock400-model32','contribution-stock400-populated-kv64','qualified-stock400-single']:
 if(p/name).exists():files += [f for f in(p/name).rglob('*')if f.is_file()and(f.suffix in ['.json','.jsonl']or f.name=='run.log')]
if(p/'contribution512').exists():
 for d in(p/'contribution512').iterdir():
  if(d/'confirmation-analysis.json').exists():
   assert len(json.loads((d/'results.json').read_text()))==36
   files += [f for f in d.rglob('*')if f.is_file()and(f.suffix in ['.json','.jsonl']or f.name=='run.log')]
files += [b/n for n in ['run_q3_contribution_stock400_model32.py','run_q3_contribution_stock400_kv64.py','run_q3_contribution_timing.py','run_q3_stock400_qualified_once.py']]
for f in files:
 if not f.exists():continue
 raw=f.read_bytes();data=raw.replace(str(root).encode(),b'${WORKSPACE}').replace(b'${CLAUDE_WORKSPACE}',b'${CLAUDE_WORKSPACE}');source='isolated/'+str(f.relative_to(b));dst=pub/'archive'/source;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
 entries[source]=dict(source=source,path='archive/'+source,source_sha256=hashlib.sha256(raw).hexdigest(),export_sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),sanitized=data!=raw)
m['files']=list(entries.values());m['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(pub/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('Exported contribution evidence; timing only if terminal')
