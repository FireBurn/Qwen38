from pathlib import Path
import json,hashlib,subprocess,shutil,difflib
p=Path(__file__).resolve().parent;b=p.parent;q=b/'q3-pad112/qualified-20261029';wide=b/'native-argmax-review';h=p/'host';h.mkdir(exist_ok=True);(h/'bin').mkdir(exist_ok=True);sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
manifest=json.loads((q/'manifest.json').read_text())
for name,digest in manifest['files'].items():assert sha(q/name)==digest,name
parent=json.loads((q/'build.json').read_text());tested=json.loads((wide/'wide-build.json').read_text());assert sha(wide/'argmax-wide.spv')==tested['shader_sha256']and sha(wide/'wide-host/ggml-vulkan.cpp')==tested['source_sha256']
for f in (q/'source').glob('*.h'):shutil.copy2(f,h/f.name)
s=(q/'source/ggml-vulkan.cpp').read_text();ws=(wide/'wide-host/ggml-vulkan.cpp').read_text();start=ws.index('    static const std::vector<uint32_t> wide_argmax_code=');end=ws.index('\n',ws.index('    ggml_vk_create_pipeline(device, device->pipeline_argmax_f32,',start))+1;block=ws[start:end]
line=next(line for line in s.splitlines(keepends=True)if 'ggml_vk_create_pipeline(device, device->pipeline_argmax_f32,'in line);assert s.count(line)==1;s=s.replace(line,block);(h/'ggml-vulkan.cpp').write_text(s);(p/'host.patch').write_text(''.join(difflib.unified_diff((q/'source/ggml-vulkan.cpp').read_text().splitlines(keepends=True),s.splitlines(keepends=True),fromfile='qualifiedQ3/ggml-vulkan.cpp',tofile='combined/ggml-vulkan.cpp')))
cmds=json.loads((q/'build-argv.json').read_text());old=Path(next(v for v in cmds[0]if v.endswith('/ggml-vulkan.cpp'))).parent;root='${CLAUDE_WORKSPACE}/prodtree'
commands=[[v.replace(str(old),str(h)).replace('-I'+root+'/build/ggml/src/ggml-vulkan','-I'+str(wide/'generated-headers')).replace('-I'+root+'/','-I'+str(wide/'pinned-headers')+'/')for v in cmd]for cmd in cmds]
objects=[Path(v)for v in commands[-1]if v.endswith('.o')and v!=str(h/'ggml-vulkan.cpp.o')]
widepins=json.loads((wide/'wide-build-inputs.json').read_text())
for f in objects:
 if f.name in parent['reused_objects']:assert sha(f)==parent['reused_objects'][f.name],f
 else:assert str(f)in widepins and sha(f)==widepins[str(f)],f
assets=[q/'manifest.json',q/'build.json',q/'source/ggml-vulkan.cpp',*(q/'source').glob('*.h'),wide/'wide-build.json',wide/'argmax-wide.spv',wide/'wide-host/ggml-vulkan.cpp',*objects,*[f for folder in [wide/'pinned-headers',wide/'generated-headers']for f in folder.rglob('*')if f.is_file()]]
(p/'inputs.json').write_text(json.dumps({str(f):sha(f)for f in assets},indent=2)+'\n');(h/'build-argv.json').write_text(json.dumps(commands,indent=2)+'\n')
for cmd in commands:subprocess.run(cmd,check=True,cwd=h)
lib=h/'bin/libggml-vulkan.so.0.27.0'
for name in ['libggml-vulkan.so','libggml-vulkan.so.0']:
 f=h/'bin'/name
 if not f.exists():f.symlink_to(lib.name)
(p/'build.json').write_text(json.dumps(dict(library_sha256=sha(lib),source_sha256=sha(h/'ggml-vulkan.cpp'),context_header_sha256=sha(h/'ggml-vulkan-types.h'),parent_context_header_identical=sha(h/'ggml-vulkan-types.h')==sha(q/'source/ggml-vulkan-types.h'),shader_sha256=sha(wide/'argmax-wide.spv'),matching_extended_context_objects=parent['reused_objects'],scope='Newprivatecombinedhost:qualifiedQ3parent+exacttestedargmaxselectionblock. Originalcontextlayout/matchingobjectsretained,noothernewfeature. NotGPU/model/performancequalified.'),indent=2)+'\n');print('PAD_WIDE_PRIVATE_HOST_BUILT')
