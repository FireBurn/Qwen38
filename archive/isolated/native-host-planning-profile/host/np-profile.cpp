#include "np-profile.h"
#include <atomic>
#include <cstdio>
struct alignas(64) metric {std::atomic<uint64_t> count{0},wall{0},cpu{0};};
static metric values[NP_EVENTS];static std::atomic<bool> enabled{false};
bool np_profile_active(){return enabled.load(std::memory_order_relaxed);}
void np_profile_record(unsigned e,uint64_t wall,uint64_t cpu){values[e].count.fetch_add(1,std::memory_order_relaxed);values[e].wall.fetch_add(wall,std::memory_order_relaxed);values[e].cpu.fetch_add(cpu,std::memory_order_relaxed);}
extern "C" __attribute__((visibility("default"))) void np_profile_select(int arm){enabled.store(false);for(auto&v:values){v.count=0;v.wall=0;v.cpu=0;}enabled.store(arm>=0);}
extern "C" __attribute__((visibility("default"))) void np_profile_dump(int arm){enabled.store(false);const char*names[]={"gate","mmvq","request","dispatch","descriptor_write","commands","submit_nonempty","graph","all_request","all_dispatch","all_descriptor_write","all_commands","wait_fence","synchronize","build_node","fusion_select","fusion_alias","dependency_check","gdn_state_scan","empty_scope"};for(unsigned i=0;i<NP_EVENTS;++i){fprintf(stderr,"NP_PROFILE arm=%d event=%s count=%llu wall_ns=%llu cpu_ns=%llu",arm,names[i],(unsigned long long)values[i].count.load(),(unsigned long long)values[i].wall.load(),(unsigned long long)values[i].cpu.load());fputc(10,stderr);}}
