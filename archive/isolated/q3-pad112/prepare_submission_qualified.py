from pathlib import Path
import json,hashlib
p=Path(__file__).resolve().parent;b=p.parent
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
d=sorted((p/'submission-system-effect512').iterdir())[-1];report=d/'confirmation-analysis.json';a=json.loads(report.read_text());kv=p/'submission-populated-kv64/comparison.json';k=json.loads(kv.read_text())
assert a['stock_gain_supported'] and a['incremental_gain_supported'] and a['primary_stock']['blocks']>=4
assert k['all_requested_target_logit_bits_identical'] and k['all_tokens_and_counters_identical'] and k['minimum_target_audit_position']>=2048
q=p/'qualified-20261029';m=json.loads((q/'manifest.json').read_text())
for n,h in m['files'].items():assert sha(q/n)==h,n
cfg=dict(scope='Scoped whole-configuration candidate under natural DVFS; unchanged qualified Q3 library,existing nodecap400. Not equal-clock shader or mega gain. Original cap100clock-matched rejection remains retained.',node_cap=400,snapshot='qualified-20261029',library_sha256=sha(q/'bin/libggml-vulkan.so.0.27.0'),primary_stock=a['primary_stock'],secondary_incremental=a['secondary_incremental'],proof_files={str(f.relative_to(p)):sha(f)for f in [report,kv,d/'outcomes-summary.json',p/'submission-system-effect-plan.json']},model=k['scope'],proof_minimum_target_position=k['minimum_target_audit_position'])
f=p/'submission-qualified-20261029.json';assert not f.exists(),'Do not replace an existing qualified configuration';f.write_text(json.dumps(cfg,indent=2)+'\n');f.chmod(0o444)
s=(b/'run_q3_pad112_qualified_once.py').read_text().replace("mode=os.environ.get('Q3_QUALIFIED_MODE','pad')","mode='pad'").replace("out=p/'qualified-single'","out=p/'qualified-submit400-single'")
needle="def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()\n";assert needle in s
s=s.replace(needle,needle+"config_path=p/'submission-qualified-20261029.json';config=json.loads(config_path.read_text());assert config['node_cap']==400\nfor name,value in config['proof_files'].items():assert sha(p/name)==value,name\n")
s=s.replace("env.update(GGML_VK_VISIBLE_DEVICES=","env.update(GGML_VK_MAX_NODES_PER_SUBMIT='400',GGML_VK_VISIBLE_DEVICES=",1)
s=s.replace("report={'mode':mode,","report={'submission_cap':400,'submission_config_sha256':sha(config_path),'mode':mode,",1)
s=s.replace('Single reproduction/smoke arm only; not another A/B confirmation or general deployment.','Single guarded cap400 whole-configuration reproduction/smoke only; not another throughput confirmation or general deployment.')
f=b/'run_q3_submit400_qualified_once.py';assert not f.exists();f.write_text(s)
f=b/'run_private_guarded_batch.py';s=f.read_text().replace("'run_q3_submission_system_effect.py'","'run_q3_submission_system_effect.py','run_q3_submit400_qualified_once.py'",1);f.write_text(s)
print('Prepared scoped guarded cap400 reproduction; frozen snapshot unchanged')
