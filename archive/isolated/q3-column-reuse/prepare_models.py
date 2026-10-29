from pathlib import Path
import shutil
p=Path(__file__).resolve().parent;b=p.parent;q=b/'q3-pad112';sd=p/'model-shaders';sd.mkdir(exist_ok=True)
shutil.copy2(p/'reuse_subgroup_no_shmem.spv',sd/'pad16_subgroup_no_shmem.spv');shutil.copy2(q/'qualified-20261029/shaders/repack.spv',sd/'repack.spv')
names=[]
for suffix in ['model32','prompts128','kv64','boundary128']:
 s=(b/('run_gdn_reader_'+suffix+'.py')).read_text().replace("p=base/'native-gdn-reader-index'","p=base/'q3-column-reuse'").replace("host=p/'host'","host=base/'q3-pad112/qualified-20261029'")
 s=s.replace("assets=[", "assets=[p/'build.json',p/'model-shaders/pad16_subgroup_no_shmem.spv',p/'model-shaders/repack.spv',")
 s=s.replace("json.loads((p/'build.json').read_text())['library_sha256']","'4e1381cd1f5d3e047431d3cc5fbded37e72c840a1388559d0dcade1c531d03a3'")
 s=s.replace("('verify400',8,2),('index400',8,1)","('verify400',8,0),('index400',8,0)").replace("('verify400',400,2),('index400',400,1)","('verify400',400,0),('index400',400,0)")
 s=s.replace("for reader_mode in [2,1]:","for reader_mode in [0]:").replace("label='reader'+str(reader_mode)","label='reuse400'")
 # Frozen padded control only in short audit; longer audits candidate plus fresh/historical native reference.
 s=s.replace("GGML_VK_Q3_PAD112_DIR=str(base/'q3-pad112/qualified-20261029/shaders')","GGML_VK_Q3_PAD112_DIR=str(base/'q3-pad112/qualified-20261029/shaders' if mode=='verify400' else p/'model-shaders')" if suffix!='prompts128' else "GGML_VK_Q3_PAD112_DIR=str(p/'model-shaders')")
 s=s.replace('verify400','frozen400').replace('index400','reuse400')
 s=s.replace("'arms':4","'arms':2").replace('GDNreader-index modes2oracle and1release','Q3 explicit column-reuse shader with frozen host/cap400').replace('GDNreader-index modes2oracle and1release','Q3 column-reuse').replace('GDN_READER_','Q3_COLUMN_REUSE_')
 # Reader oracle fields inherited as zero; remove inactive opt-in env entirely.
 s='\n'.join(line for line in s.split('\n')if "trial['GGML_VK_GDN_READER_INDEX']="not in line or ';'in line)
 s=s.replace("trial['GGML_VK_GDN_READER_INDEX']=str(indexmode);",'')
 name='run_q3_column_reuse_'+suffix+'.py';(b/name).write_text(s);names.append(name)
f=b/'run_private_guarded_batch.py';s=f.read_text().replace('allowed={','allowed={'+','.join(repr(n)for n in names)+',',1);f.write_text(s)
