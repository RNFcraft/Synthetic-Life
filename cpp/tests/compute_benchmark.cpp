#include "se/compute_runtime.hpp"
#include <chrono>
#include <iostream>
using namespace se;
int main(){
  std::cout<<"outputs,degree,serial_us,parallel_us,gpu_total_us,selected,switches\n";
  for(std::size_t n:{8,128,4096,100000,1000000})for(std::size_t degree:{4,32}){
    ReductionBatch b;for(std::size_t i=0;i<n;++i){b.initial.push_back(.8);for(std::size_t j=0;j<degree;++j)b.factors.push_back(.9+double((i+j)%13)*.001);b.offsets.push_back(b.factors.size());}
    ComputeDispatcher d;d.calibrate(KernelClass::ACTION_PREDICTION_BATCH,b);WorkloadShape w;w.pairs=b.initial.size()+b.factors.size();w.bytes=n*16+b.factors.size()*8+b.offsets.size()*8;
    for(int i=0;i<4;++i)d.select(KernelClass::ACTION_PREDICTION_BATCH,w);
    auto&t=d.telemetry(KernelClass::ACTION_PREDICTION_BATCH);
    std::cout<<n<<','<<degree<<','<<t.estimates[0].ema_us<<','<<t.estimates[1].ema_us<<',';
    if(d.gpu_available)std::cout<<t.estimates[2].ema_us;else std::cout<<"UNAVAILABLE";
    std::cout<<','<<int(t.selected)<<','<<t.switches<<std::endl;
  }
}
