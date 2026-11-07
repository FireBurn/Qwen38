#include <dlfcn.h>
#include <cstdio>
#include <fstream>
#include <string>
int main(){void *p=dlopen("/usr/lib64/llama.cpp/libllama-server-impl.so",RTLD_NOW|RTLD_LOCAL);if(!p){fprintf(stderr,"dlopen: %s\n",dlerror());return 1;}std::ifstream f("/proc/self/maps");std::string line;while(std::getline(f,line))if(line.find("libllama.so")!=std::string::npos||line.find("libggml")!=std::string::npos)puts(line.c_str());return 0;}
