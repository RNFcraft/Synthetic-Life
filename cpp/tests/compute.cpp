#ifdef NDEBUG
#undef NDEBUG
#endif
#include "se/compute_runtime.hpp"
#include <cassert>
#include <bit>
#include <iostream>
#include <stdexcept>
using namespace se;
int main(){
  ComputeDispatcher d;WorkloadShape w;w.pairs=100;w.bytes=1024;
  auto k=KernelClass::ACTION_PREDICTION_BATCH;
  assert(d.select(k,w)==ComputeBackend::CPU_SERIAL);
  d.mode=ComputeMode::FORCE_GPU;bool failed=false;try{d.select(k,w);}catch(const std::runtime_error&){failed=true;}assert(failed);
  d.mode=ComputeMode::AUTO;d.gpu_available=true;d.gpu_free_bytes=4096;
  d.sample(k,ComputeBackend::CPU_SERIAL,100,100);d.sample(k,ComputeBackend::GPU,30,100);
  for(int i=0;i<3;++i)assert(d.select(k,w)==ComputeBackend::CPU_SERIAL);
  assert(d.select(k,w)==ComputeBackend::GPU);
  d.sample(k,ComputeBackend::CPU_SERIAL,1,100);
  assert(d.select(k,w)==ComputeBackend::GPU); // one noisy observation is insufficient
  for(int i=0;i<40;++i)d.sample(k,ComputeBackend::CPU_SERIAL,1,100);
  for(int i=0;i<3;++i)assert(d.select(k,w)==ComputeBackend::GPU);
  assert(d.select(k,w)==ComputeBackend::CPU_SERIAL);
  w.required_revision=2;w.applied_revision=1;assert(d.select(k,w)!=ComputeBackend::GPU);
  w.required_revision=1;w.bytes=5000;assert(d.select(k,w)!=ComputeBackend::GPU);
  ComputeDispatcher planner;WorkloadShape sparse,dense;
  sparse.states=8;sparse.actions=17;sparse.pairs=136;sparse.numeric_units=1024;sparse.average_degree=4;
  dense=sparse;dense.average_degree=64;
  auto pk=KernelClass::PLANNER_TRANSITION_BATCH;
  planner.sample(pk,ComputeBackend::CPU_SERIAL,100,1024,&sparse);
  planner.sample(pk,ComputeBackend::CPU_PARALLEL,10,1024,&sparse);
  for(int i=0;i<4;++i)planner.select(pk,sparse);
  assert(planner.select(pk,sparse)==ComputeBackend::CPU_PARALLEL);
  // Equal pairs AND equal derived work must not reuse an unrelated degree cell.
  assert(planner.select(pk,dense)==ComputeBackend::CPU_SERIAL);
  planner.sample(pk,ComputeBackend::CPU_SERIAL,10,1024,&dense);
  planner.sample(pk,ComputeBackend::CPU_PARALLEL,100,1024,&dense);
  for(int i=0;i<4;++i)assert(planner.select(pk,dense)==ComputeBackend::CPU_SERIAL);
  ReductionBatch b;
  for(int i=0;i<10000;++i){b.initial.push_back(.83);for(int j=0;j<i%17;++j)b.factors.push_back(.9+double((i+j)%13)*.001);b.offsets.push_back(b.factors.size());}
  auto serial=reduce_absence(b,ComputeBackend::CPU_SERIAL);
  for(int repeat=0;repeat<8;++repeat)assert(serial==reduce_absence(b,ComputeBackend::CPU_PARALLEL));
  std::size_t bytes;bool gpu=cuda_compute_available(bytes);
  if(gpu){auto out=reduce_absence(b,ComputeBackend::GPU);for(std::size_t i=0;i<out.size();++i)assert(std::bit_cast<std::uint64_t>(out[i])==std::bit_cast<std::uint64_t>(serial[i]));}
  std::cout<<"CPU parallel exact PASS; GPU "<<(gpu?"exact PASS":"SKIPPED: backend/device unavailable")<<'\n';
}
