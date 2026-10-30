from pathlib import Path
import json,subprocess,hashlib,difflib
p=Path(__file__).resolve().parent;f=p/'source/src/llama-kv-cache.cpp';orig=(p/'original-kv-cache.cpp').read_text();s=orig
helper=r'''
static bool qcr_context(ggml_context*ctx){auto*t=ggml_get_first_tensor(ctx);return t&&strcmp(t->name,"__qwen_const_rot_marker")==0;}
static ggml_tensor*qcr_find(const std::vector<std::pair<ggml_context_ptr,ggml_backend_buffer_ptr>>&owned,uint32_t n){
 if(!n)return nullptr;char name[64];snprintf(name,sizeof(name),"__qwen_const_rot_%u",n);
 for(const auto&entry:owned)if(qcr_context(entry.first.get()))if(auto*t=ggml_get_tensor(entry.first.get(),name))return t;
 return nullptr;
}
'''
a=s.index('llama_kv_cache::llama_kv_cache(');s=s[:a]+helper+'\n'+s[a:]
needle='    const char * LLAMA_KV_CACHE_DEBUG = getenv("LLAMA_KV_CACHE_DEBUG");';assert s.count(needle)==1
s=s.replace(needle,r'''    // Immutable rotations belong to the cache, not reusable graph allocations.
    const char*qcr_env=getenv("LLAMA_VK_CONST_ROT");
    if(qcr_env&&strcmp(qcr_env,"1")==0&&!hparams.no_alloc&&(n_rot_k||n_rot_v)&&ctxs_bufs.size()==1){
        auto*base_buf=ctxs_bufs.front().second.get();const char*backend_name=ggml_backend_buffer_name(base_buf);
        if(!ggml_backend_buffer_is_host(base_buf)&&strncmp(backend_name,"Vulkan",6)==0){
            ggml_init_params params={4*ggml_tensor_overhead(),nullptr,true};ggml_context_ptr const_ctx{ggml_init(params)};
            if(const_ctx){
                auto*marker=ggml_new_tensor_1d(const_ctx.get(),GGML_TYPE_I32,1);ggml_set_name(marker,"__qwen_const_rot_marker");
                std::vector<ggml_tensor*>mats;std::vector<uint32_t>sizes;
                if(n_rot_k)sizes.push_back(n_rot_k);if(n_rot_v&&n_rot_v!=n_rot_k)sizes.push_back(n_rot_v);
                for(auto n:sizes){GGML_ASSERT(attn_rot_hadamard.count(n));auto*t=ggml_new_tensor_2d(const_ctx.get(),GGML_TYPE_F32,n,n);ggml_format_name(t,"__qwen_const_rot_%u",n);mats.push_back(t);}
                auto*buft=ggml_backend_buffer_get_type(base_buf);ggml_backend_buffer_ptr const_buf{ggml_backend_alloc_ctx_tensors_from_buft(const_ctx.get(),buft)};
                if(const_buf){
                    ggml_backend_buffer_set_usage(const_buf.get(),GGML_BACKEND_BUFFER_USAGE_WEIGHTS);int32_t tag=1;ggml_backend_tensor_set(marker,&tag,0,sizeof(tag));size_t bytes=0;
                    for(size_t i=0;i<mats.size();++i){auto*t=mats[i];ggml_backend_tensor_set(t,attn_rot_hadamard.at(sizes[i]).data(),0,ggml_nbytes(t));bytes+=ggml_nbytes(t);}
                    if(getenv("LLAMA_VK_CONST_ROT_AUDIT"))fprintf(stderr,"LLAMA_CONST_ROT_CREATED matrices=%zu bytes=%zu\n",mats.size(),bytes);
                    ctxs_bufs.emplace_back(std::move(const_ctx),std::move(const_buf));
                }else LLAMA_LOG_WARN("LLAMA_CONST_ROT_FALLBACK allocation\n");
            }else LLAMA_LOG_WARN("LLAMA_CONST_ROT_FALLBACK context\n");
        }
    }
'''+needle)
needle='''        for (auto & [_, buf] : ctxs_bufs) {
            ggml_backend_buffer_clear(buf.get(), 0);
        }''';assert s.count(needle)==1;s=s.replace(needle,'''        for (auto & [owned_ctx, buf] : ctxs_bufs) {
            if(qcr_context(owned_ctx.get()))continue;
            ggml_backend_buffer_clear(buf.get(), 0);
        }''')
for kind in ['k','v']:
 needle='ggml_tensor * llama_kv_cache::build_input_'+kind+'_rot(ggml_context * ctx) const {';assert s.count(needle)==1;s=s.replace(needle,needle+'\n    if(auto*t=qcr_find(ctxs_bufs,n_rot_'+kind+'))return t;')
 needle='void llama_kv_cache::set_input_'+kind+'_rot(ggml_tensor * dst) const {';assert s.count(needle)==1;s=s.replace(needle,needle+r'''
    if(dst==qcr_find(ctxs_bufs,n_rot_'''+kind+r''')){if(getenv("LLAMA_VK_CONST_ROT_AUDIT"))fprintf(stderr,"LLAMA_CONST_ROT_BYPASS kind='''+kind+r''' n=%lld\n",(long long)dst->ne[0]);return;}
''')
f.write_text(s);(p/'core.patch').write_text(''.join(difflib.unified_diff(orig.splitlines(True),s.splitlines(True),fromfile='a/src/llama-kv-cache.cpp',tofile='b/src/llama-kv-cache.cpp')))
d=json.loads((p/'inputs.json').read_text());subprocess.run(d['compile_command'],check=True,cwd=p)
cmd=d['link_command'];cmd=[str(p/'kv-cache.o')if v==str(p/'objects/llama-kv-cache.cpp.o')else v for v in cmd];cmd[cmd.index('-o')+1]=str(p/'bin/libllama.so.0.7.0');subprocess.run(cmd,check=True,cwd=p)
for name in ['libllama.so','libllama.so.0']:
 if not(p/'bin'/name).exists():(p/'bin'/name).symlink_to('libllama.so.0.7.0')
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'build.json').write_text(json.dumps(dict(library_sha256=sha(p/'bin/libllama.so.0.7.0'),source_sha256=sha(f),source_head=d['source_head'],compile_command=d['compile_command'],link_command=cmd,headers_and_class_layout_unchanged=True,scope='PrivateKVcachecpp-onlyconstantHadamarddevicecache;ownedexistingctxs_bufs,noinput/barrier/mathchanges.Othercoreobjectsfromfrozencontrol,sourceaa8;qualificationpending.'),indent=2)+'\n');print('PRIVATE_CONST_ROT_CORE_BUILT')
