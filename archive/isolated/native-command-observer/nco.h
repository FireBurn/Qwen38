#pragma once
#include <atomic>
#include <cstdint>
#include <cstring>
#include <initializer_list>
#include <vector>
struct nco_binding { uint64_t buffer,offset,range; };
struct nco_region { uint64_t source,destination,size; };
template<class T> inline uint64_t nco_bits(const T &v){static_assert(sizeof(T)<=8);uint64_t x=0;std::memcpy(&x,&v,sizeof v);return x;}
struct nco_state;
struct nco_scope {
 nco_state *state=nullptr,*previous=nullptr;
 nco_scope(void*,uint64_t,const std::atomic<uint64_t>*,uint64_t);
 ~nco_scope();
};
bool nco_active();
void nco_emit(uint64_t,std::initializer_list<uint64_t>,bool schedule=false);
void nco_vector(uint64_t,const std::vector<uint64_t>&,bool schedule=false);
void nco_dispatch(const char*,uint64_t,uint64_t,uint64_t,const uint32_t*,const nco_binding*,uint32_t,const void*,uint32_t);
void nco_copy(uint64_t,uint64_t,const std::vector<nco_region>&);
void nco_fill(uint64_t,uint64_t,uint64_t,uint32_t);
void nco_unhandled(const char*);
void nco_descriptor_write();
