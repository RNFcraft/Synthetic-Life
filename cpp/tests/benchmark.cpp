#include "se/native_brain_engine.hpp"
#include <chrono>
#include <iostream>
#include <vector>
#ifdef _WIN32
#include <windows.h>
#include <psapi.h>
#endif
using namespace se;
static std::size_t rss(){
#ifdef _WIN32
 PROCESS_MEMORY_COUNTERS_EX x{};x.cb=sizeof(x);GetProcessMemoryInfo(GetCurrentProcess(),(PROCESS_MEMORY_COUNTERS*)&x,sizeof(x));return x.WorkingSetSize;
#else
 return 0;
#endif
}
static void add_nodes(NativeBrainEngine&e,std::uint32_t n,std::uint32_t active=0){for(std::uint32_t i=0;i<n;++i)e.graph().add_cognit(i<active?1.f:0.f,.05f,.5f);}
int main(){
 std::cout<<"family,cognits,relations,frontier,degree,depth,latency_us,relations_per_sec,touched_per_sec,logical_bytes,reserved_bytes,rss_delta\n";
 for(std::uint32_t n:{10000u,100000u,1000000u}){
  auto base=rss();NativeBrainEngine e;add_nodes(e,n);constexpr std::uint32_t degree=4;
  for(std::uint32_t i=0;i<n;++i)for(std::uint32_t d=1;d<=degree;++d)e.add_relation(i,(i*degree+d)%n,RelationType::Sequential,0,.8f,.8f,.7f);e.prepare();
  for(std::uint32_t frontier:{8u,100u,1000u}){
   std::vector<std::uint32_t>seeds;for(std::uint32_t i=0;i<(std::min)(n,frontier);++i){seeds.push_back(i);e.set_activity(i,1);}
   std::uint64_t traversed=0,touched=0;auto start=std::chrono::steady_clock::now();constexpr int repeats=30;
   for(int r=0;r<repeats;++r){auto result=e.propagate(seeds,r,8);traversed+=result.relations_traversed;touched+=result.active.size();}
   auto seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
   std::cout<<"scaling,"<<n<<","<<e.relation_count()<<","<<frontier<<","<<degree<<",8,"<<seconds*1e6/repeats<<","<<traversed/seconds<<","<<touched/seconds<<","<<e.logical_bytes()<<","<<e.reserved_bytes()<<","<<rss()-base<<std::endl;
  }
 }
 {constexpr std::uint32_t n=100000;auto base=rss();NativeBrainEngine e;add_nodes(e,n,100);e.prepare();std::vector<std::uint32_t>seeds(100);for(std::uint32_t i=0;i<100;++i)seeds[i]=i;
  for(std::uint32_t degree=1;degree<=64;++degree){for(std::uint32_t i=0;i<n;++i)e.add_relation(i,(i+degree)%n,RelationType::Sequential,0,.8f,.8f,.7f);if(degree!=1&&degree!=2&&degree!=4&&degree!=5&&degree!=8&&degree!=9&&degree!=16&&degree!=32&&degree!=64)continue;auto start=std::chrono::steady_clock::now();std::uint64_t traversed=0;for(int r=0;r<20;++r)traversed+=e.propagate(seeds,r,8).relations_traversed;auto seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();std::cout<<"growing,"<<n<<","<<e.relation_count()<<",100,"<<degree<<",8,"<<seconds*1e6/20<<","<<traversed/seconds<<",0,"<<e.logical_bytes()<<","<<e.reserved_bytes()<<","<<rss()-base<<std::endl;}
 }
}
