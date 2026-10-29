from pathlib import Path
import json,subprocess,shutil,hashlib,difflib
p=Path(__file__).resolve().parent;old=p.parent/'q3-pad112/host-fast-guard-v2';h=p/'host';h.mkdir(exist_ok=True);(h/'bin').mkdir(exist_ok=True)
for f in old.glob('*.h'):shutil.copy2(f,h/f.name)
s=(old/'ggml-vulkan.cpp').read_text();needle='    uint64_t flops_per_submit = std::min(flops_cap, ctx->last_total_flops / 40u);';assert s.count(needle)==1;s=s.replace(needle,'''    const char*nsb_env=getenv("GGML_VK_NATIVE_SUBMIT_DIVISOR");
    const uint32_t nsb_divisor=nsb_env&&strcmp(nsb_env,"20")==0?20u:40u;
    uint64_t flops_per_submit = std::min(flops_cap, ctx->last_total_flops / nsb_divisor);
''')
needle='    ctx->last_total_flops = total_flops;';assert s.count(needle)==1;s=s.replace(needle,'''    if(getenv("GGML_VK_NATIVE_SUBMIT_AUDIT"))fprintf(stderr,"NATIVE_SUBMIT_BUDGET divisor=%u nodes=%d batches=%u flops=%llu\\n",nsb_divisor,cgraph->n_nodes,submit_count,(unsigned long long)total_flops);
'''+needle)
(h/'ggml-vulkan.cpp').write_text(s)
cmds=json.loads((old/'build-argv.json').read_text());cmds=[[v.replace(str(old),str(h))for v in c]for c in cmds];(h/'build-argv.json').write_text(json.dumps(cmds,indent=2)+'\n');subprocess.run(cmds[0],check=True,cwd=h);subprocess.run(cmds[-1],check=True,cwd=h)
lib=h/'bin/libggml-vulkan.so.0.27.0'
for n in ['libggml-vulkan.so','libggml-vulkan.so.0']:
 if not(h/'bin'/n).exists():(h/'bin'/n).symlink_to(lib.name)
(p/'host.patch').write_text(''.join(difflib.unified_diff((old/'ggml-vulkan.cpp').read_text().splitlines(True),s.splitlines(True),fromfile='a/ggml-vulkan.cpp',tofile='b/ggml-vulkan.cpp')))
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'build.json').write_text(json.dumps(dict(library_sha256=sha(lib),main_source_sha256=sha(h/'ggml-vulkan.cpp'),base_source_sha256=sha(old/'ggml-vulkan.cpp'),commands=[cmds[0],cmds[-1]],matching_headers_from=str(old),buffer_debug_objects_retained_from_frozen_link=True,scope='OnlyinitialnativeFLOPsubmitbudgetdivisor40(default)or20(optin),unchangedfirst3doubling/nodecap/AMDcaps/fences/commands/shaders. No CPUplancache/megapath. Correctnesspending.'),indent=2)+'\n')
