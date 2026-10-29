from pathlib import Path
import json,hashlib,datetime
p=Path(__file__).resolve().parent;root=p.parents[1];pub=root/'public/Qwen38';m=json.loads((pub/'manifest.json').read_text());entries={e['source']:e for e in m['files']}
files=[p/n for n in ['publish_fusion_round.py','q6-alignment-plan.md','q6-alignment-cpu-proof.json','fusion-combination-plan.json','fusion-module-proof.json','fusion-options.patch','build_fusion_options.py','prepare_combination_screen.py','prepare_combination_confirm.py']]
files += [p/'host-fusion-options/build.json']
for name in ['fusion-options-operators','fusion-options-model32','fusion-options-model136','fusion-options-prompts128','fusion-options-quant32','fusion-screen512','fusion-combination-confirm512']:
 parent=p/name
 if parent.exists():
  files += [f for f in parent.rglob('*') if f.is_file() and (f.suffix in ['.json','.jsonl'] or f.name=='run.log')]
files += list(p.parent.glob('run_q3_pad112_fusion_*.py'))
files += [p.parent/('run_q3_pad112_combination_'+n+'.py') for n in ['screen','confirm']]
for f in files:
 if not f.exists():continue
 source='isolated/'+str(f.relative_to(p.parent));raw=f.read_bytes();data=raw.replace(str(root).encode(),b'${WORKSPACE}').replace(b'${CLAUDE_WORKSPACE}',b'${CLAUDE_WORKSPACE}');dst=pub/'archive'/source;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
 entries[source]={'source':source,'path':'archive/'+source,'source_sha256':hashlib.sha256(raw).hexdigest(),'export_sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'sanitized':data!=raw}
m['files']=list(entries.values());m['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(pub/'manifest.json').write_text(json.dumps(m,indent=2)+chr(10));print('Exported',len(files),'host-round files')
