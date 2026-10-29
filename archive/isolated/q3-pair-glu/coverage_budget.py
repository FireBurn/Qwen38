from pathlib import Path
import json,re,collections
p=Path(__file__).resolve().parent;seen={}
for line in(p/'model32/audit400.log').read_text().splitlines():
 if not line.startswith('PAIR_GRAPH '):continue
 fields=dict(re.findall(r'(\w+)=(\S+)',line))
 if fields.get('C')!='2':continue
 seen[fields['name']]=fields
counts=collections.Counter((r['type_a'],r['type_b'])for r in seen.values());profiles=json.loads((p.parent/'native-gdn-reader-index/gpu-profile-summary.json').read_text());profile=next(r for r in profiles if r['grouped']);families=[]
for row in profile['families']:
 name=row['name']
 if name.count('m=17408 n=2 k=5120')==2 and name.count('MUL_MAT_VEC')==2:families.append(row)
q3=next(x for x in families if'q3_K'in x['name']);micro=json.loads(sorted((p/'timing').glob('*/analysis.json'))[-1].read_text());saving=-micro['primary']['time_change_percent'];resident=json.loads(sorted((p/'resident').glob('*/analysis.json'))[-1].read_text())
r=dict(unique_C2_FFN_pairs=len(seen),quant_pair_counts={a+'/'+b:n for(a,b),n in counts.items()},prior_intrusive_profile_pair_groups=families,operator_primary_time_saving_percent=saving,rough_Q3_total_GPU_time_saving_percent=q3['share_percent']*saving/100,resident_matched_full_generation=resident['matched_full_generation'],scope='Rough budget only: multiply prior intrusive short-context groupedGPU-time share by separately measured operator time reduction,assumingunchangedothercosts/nooverlapchanges. These are differentdiagnostics,not anendtoendprediction/proof orstackingqualifiedspeedups. Includesprompt/warmprofile;CPU/queue/DVFS effects omitted. Aim is toidentifylimitedcoverage:optimizing~15%ofrecordedGPUtimeby~4% suggestsroughly0.6%totalGPU-time scale,consistentwithsmallresidentestimatebutnot proof ofmechanism. Do notclaimmeasuredGPUbottleneckoractualbasegain.')
(p/'coverage-budget.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
