from pathlib import Path
import subprocess,json,hashlib
p=Path(__file__).resolve().parent;b=p.parent;sh=b/'installed-source/ggml/src/ggml-vulkan/vulkan-shaders'
source=(sh/'mul_mat_vecq_funcs.glsl').read_text()
a=source.index('#if defined(DATA_A_Q3_K)');z=source.index('#if defined(DATA_A_Q4_K)',a)
section=source[a:z]
start=section.index('    // Subtract 4 by twiddling bits')
end=section.index('\n}',start)
section=section[:start]+'    return i32vec4(vals0, vals1, vals2, vals3);'+section[end:]
needle='    return FLOAT_TYPE(float(cache_b_ds.x) * d_scale * float(q_sum));'
assert section.count(needle)==1
section=section.replace(needle,'''    const int32_t y_sum = dotPacked4x8EXT(0x01010101, cache_b_qs[0])
                        + dotPacked4x8EXT(0x01010101, cache_b_qs[1])
                        + dotPacked4x8EXT(0x01010101, cache_b_qs[2])
                        + dotPacked4x8EXT(0x01010101, cache_b_qs[3]);
    q_sum -= 4 * y_sum;
'''+needle)
(p/'mul_mat_vecq_funcs.glsl').write_text(source[:a]+section+source[z:])
(p/'mul_mat_vecq.comp').write_bytes((sh/'mul_mat_vecq.comp').read_bytes())
records=[]
for suffix,extra in [('',[]),('_subgroup',['USE_SUBGROUP_ADD=1']),('_subgroup_no_shmem',['USE_SUBGROUP_ADD_NO_SHMEM=1'])]:
 name='mul_mat_vec_q3_k_q8_1_f32'+suffix
 defines=['DATA_A_Q3_K=1','D_TYPE=float','FLOAT_TYPE=float','FLOAT_TYPEV2=vec2','ACC_TYPE=float']+extra
 for candidate in [False,True]:
  out=p/(('candidate-' if candidate else 'native-')+name+'.spv')
  src=p/'mul_mat_vecq.comp' if candidate else sh/'mul_mat_vecq.comp'
  cmd=['glslc','-fshader-stage=compute','--target-env=vulkan1.2','-O','-I'+str(sh),*[('-D'+d)for d in defines],str(src),'-o',str(out)]
  subprocess.run(cmd,check=True);subprocess.run(['spirv-val','--target-env','vulkan1.2',str(out)],check=True)
  ref=b/'installed-build/ggml/src/ggml-vulkan/vulkan-shaders.spv'/ (name+'.spv')
  if not candidate:assert out.read_bytes()==ref.read_bytes(),name
  records.append({'shader':name,'candidate':candidate,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'baseline_matches_reconstructed_module':not candidate,'command':cmd})
(p/'shader-build.json').write_text(json.dumps(records,indent=2)+'\n')
print('CURRENT_Q3_ALL_THREE_CONTROLS_MATCH_RECONSTRUCTED_MODULES')
