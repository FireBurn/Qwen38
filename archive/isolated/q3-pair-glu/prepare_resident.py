from pathlib import Path
import json,hashlib,subprocess
p=Path(__file__).resolve().parent;q=p.parent/'q3-pad112';(p/'resident-bin').mkdir(exist_ok=True)
s=(q/'profile-runner.cpp').read_text();a=s.index('    auto np_select=');z=s.index('    for(int arm=',a);s=s[:a]+'    const char*pair_env=getenv("PAIR_RESIDENT_SHADER");check(pair_env,"pair shader path");std::string pair_path=pair_env;\n'+s[z:]
s=s.replace('arm<8','arm<24').replace('bool pad=arm<0||','bool fused=arm<0||').replace('        np_select(arm);\n','')
s=s.replace('        if(pad)setenv("GGML_VK_Q3_PAD112_DIR",pad_dir.c_str(),1);else unsetenv("GGML_VK_Q3_PAD112_DIR");','        if(fused)setenv("GGML_VK_PAIR_GLU_SHADER",pair_path.c_str(),1);else unsetenv("GGML_VK_PAIR_GLU_SHADER");')
s=s.replace('pad?"pad":"control"','fused?"active":"inactive"').replace('        if(arm>=0)np_dump(arm);\n','')
s=s.replace('    const auto t_enc_end = ggml_time_us();','    llama_synchronize(ctx_tgt);if(ctx_dft)llama_synchronize(ctx_dft);\n    const auto t_enc_end = ggml_time_us();')
s=s.replace('const auto t_dec_start = ggml_time_us();int64_t warm_end=0;int warm_tokens=0;','const auto t_dec_start = ggml_time_us();fprintf(stderr,"RESIDENT_DEC_BEGIN time_us=%lld\\n",(long long)t_dec_start);int64_t warm_end=0;int warm_tokens=0;')
s=s.replace('if(!warm_end&&n_predict>=16){warm_end=', 'if(!warm_end&&n_predict>=16){llama_synchronize(ctx_tgt);if(ctx_dft)llama_synchronize(ctx_dft);warm_end=')
s=s.replace('    auto t_dec_end = ggml_time_us();','    llama_synchronize(ctx_tgt);if(ctx_dft)llama_synchronize(ctx_dft);\n    auto t_dec_end = ggml_time_us();')
(p/'resident-runner.cpp').write_text(s)
cmd=json.loads((q/'profile-runner-build.json').read_text())['command'];cmd=[str(p/'resident-runner.cpp')if x.endswith('/profile-runner.cpp')else x for x in cmd];cmd[cmd.index('-o')+1]=str(p/'resident-bin/model-bench');subprocess.run(cmd,check=True)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'resident-build.json').write_text(json.dumps(dict(command=cmd,source_sha256=sha(p/'resident-runner.cpp'),binary_sha256=sha(p/'resident-bin/model-bench')),indent=2)+'\n');print('PAIR_RESIDENT_RUNNER_BUILT')
