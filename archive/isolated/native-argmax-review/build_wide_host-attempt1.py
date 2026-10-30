from pathlib import Path
import json,hashlib,subprocess,io,tarfile,shutil
p=Path(__file__).resolve().parent;b=p.parent;old=b/'production-native-shaders/host';h=p/'wide-host';h.mkdir(exist_ok=True);(h/'bin').mkdir(exist_ok=True);snap=p/'pinned-headers';snap.mkdir(exist_ok=True)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
raw=subprocess.run(['git','-C','${CLAUDE_WORKSPACE}/prodtree','archive','aa8ab0504deda8ef55958aa2c7ccdee3eab924ca','ggml/src','ggml/include'],capture_output=True,check=True).stdout
with tarfile.open(fileobj=io.BytesIO(raw))as archive:
 for member in archive.getmembers():
  if member.isfile()and member.name.endswith(('.h','.hpp')):archive.extract(member,snap,filter='data')
for f in old.glob('*.h'):shutil.copy2(f,h/f.name)
generated=p/'generated-headers';generated.mkdir(exist_ok=True);original=Path('${CLAUDE_WORKSPACE}/prodtree/build/ggml/src/ggml-vulkan/ggml-vulkan-shaders.hpp');shutil.copy2(original,generated/original.name)
s=(old/'ggml-vulkan.cpp').read_text();needle=next(line for line in s.splitlines()if 'ggml_vk_create_pipeline(device, device->pipeline_argmax_f32,'in line)
helper='''    static const std::vector<uint32_t> wide_argmax_code=[](){
        std::vector<uint32_t> code;const char*path=getenv("GGML_VK_ARGMAX_WIDE_SHADER");if(!path)return code;
        std::ifstream f(path,std::ios::binary|std::ios::ate);GGML_ASSERT(f.good());const auto bytes=f.tellg();GGML_ASSERT(bytes>=20&&uint64_t(bytes)%4==0);code.resize(size_t(bytes)/4);f.seekg(0);f.read((char*)code.data(),bytes);GGML_ASSERT(f.good()&&code[0]==0x07230203u);fprintf(stderr,"ARGMAX_WIDE_MODULE words=%zu\\n",code.size());return code;
    }();
    const bool wide_argmax=!wide_argmax_code.empty()&&device->vendor_id==VK_VENDOR_ID_AMD&&device->properties.deviceID==0x7551&&device->subgroup_size<=256&&device->max_workgroup_size_log2>=8;
'''
replacement=needle.replace('"argmax_f32", argmax_f32_len, argmax_f32_data,','wide_argmax?"argmax_wide_f32":"argmax_f32", wide_argmax?wide_argmax_code.size()*4:argmax_f32_len, wide_argmax?wide_argmax_code.data():argmax_f32_data,')
s=s.replace(needle,helper+replacement);(h/'ggml-vulkan.cpp').write_text(s)
cmds=json.loads((old/'build-argv.json').read_text());root='${CLAUDE_WORKSPACE}/prodtree'
commands=[]
for cmd in cmds:
 commands.append([v.replace(str(old/'host.o'),str(h/'host.o')).replace(str(old/'ggml-vulkan.cpp'),str(h/'ggml-vulkan.cpp')).replace(str(old/'bin'),str(h/'bin')).replace('-I'+root+'/build/ggml/src/ggml-vulkan','-I'+str(generated)).replace('-I'+root+'/', '-I'+str(snap)+'/')for v in cmd])
assets=[old/'ggml-vulkan.cpp',old/'build-argv.json',p/'argmax-wide.comp',p/'argmax-wide.spv',*(Path(v)for v in commands[-1]if v.endswith('.o')and v!=str(h/'host.o')),*(f for f in snap.rglob('*')if f.is_file()),*(h.glob('*.h')),generated/original.name]
(p/'wide-build-inputs.json').write_text(json.dumps({str(f):sha(f)for f in assets},indent=2)+'\n');(h/'build-argv.json').write_text(json.dumps(commands,indent=2)+'\n')
for cmd in commands:subprocess.run(cmd,check=True,cwd=h)
lib=h/'bin/libggml-vulkan.so.0.27.0'
for name in ['libggml-vulkan.so','libggml-vulkan.so.0']:
 f=h/'bin'/name
 if not f.exists():f.symlink_to(lib.name)
(p/'wide-build.json').write_text(json.dumps(dict(library_sha256=sha(lib),shader_sha256=sha(p/'argmax-wide.spv'),source_sha256=sha(h/'ggml-vulkan.cpp'),parent_source_sha256=sha(old/'ggml-vulkan.cpp'),headers_unchanged=True,scope='Opt-in256lane argmax, original specialization preserved asnative tie rank, NaN legacyfallback. No device/context/ABI/header changes. Other originalprivate shader/buffer/debug objects linked readonly. Not GPUqualified/performanceproof.'),indent=2)+'\n')
print('WIDE_ARGMAX_HOST_BUILT')
