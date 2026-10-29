from pathlib import Path
import json,struct,collections
p=Path(__file__).resolve().parent;cases=['model32','prompts128/coding','prompts128/math','populated-kv64','boundary128'];total=collections.Counter();rows=[]
for name in cases:
 d=p/name/'observer';g=[json.loads(x)for x in(d/'graphs.jsonl').read_text().splitlines()];weights=collections.Counter(x['program_id']for x in g);counts=collections.Counter()
 for i,w in weights.items():
  raw=(d/f'program-{i:04d}.bin').read_bytes();o=0;last=None
  while o<len(raw):
   tag,n=struct.unpack_from('<QQ',raw,o);o+=16;b=raw[o:o+n];o+=n
   if tag in [12,13]:last=None
   if tag!=1:continue
   pipeline,layout,ds=struct.unpack_from('<QQQ',b);q=48;nb=struct.unpack_from('<Q',b,q)[0];q+=8+nb*24;ns=struct.unpack_from('<Q',b,q)[0];q+=8;pc=b[q:q+ns];counts['dispatches']+=w
   if last:
    lp,ll,ld,lpc=last;counts['same_pipeline']+=w*(lp==pipeline);counts['same_pc_exact_layout']+=w*(ll==layout and lpc==pc);counts['same_ds_exact_layout']+=w*(ld==ds and ll==layout)
   last=pipeline,layout,ds,pc
 rows.append(dict(case=name,counts=dict(counts)));total.update(counts)
a=dict(cases=rows,total=dict(total),scope='Repeated consecutive state arguments within observed command-buffer boundaries. Native helper still makes each original API call. Driver may already deduplicate;these counts do not measure CPUcost,GPUcommands eliminated or token gain. No state-call skipping implemented.')
(p/'state-redundancy.json').write_text(json.dumps(a,indent=2)+'\n');print(dict(total))
