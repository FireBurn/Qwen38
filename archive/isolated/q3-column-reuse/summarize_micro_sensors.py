from pathlib import Path
import json,statistics
p=sorted((Path(__file__).resolve().parent/'micro').iterdir())[-1];rows=[json.loads(l)for l in(p/'telemetry.jsonl').read_text().splitlines()];valid=[r for r in rows if'sensor_error'not in r];r=json.loads((p/'summary.json').read_text())
summary=dict(samples=len(rows),sensor_errors=[x for x in rows if'sensor_error'in x],cpu_busy_range=[min(x['cpu_busy_fraction']for x in valid if'cpu_busy_fraction'in x),max(x['cpu_busy_fraction']for x in valid if'cpu_busy_fraction'in x)],clock_mhz_range=[min(float(x['freq1_input'])/1e6 for x in valid),max(float(x['freq1_input'])/1e6 for x in valid)],scope='Process-wide sensor samples, not precisely per-arm attributed. Errors retained; no strict per-arm matched-clock qualification. Payload rate below is nominal matrix bytes per dispatch-time, not measured physical DRAM throughput.',streamed_payload_rates=[])
for c in r['cases']:
 if c['replicas']==16:
  size=c['k']*c['rows']*112//256
  summary['streamed_payload_rates'].append(dict(cols=c['cols'],k=c['k'],rows=c['rows'],matrix_bytes=size,frozen_nominal_payload_GB_s=size/c['frozen_us']/1000,reuse_nominal_payload_GB_s=size/c['reuse_us']/1000))
(p/'sensors-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print({k:v for k,v in summary.items()if k!='sensor_errors'})
