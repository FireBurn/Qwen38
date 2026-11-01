"""Model relevant fixed-width source loads for aligned RADV non-sparse copy; CPU only."""
import json
from pathlib import Path
P=4096
results=[]
for size in (4,8,20):
 for dwords in (1,2,4):
  page_cross=[];past_range=[]
  for start in range(0,P,4):
   span=dwords*4;threads=(size+span-1)//span
   loads=[(start+i*span,start+(i+1)*span) for i in range(threads)]
   if loads[-1][1]>start+size:past_range.append(start)
   if start+size<=P and any(a//P!=(b-1)//P for a,b in loads):page_cross.append(start)
  results.append(dict(bytes=size,dwords_per_thread=dwords,source_offsets_checked=1024,loads_beyond_requested_range=len(past_range),page_crossing_vector_loads=len(page_cross),page_cross_offsets=page_cross))
assert next(r for r in results if r['bytes']==20 and r['dwords_per_thread']==2)['page_cross_offsets']==[4076]
assert next(r for r in results if r['bytes']==20 and r['dwords_per_thread']==1)['page_crossing_vector_loads']==0
out={'assumptions':'4-byte aligned source, destination aligned to thread width, non-sparse raw-address compute copy, 4096-byte pages; simplified NIR source-load geometry only.', 'results':results,'scope':'CPU arithmetic example; no GPU addresses, actual dispatch or compiled ISA captured; does not establish cause of observed fault.'}
Path(__file__).with_name('copy-tail-model.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(results))
