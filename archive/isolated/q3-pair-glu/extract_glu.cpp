#include <cstdint>
#include <cstdio>
extern const unsigned char swiglu_f32_data[];extern const uint64_t swiglu_f32_len;int main(int argc,char**argv){if(argc!=2)return 2;FILE*f=fopen(argv[1],"wb");if(!f)return 3;auto n=fwrite(swiglu_f32_data,1,swiglu_f32_len,f);fclose(f);return n==swiglu_f32_len?0:4;}