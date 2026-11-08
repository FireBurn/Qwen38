from pathlib import Path
import subprocess,json,hashlib,time,struct,traceback
base=Path(__file__).resolve().parent;root=base/'current-server-scope/q3-recenter';out=root/'target-audit-check'/time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());out.mkdir(parents=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assets=[root/'trace-baseline/libggml-vulkan.so.0.28.0',root/'trace-candidate/libggml-vulkan.so.0.28.0',root/'target-audit/libllama.so.0.8.0',base/'current-server-scope/installed-build/bin/libllama-common.so.0.8.0',base/'run_current_q3_target_audit_arm.py',Path(__file__),root/'TARGET-AUDIT-PLAN.md'];hashes={str(p):sha(p) for p in assets};(out/'assets.json').write_text(json.dumps(hashes,indent=2)+'\n');report={'passed':False,'scope':'one seeded DFlash prompt plus warmup with target-logit audit; not speed or general quality qualification'}
try:
 for arm in ('baseline','candidate'):
  assert all(sha(p)==hashes[str(p)] for p in assets),'asset changed';print('starting',arm,flush=True);subprocess.run(['python3','-u',str(base/'run_current_q3_target_audit_arm.py'),arm,str(out)],check=True,timeout=900)
 def read(arm):
  d=out/arm;data=(d/'lattice.bin').read_bytes();offset=0;shapes=[]
  while offset<len(data):
   assert offset+12<=len(data),'partial header';magic,n,w=struct.unpack_from('<III',data,offset);offset+=12;assert magic==0x44464c54 and 1<=n<=5 and 1<=w<=16384,(magic,n,w);size=n*w*4;assert offset+size<=len(data),'partial lattice';offset+=size;shapes.append([n,w])
  assert shapes,'empty lattice';return data,shapes,json.loads((d/'result.json').read_text()),json.loads((d/'identity.json').read_text())
 a,sa,ra,ia=read('baseline');b,sb,rb,ib=read('candidate');report.update({'lattice_sha256':{'baseline':hashlib.sha256(a).hexdigest(),'candidate':hashlib.sha256(b).hexdigest()},'lattice_rows':{'baseline':sa,'candidate':sb},'lattice_exact':a==b,'response_hashes_match':all(ra[x]['response_sha256']==rb[x]['response_sha256'] for x in ('warmup','request')),'model_identities_match':ia['models']==ib['models'],'results':{'baseline':ra,'candidate':rb}});assert report['lattice_exact'],'full lattice bytes differ';assert report['response_hashes_match'],'response hash differs';assert report['model_identities_match'],'model identities changed';assert all(ra[x]['timings'].get('draft_n')==rb[x]['timings'].get('draft_n') and ra[x]['timings'].get('draft_n_accepted')==rb[x]['timings'].get('draft_n_accepted') for x in ('warmup','request')),'draft counters differ';
 def inspect_logits(path):
  count=0; total=0
  with path.open('rb') as f:
   while header:=f.read(16):
    assert len(header)==16,'truncated header'; magic,cols,rows,size=struct.unpack('<4I',header);assert magic==0x51334c47 and cols==248320 and rows>0 and size==cols*rows*4,(magic,cols,rows,size);assert len(f.read(size))==size,'truncated logits';count+=1;total+=rows
  assert count>0,'empty target audit';return {'tensors':count,'rows':total,'bytes':path.stat().st_size,'sha256':sha(path)}
 report['target_logits']={arm:inspect_logits(out/arm/'target-logits.bin') for arm in ('baseline','candidate')};report['target_logits_exact']=report['target_logits']['baseline']==report['target_logits']['candidate'];assert report['target_logits_exact'],'target logits differ';report['passed']=True
except BaseException:
 report['failure']=traceback.format_exc();raise
finally:
 (out/'comparison.json').write_text(json.dumps(report,indent=2)+'\n');print('LATTICE_RESULT',out,json.dumps({k:v for k,v in report.items() if k!='results'}),flush=True)
