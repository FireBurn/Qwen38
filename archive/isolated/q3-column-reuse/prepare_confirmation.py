from pathlib import Path
import json
p=Path(__file__).resolve().parent;b=p.parent
# Only invoke after the separate fixed discovery report exists and passes its preset gate.
reports=sorted((p/'timing512').glob('*/confirmation-analysis.json'));assert reports
r=json.loads(reports[-1].read_text());assert r['incremental_gain_supported'] and r['matched_primary']['blocks']>=4
s=(b/'run_q3_column_reuse_timing.py').read_text().replace("out=project/'timing512'","out=project/'confirmation512'").replace("project/'TIMING-PLAN.md'","project/'CONFIRMATION-PLAN.md'")
s=s.replace('Fixed24fresh512token confirmation','Independent fixed24fresh512token replication').replace('Q3_COLUMN_REUSE_CONFIRMATION','Q3_COLUMN_REUSE_INDEPENDENT_REPLICATION')
(b/'run_q3_column_reuse_confirmation.py').write_text(s)
f=b/'run_private_guarded_batch.py';f.write_text(f.read_text().replace('allowed={',"allowed={'run_q3_column_reuse_confirmation.py',",1))
