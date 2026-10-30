from pathlib import Path
import json,shutil,subprocess,hashlib
p=Path(__file__).resolve().parent;old=p/'host';h=p/'metadata-host';h.mkdir(exist_ok=True);(h/'bin').mkdir(exist_ok=True)
for f in old.glob('*.h'):shutil.copy2(f,h/f.name)
for name in ['ggml-vulkan-buffers.cpp.o','ggml-vulkan-debug.cpp.o']:shutil.copy2(old/name,h/name)
s=(old/'ggml-vulkan.cpp').read_text();a=s.index('extern "C" __attribute__((visibility("default"))) void np_profile_select')
helpers=r'''
#include <tuple>
using nwm_key=std::tuple<std::string,int,int,int,uint64_t>;
static std::map<nwm_key,uint64_t>nwm_counts;
static uint64_t nwm_dropped=0;
static void nwm_record(const ggml_tensor*t,uint64_t bytes){
 if(!nwt_on.load(std::memory_order_relaxed))return;
 std::string hex;hex.reserve(GGML_MAX_NAME*2);const char*digits="0123456789abcdef";
 for(size_t i=0;i<strnlen(t->name,GGML_MAX_NAME);++i){auto c=static_cast<unsigned char>(t->name[i]);hex+=digits[c>>4];hex+=digits[c&15];}
 nwm_key key{hex,int(t->type),int(t->op),int(t->flags),bytes};std::lock_guard<std::mutex>lock(nwt_mutex);
 auto it=nwm_counts.find(key);if(it!=nwm_counts.end())++it->second;else if(nwm_counts.size()<4096)nwm_counts.emplace(std::move(key),1);else ++nwm_dropped;
}
static void nwm_dump(int arm){
 const char*dir=getenv("NFP_TIMELINE_DIR");GGML_ASSERT(dir);std::string path=std::string(dir)+"/metadata-"+std::to_string(arm)+".json";FILE*f=fopen(path.c_str(),"w");GGML_ASSERT(f);fprintf(f,"{\"dropped\":%llu,\"records\":[",(unsigned long long)nwm_dropped);bool first=true;
 for(const auto&item:nwm_counts){const auto&k=item.first;fprintf(f,"%s{\"name_hex\":\"%s\",\"type\":%d,\"op\":%d,\"flags\":%d,\"bytes_requested\":%llu,\"calls\":%llu}",first?"":",",std::get<0>(k).c_str(),std::get<1>(k),std::get<2>(k),std::get<3>(k),(unsigned long long)std::get<4>(k),(unsigned long long)item.second);first=false;}
 fprintf(f,"]}\n");fclose(f);
}
'''
s=s[:a]+helpers+s[a:];s=s.replace('nwt_events.clear();nwt_events.reserve(8192);','nwt_events.clear();nwt_events.reserve(8192);nwm_counts.clear();nwm_dropped=0;')
s=s.replace('fclose(f);fprintf(stderr,"NFP_TIMELINE','fclose(f);nwm_dump(arm);fprintf(stderr,"NFP_TIMELINE',1)
s=s.replace('nwt_scope io_trace(4,size);','nwt_scope io_trace(4,size);nwm_record(tensor,size);').replace('nwt_scope io_trace(4,size*n_copies);','nwt_scope io_trace(4,size*n_copies);nwm_record(tensor,size*n_copies);')
(h/'ggml-vulkan.cpp').write_text(s)
cmds=json.loads((p/'commands.json').read_text());cmds=[[v.replace(str(old),str(h))for v in c]for c in cmds]
for c in cmds:subprocess.run(c,check=True,cwd=h)
lib=h/'bin/libggml-vulkan.so.0.27.0'
for name in ['libggml-vulkan.so','libggml-vulkan.so.0']:
 if not(h/'bin'/name).exists():(h/'bin'/name).symlink_to(lib.name)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'metadata-build.json').write_text(json.dumps(dict(binary_sha256=sha(p/'bin/model-bench'),library_sha256=sha(lib),source_sha256=sha(h/'ggml-vulkan.cpp'),commands=cmds,scope='OnlyCPUmetadataforobservedsyncsetcalls;4096distinctkeybound/overflowcounter,copiedname/type/op/flags/requestbytes,normalcommands/ownership/shadersunchanged.'),indent=2)+'\n')
