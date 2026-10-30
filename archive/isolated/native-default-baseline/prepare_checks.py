from pathlib import Path
import json,hashlib,re
p=Path(__file__).resolve().parent;b=p.parent;frozen=b/'q3-pad112/qualified-20261029';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'build.json').write_text(json.dumps(dict(library_sha256=sha(frozen/'bin/libggml-vulkan.so.0.27.0'),scope='Unmodifiedstockdefault100,stock400,andfrozenQ3default400;nativeallocation/queue/suballocationdefaults.Nobuild.'),indent=2)+'\n')
clear="[trial.pop(k,None)for k in ['GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM','GGML_VK_PREFER_HOST_MEMORY','GGML_VK_ALLOW_GRAPHICS_QUEUE','GGML_VK_SUBALLOCATION_BLOCK_SIZE']];trial.pop('GGML_VK_MAX_NODES_PER_SUBMIT',None)if cap==100 else trial.update(GGML_VK_MAX_NODES_PER_SUBMIT=str(cap))"
for suffix in ['model32','prompts128','kv64','boundary128']:
 s=(b/('run_native_rebar_'+suffix+'.py')).read_text().replace("p=base/'native-rebar-input'","p=base/'native-default-baseline'")
 if suffix=='model32':
  s=s.replace("[('stock400',0,0),('frozen400',8,0),('mapped400',8,1)]","[('stock100',0,0),('stock400',0,0),('q3_400',8,1)]").replace(' cap=400',' cap=100 if mode==\'stock100\'else400').replace('else400','else 400')
  s=s.replace("selected_host=stock if mode=='stock400'else base/'q3-pad112/qualified-20261029'if mode=='frozen400'else host","selected_host=stock if mask==0 else host")
  s=s.replace("trial.pop('GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM',None)if indexmode==1 else None",clear)
  s=s.replace("['stock400','frozen400','mapped400']","['stock100','stock400','q3_400']").replace("out/'stock400.bin'","out/'stock100.bin'")
 elif suffix=='prompts128':
  s=s.replace(' for reader_mode in [0,1]:\n  mask=8'," for mode,mask,cap in [('stock100',0,100),('stock400',0,400),('q3_400',8,400)]:\n  reader_mode=int(mask==8);selected_host=stock if mask==0 else host")
  s=s.replace("label='mapped'+str(reader_mode)","label=mode").replace("str(host/'bin')","str(selected_host/'bin')").replace("str(host/'bin/libggml-vulkan.so.0.27.0')","str(selected_host/'bin/libggml-vulkan.so.0.27.0')")
  s=s.replace("trial.pop('GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM',None)if reader_mode==1 else None",clear)
  s=s.replace("assert 'Q3_PAD112_CACHE 'in text,'Arena not used'","assert ('Q3_PAD112_CACHE 'in text)if mask==8 else True,'Arena not used'")
  s=s.replace('row=dict(case=case,','row=dict(case=case,mode=mode,cap=cap,').replace("'arms':4","'arms':6")
 else:
  s=s.replace("[('stock400',400,0),('frozen400',400,0),('mapped400',400,1)]","[('stock100',100,0),('stock400',400,0),('q3_400',400,1)]")
  s=s.replace("mask=0 if mode=='stock400'else 8","mask=0 if mode in ['stock100','stock400']else 8").replace("selected_host=stock if mode=='stock400'else host","selected_host=stock if mask==0 else host")
  s=s.replace("trial.pop('GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM',None)if reader_mode==1 else None",clear)
  s=s.replace("if mode!='stock400'else True","if mask==8 else True").replace("['stock400','frozen400','mapped400']","['stock100','stock400','q3_400']").replace("out/'stock400.bin'","out/'stock100.bin'")
 s=s.replace('row=dict(case=case,mode=mode,cap=cap,','row=dict(effective_legacy_overrides={k:trial.get(k)for k in [\"GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM\",\"GGML_VK_PREFER_HOST_MEMORY\",\"GGML_VK_ALLOW_GRAPHICS_QUEUE\",\"GGML_VK_SUBALLOCATION_BLOCK_SIZE\"]},case=case,mode=mode,cap=cap,')
 s=s.replace('mapped_vram_requested=','candidate_q3=').replace('nativeunmappedversusmappedVRAM','stocknative-default100/400versusQ3default400').replace('NATIVE_REBAR_INPUT','NATIVE_DEFAULT_BASELINE')
 # Pin exact effective runtime mode with each result.
 marker="scope='Productionaa8";s=s.replace(marker,"effective_legacy_overrides={k:trial.get(k)for k in ['GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM','GGML_VK_PREFER_HOST_MEMORY','GGML_VK_ALLOW_GRAPHICS_QUEUE','GGML_VK_SUBALLOCATION_BLOCK_SIZE']},"+marker)
 s=s.replace("assert 'NQ_PLAN_EXACT'in text", "assert ('NQ_PLAN_EXACT'in text)if mask==8 else True")
 s=s.replace('assets=[',"stock_manifest=json.loads((stock/'manifest.json').read_text());stock_libraries=[stock/'bin'/r['name']for r in stock_manifest['files']if r['name'].startswith('lib')]\nfor r in stock_manifest['files']:\n if r['name'].startswith('lib'):assert sha(stock/'bin'/r['name'])==r['sha256']\nassets=[*stock_libraries,",1)
 (b/('run_native_default_'+suffix+'.py')).write_text(s)
f=b/'run_private_guarded_batch.py';s=f.read_text().replace('allowed={','allowed={'+','.join(repr('run_native_default_'+v+'.py')for v in ['model32','prompts128','kv64','boundary128'])+',',1);f.write_text(s)
