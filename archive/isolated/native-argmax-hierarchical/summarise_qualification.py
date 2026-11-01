from pathlib import Path
import hashlib,json
q=Path(__file__).resolve().parent
folders=['model32','prompts128','kv64','boundary128'];modes={'stock100','private_hier','private_wide'};sums={m:0 for m in modes};changed=[];records=[]
for name in folders:
 folder=q/name;comparison=json.loads((folder/'comparison.json').read_text());assert comparison['all_requested_target_logit_bits_identical'] and comparison['all_tokens_and_counters_identical']
 rows=json.loads((folder/'checks.json').read_text());assert {r['mode'] for r in rows}==modes
 for r in rows:assert not r['new_driver_errors'];sums[r['mode']]+=r['target_logit_rows']
 logpaths=list(folder.glob('**/private_hier.log'));assert len(logpaths)==(2 if name=='prompts128' else 1)
 for log in logpaths:assert 'HIER_ARGMAX_DISPATCH k=248320' in log.read_text()
 for filename,expected in json.loads((folder/'assets.json').read_text()).items():
  p=Path(filename)
  if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:changed.append(filename)
 records.append({'folder':name,'runs':len(rows),'rows_by_mode':{m:sum(r['target_logit_rows'] for r in rows if r['mode']==m) for m in modes},'hierarchical_dispatch_logs':len(logpaths)})
assert not changed,changed
assert all(v==530 for v in sums.values()),sums
report={'all_native_raw_bits_tokens_counters_identical':True,'target_rows_per_mode':530,'rows_by_mode':sums,'records':records,'pinned_assets_unchanged':True,'new_gpu_errors':[],'scope':'Stock/wide/hier in tested short, coding, maths, populated-KV and 256-position boundary workloads, one-dword-copy private driver. Not universal model, sampling or context equivalence; not a speed result.'}
(q/'model-qualification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
