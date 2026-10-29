from pathlib import Path
import re,json,hashlib,subprocess,struct
p=Path(__file__).resolve().parent;b=p.parent;sh=b.parent/'production/llama.cpp/ggml/src/ggml-vulkan/vulkan-shaders'
files=set()
def visit(n):
 if n in files:return
 files.add(n)
 for q in re.findall(r'^\s*#include\s+"([^"]+)"',(sh/n).read_text(),re.M):visit(q)
visit('mul_mat_vec_q6_k.comp');records=[]
for variant in ['native','pad16','pad32']:
 out=p/variant;out.mkdir(exist_ok=True)
 for n in files:(out/n).write_bytes((sh/n).read_bytes())
 if variant!='native':
  f=out/'types.glsl';s=f.read_text()
  for name in ['block_q6_K','block_q6_K_packed16']:
   m=re.search(r'(struct '+name+r'\s*\{.*?)(\n\};)',s,re.S);assert m
   s=s[:m.end(1)]+'\n    uint16_t alignment_pad;'+s[m.end(1):]
  if variant=='pad32':
   decl='''struct block_q6_K_packed32 {
    uint ql[32];
    uint qh[16];
    int8_t scales[16];
    float16_t d;
    uint16_t alignment_pad;
};
'''
   s=s.replace('#if defined(DATA_A_Q6_K)',decl+'\n#if defined(DATA_A_Q6_K)',1).replace('#define A_TYPE_PACKED16 block_q6_K_packed16','#define A_TYPE_PACKED16 block_q6_K_packed16\n#define A_TYPE_PACKED32 block_q6_K_packed32',1)
  f.write_text(s)
  if variant=='pad32':
   f=out/'mul_mat_vec_q6_k.comp';s=f.read_text()
   for name,field,offset,add in [('ql0','ql','ql_offset',''),('ql32','ql','ql_offset',' + 8'),('qh','qh','qh_offset','')]:
    s,n=re.subn(r'const uint32_t '+name+r'_u32 =[^;]+;','const uint32_t '+name+'_u32 = data_a_packed32[ib0 + i].'+field+'['+offset+' / 4'+add+'];',s);assert n==1
   f.write_text(s)
 for suffix,extra in [('',[]),('_subgroup',['USE_SUBGROUP_ADD=1']),('_subgroup_no_shmem',['USE_SUBGROUP_ADD_NO_SHMEM=1'])]:
  target=p/(variant+suffix+'.spv');defines=['DATA_A_Q6_K=1','FLOAT_TYPE=float','FLOAT_TYPEV2=vec2','B_TYPE=float','B_TYPEV2=vec2','B_TYPEV4=vec4','D_TYPE=float']+extra
  cmd=['glslc','-fshader-stage=compute','--target-env=vulkan1.2','-O','-I'+str(out),*['-D'+v for v in defines],str(out/'mul_mat_vec_q6_k.comp'),'-o',str(target)]
  subprocess.run(cmd,check=True);subprocess.run(['spirv-val','--target-env','vulkan1.2',str(target)],check=True)
  asm=subprocess.check_output(['spirv-dis',str(target)],text=True);(p/(target.stem+'.spvasm')).write_text(asm)
  strides=[int(x)for x in re.findall(r'OpDecorate .*? ArrayStride (\d+)',asm)]
  assert (210 if variant=='native'else 212)in strides
  if variant!='native':assert 210 not in strides
  records.append(dict(variant=variant,reduction=suffix,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),bytes=target.stat().st_size,array_strides=strides,command=cmd))
lib=b/'production-baseline-aa8/bin/libggml-vulkan.so.0.27.0';raw=lib.read_bytes();assert raw[:6]==b'\x7fELF\x02\x01'
phoff=struct.unpack_from('<Q',raw,32)[0];ents,num=struct.unpack_from('<HH',raw,54);proof=[]
nm=subprocess.check_output(['nm','-S','--defined-only',str(lib)],text=True)
for suffix in ['','_subgroup','_subgroup_no_shmem']:
 name='mul_mat_vec_q6_k_f32_f32'+suffix+'_data';m=re.search(r'^([0-9a-f]+) ([0-9a-f]+) \w '+name+r'$',nm,re.M);assert m
 addr,size=[int(x,16)for x in m.groups()];embedded=None
 for i in range(num):
  typ,flags,off,va,pa,fs,ms,al=struct.unpack_from('<IIQQQQQQ',raw,phoff+i*ents)
  if typ==1 and va<=addr and addr+size<=va+fs:embedded=raw[off+addr-va:off+addr-va+size]
 assert embedded is not None
 assert embedded==(p/('native'+suffix+'.spv')).read_bytes(),name
 proof.append(dict(symbol=name,bytes=size,sha256=hashlib.sha256(embedded).hexdigest(),byte_identical=True))
(p/'build.json').write_text(json.dumps(dict(scope='Shader build and embedded-stock byte proof only; runtime/performance unqualified',stock_library_sha256=hashlib.sha256(raw).hexdigest(),native_module_proof=proof,source_include_closure={n:hashlib.sha256((sh/n).read_bytes()).hexdigest()for n in sorted(files)},modules=records),indent=2)+'\n')
print('Q6_FLOAT_NATIVE_STOCK_EXACT_AND_PAD212_BUILT')
