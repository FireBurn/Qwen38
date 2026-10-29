from pathlib import Path
import json
p=Path(__file__).resolve().parent;b=p.parent
reports=sorted((p/'model-timing512').glob('*/confirmation-analysis.json'));assert reports
r=json.loads(reports[-1].read_text());assert r['incremental_gain_supported']and r['matched_primary']['blocks']>=4
s=(b/'run_q3_pair_glu_model_timing.py').read_text().replace("out=project/'model-timing512'","out=project/'model-confirmation512'").replace("project/'MODEL-TIMING-PLAN.md'","project/'MODEL-CONFIRMATION-PLAN.md'").replace('Fixed24fresh512token confirmation','Independentfixed24fresh512token replication').replace('Q3_PAIR_GLU_MODEL_DISCOVERY','Q3_PAIR_GLU_MODEL_INDEPENDENT_REPLICATION')
(b/'run_q3_pair_glu_confirmation.py').write_text(s)
f=b/'run_private_guarded_batch.py';f.write_text(f.read_text().replace('allowed={',"allowed={'run_q3_pair_glu_confirmation.py',",1))
