from pathlib import Path
import json
p=Path(__file__).resolve().parent;out={}
for cap,folder in [(100,'host-profile-v2-runs'),(400,'host-profile-v2-cap400-runs')]:
 d=sorted((p/folder).iterdir())[-1];a=json.loads((d/'analysis.json').read_text());assert json.loads((d/'behavior-check.json').read_text())['all_tokens_and_counters_identical'];out[cap]={}
 for mode in ['control','pad']:
  rr=[r for r in a['arms']if r['mode']==mode];totals={event:{k:sum(r['events'][event][k]for r in rr)for k in ['count','cpu_ns','wall_ns']}for event in rr[0]['events']}
  out[cap][mode]={'generations':len(rr),'graphs':totals['graph']['count'],'nonempty_submits':totals['submit_nonempty']['count'],'submits_per_graph':totals['submit_nonempty']['count']/totals['graph']['count'],'dispatches':totals['all_dispatch']['count'],'build_nodes':totals['build_node']['count'],'submit_cpu_ms_per_generation':totals['submit_nonempty']['cpu_ns']/len(rr)/1e6,'graph_cpu_ms_per_generation':totals['graph']['cpu_ns']/len(rr)/1e6,'wait_cpu_ms_per_generation':totals['wait_fence']['cpu_ns']/len(rr)/1e6}
assert all(out[100][m]['dispatches']==out[400][m]['dispatches']and out[100][m]['graphs']==out[400][m]['graphs']and out[100][m]['build_nodes']==out[400][m]['build_nodes']for m in ['control','pad'])
report=dict(profiles=out,counts_match_except_submissions=True,scope='Intrusive CPU/wall profiles on separate runs with same9generations and alternating Q3control/pad. Counts compare work; CPU costs include timers and different background load. No throughput inference and no sum of nested scopes.')
(p/'submission-count-profile.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
