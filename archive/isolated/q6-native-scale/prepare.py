from pathlib import Path
import shutil,re,subprocess,json,hashlib
p=Path(__file__).resolve().parent;ref=p.parent/'q6-pad212/native';records=[]
for mode in ['native','shuffle','direct']:
 d=p/mode;d.mkdir(exist_ok=True)
 for f in ref.iterdir():shutil.copy2(f,d/f.name)
 f=d/'mul_mat_vec_q6_k.comp';s=f.read_text()
 if mode!='native':
  s=s.replace('shared FLOAT_TYPE sccache[2][BLOCK_SIZE/16][16];','').replace('uint csel = 0;','').replace('        csel ^= 1;','')
  a=s.index('        if (!all_threads)');z=s.index('        const uint32_t ql0_u32',a)
  s=s[:a]+'        if (!all_threads && i >= num_blocks_per_row) continue;\n\n'+s[z:]
  a=s.index('        if (all_threads)');z=s.index('        const FLOAT_TYPE d =',a);s=s[:a]+s[z:]
  if mode=='shuffle':
   s=s.replace('#version 450','#version 450\n#extension GL_KHR_shader_subgroup_basic : require\n#extension GL_KHR_shader_subgroup_shuffle : require')
   s=s.replace('        const FLOAT_TYPE d =','        const FLOAT_TYPE sc = FLOAT_TYPE(data_a[ib0 + i].scales[itid]);\n        const FLOAT_TYPE d =')
  for delta in [0,2,4,6]:
   idx='s_offset'+(' + '+str(delta)if delta else'');needle='sccache[csel][ix]['+idx+']';assert needle in s
   replacement='subgroupShuffle(sc, ix*16 + '+idx+')'if mode=='shuffle'else'FLOAT_TYPE(data_a[ib0 + i].scales['+idx+'])'
   s=s.replace(needle,replacement)
  assert 'sccache'not in s and 'barrier()'not in s
 f.write_text(s)
 target=p/(mode+'_subgroup_no_shmem.spv');cmd=['glslc','-fshader-stage=compute','--target-env=vulkan1.2','-O','-I'+str(d),*['-D'+v for v in ['DATA_A_Q6_K=1','FLOAT_TYPE=float','FLOAT_TYPEV2=vec2','B_TYPE=float','B_TYPEV2=vec2','B_TYPEV4=vec4','D_TYPE=float','USE_SUBGROUP_ADD_NO_SHMEM=1']],str(f),'-o',str(target)]
 subprocess.run(cmd,check=True);subprocess.run(['spirv-val','--target-env','vulkan1.2',str(target)],check=True)
 if mode=='native':assert target.read_bytes()==(ref.parent/'native_subgroup_no_shmem.spv').read_bytes()
 records.append(dict(mode=mode,source_sha256=hashlib.sha256(s.encode()).hexdigest(),shader_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),command=cmd))
cases=0
for blocks in range(1,257):
 for start in range(0,blocks+4,4):
  for tid in range(64):
   cohort,lane=divmod(tid,16)
   if start+cohort>=blocks:continue
   offset=8*(lane//8)+(lane%8)//4
   for delta in [0,2,4,6]:
    src=cohort*16+offset+delta;assert src//16==cohort and start+src//16<blocks;cases+=1
(p/'build.json').write_text(json.dumps(dict(scope='Native float Q6 scale handoff only, no padding/new activation quantization. Native stock module byte identical; fixed64WG/wave64. Runtime/performance pending.',lane_ownership_cases=cases,modules=records),indent=2)+'\n')
print('NATIVE_Q6_SCALE_VARIANTS_BUILT',cases)
