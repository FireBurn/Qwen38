from pathlib import Path
import sys,struct,numpy as np,json
p=Path(sys.argv[1])
def records(arm):
 b=(p/(arm+'-nodes.bin')).read_bytes();o=0;r=[]
 while o<len(b):
  name,ty,*v=struct.unpack_from('<64sI4q4QQ',b,o);o+=140;ne=v[:4];size=v[8];assert ty==0 and size==np.prod(ne)*4;r.append((name.split(b'\0')[0].decode(),np.frombuffer(b,dtype='<f4',count=size//4,offset=o).copy()));o+=size
 return r
a=records('baseline');b=records('candidate');cut=len(b);assert len(a)==2*cut;report=[]
for i,(name,y) in enumerate(b[:10]):
 assert a[i][0]==name and a[i+cut][0]==name;x=np.concatenate((a[i][1],a[i+cut][1]));assert x.shape==y.shape;finite=np.isfinite(x)&np.isfinite(y);delta=np.abs(x-y);report.append({'node':name,'elements':int(x.size),'bitwise_differences':int(np.sum(x.view(np.uint32)!=y.view(np.uint32))),'max_abs':float(np.max(delta[finite])) if finite.any() else None,'mean_abs':float(np.mean(delta[finite])) if finite.any() else None,'nonfinite_mismatch':int(np.sum(np.isfinite(x)!=np.isfinite(y)))})
result={'first_layer':report,'scope':'F32 contiguous captures paired by callback order; intrusive synthetic empty-KV graph'};(p/'analysis.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
