from pathlib import Path
p=Path(__file__).resolve().parent;b=p.parent
s=(b/'run_q3_column_reuse_timing.py').read_text().replace("project=base/'q3-column-reuse'","project=base/'q3-pair-glu'").replace("out=project/'timing512'","out=project/'model-timing512'")
s=s.replace("project/name/'comparison.json'","project/('host-'+name)/'comparison.json'")
a=s.index("assert hashlib.sha256((project/'model-shaders/");z=s.index('assets=',a)
s=s[:a]+'''assert hashlib.sha256((project/'host/bin/libggml-vulkan.so.0.27.0').read_bytes()).hexdigest()==json.loads((project/'host-build.json').read_text())['library_sha256']
for folder in ['host-model32','host-prompts128','host-populated-kv64','host-boundary128']:
 rr=json.loads((project/folder/'checks.json').read_text());active=[v for v in rr if v.get('pair_mode')==1];assert active and all(v['pair_calls']>100 for v in active)
'''+s[z:]
s=s.replace("project/'model-shaders/pad16_subgroup_no_shmem.spv',project/'model-shaders/repack.spv',", "project/'pair_subgroup_no_shmem.spv',project/'host-build.json',project/'host/bin/libggml-vulkan.so.0.27.0',")
s=s.replace("project/'TIMING-PLAN.md'","project/'MODEL-TIMING-PLAN.md'").replace("project/'build.json'","project/'shader-build.json'")
s=s.replace("mode_frozen='qualified shader',mode_reuse='explicit column reuse shader'","mode_frozen='preservedqualifiedQ3/cap400',mode_reuse='privatehost/boundedpairGLU'")
s=s.replace('selected_host=frozen',"selected_host=frozen if mode=='frozen'else project/'host'")
s=s.replace("GGML_VK_Q3_PAD112_DIR=str(project/'model-shaders' if mode=='reuse' else frozen/'shaders')","GGML_VK_Q3_PAD112_DIR=str(frozen/'shaders')")
needle=" before_driver=set(subprocess.run";s=s.replace(needle," if mode=='reuse':trial['GGML_VK_PAIR_GLU_SHADER']=str(project/'pair_subgroup_no_shmem.spv')\n"+needle)
s=s.replace('Fixed24frozen-versus-columnreuse512token underload A/B. Same qualifiedhost/cap400,onlyprivateQ3shader differs.', 'Fixed24frozen-versus-boundedpairGLU512token underload A/B. Preservedqualifiedhost/cap400 versusprivatepairhost,samefrozenpaddedQ3shaders/cap400;oneadditionalpairshader.')
s=s.replace('Same preserved frozen library/cap400;only Q3shader directory differs. Primary increment versuspreservedqualifiedQ3/cap400;not directstock.', 'PreservedfrozenQ3/cap400 versusprivateboundedpairGLUhost/cap400,samepaddedweightcache/nativeactivationpolicy;additionalpairshader. Primaryincrementversuspreservedqualifiedconfig,notdirectstock.')
s=s.replace('reuse','fused').replace('Q3_COLUMN_REUSE_CONFIRMATION','Q3_PAIR_GLU_MODEL_DISCOVERY')
(b/'run_q3_pair_glu_model_timing.py').write_text(s)
f=b/'run_private_guarded_batch.py';f.write_text(f.read_text().replace('allowed={',"allowed={'run_q3_pair_glu_model_timing.py',",1))
