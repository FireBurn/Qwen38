from pathlib import Path
import json
p=Path(__file__).resolve().parent/'metadata-runs/20261029T210122Z';rows=[]
for f in sorted(p.glob('metadata-[0-9].json')):
 d=json.loads(f.read_text());assert not d['dropped'];r=[{**v,'name':bytes.fromhex(v['name_hex']).decode()}for v in d['records']];assert sum(v['calls']for v in r)==1850
 if rows:assert rows[0]==r
 rows.append(r)
assert len(rows)==4;assert json.loads((p/'behavior-check.json').read_text())['all_tokens_and_counters_identical'];assert not json.loads((p/'execution.json').read_text())['new_driver_errors']
(p/'metadata-summary.json').write_text(json.dumps(dict(generations=4,zero_overflow=True,identical_records_all_generations=True,calls_per_generation=1850,records=rows[0],scope='CPUmetadataonly,noshader/transfer/ownershipchanges;destinationcopiesflags0withVulkan0#names. Pinnedsource scheduler creates these copies for graph inputs. Namesandconstantsconfirmedbyoriginal aa8 graph/KV code.'),indent=2)+'\n');print('SYNC_SET_METADATA_1850_CALLS_17_RECORDS_EXACT')
