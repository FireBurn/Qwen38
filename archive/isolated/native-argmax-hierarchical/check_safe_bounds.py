"""CPU arithmetic sanity check for proposed guard, not a GPU correctness test."""
import json,random
from pathlib import Path
U=(1<<32)-1

def eligible(k,rows):
    if not(2048<=k<=U-2047 and rows>0 and rows<=U//k):return False
    chunks=(k+2047)//2048
    return chunks<=65535 and rows<=65535 and rows*chunks*512<=64*1024*1024

tests=[(2047,1),(2048,1),(2049,5),(248320,1),(248320,5),(U,1),(U-2047,1),(1<<63,2),(2048,1<<55),(4096,0)]
r=random.Random(42)
for _ in range(100000):tests.append((r.randrange(1,1<<36),r.randrange(0,1<<20)))
accepted=0
for k,rows in tests:
 if eligible(k,rows):
  accepted+=1;chunks=(k+2047)//2048
  assert k*rows<=U and (chunks-1)*2048+2048<=U and rows*chunks*64*8<=64*1024*1024
assert eligible(248320,1) and eligible(248320,5)
assert not eligible(U,1) and not eligible(2048,1<<55)
out={'all_pass':True,'checks':len(tests),'accepted':accepted,'scope':'Python arithmetic model for proposed guard, assumed 65535 workgroup limits. Not a compiled backend or GPU test.'}
Path(__file__).with_name('safe-bounds-result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
