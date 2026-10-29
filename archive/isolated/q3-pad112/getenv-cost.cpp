#include <cstdlib>
#include <cstdio>
#include <cstdint>
#include <ctime>
static uint64_t now(){timespec t;clock_gettime(CLOCK_THREAD_CPUTIME_ID,&t);return uint64_t(t.tv_sec)*1000000000+t.tv_nsec;}
int main(){char*(*volatile fn)(const char*)=getenv;uintptr_t acc=0;for(const char*name:{"GGML_VK_Q3_PAD112_DIR","GGML_VK_Q3_PAD112_IMMUTABLE","GGML_VK_MEGA"}){uint64_t begin=now();for(int i=0;i<100000;++i)acc^=(uintptr_t)fn(name);auto end=now();printf("ENV_COST name=%s calls=100000 cpu_ns_per_call=%.3f",name,double(end-begin)/100000);fputc(10,stdout);}return acc!=0;}
