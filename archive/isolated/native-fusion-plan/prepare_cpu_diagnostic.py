from pathlib import Path
import json,shutil,subprocess,hashlib
p=Path(__file__).resolve().parent;old=p/'reuse-host';h=p/'cpu-host';h.mkdir(exist_ok=True);(h/'bin').mkdir(exist_ok=True)
for f in old.glob('*.h'):shutil.copy2(f,h/f.name)
for name in ['ggml-vulkan-buffers.cpp.o','ggml-vulkan-debug.cpp.o']:shutil.copy2(old/name,h/name)
s=(old/'ggml-vulkan.cpp').read_text();a=s.index('static ggml_status ggml_backend_vk_graph_compute(')
s=s[:a]+'''static bool nfp_profile_on=false;
static uint64_t nfp_profile_graph=0,nfp_profile_fast=0,nfp_profile_key=0,nfp_profile_count=0;
extern "C" __attribute__((visibility("default"))) void np_profile_select(int arm){nfp_profile_on=arm>=0;nfp_profile_graph=nfp_profile_fast=nfp_profile_key=nfp_profile_count=0;}
extern "C" __attribute__((visibility("default"))) void np_profile_dump(int arm){fprintf(stderr,"NFP_CPU arm=%d graph_ns=%llu fast_ns=%llu key_ns=%llu graphs=%llu\\n",arm,(unsigned long long)nfp_profile_graph,(unsigned long long)nfp_profile_fast,(unsigned long long)nfp_profile_key,(unsigned long long)nfp_profile_count);nfp_profile_on=false;}
'''+s[a:]
s=s.replace('    VK_LOG_DEBUG("ggml_backend_vk_graph_compute("', '    const uint64_t nfp_graph_start=nfp_profile_on?nfp_cpu_ns():0;\n    VK_LOG_DEBUG("ggml_backend_vk_graph_compute("',1)
a=s.index('    return GGML_STATUS_SUCCESS;',s.index('static ggml_status ggml_backend_vk_graph_compute('));s=s[:a]+'''    if(nfp_profile_on){nfp_profile_graph+=nfp_cpu_ns()-nfp_graph_start;nfp_profile_fast+=nfp_fast_cpu;nfp_profile_key+=nfp_key_cpu;++nfp_profile_count;}
'''+s[a:];(h/'ggml-vulkan.cpp').write_text(s)
cmds=json.loads((old/'build-argv.json').read_text());cmds=[[v.replace(str(old),str(h))for v in c]for c in cmds];subprocess.run(cmds[0],check=True,cwd=h);subprocess.run(cmds[-1],check=True,cwd=h)
lib=h/'bin/libggml-vulkan.so.0.27.0'
for n in ['libggml-vulkan.so','libggml-vulkan.so.0']:
 if not(h/'bin'/n).exists():(h/'bin'/n).symlink_to(lib.name)
s=(p.parent/'q3-pad112/profile-runner.cpp').read_text().replace('arm=-1;arm<8','arm=-2;arm<24').replace('bool pad=arm<0||','bool active=arm==-1||').replace('np_select(arm);','np_select(-1);').replace('if(pad)setenv("GGML_VK_Q3_PAD112_DIR",pad_dir.c_str(),1);else unsetenv("GGML_VK_Q3_PAD112_DIR");','setenv("GGML_VK_FUSION_PLAN_REUSE",active?"1":"0",1);').replace('pad?"pad":"control"','active?"active":"inactive"')
s=s.replace('    const auto t_enc_end = ggml_time_us();','    llama_synchronize(ctx_tgt);if(ctx_dft)llama_synchronize(ctx_dft);\n    const auto t_enc_end = ggml_time_us();')
s=s.replace('    const auto t_dec_start = ggml_time_us();','    np_select(arm);\n    const auto t_dec_start = ggml_time_us();fprintf(stderr,"RESIDENT_DEC_BEGIN time_us=%lld\\n",(long long)t_dec_start);')
s=s.replace('if(!warm_end&&n_predict>=16){warm_end=', 'if(!warm_end&&n_predict>=16){llama_synchronize(ctx_tgt);if(ctx_dft)llama_synchronize(ctx_dft);warm_end=')
s=s.replace('    auto t_dec_end = ggml_time_us();','    llama_synchronize(ctx_tgt);if(ctx_dft)llama_synchronize(ctx_dft);\n    auto t_dec_end = ggml_time_us();')
(p/'cpu-runner.cpp').write_text(s);(p/'cpu-bin').mkdir(exist_ok=True)
cmd=json.loads((p.parent/'q3-pad112/profile-runner-build.json').read_text())['command'];cmd=[str(p/'cpu-runner.cpp')if x.endswith('/profile-runner.cpp')else x for x in cmd];cmd[cmd.index('-o')+1]=str(p/'cpu-bin/model-bench');subprocess.run(cmd,check=True)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
(p/'cpu-build.json').write_text(json.dumps(dict(library_sha256=sha(lib),binary_sha256=sha(p/'cpu-bin/model-bench'),commands=[cmds[0],cmds[-1],cmd],scope='Identical reuse headers/buffer/debug objects; only two graph-level CLOCK_THREAD_CPUTIME_ID reads, accumulated counters and exports added. Both arms same instrumented library; no per-node timing.'),indent=2)+'\n')
