from pathlib import Path
import json,shutil,subprocess,hashlib
p=Path(__file__).resolve().parent;old=p/'reuse-host';h=p/'timeline-host';h.mkdir(exist_ok=True);(h/'bin').mkdir(exist_ok=True)
for f in old.glob('*.h'):shutil.copy2(f,h/f.name)
for name in ['ggml-vulkan-buffers.cpp.o','ggml-vulkan-debug.cpp.o']:shutil.copy2(old/name,h/name)
code=r'''
#include <atomic>
#include <mutex>
#include <ctime>
#include <unistd.h>
#include <sys/syscall.h>
struct nwt_event{unsigned kind;uint64_t begin,end,cpu,tag;long tid;};
static std::atomic<bool> nwt_on{false};
static std::mutex nwt_mutex;
static std::vector<nwt_event>nwt_events;
static uint64_t nwt_clock(clockid_t id){timespec t;clock_gettime(id,&t);return uint64_t(t.tv_sec)*1000000000ull+t.tv_nsec;}
struct nwt_scope{unsigned kind;bool on;uint64_t begin=0,cpu=0,tag;long tid=0;nwt_scope(unsigned k,uint64_t arg=0):kind(k),on(nwt_on.load(std::memory_order_relaxed)),tag(arg){if(on){tid=syscall(SYS_gettid);cpu=nwt_clock(CLOCK_THREAD_CPUTIME_ID);begin=nwt_clock(CLOCK_MONOTONIC);}}~nwt_scope(){if(on){const auto end=nwt_clock(CLOCK_MONOTONIC),used=nwt_clock(CLOCK_THREAD_CPUTIME_ID)-cpu;std::lock_guard<std::mutex>lock(nwt_mutex);nwt_events.push_back({kind,begin,end,used,tag,tid});}}};
extern "C" __attribute__((visibility("default"))) void np_profile_select(int arm){nwt_on.store(false);std::lock_guard<std::mutex>lock(nwt_mutex);nwt_events.clear();nwt_events.reserve(8192);nwt_on.store(arm>=0);}
extern "C" __attribute__((visibility("default"))) void np_profile_dump(int arm){nwt_on.store(false);std::lock_guard<std::mutex>lock(nwt_mutex);const char*dir=getenv("NFP_TIMELINE_DIR");GGML_ASSERT(dir);std::string path=std::string(dir)+"/arm-"+std::to_string(arm)+".json";FILE*f=fopen(path.c_str(),"w");GGML_ASSERT(f);fprintf(f,"[\n");for(size_t i=0;i<nwt_events.size();++i){const auto&e=nwt_events[i];fprintf(f,"%s{\"kind\":%u,\"begin_ns\":%llu,\"end_ns\":%llu,\"cpu_ns\":%llu,\"tag\":%llu,\"tid\":%ld}",i?",\n":"",e.kind,(unsigned long long)e.begin,(unsigned long long)e.end,(unsigned long long)e.cpu,(unsigned long long)e.tag,e.tid);}fprintf(f,"\n]\n");fclose(f);fprintf(stderr,"NFP_TIMELINE arm=%d events=%zu path=%s\n",arm,nwt_events.size(),path.c_str());}
'''
s=(old/'ggml-vulkan.cpp').read_text();needle='#include "ggml-vulkan-common.h"';s=s.replace(needle,needle+'\n'+code,1)
marks=[('void ggml_vk_synchronize(ggml_backend_vk_context * ctx) {','nwt_scope trace(1,reinterpret_cast<uintptr_t>(ctx));'),('static ggml_status ggml_backend_vk_graph_compute(ggml_backend_t backend, ggml_cgraph * cgraph) {','nwt_scope trace(0,reinterpret_cast<uintptr_t>(backend->context));'),('void vk_queue_handle_synchronized::submit(vk::ArrayProxy<const vk::SubmitInfo> submits, vk::Fence fence) {','nwt_scope trace(3,submits.size());'),('void vk_queue_handle_unsynchronized::submit(vk::ArrayProxy<const vk::SubmitInfo> submits, vk::Fence fence) {','nwt_scope trace(3,submits.size());')]
# Locate the native fence helper without changing its logic.
import re
m=re.search(r'(?:static )?void ggml_vk_wait_for_fence\([^\n]+\) \{',s);assert m;m=m[0];marks.append((m,'nwt_scope trace(2,reinterpret_cast<uintptr_t>(ctx));'))
for needle,addition in marks:assert s.count(needle)==1,needle;s=s.replace(needle,needle+'\n    '+addition,1)
(h/'ggml-vulkan.cpp').write_text(s)
cmds=json.loads((old/'build-argv.json').read_text());cmds=[[v.replace(str(old),str(h))for v in c]for c in cmds];subprocess.run(cmds[0],check=True,cwd=h);subprocess.run(cmds[-1],check=True,cwd=h)
lib=h/'bin/libggml-vulkan.so.0.27.0'
for n in ['libggml-vulkan.so','libggml-vulkan.so.0']:
 if not(h/'bin'/n).exists():(h/'bin'/n).symlink_to(lib.name)
s=(p/'cpu-runner.cpp').read_text().replace('arm<24','arm<4');s=s.replace('    np_select(arm);','    timespec nwt_cpu;clock_gettime(CLOCK_THREAD_CPUTIME_ID,&nwt_cpu);const uint64_t nwt_cpu_begin=uint64_t(nwt_cpu.tv_sec)*1000000000ull+nwt_cpu.tv_nsec;\n    np_select(arm);')
s='#include <ctime>\n'+s;s=s.replace('    auto t_dec_end = ggml_time_us();','    auto t_dec_end = ggml_time_us();\n    clock_gettime(CLOCK_THREAD_CPUTIME_ID,&nwt_cpu);fprintf(stderr,"NFP_DECODE_CPU ns=%llu\\n",(unsigned long long)(uint64_t(nwt_cpu.tv_sec)*1000000000ull+nwt_cpu.tv_nsec-nwt_cpu_begin));')
(p/'timeline-runner.cpp').write_text(s);(p/'timeline-bin').mkdir(exist_ok=True)
cmd=json.loads((p/'cpu-build.json').read_text())['commands'][-1];cmd=[v.replace('cpu-runner.cpp','timeline-runner.cpp').replace('cpu-bin/model-bench','timeline-bin/model-bench')for v in cmd];subprocess.run(cmd,check=True)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'timeline-build.json').write_text(json.dumps(dict(library_sha256=sha(lib),binary_sha256=sha(p/'timeline-bin/model-bench'),commands=[cmds[0],cmds[-1],cmd],kind_mapping={'0':'graph_compute','1':'synchronize','2':'wait_for_fence','3':'queue_submit'},scope='CPUwall/threadtimelinesonly;unchangednativecommands/shaders;fourmeasuredresidentgenerationsaftertwowarmups;noA/Bspeedclaim'),indent=2)+'\n')
