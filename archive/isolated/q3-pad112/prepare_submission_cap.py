from pathlib import Path
p=Path(__file__).resolve().parent;b=p.parent
s=(b/'run_q3_pad112_guard_v2_model32.py').read_text().replace("out=p/'guard-v2-model32'","out=p/'submission-cap-model32'").replace("host=p/'host-fast-guard-v2'","host=p/'qualified-20261029'")
s=s.replace('for mask in [0,8]:\n assert','for cap in [100,200,400]:\n mask=8\n assert',1).replace("label='mask'+str(mask)","label='cap'+str(cap)").replace("trial=env.copy();binary=","trial=env.copy();trial['GGML_VK_MAX_NODES_PER_SUBMIT']=str(cap);binary=").replace('GGML_VK_Q3_PAD112_DIR=str(p)','GGML_VK_Q3_PAD112_DIR=str(host/\'shaders\')').replace('row=dict(mask=mask,','row=dict(cap=cap,mask=mask,')
s=s.replace("(out/'mask0.bin')","(out/'cap100.bin')").replace("'arms':2","'arms':3").replace("['mask'+str(i)+'.bin'for i in [0,8]]","['cap'+str(i)+'.bin'for i in [100,200,400]]").replace("for mask in [0,8]:(out/('mask'+str(mask)+'.bin')).unlink()","for cap in [100,200,400]:(out/('cap'+str(cap)+'.bin')).unlink()")
s=s.replace('native/paddedQ3 immutablecache,stockactivationpolicy,16fusiongroups','frozen paddedQ3 immutablecache,stockactivationpolicy,nodecaps100/200/400').replace('PRODUCTION_NATIVE_FUSION_MODEL_TARGET_LOGITS_ALL_EXACT','SUBMISSION_CAP_MODEL_TARGET_LOGITS_ALL_EXACT')
(b/'run_q3_submission_cap_model32.py').write_text(s)
s=(b/'run_q3_pad112_combination_screen.py').read_text().replace("out=project/'fusion-screen512'","out=project/'submission-cap-screen512'")
a=s.index("assert json.loads((project/'fusion-options-quant32");z=s.index('(out/\'assets.json\')',a)
s=s[:a]+'''qualified=json.loads((project/'submission-cap-model32/comparison.json').read_text());assert qualified['all_requested_target_logit_bits_identical'] and qualified['all_tokens_and_counters_identical']
assets=[Path(__file__),project/'qualified-20261029/manifest.json',project/'qualified-20261029/bin/libggml-vulkan.so.0.27.0',project/'qualified-20261029/shaders/pad16_subgroup_no_shmem.spv',project/'qualified-20261029/shaders/repack.spv',base/'mtp-production-throughput/model-bench',base/'mtp-production-throughput/runner.cpp',stock/'bin/libllama.so.0.7.0',stock/'bin/libllama-common.so.0.7.0',driver/'libvulkan_radeon.so']
(out/'protocol.json').write_text((project/'submission-cap-plan.json').read_text())
'''+s[z:]
a=s.index("modes=['frozen'");z=s.index('runtime_lib=',a);s=s[:a]+"modes=['cap100','cap200','cap400'];sequence=modes+list(reversed(modes));rows=[]\n"+s[z:]
a=s.index(' selected_host=');z=s.index(' before_driver=',a)
s=s[:a]+''' selected_host=project/'qualified-20261029'
 trial.update(LD_LIBRARY_PATH=str(selected_host/'bin')+':'+str(stock/'bin')+':'+str(base/'mtp-head-bound-audit/driver-deps')+':'+str(driver),EXPECTED_VK_BACKEND_PATH=str(selected_host/'bin/libggml-vulkan.so.0.27.0'),EXPECTED_LLAMA_CORE_PATH=str(stock/'bin/libllama.so.0.7.0'),EXPECTED_LLAMA_COMMON_PATH=str(stock/'bin/libllama-common.so.0.7.0'),MESA_SHADER_CACHE_DIR=str(project/'model-timing-cache-pad'),radv_enable_transfer_queue='false',GGML_VK_MAX_NODES_PER_SUBMIT=mode[3:])
 trial.update(GGML_VK_Q3_PAD112_ARENA='1',GGML_VK_Q3_PAD112_DIR=str(selected_host/'shaders'),GGML_VK_Q3_PAD112_IMMUTABLE='1')
'''+s[z:]
s=s.replace("max(['both','fuse','quant']","max(['cap200','cap400']").replace('Fixed10arm','Fixed6arm').replace('Separate fixed36arm confirmation against frozen andstock','Separate fixed24arm confirmation against frozen cap100').replace('FUSION_COMBINATION_SCREEN_COMPLETE','SUBMISSION_CAP_SCREEN_COMPLETE')
s='\n'.join(v.rstrip()for v in s.splitlines())+'\n';(b/'run_q3_submission_cap_screen.py').write_text(s)
f=b/'run_private_guarded_batch.py';s=f.read_text().replace("'run_q3_pad112_host_profile_v2.py'","'run_q3_pad112_host_profile_v2.py','run_q3_submission_cap_model32.py','run_q3_submission_cap_screen.py'",1);f.write_text(s)
