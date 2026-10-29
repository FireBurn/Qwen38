from pathlib import Path
import json,subprocess,shutil,hashlib
p=Path(__file__).resolve().parent;old=p/'host';h=p/'cost-host';h.mkdir(exist_ok=True);(h/'bin').mkdir(exist_ok=True)
for f in old.glob('*.h'):shutil.copy2(f,h/f.name)
src=p.parent/'native-host-planning-profile/host'
s=(src/'np-profile.h').read_text();a=s.index('enum np_event');z=s.index(';',a);s=s[:a]+'enum np_event {NP_GRAPH,NP_BUILD,NP_LEGACY,NP_INDEX,NP_EMPTY,NP_EVENTS}'+s[z:];(h/'np-profile.h').write_text(s)
s=(src/'np-profile.cpp').read_text();a=s.index('const char*names[]={');z=s.index('};',a);s=s[:a]+'const char*names[]={"graph","index_build","legacy_query","index_query","empty_scope"'+s[z:];(h/'np-profile.cpp').write_text(s)
s=(old/'ggml-vulkan.cpp').read_text();s='#include "np-profile.h"\n'+s
for sig,event in [('static gdn_reader_index ggml_vk_gdn_readers(const ggml_cgraph*graph){','NP_BUILD'),('static int ggml_vk_find_gdn_state_cpy(const struct ggml_cgraph * cgraph, int node_idx) {','NP_LEGACY'),('static int ggml_vk_find_gdn_state_cpy_indexed(const struct ggml_cgraph * cgraph, int node_idx, const gdn_reader_index& readers) {','NP_INDEX'),('static ggml_status ggml_backend_vk_graph_compute(ggml_backend_t backend, ggml_cgraph * cgraph) {','NP_GRAPH')]:
 assert s.count(sig)==1,sig;s=s.replace(sig,sig+'\n    np_scope np_measure('+event+');')
needle='            ++reader_calls;';assert s.count(needle)==1;s=s.replace(needle,'            {np_scope np_empty(NP_EMPTY);}\n'+needle)
(h/'ggml-vulkan.cpp').write_text(s);cmds=json.loads((old/'build-argv.json').read_text());cmds=[[v.replace(str(old),str(h))for v in c]for c in cmds]
extra=[cmds[0][0],'-std=c++17','-stdlib=libc++','-O3','-fPIC','-fvisibility=hidden','-c',str(h/'np-profile.cpp'),'-o',str(h/'np-profile.cpp.o')];cmds.insert(1,extra);cmds[-1].insert(cmds[-1].index('-lvulkan'),str(h/'np-profile.cpp.o'));(h/'build-argv.json').write_text(json.dumps(cmds,indent=2)+'\n')
for c in cmds:subprocess.run(c,check=True,cwd=h)
lib=h/'bin/libggml-vulkan.so.0.27.0'
for n in ['libggml-vulkan.so','libggml-vulkan.so.0']:
 f=h/'bin'/n
 if not f.exists():f.symlink_to(lib.name)
(h/'build.json').write_text(json.dumps(dict(library_sha256=hashlib.sha256(lib.read_bytes()).hexdigest(),sources={f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in h.iterdir()if f.suffix in ['.h','.cpp']},scope='CPU-cost diagnostic only;graph includes index construction/destruction,queries/timers. No throughput inference.'),indent=2)+'\n')
q=p.parent/'q3-pad112';s=(q/'profile-runner.cpp').read_text();needle='        bool pad=arm<0||((arm/4)%2==0?(arm%4==1||arm%4==2):(arm%4==0||arm%4==3));';assert needle in s;s=s.replace(needle,'        bool indexed=arm<0||((arm/4)%2==0?(arm%4==1||arm%4==2):(arm%4==0||arm%4==3));bool pad=true;setenv("GGML_VK_GDN_READER_INDEX",indexed?"1":"0",1);').replace('pad?"pad":"control"','indexed?"indexed":"legacy"');(p/'cost-runner.cpp').write_text(s)
c=json.loads((q/'profile-runner-build.json').read_text())['command'];c=[v.replace(str(q/'profile-runner.cpp'),str(p/'cost-runner.cpp')).replace(str(q/'profile-model-bench'),str(p/'cost-model-bench'))for v in c];subprocess.run(c,check=True,cwd=p)
(p/'cost-runner-build.json').write_text(json.dumps(dict(command=c,source_sha256=hashlib.sha256(s.encode()).hexdigest(),binary_sha256=hashlib.sha256((p/'cost-model-bench').read_bytes()).hexdigest()),indent=2)+'\n');print('GDN_COST_PROFILE_BUILT')
