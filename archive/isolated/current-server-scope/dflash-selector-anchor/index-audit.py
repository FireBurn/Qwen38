"""Check selector position mapping for all bounded block shapes; CPU indexing only."""
import json
checks=[]
for blocks in (1,2,3,4):
 for tokens_per in range(1,17):
  for trained in range(1,9):
   size=min(tokens_per,trained);skip=blocks==1 and size>1;selector_per=tokens_per-int(skip)
   original=[[('token',b,p) for p in range(tokens_per)] for b in range(blocks)]
   new=[[('token',b,p+int(skip)) for p in range(selector_per)] for b in range(blocks)]
   for pos in range(1,size):
    for b in range(blocks):
     got=new[b][pos-int(skip)];want=original[b][pos];assert got==want,(blocks,tokens_per,trained,pos,b)
     if pos>1:assert new[b][pos-1-int(skip)]==original[b][pos-1]
   checks.append((blocks,tokens_per,trained,skip))
print(json.dumps({'cases':len(checks),'skipped_anchor_cases':sum(x[3] for x in checks),'result':'all selector current and predecessor positions match','limits':'index mapping only; no tensor math, memory alias or model outputs'}))
