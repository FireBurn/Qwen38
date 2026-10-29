from pathlib import Path
import json,subprocess,hashlib,shutil
p=Path(__file__).resolve().parent;q=p.parent/'q3-pad112';src=p/'shader';src.mkdir(exist_ok=True)
for f in(q/'pad16').iterdir():
 if f.suffix in ['.glsl','.comp']:shutil.copy2(f,src/f.name)
f=src/'mul_mat_vec_iface.glsl';s=f.read_text()+'''\nlayout(binding=3)readonly buffer A1 {A_TYPE data_a1[];};
layout(binding=3)readonly buffer A1_PACKED16 {A_TYPE_PACKED16 data_a1_packed16[];};\n''';f.write_text(s)
f=src/'mul_mat_vecq_funcs.glsl';s=f.read_text();a=s.index('i32vec4 repack4(',s.index('#if defined(DATA_A_Q3_K)'));z=s.index('FLOAT_TYPE mmvq_dot_product',a);block=s[a:z]
new=block.replace('repack4(','repack4_gate(').replace('get_d_scale(','get_d_scale_gate(')+block.replace('repack4(','repack4_up(').replace('get_d_scale(','get_d_scale_up(').replace('data_a_packed16','data_a1_packed16').replace('data_a[','data_a1[')+'''\ni32vec4 repack4(uint ib,uint iqs){if(pair_weight==0)return repack4_gate(ib,iqs);return repack4_up(ib,iqs);}
float get_d_scale(uint ib,uint iqs){if(pair_weight==0)return get_d_scale_gate(ib,iqs);return get_d_scale_up(ib,iqs);}\n'''
f.write_text(s[:a]+new+s[z:])
f=src/'mul_mat_vecq.comp';s=f.read_text().replace('#include "mul_mat_vecq_funcs.glsl"','uint pair_weight;\n#include "mul_mat_vecq_funcs.glsl"').replace('uint ibi = first_row*p.ncols;','uint ibi = (first_row/2)*p.ncols;').replace('            ibi += p.ncols;','            pair_weight=n;')
a=s.index('void main() {');s=s[:a]+'''void main(){
    const uint first_row=2*(gl_WorkGroupID.x+gl_NumWorkGroups.x*gl_WorkGroupID.z);
    if(first_row>=p.stride_d)return;
    compute_outputs(first_row,2);
}\n''';f.write_text(s)
f=src/'mul_mat_vec_base.glsl';s=f.read_text();a=s.index('void reduce_result(',s.index('#ifdef USE_SUBGROUP_ADD_NO_SHMEM'));z=s.index('#else\nshared',a)
s=s.replace('const uint NUM_ROWS = 1;','const uint NUM_ROWS = 2;')
a=s.index('void reduce_result(',s.index('#ifdef USE_SUBGROUP_ADD_NO_SHMEM'));z=s.index('#else\nshared',a)
s=s[:a]+'''void reduce_result(inout FLOAT_TYPE temp[NUM_COLS][NUM_ROWS], const uint32_t d_offset, const uint32_t first_row, const uint32_t num_rows, const uint32_t tid){
    [[unroll]] for(uint j=0;j<NUM_COLS;++j){
        temp[j][0]=subgroupAdd(temp[j][0]);
        temp[j][1]=subgroupAdd(temp[j][1]);
        if(tid==0){
            float a=temp[j][0],b=temp[j][1];
            data_d[j*p.batch_stride_d+d_offset+first_row/2]=D_TYPE(a/(1.0f+exp(-a))*b);
        }
    }
}
'''+s[z:];f.write_text(s)
ref=next(x for x in json.loads((q/'build.json').read_text())['modules']if x['variant']=='pad16'and x['reduction']=='_subgroup_no_shmem');cmd=[str(src/'mul_mat_vecq.comp')if x.endswith('/pad16/mul_mat_vecq.comp')else'-I'+str(src)if x.startswith('-I')else x for x in ref['command']];cmd[cmd.index('-o')+1]=str(p/'pair_subgroup_no_shmem.spv');subprocess.run(cmd,check=True);subprocess.run(['spirv-val','--target-env','vulkan1.2',str(p/'pair_subgroup_no_shmem.spv')],check=True)
shutil.copy2(q/'qualified-20261029/shaders/pad16_subgroup_no_shmem.spv',p/'pad16_subgroup_no_shmem.spv')
# Extract exact production GLU module from its linked object, not a reimplementation.
extract='''#include <cstdint>\n#include <cstdio>\nextern const unsigned char swiglu_f32_data[];extern const uint64_t swiglu_f32_len;int main(int argc,char**argv){if(argc!=2)return2;FILE*f=fopen(argv[1],"wb");if(!f)return3;auto n=fwrite(swiglu_f32_data,1,swiglu_f32_len,f);fclose(f);return n==swiglu_f32_len?0:4;}'''.replace('return2','return 2').replace('return3','return 3')
(p/'extract_glu.cpp').write_text(extract);obj=p.parent/'production-native-shaders/host/objects/swiglu.comp.cpp.o';ecmd=['clang++',str(p/'extract_glu.cpp'),str(obj),'-o',str(p/'extract-glu')];subprocess.run(ecmd,check=True);subprocess.run([str(p/'extract-glu'),str(p/'swiglu_ref.spv')],check=True);subprocess.run(['spirv-val','--target-env','vulkan1.2',str(p/'swiglu_ref.spv')],check=True)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
(p/'shader-build.json').write_text(json.dumps(dict(command=cmd,extract_command=ecmd,production_glu_object_sha256=sha(obj),modules={f.name:sha(f)for f in p.glob('*.spv')},sources={f.name:sha(f)for f in src.iterdir()}),indent=2)+'\n');print('PAIR_SHADER_BUILT')
