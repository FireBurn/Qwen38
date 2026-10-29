from pathlib import Path
import re,json,collections
p=Path(__file__).resolve().parent
reports=[]
for d in sorted((p/'gpu-profile32').iterdir()):
 if not(d/'checks.json').exists():continue
 checks=json.loads((d/'checks.json').read_text());assert checks['all_tokens_match_reference']and not checks['new_driver_errors']
 rows=[]
 for line in(d/'run.log').read_text().splitlines():
  m=re.match(r'(.+): (\d+) x ([0-9.e+\-]+) us = ([0-9.e+\-]+) us',line)
  if m:
   name,n,mean,total=m.groups();rows.append(dict(name=name,count=int(n),mean_us=float(mean),total_us=float(total)))
 assert rows
 families=collections.defaultdict(float)
 for r in rows:families[r['name'].split(' dst(')[0]]+=r['total_us']
 broad=collections.defaultdict(float)
 for r in rows:
  name=r['name'];family='matrix-containing' if 'MUL_MAT' in name else 'attention-containing' if 'FLASH_ATTN' in name else 'GDN-containing' if 'GATED_DELTA' in name else 'other'
  broad[family]+=r['total_us']
 total=sum(families.values());report=dict(broad_categories={k:dict(total_us=v,share_percent=100*v/total)for k,v in broad.items()},grouped=checks['grouped'],total_recorded_us=total,families=[dict(name=k,total_us=v,share_percent=100*v/total)for k,v in sorted(families.items(),key=lambda x:-x[1])],rows=rows,scope=checks['scope'])
 (d/'analysis.json').write_text(json.dumps(report,indent=2)+'\n');reports.append(dict(directory=d.name,**report))
(p/'gpu-profile-summary.json').write_text(json.dumps(reports,indent=2)+'\n')
for r in reports:print(r['directory'],'grouped',r['grouped'],r['families'][:12])
