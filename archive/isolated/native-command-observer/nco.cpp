#include "nco.h"
#include <cstdio>
#include <cstdlib>
#include <string>
#include <mutex>
#include <algorithm>
#include <utility>
struct nco_state {
 void*ctx;uint64_t graph,nodes,destroy_begin,flags,dispatches=0,barriers=0,copies=0,fills=0,desc_writes=0;
 const std::atomic<uint64_t>*destroy;
 std::string dir;std::vector<uint8_t> program,schedule;std::vector<std::string> unhandled;
};
static thread_local nco_state*current=nullptr;
static std::atomic<uint64_t> next_graph{0};
struct saved {void*ctx;uint64_t nodes,destroy,flags,first;std::vector<uint8_t> bytes;};
static std::mutex guard;static std::vector<saved> programs;static uint64_t saved_bytes=0;
static void u64(std::vector<uint8_t>&v,uint64_t n){for(int i=0;i<8;++i)v.push_back(uint8_t(n>>(8*i)));}
static void raw(std::vector<uint8_t>&v,const void*p,size_t n){if(!n)return;auto*b=static_cast<const uint8_t*>(p);v.insert(v.end(),b,b+n);}
static void record(std::vector<uint8_t>&v,uint64_t tag,const std::vector<uint8_t>&p){u64(v,tag);u64(v,p.size());v.insert(v.end(),p.begin(),p.end());}
static uint64_t hash(const std::vector<uint8_t>&v){uint64_t h=14695981039346656037ull;for(uint8_t b:v){h^=b;h*=1099511628211ull;}return h;}
bool nco_active(){return current!=nullptr;}
void nco_vector(uint64_t tag,const std::vector<uint64_t>&x,bool schedule){if(!current)return;std::vector<uint8_t> p;for(auto v:x)u64(p,v);record(schedule?current->schedule:current->program,tag,p);if(tag==2)++current->barriers;}
void nco_emit(uint64_t tag,std::initializer_list<uint64_t>x,bool schedule){if(current)nco_vector(tag,std::vector<uint64_t>(x),schedule);}
void nco_unhandled(const char*s){if(!current)return;current->unhandled.emplace_back(s);std::vector<uint8_t>p;raw(p,s,std::strlen(s));record(current->program,255,p);}
void nco_descriptor_write(){if(current)++current->desc_writes;}
void nco_dispatch(const char*name,uint64_t pl,uint64_t layout,uint64_t ds,const uint32_t*wg,const nco_binding*b,uint32_t nb,const void*pc,uint32_t np){
 if(!current)return;std::vector<uint8_t>p;for(auto v:{pl,layout,ds})u64(p,v);for(int i=0;i<3;++i)u64(p,wg[i]);u64(p,nb);
 for(uint32_t i=0;i<nb;++i){u64(p,b[i].buffer);u64(p,b[i].offset);u64(p,b[i].range);}u64(p,np);raw(p,pc,np);u64(p,std::strlen(name));raw(p,name,std::strlen(name));record(current->program,1,p);++current->dispatches;
}
void nco_copy(uint64_t src,uint64_t dst,const std::vector<nco_region>&r){if(!current)return;std::vector<uint8_t>p;u64(p,src);u64(p,dst);u64(p,r.size());for(auto&x:r){u64(p,x.source);u64(p,x.destination);u64(p,x.size);}record(current->program,5,p);++current->copies;}
void nco_fill(uint64_t dst,uint64_t offset,uint64_t size,uint32_t value){if(!current)return;nco_emit(4,{dst,offset,size,value});++current->fills;}
nco_scope::nco_scope(void*ctx,uint64_t nodes,const std::atomic<uint64_t>*destroy,uint64_t flags){
 previous=current;current=nullptr;const char*dir=std::getenv("GGML_VK_CMD_OBSERVER_DIR");if(!dir||!*dir)return;
 state=new nco_state{};state->ctx=ctx;state->nodes=nodes;state->destroy=destroy;state->destroy_begin=destroy->load(std::memory_order_acquire);state->flags=flags;state->dir=dir;state->graph=next_graph.fetch_add(1);current=state;
}
static bool write_file(const std::string&name,const std::vector<uint8_t>&v){FILE*f=std::fopen(name.c_str(),"wb");if(!f)return false;bool ok=std::fwrite(v.data(),1,v.size(),f)==v.size();return std::fclose(f)==0&&ok;}
nco_scope::~nco_scope(){
 current=previous;if(!state)return;auto&s=*state;uint64_t end=s.destroy->load(std::memory_order_acquire);std::lock_guard<std::mutex>lock(guard);int64_t id=-1,repeat=-1;bool dropped=false,io_ok=true;
 for(size_t i=0;i<programs.size();++i){auto&r=programs[i];if(r.ctx==s.ctx&&r.nodes==s.nodes&&r.destroy==s.destroy_begin&&r.flags==s.flags&&r.bytes==s.program){id=i;repeat=r.first;break;}}
 if(id<0){if(saved_bytes+s.program.size()>(128ull<<20)||programs.size()>=1024)dropped=true;else{id=programs.size();programs.push_back({s.ctx,s.nodes,s.destroy_begin,s.flags,s.graph,s.program});saved_bytes+=s.program.size();char name[64];std::snprintf(name,sizeof name,"/program-%04lld.bin",(long long)id);io_ok=write_file(s.dir+name,s.program);}}
 char name[64];std::snprintf(name,sizeof name,"/schedule-%05llu.bin",(unsigned long long)s.graph);io_ok=write_file(s.dir+name,s.schedule)&&io_ok;
 FILE*f=std::fopen((s.dir+"/graphs.jsonl").c_str(),"a");if(f){
  std::fprintf(f,"{\"graph\":%llu,\"context\":\"%p\",\"nodes\":%llu,\"entry_flags\":%llu,\"destroy_begin\":%llu,\"destroy_end\":%llu,\"program_id\":%lld,\"repeat_of_graph\":%lld,\"program_bytes\":%zu,\"program_hash_fnv64\":\"%016llx\",\"schedule_bytes\":%zu,\"schedule_hash_fnv64\":\"%016llx\",\"dispatches\":%llu,\"barriers\":%llu,\"copies\":%llu,\"fills\":%llu,\"descriptor_writes\":%llu,\"dropped\":%s,\"io_ok\":%s,\"unhandled\":[",(unsigned long long)s.graph,s.ctx,(unsigned long long)s.nodes,(unsigned long long)s.flags,(unsigned long long)s.destroy_begin,(unsigned long long)end,(long long)id,(long long)repeat,s.program.size(),(unsigned long long)hash(s.program),s.schedule.size(),(unsigned long long)hash(s.schedule),(unsigned long long)s.dispatches,(unsigned long long)s.barriers,(unsigned long long)s.copies,(unsigned long long)s.fills,(unsigned long long)s.desc_writes,dropped?"true":"false",io_ok?"true":"false");
  for(size_t i=0;i<s.unhandled.size();++i)std::fprintf(f,"%s\"%s\"",i?",":"",s.unhandled[i].c_str());std::fputs("]}\n",f);std::fclose(f);
 }else std::fprintf(stderr,"NCO_IO_FAILED graph=%llu\n",(unsigned long long)s.graph);delete state;
}
