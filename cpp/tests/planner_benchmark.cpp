#include "se/native_brain_engine.hpp"
#include <algorithm>
#include <chrono>
#include <iostream>
#include <stdexcept>
using namespace se;
int main() {
  std::cout<<"nodes,degree,relations,states,active_per_state,actions,serial_us,parallel_us,gpu_total_us,auto_backend,exact,native_launches\n";
  for(auto nodes:{10000u,100000u,250000u,500000u,1000000u})for(auto degree:{16u,64u}) {
    NativeBrainEngine engine;engine.add_cognits(nodes,.73,.25,.63);
    for(std::uint32_t source=0;source<nodes;++source)for(std::uint32_t k=1;k<=degree;++k)
      engine.add_relation(source,(source+k)%nodes,k%2?RelationType::SelfAction:RelationType::Sequential,
                          k%2?1+k%4:0,.31,.67,.53);
    std::vector<std::uint8_t> actions;for(std::uint8_t action=1;action<=17;++action)actions.push_back(action);
    for(auto [count,active]:{std::pair{1u,8u},std::pair{4u,128u},std::pair{8u,1024u},std::pair{32u,4096u}}) {
      std::vector<std::vector<std::uint32_t>> states(count);
      for(std::uint32_t i=0;i<count;++i)for(std::uint32_t j=0;j<active;++j)states[i].push_back((i*active+j)%nodes);
      engine.set_compute_mode("FORCE_CPU_SERIAL");
      auto expected=engine.planner_transition_batch(states,actions,7,.997,.05);
      bool exact=true;
      auto run=[&](const char*mode) {
        engine.set_compute_mode(mode);std::vector<double> times;
        for(int repeat=0;repeat<6;++repeat) {
          auto start=std::chrono::steady_clock::now();
          auto rows=engine.planner_transition_batch(states,actions,7,.997,.05);
          double us=std::chrono::duration<double,std::micro>(std::chrono::steady_clock::now()-start).count();
          for(std::size_t i=0;i<rows.size();++i)
            exact=exact&&rows[i].predictions==expected[i].predictions&&rows[i].effects==expected[i].effects;
          if(repeat)times.push_back(us);
        }
        std::sort(times.begin(),times.end());return times[times.size()/2];
      };
      auto serial=run("FORCE_CPU_SERIAL"),parallel=run("FORCE_CPU_PARALLEL");
      double gpu=-1.;try {gpu=run("FORCE_GPU");}catch(const std::runtime_error&) {}
      // Compare measured alternatives against a fresh serial incumbent, rather
      // than inheriting the preceding forced-GPU selection during calibration.
      engine.set_compute_mode("FORCE_CPU_SERIAL");engine.planner_transition_batch(states,actions,7,.997,.05);
      engine.set_compute_mode("AUTO");
      for(int i=0;i<8;++i)engine.planner_transition_batch(states,actions,7,.997,.05);
      auto backend=engine.compute_dispatcher().telemetry(KernelClass::PLANNER_TRANSITION_BATCH).selected;
      std::cout<<nodes<<','<<degree<<','<<engine.relation_count()<<','<<count<<','<<active<<','<<actions.size()<<','
               <<serial<<','<<parallel<<','<<gpu<<','<<int(backend)<<','<<exact<<','<<engine.planner_numeric_launches()<<std::endl;
      if(!exact)return 1;
    }
  }
}
