#pragma once
#include <cstdint>
#include <ctime>
#include <string>
enum np_event {NP_GRAPH,NP_BUILD,NP_LEGACY,NP_INDEX,NP_EMPTY,NP_EVENTS};
extern bool np_profile_active();
extern void np_profile_record(unsigned,uint64_t,uint64_t);
inline uint64_t np_clock(clockid_t id){timespec t;clock_gettime(id,&t);return uint64_t(t.tv_sec)*1000000000+uint64_t(t.tv_nsec);}
struct np_scope {unsigned event;bool active;uint64_t w=0,c=0;np_scope(unsigned e,bool eligible=true):event(e),active(eligible&&np_profile_active()){if(active){c=np_clock(CLOCK_THREAD_CPUTIME_ID);w=np_clock(CLOCK_MONOTONIC);}}void stop(){if(active){active=false;auto we=np_clock(CLOCK_MONOTONIC),ce=np_clock(CLOCK_THREAD_CPUTIME_ID);np_profile_record(event,we-w,ce-c);}}~np_scope(){stop();}};
inline bool np_q3_name(const std::string&n){return n=="q3_pad112_matrix"||n=="mul_mat_vec_q3_k_q8_1_f32";}
