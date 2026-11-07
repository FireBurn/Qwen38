from pathlib import Path
import struct,collections,numpy as np,json,sys
p=Path(sys.argv[1])
def read(arm):
 b=(p/(arm+'-nodes.bin')).read_bytes();off=0;out=collections.defaultdict(list);order=[]
 while off<len(b):
  name,ty,*v=struct.unpack_from('<64sI4q4QQ',b,off);off+=140;ne=v[:4];size=v[8];name=name.split(b'\0')[0].decode();assert ty==0 and size==np.prod(ne)*4;out[name].append(np.frombuffer(b,dtype='<f4',count=size//4,offset=off).copy());off+=size
  if name not in order:order.append(name)
 return out,order
a,order=read('baseline');b,_=read('candidate');report={}
for k in order:
 x=np.concatenate(a[k]);y=np.concatenate(b[k]);assert x.shape==y.shape;finite=np.isfinite(x)&np.isfinite(y);delta=np.abs(x-y);report[k]={'count':int(x.size),'bitwise_differences':int(np.sum(x.view(np.uint32)!=y.view(np.uint32))),'max_abs':float(np.max(delta[finite])) if finite.any() else None,'mean_abs':float(np.mean(delta[finite])) if finite.any() else None,'nonfinite_mismatch':int(np.sum(np.isfinite(x)!=np.isfinite(y)))}
result={'execution_order':order,'nodes':report,'scope':'F32 contiguous captures only; baseline concatenated in callback order; no performance claim'};(p/'node-analysis.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
