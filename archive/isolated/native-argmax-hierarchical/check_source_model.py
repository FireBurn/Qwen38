"""Exact native argmax ordering versus per-lane chunk summaries; CPU only."""
from itertools import product
from pathlib import Path
import json, math, random

def native(a, b):
    v=[a[i] if i<len(a) else -3.402823466e38 for i in range(b)]
    ix=list(range(b))
    for lane in range(b):
        for i in range(lane+b,len(a),b):
            if a[i]>v[lane]:v[lane],ix[lane]=a[i],i
    return tree(v,ix,len(a),b)

def tree(v,ix,n,b):
    step=b//2
    while step:
        for lane in range(step):
            if lane+step<n and v[lane]<v[lane+step]:v[lane],ix[lane]=v[lane+step],ix[lane+step]
        step//=2
    return ix[0]

def chunked(a,b,c):
    # Each chunk produces a max per native lane; skip NaNs after each lane's
    # initial element because strict '>' ignores them. Store earliest index on ties.
    summaries=[]
    for start in range(0,len(a),c):
        z=[None]*b
        for i in range(start,min(start+c,len(a))):
            if i<b or math.isnan(a[i]):continue
            lane=i%b; old=z[lane]
            if old is None or a[i]>old[0] or (a[i]==old[0] and i<old[1]):z[lane]=(a[i],i)
        summaries.append(z)
    v=[a[i] if i<len(a) else -3.402823466e38 for i in range(b)];ix=list(range(b))
    for lane in range(b):
        for z in summaries:
            pair=z[lane]
            if pair is not None and pair[0]>v[lane]:v[lane],ix[lane]=pair
    return tree(v,ix,len(a),b)

vals=[-math.inf,-1.,-0.,0.,1.,math.inf,math.nan];checks=0
for b in (2,4,8):
 for n in range(1,7):
  for a in product(vals,repeat=n):
   expected=native(a,b)
   for c in (1,3,7):
    got=chunked(a,b,c)
    assert got==expected,(a,b,c,expected,got)
    checks+=1
rng=random.Random(1907)
for _ in range(5000):
 b=rng.choice((2,4,8,32,64));n=rng.randint(1,1024);a=[rng.choice(vals) for _ in range(n)];expected=native(a,b)
 for c in (1,7,31,64,257):
  assert chunked(a,b,c)==expected
  checks+=1
out={'all_pass':True,'checks':checks,'scope':'CPU transcription only; ordered per-native-lane chunk maxima with native scan initializer and native reduction tree, including NaNs, infinities, signed zeros and ties. No GPU implementation, model correctness, or performance claim.'}
Path(__file__).with_name('source-model-result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
