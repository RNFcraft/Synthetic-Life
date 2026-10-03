#include "se/compute_runtime.hpp"
#include <algorithm>
#include <cmath>
#include <bit>
#include <condition_variable>
#include <chrono>
#include <exception>
#include <mutex>
#include <stdexcept>
#include <thread>
namespace se {
static std::size_t workload_bucket(double units){std::size_t b=0;while(units>=2. && b<23){units/=2.;++b;}return b;}
void ComputeDispatcher::calibrate(KernelClass k,const ReductionBatch& batch) {
  gpu_available=cuda_compute_available(gpu_free_bytes);
  auto expected=reduce_absence(batch,ComputeBackend::CPU_SERIAL);
  const auto bytes=batch.initial.size()*16+batch.factors.size()*8+batch.offsets.size()*8;
  for(auto b:{ComputeBackend::CPU_SERIAL,ComputeBackend::CPU_PARALLEL,ComputeBackend::GPU}) {
    if(b==ComputeBackend::GPU && (!gpu_available || bytes>policy.memory_budget || bytes>gpu_free_bytes))continue;
    for(int repeat=0;repeat<6;++repeat){
      auto start=std::chrono::steady_clock::now();auto out=reduce_absence(batch,b);
      auto us=std::chrono::duration<double,std::micro>(std::chrono::steady_clock::now()-start).count();
      if(out.size()!=expected.size())throw std::runtime_error("compute calibration failed output size");
      for(std::size_t i=0;i<out.size();++i)if(std::bit_cast<std::uint64_t>(out[i])!=std::bit_cast<std::uint64_t>(expected[i]))throw std::runtime_error("compute calibration failed exact numerical contract");
      if(repeat)sample(k,b,us,double(std::max<std::size_t>(1,batch.initial.size()+batch.factors.size())));
    }
  }
}
void ComputeDispatcher::sample(KernelClass k, ComputeBackend b, double us, double units) {
  if (!std::isfinite(us) || us<0 || !std::isfinite(units) || units<=0) throw std::invalid_argument("invalid performance sample");
  auto &e=kernels_[std::size_t(k)].estimates[std::size_t(b)];
  e.ema_us=e.count ? .8*e.ema_us+.2*us : us;
  e.units=e.count ? .8*e.units+.2*units : units; ++e.count;
  auto &bucket=costs_[std::size_t(k)][workload_bucket(units)][std::size_t(b)];
  bucket.ema_us=bucket.count ? .8*bucket.ema_us+.2*us : us;
  bucket.units=bucket.count ? .8*bucket.units+.2*units : units;++bucket.count;
}
ComputeBackend ComputeDispatcher::select(KernelClass k, const WorkloadShape& w) {
  auto &t=kernels_[std::size_t(k)];
  bool gpu_ok=gpu_available && w.bytes<=policy.memory_budget && w.bytes<=gpu_free_bytes && w.required_revision==w.applied_revision;
  if (mode==ComputeMode::FORCE_GPU && !gpu_ok) throw std::runtime_error("FORCE_GPU unavailable: device, memory budget or mirror revision");
  auto forced=mode==ComputeMode::FORCE_GPU ? ComputeBackend::GPU : mode==ComputeMode::FORCE_CPU_PARALLEL ? ComputeBackend::CPU_PARALLEL : ComputeBackend::CPU_SERIAL;
  auto change=[&](ComputeBackend b){if(t.selected!=b){++t.switches;t.selected=b;}t.streak=0;};
  if(mode!=ComputeMode::AUTO){change(forced);t.reason="forced host mode";return forced;}
  if(t.selected==ComputeBackend::GPU && !gpu_ok){change(ComputeBackend::CPU_SERIAL);t.reason="GPU memory/revision/device fallback";}
  const double units=double(std::max<std::size_t>(1,w.pairs));
  if(!costs_[std::size_t(k)][workload_bucket(units)][std::size_t(t.selected)].count && t.selected!=ComputeBackend::CPU_SERIAL){change(ComputeBackend::CPU_SERIAL);t.reason="uncalibrated workload bucket: CPU serial";}
  auto cost=[&](ComputeBackend b){const auto&e=costs_[std::size_t(k)][workload_bucket(units)][std::size_t(b)];return e.count ? e.ema_us*units/e.units+(b==ComputeBackend::GPU?w.transfer_us+w.synchronization_us+w.queue_us:0.) : 1e300;};
  auto best=t.selected;
  for(auto b:{ComputeBackend::CPU_SERIAL,ComputeBackend::CPU_PARALLEL,ComputeBackend::GPU})
    if((b!=ComputeBackend::GPU||gpu_ok) && cost(b)<cost(best))best=b;
  if(best!=t.selected && cost(best)<cost(t.selected)*(1.-std::clamp(policy.margin,0.,.9))){
    if(t.candidate!=best){t.candidate=best;t.streak=0;}
    if(++t.streak>=std::clamp(policy.observations,1u,100u)){change(best);t.reason="sustained measured cost advantage";}
    else t.reason="hysteresis: collecting sustained advantage";
  } else {t.streak=0;t.reason="retain measured backend / conservative fallback";}
  return t.selected;
}
class WorkerPool::Impl {
public:
  std::mutex call_mutex,mutex; std::condition_variable start,done;
  std::vector<std::thread> threads; bool stopping{}; std::size_t epoch{},remaining{},count{};
  std::function<void(std::size_t)> task; std::exception_ptr error;
  explicit Impl(unsigned n){
    n=std::clamp(n?n:std::thread::hardware_concurrency()/2,1u,8u);
    for(unsigned id=0;id<n;++id)threads.emplace_back([this,id,n]{
      std::size_t seen=0;
      for(;;){std::unique_lock lock(mutex);start.wait(lock,[&]{return stopping||epoch!=seen;});if(stopping)return;
        seen=epoch;auto f=task;auto total=count;lock.unlock();
        try{for(std::size_t i=total*id/n;i<total*(id+1)/n;++i)f(i);}catch(...){std::lock_guard guard(mutex);if(!error)error=std::current_exception();}
        lock.lock();if(--remaining==0)done.notify_one();
      }
    });
  }
  ~Impl(){{std::lock_guard lock(mutex);stopping=true;}start.notify_all();for(auto&t:threads)t.join();}
};
WorkerPool::WorkerPool(unsigned n):impl_(std::make_unique<Impl>(n)){}
WorkerPool::~WorkerPool()=default;
void WorkerPool::run(std::size_t n,const std::function<void(std::size_t)>&f){
  auto &p=*impl_;std::lock_guard call(p.call_mutex);std::unique_lock lock(p.mutex);
  // A caller owns the pool until all workers complete. Native engine itself is single-owner.
  p.done.wait(lock,[&]{return p.remaining==0;});p.task=f;p.count=n;p.error=nullptr;p.remaining=p.threads.size();++p.epoch;p.start.notify_all();
  p.done.wait(lock,[&]{return p.remaining==0;});p.task={};if(p.error)std::rethrow_exception(p.error);
}
WorkerPool& numeric_workers(){static WorkerPool pool;return pool;}
std::vector<double> reduce_absence(const ReductionBatch&b,ComputeBackend backend){
  if(b.offsets.size()!=b.initial.size()+1 || b.offsets.back()!=b.factors.size())throw std::invalid_argument("invalid reduction batch");
  if(b.offsets.front()!=0 || !std::is_sorted(b.offsets.begin(),b.offsets.end()))throw std::invalid_argument("invalid reduction offsets");
  if(backend==ComputeBackend::GPU)return cuda_reduce_absence(b);
  std::vector<double> out(b.initial.size());
  auto one=[&](std::size_t i){double p=b.initial[i];for(auto j=b.offsets[i];j<b.offsets[i+1];++j)p*=b.factors[j];out[i]=1.-p;};
  if(backend==ComputeBackend::CPU_PARALLEL && out.size()>1)numeric_workers().run(out.size(),one);
  else for(std::size_t i=0;i<out.size();++i)one(i);
  return out;
}
#ifndef SE_WITH_CUDA
bool cuda_compute_available(std::size_t& bytes){bytes=0;return false;}
std::vector<double> cuda_reduce_absence(const ReductionBatch&){throw std::runtime_error("CUDA compute backend was not built (SE_ENABLE_CUDA=OFF)");}
#endif
}
