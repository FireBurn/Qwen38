// CPU-only reconstruction of the checker's fwrite sizes, not of GPU execution.
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <sys/stat.h>
#include <unistd.h>
int main(int argc,char**argv){
 if(argc!=2)return 2;FILE*f=fopen(argv[1],"wb");if(!f)return 3;
 int ks[]={1,2,3,31,32,33,63,64,65,127,255,256,257,1025,2047,2048,2049,4095,4096,4097,248320};
 int rs[]={1,2,5};int32_t indices[5]={};unsigned records=0;
 for(int k:ks)for(int rows:rs)for(int pattern=0;pattern<14;++pattern){
  uint32_t header[]={0x4152474d,uint32_t(k),uint32_t(rows),uint32_t(pattern)};
  if(fwrite(header,sizeof(header),1,f)!=1||fwrite(indices,sizeof(int32_t),rows,f)!=size_t(rows))return 4;
  ++records;struct stat st;if(stat(argv[1],&st))return 5;
  if(st.st_size==15360)printf("%u %d %d %d\n",records,k,rows,pattern);
 }
 // The failed process aborted, so bypass fclose/flush.
 fflush(stdout);_exit(0);
}
