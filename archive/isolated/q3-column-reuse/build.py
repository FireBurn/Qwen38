from pathlib import Path
import json,subprocess,hashlib,shutil,difflib
p=Path(__file__).resolve().parent;q=p.parent/'q3-pad112';src=p/'shader';src.mkdir(exist_ok=True)
for f in(q/'pad16').iterdir():
 if f.suffix in ['.glsl','.comp']:shutil.copy2(f,src/f.name)
f=src/'mul_mat_vecq.comp';old=f.read_text();start=old.index('void iter(');end=old.index('\n#if defined(DATA_A_Q4_K)',start)
new='''#if defined(DATA_A_Q3_K)
// Share identical A-side decode and scale across activation columns.
void iter(inout FLOAT_TYPE temp[NUM_COLS][NUM_ROWS], const uint first_row, const uint num_rows, const uint col, const uint b_qs_idx) {
    i32vec4 b_qs[NUM_COLS];
    float b_d[NUM_COLS];
    [[unroll]] for (uint j = 0; j < NUM_COLS; ++j) {
        const uint bi = (j*p.batch_stride_b + col) / QUANT_K_Q8_1 + b_offset;
        const uint outer = bi / 4;
        const uint inner = bi % 4;
        b_d[j] = float(data_b[outer].ds[inner].x);
        const uint qi = inner * 8 + b_qs_idx * 4;
        b_qs[j] = i32vec4(data_b[outer].qs[qi], data_b[outer].qs[qi+1], data_b[outer].qs[qi+2], data_b[outer].qs[qi+3]);
    }
    [[unroll]] for (uint n = 0; n < num_rows; ++n) {
        const uint ai = ((first_row+n)*p.ncols + col) / QUANT_K_Q8_1 + a_offset;
        const i32vec4 a_qs = repack4(ai, b_qs_idx*4);
        const float d_scale = get_d_scale(ai, b_qs_idx*4);
        [[unroll]] for (uint j = 0; j < NUM_COLS; ++j) {
            int32_t q_sum = 0;
            q_sum += dotPacked4x8EXT(a_qs.x, b_qs[j].x);
            q_sum += dotPacked4x8EXT(a_qs.y, b_qs[j].y);
            q_sum += dotPacked4x8EXT(a_qs.z, b_qs[j].z);
            q_sum += dotPacked4x8EXT(a_qs.w, b_qs[j].w);
            temp[j][n] += FLOAT_TYPE(b_d[j] * d_scale * float(q_sum));
        }
    }
}
#else
'''+old[start:end]+'\n#endif\n'
s=old[:start]+new+old[end:];f.write_text(s);(p/'shader.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='pad16/mul_mat_vecq.comp',tofile='column-reuse/mul_mat_vecq.comp')))
modules=json.loads((q/'build.json').read_text())['modules'];ref=next(x for x in modules if x['variant']=='pad16'and x['reduction']=='_subgroup_no_shmem');cmd=ref['command'][:]
cmd=[str(src/f.name)if x.endswith('/pad16/mul_mat_vecq.comp')else '-I'+str(src)if x.startswith('-I')else x for x in cmd];cmd[cmd.index('-o')+1]=str(p/'reuse_subgroup_no_shmem.spv');subprocess.run(cmd,check=True);subprocess.run(['spirv-val','--target-env','vulkan1.2',str(p/'reuse_subgroup_no_shmem.spv')],check=True)
for name in ['native','pad16']:shutil.copy2(q/(name+'_subgroup_no_shmem.spv'),p/(name+'_subgroup_no_shmem.spv'))
s=(q/'production-probe.cpp').read_text().replace('"pad32"','"reuse"').replace('pad32_c','reuse_c');(p/'probe.cpp').write_text(s)
build=['clang++','-std=c++17','-O2',str(p/'probe.cpp'),'-lvulkan','-o',str(p/'operator_bench')];subprocess.run(build,check=True)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
(p/'build.json').write_text(json.dumps(dict(shader_command=cmd,probe_command=build,shader_sha256=sha(p/'reuse_subgroup_no_shmem.spv'),binary_sha256=sha(p/'operator_bench'),source_sha256=sha(p/'probe.cpp'),shader_sources={f.name:sha(f)for f in src.iterdir()}),indent=2)+'\n')
s=(p.parent/'run_q3_pad112_production_probe.py').read_text().replace("p=base/'q3-pad112'","p=base/'q3-column-reuse'").replace("out=p/'production-diagnostics'","out=p/'operators'").replace('production-probe-build.json','build.json').replace('production-operator_bench','operator_bench').replace('production-probe.cpp','probe.cpp').replace("'pad32'","'reuse'").replace('pad32_c','reuse_c').replace('ActualnativeQ3matrix vs112bytepaddingcontrols.','Native110/padded112/explicitcolumnreuse112;samearithmeticalorder. ')
(p.parent/'run_q3_column_reuse_operators.py').write_text(s)
f=p.parent/'run_private_guarded_batch.py';f.write_text(f.read_text().replace('allowed={',"allowed={'run_q3_column_reuse_operators.py',",1))
print('COLUMN_REUSE_BUILT',flush=True)
