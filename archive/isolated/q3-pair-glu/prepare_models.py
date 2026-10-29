from pathlib import Path
p=Path(__file__).resolve().parent;b=p.parent
for suffix in ['model32','prompts128','kv64','boundary128']:
 s=(b/('run_gdn_reader_'+suffix+'.py')).read_text().replace("p=base/'native-gdn-reader-index'","p=base/'q3-pair-glu'")
 for folder in ['model32','prompts128','populated-kv64','boundary128']:s=s.replace("out=p/'"+folder+"'","out=p/'host-"+folder+"'")
 s=s.replace("p/'build.json'","p/'host-build.json'").replace("assets=[", "assets=[p/'host-build.json',p/'pair_subgroup_no_shmem.spv',base/'q3-pad112/qualified-20261029/bin/libggml-vulkan.so.0.27.0',")
 s=s.replace("[('stock400',0,0),('verify400',8,2),('index400',8,1)]","[('stock400',0,0),('frozen400',8,0),('verify400',8,0),('index400',8,1)]")
 s=s.replace("[('stock400',400,0),('verify400',400,2),('index400',400,1)]","[('stock400',400,0),('verify400',400,0),('index400',400,1)]")
 s=s.replace("selected_host=stock if mode=='stock400'else host", "selected_host=stock if mode=='stock400'else base/'q3-pad112/qualified-20261029' if mode=='frozen400'else host")
 s=s.replace("trial['GGML_VK_GDN_READER_INDEX']=str(indexmode);", "trial['GGML_VK_PAIR_GLU_AUDIT']='1';\n if indexmode:trial['GGML_VK_PAIR_GLU_SHADER']=str(p/'pair_subgroup_no_shmem.spv')\n ")
 s=s.replace(" trial['GGML_VK_GDN_READER_INDEX']=str(reader_mode)", " trial['GGML_VK_PAIR_GLU_AUDIT']='1'\n if reader_mode:trial['GGML_VK_PAIR_GLU_SHADER']=str(p/'pair_subgroup_no_shmem.spv')")
 s=s.replace(' for reader_mode in [2,1]:',' for reader_mode in [0,1]:')
 # The two-prompt body needs the existing two-space nesting.
 if suffix=='prompts128':s=s.replace("\n if reader_mode:trial", "\n  if reader_mode:trial")
 s=s.replace("('verify400',400,2)","('verify400',400,0)")
 if suffix=='model32':
  s=s.replace("['stock400','verify400','index400']","['stock400','frozen400','verify400','index400']").replace("'arms':3","'arms':4")
 s=s.replace('verify400','inactive400').replace('index400','active400').replace("label='reader'+str(reader_mode)","label='active400'if reader_mode else'inactive400'")
 # Old reader verification branch is dead (modes0/1); reader-oracle fields remain zero.
 s=s.replace('reader_mode=', 'pair_mode=').replace('if pair_mode==2:','if reader_mode==2:').replace('GDNreader-index modes2oracle and1release','boundedQ3pairGLU inactive/active').replace('GDN_READER_','Q3_PAIR_GLU_')
 if suffix=='prompts128':
  needle='  row=dict(case=case,';insert="  pair_calls=len(re.findall(r'^PAIR_GLU_DISPATCH ',text,re.M))\n  assert pair_calls>100 if reader_mode else pair_calls==0\n"
  s=s.replace(needle,insert+needle+'pair_calls=pair_calls,')
 else:
  needle=' row=dict(mode=mode,';flag='indexmode'if suffix=='model32'else'reader_mode';insert=" pair_calls=len(re.findall(r'^PAIR_GLU_DISPATCH ',text,re.M))\n assert pair_calls>100 if "+flag+" else pair_calls==0\n"
  s=s.replace(needle,insert+needle+'pair_calls=pair_calls,')
 # Replacing keyword reader_mode above must not change local loop/conditional names.
 name='run_q3_pair_glu_'+suffix+'.py';(b/name).write_text(s)
f=b/'run_private_guarded_batch.py';s=f.read_text().replace('allowed={','allowed={'+','.join(repr('run_q3_pair_glu_'+x+'.py')for x in ['model32','prompts128','kv64','boundary128'])+',',1);f.write_text(s)
