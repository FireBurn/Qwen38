from pathlib import Path
import json,hashlib,datetime
p=Path(__file__).resolve().parent;base=p.parent;root=base.parent;pub=root/'public/Qwen38';m=json.loads((pub/'manifest.json').read_text());entries={e['source']:e for e in m['files']};files=[]
for prefix in ['host-profile-v2-runs','host-profile-v2-cap400-runs','submission-cap-model32','submission-cap-prompts128','submission-cap-screen512','submission-cap-confirm512']:
 d=p/prefix
 if d.exists():files += [f for f in d.rglob('*')if f.is_file()and(f.suffix in ['.json','.jsonl']or f.name=='run.log')]
files += [p/n for n in ['prepare_submission_system.py','submission-system-effect-plan.json','compare_submission_profiles.py','submission-count-profile.json','profile-v2-plan.json','prepare_profile_v2.py','build_profile_v2.py','analyse_profile_v2.py','submission-cap-plan.json','prepare_submission_cap.py','prepare_submission_cap_confirm.py','publish_submission_round.py']]
files += [p/'host-profile-v2'/n for n in ['build.json','np-profile.h','np-profile.cpp']]
files += [base/n for n in ['run_q3_submission_system_effect.py','run_q3_pad112_host_profile_v2.py','run_q3_host_profile_cap400.py','run_q3_submission_cap_model32.py','run_q3_submission_cap_screen.py','run_q3_submission_cap_prompts128.py','run_q3_submission_cap_confirm.py']]
for f in files:
 if not f.exists():continue
 source='isolated/'+str(f.relative_to(base));raw=f.read_bytes();data=raw.replace(str(root).encode(),b'${WORKSPACE}').replace(b'${CLAUDE_WORKSPACE}',b'${CLAUDE_WORKSPACE}');dst=pub/'archive'/source;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
 entries[source]=dict(source=source,path='archive/'+source,source_sha256=hashlib.sha256(raw).hexdigest(),export_sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),sanitized=data!=raw)
m['files']=list(entries.values());m['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(pub/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('Exported',len(files),'submission-profile files')
