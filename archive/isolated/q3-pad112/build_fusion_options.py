from pathlib import Path
import shutil,json,subprocess,hashlib,difflib
p=Path(__file__).resolve().parent;old=p/'host-fast-guard-v2';h=p/'host-fusion-options';h.mkdir(exist_ok=True);(h/'bin').mkdir(exist_ok=True)
for f in old.glob('*.h'):shutil.copy2(f,h/f.name)
f=h/'ggml-vulkan-types.h';s=f.read_text().replace('    vk_pipeline nq_pipeline;','    uint64_t nq_group_limit=16;\n    bool nq_enabled=false,nq_expanded=false,nq_audit=false,nq_coalesce_enabled=false;\n    vk_pipeline nq_pipeline;');f.write_text(s)
s=(old/'ggml-vulkan.cpp').read_text();needle='    uint32_t limit=16;\n    if(const char*v=getenv("GGML_VK_NATIVE_GLUQ_GROUPS")){unsigned long n=strtoul(v,nullptr,10);GGML_ASSERT(n>0&&n<=136);limit=uint32_t(n);}';assert s.count(needle)==1
s=s.replace(needle,'    GGML_ASSERT(ctx->nq_group_limit>0&&ctx->nq_group_limit<=136);\n    const uint32_t limit=uint32_t(ctx->nq_group_limit);')
s=s.replace('getenv("GGML_VK_NATIVE_GLUQ_COALESCE")','ctx->nq_coalesce_enabled').replace('getenv("GGML_VK_NATIVE_GLUQ_AUDIT")','ctx->nq_audit').replace('getenv("GGML_VK_NATIVE_GLUQ_EXPAND_VIEWS")!=nullptr','ctx->nq_expanded').replace('if(getenv("GGML_VK_NATIVE_GLUQ_EXPAND_VIEWS"))','if(ctx->nq_expanded)')
guard='!getenv("GGML_VK_NATIVE_GLUQ_FUSE")||getenv("GGML_VK_MEGA")||ctx->device->vendor_id!=VK_VENDOR_ID_AMD||!ctx->device->integer_dot_product||ctx->device->properties.deviceID!=0x7551||ctx->device->subgroup_size!=64||!ctx->device->subgroup_shuffle||!ctx->device->subgroup_require_full_support';assert s.count(guard)==2;s=s.replace(guard,'!ctx->nq_enabled')
needle='static void nq_prepare(ggml_backend_vk_context*ctx,const ggml_cgraph*graph){';assert s.count(needle)==1
cfg='''static void nq_prepare_options(ggml_backend_vk_context*ctx){
    ctx->nq_enabled=getenv("GGML_VK_NATIVE_GLUQ_FUSE")&&!getenv("GGML_VK_MEGA")&&ctx->device->vendor_id==VK_VENDOR_ID_AMD&&ctx->device->integer_dot_product&&ctx->device->properties.deviceID==0x7551&&ctx->device->subgroup_size==64&&ctx->device->subgroup_shuffle&&ctx->device->subgroup_require_full_support;
    ctx->nq_group_limit=16;ctx->nq_expanded=false;ctx->nq_audit=false;ctx->nq_coalesce_enabled=false;
    if(!ctx->nq_enabled)return;
    if(const char*v=getenv("GGML_VK_NATIVE_GLUQ_GROUPS"))ctx->nq_group_limit=strtoul(v,nullptr,10);
    ctx->nq_expanded=getenv("GGML_VK_NATIVE_GLUQ_EXPAND_VIEWS")!=nullptr;
    ctx->nq_audit=getenv("GGML_VK_NATIVE_GLUQ_AUDIT")!=nullptr;
    ctx->nq_coalesce_enabled=getenv("GGML_VK_NATIVE_GLUQ_COALESCE")!=nullptr;
}
'''
s=s.replace(needle,cfg+needle+'\n    nq_prepare_options(ctx);')
(h/'ggml-vulkan.cpp').write_text(s)
cmds=[[v.replace(str(old),str(h))for v in cmd]for cmd in json.loads((old/'build-argv.json').read_text())]
# v2 reused these two objects because its layout was unchanged. This layout changes;
# rebuild the three host translation units with the new private header.
basecmds=json.loads((p/'host-fast-guard/build-argv.json').read_text());cmds=[[v.replace(str(p/'host-fast-guard'),str(h))for v in cmd]for cmd in basecmds]
for n in ['ggml-vulkan-buffers.cpp','ggml-vulkan-debug.cpp']:shutil.copy2(p/'host-fast-guard'/n,h/n)
(h/'build-argv.json').write_text(json.dumps(cmds,indent=2)+chr(10))
for cmd in cmds:subprocess.run(cmd,check=True,cwd='${CLAUDE_WORKSPACE}/prodtree/build')
lib=h/'bin/libggml-vulkan.so.0.27.0'
for n in ['libggml-vulkan.so','libggml-vulkan.so.0']:
 f=h/'bin'/n
 if not f.exists():f.symlink_to(lib.name)
(h/'build.json').write_text(json.dumps({'library_sha256':hashlib.sha256(lib.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(s.encode()).hexdigest(),'types_sha256':hashlib.sha256((h/'ggml-vulkan-types.h').read_bytes()).hexdigest(),'host_translation_units_rebuilt':3,'scope':'Graph-level fusion options, preserving default16 and1..136validation at actual use, alias/consumer proofs, shader math and native fallback. Runtime checks pending. Qualified snapshot untouched.'},indent=2)+chr(10))
patch=[]
for n in ['ggml-vulkan.cpp','ggml-vulkan-types.h']:patch+=difflib.unified_diff((old/n).read_text().splitlines(True),(h/n).read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n)
(p/'fusion-options.patch').write_text(''.join(patch))
