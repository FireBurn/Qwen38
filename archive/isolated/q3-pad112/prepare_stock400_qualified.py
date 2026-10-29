from pathlib import Path
import json,hashlib
p=Path(__file__).resolve().parent;b=p.parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
d=sorted((p/'contribution512').iterdir())[-1];a=json.loads((d/'confirmation-analysis.json').read_text());assert a['stock400_gain_supported']and a['matched']['cap_only']['blocks']>=4
proofs=[d/'confirmation-analysis.json',d/'outcomes-summary.json',p/'contribution-plan.json',p/'contribution-stock400-model32/comparison.json',p/'contribution-stock400-populated-kv64/comparison.json']
for name in ['contribution-stock400-model32','contribution-stock400-populated-kv64']:
 assert json.loads((p/name/'comparison.json').read_text())['all_requested_target_logit_bits_identical']
m=json.loads((p/'qualified-20261029/manifest.json').read_text());m['files']={};m['proof_files']={str(f.relative_to(p)):sha(f)for f in proofs};m.update(scope='Stock backend plus existing submission cap400,without paddedQ3 cache. Scoped naturalDVFS whole-configuration result,not fastermega/equalclock/arbitrarycontext claim. Both measured options remain available; compare speed/VRAM tradeoff.',node_cap=400,primary_stock_gain=a['matched']['cap_only'],cache_incremental=a['matched']['cache_incremental'],stock400_vs_frozen400_noninferiority=a['stock400_vs_frozen400_noninferiority'])
f=p/'stock400-qualified-20261029.json';assert not f.exists();f.write_text(json.dumps(m,indent=2)+'\n');f.chmod(0o444)
s=(b/'run_q3_pad112_qualified_once.py').read_text().replace("q=p/'qualified-20261029';m=json.loads((q/'manifest.json').read_text())","q=None;config_path=p/'stock400-qualified-20261029.json';m=json.loads(config_path.read_text())")
s=s.replace("mode=os.environ.get('Q3_QUALIFIED_MODE','pad')","mode='stock'").replace("out=p/'qualified-single'","out=p/'qualified-stock400-single'")
needle='def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()\n';assert needle in s;s=s.replace(needle,needle+"assert m['node_cap']==400\nfor name,value in m['proof_files'].items():assert sha(p/name)==value,name\n")
s=s.replace("env.update(GGML_VK_VISIBLE_DEVICES=","env.update(GGML_VK_MAX_NODES_PER_SUBMIT='400',GGML_VK_VISIBLE_DEVICES=",1).replace("sha(q/'manifest.json')","sha(config_path)").replace("report={'mode':mode,","report={'submission_cap':400,'padded_cache_enabled':False,'mode':mode,",1).replace('Single reproduction/smoke arm only; not another A/B confirmation or general deployment.','Guarded stock400 no-padded-cache smoke/reproduction only,not another A/B confirmation or general deployment.')
f=b/'run_q3_stock400_qualified_once.py';assert not f.exists();f.write_text(s)
f=b/'run_private_guarded_batch.py';s=f.read_text().replace("'run_q3_submission_system_effect.py'","'run_q3_submission_system_effect.py','run_q3_stock400_qualified_once.py'",1);f.write_text(s)
print('Prepared stock400 lower-memory option; frozen candidate untouched')
