from pathlib import Path
import json,shutil,subprocess,hashlib,re,sys
p=Path(__file__).resolve().parent;n=p.parent/'native-fusion-plan';old=n/'timeline-host';h=p/'host';h.mkdir(exist_ok=True);(h/'bin').mkdir(exist_ok=True)
for f in old.glob('*.h'):shutil.copy2(f,h/f.name)
for name in ['ggml-vulkan-buffers.cpp.o','ggml-vulkan-debug.cpp.o']:shutil.copy2(old/name,h/name)
s=(old/'ggml-vulkan.cpp').read_text()
functions=[('ggml_backend_vk_buffer_set_tensor',4,'size'),('ggml_backend_vk_buffer_set_tensor_2d',4,'size*n_copies'),('ggml_backend_vk_buffer_get_tensor',5,'size'),('ggml_backend_vk_buffer_get_tensor_2d',5,'size*n_copies'),('ggml_backend_vk_set_tensor_2d_async',6,'size*n_copies'),('ggml_backend_vk_get_tensor_2d_async',7,'size*n_copies'),('ggml_backend_vk_cpy_tensor_async',8,'ggml_nbytes(src)'),('ggml_backend_vk_buffer_cpy_tensor',9,'ggml_nbytes(src)')]
for name,kind,size in functions:
 matches=list(re.finditer(r'(?:static )?(?:bool|void) '+name+r'\([^;{]*\) \{',s));assert len(matches)==1,(name,len(matches));m=matches[0];s=s[:m.end()]+f'\n    nwt_scope io_trace({kind},{size});'+s[m.end():]
s=re.sub(r'int nfp_mode=nfp_env[^;]+;', 'int nfp_mode=0;', s)
(h/'ggml-vulkan.cpp').write_text(s)
cmds=json.loads((n/'reuse-host/build-argv.json').read_text());cmds=[[v.replace(str(n/'reuse-host'),str(h))for v in c]for c in cmds]
# The unchanged header layout is identical to the qualified timeline/reuse build.
(p/'commands.json').write_text(json.dumps([cmds[0],cmds[-1]],indent=2)+'\n')
runner=(n/'timeline-runner.cpp').read_text().replace('active?\"1\":\"0\"','\"0\"').replace('active?\"active\":\"inactive\"','\"profile\"');(p/'runner.cpp').write_text(runner)
runner_cmd=json.loads((n/'timeline-build.json').read_text())['commands'][-1];runner_cmd=[v.replace(str(n/'timeline-runner.cpp'),str(p/'runner.cpp')).replace(str(n/'timeline-bin/model-bench'),str(p/'bin/model-bench'))for v in runner_cmd];(p/'bin').mkdir(exist_ok=True)
if '--build'not in sys.argv:print('Prepared transfer observer; no compiler or GPU launched');sys.exit(0)
subprocess.run(cmds[0],check=True,cwd=h);subprocess.run(cmds[-1],check=True,cwd=h);subprocess.run(runner_cmd,check=True)
lib=h/'bin/libggml-vulkan.so.0.27.0'
for name in ['libggml-vulkan.so','libggml-vulkan.so.0']:
 if not(h/'bin'/name).exists():(h/'bin'/name).symlink_to(lib.name)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'build.json').write_text(json.dumps(dict(binary_sha256=sha(p/'bin/model-bench'),library_sha256=sha(lib),source_sha256=sha(h/'ggml-vulkan.cpp'),commands=[cmds[0],cmds[-1],runner_cmd],kinds={0:'graph_compute',1:'synchronize',2:'fence_wait',3:'queue_submit',4:'sync_tensor_set',5:'sync_tensor_get',6:'async_tensor_set',7:'async_tensor_get',8:'async_tensor_copy',9:'sync_tensor_copy'},scope='APIbytes/CPUwalltraceonly,nocommands/ownership/mathchanges. Reusefeaturekeptoff. PendingGPUqualification.'),indent=2)+'\n')
