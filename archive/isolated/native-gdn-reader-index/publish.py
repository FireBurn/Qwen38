from pathlib import Path
import json,hashlib,datetime
p=Path(__file__).resolve().parent;b=p.parent;root=b.parent;pub=root/'public/Qwen38';m=json.loads((pub/'manifest.json').read_text());entries={e['source']:e for e in m['files']}
files=[]
for folder in [p,b/'native-host-planning-profile']:
 files += [f for f in folder.iterdir()if f.is_file()and f.suffix in ['.py','.cpp','.h','.json','.md','.patch']]
 for sub in folder.iterdir():
  if sub.is_dir()and sub.name not in ['host','cost-host','__pycache__']:
   files += [f for f in sub.rglob('*')if f.is_file()and f.suffix in ['.json','.jsonl']and not any('cache'in x for x in f.relative_to(sub).parts)]
 for name in ['host','cost-host']:
  if(folder/name).exists():files += [f for f in(folder/name).iterdir()if f.is_file()and(f.suffix=='.json'or f.name in ['np-profile.cpp','np-profile.h'])]
files += [b/n for n in ['run_native_planning_profile_model32.py','run_native_planning_profile.py','run_gdn_reader_model32.py','run_gdn_reader_prompts128.py','run_gdn_reader_kv64.py','run_gdn_reader_boundary128.py','run_gdn_reader_timing.py','run_gdn_reader_cost_profile.py','run_gdn_gpu_profile32.py']]
for f in sorted(set(files)):
 raw=f.read_bytes();data=raw.replace(str(root).encode(),b'${WORKSPACE}').replace(b'${CLAUDE_WORKSPACE}',b'${CLAUDE_WORKSPACE}');source='isolated/'+str(f.relative_to(b));dst=pub/'archive'/source;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
 entries[source]=dict(source=source,path='archive/'+source,source_sha256=hashlib.sha256(raw).hexdigest(),export_sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),sanitized=data!=raw)
m['files']=list(entries.values());m['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(pub/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('Exported',len(set(files)),'files; no binaries/models/raw logit tapes')
