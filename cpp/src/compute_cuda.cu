#include "se/compute_runtime.hpp"
#include <cuda_runtime.h>
#include <stdexcept>
namespace se {
static void checked(cudaError_t e){if(e!=cudaSuccess)throw std::runtime_error(cudaGetErrorString(e));}
template<class T> struct DeviceBuffer {
  T*ptr{};
  explicit DeviceBuffer(std::size_t n){if(n)checked(cudaMalloc(reinterpret_cast<void**>(&ptr),n*sizeof(T)));}
  ~DeviceBuffer(){if(ptr)cudaFree(ptr);}
};
__global__ void reduction(const double*initial,const double*factors,const std::uint64_t*offsets,double*out,std::size_t n){
  auto i=std::size_t(blockIdx.x)*blockDim.x+threadIdx.x;if(i>=n)return;
  double p=initial[i];for(auto j=offsets[i];j<offsets[i+1];++j)p=__dmul_rn(p,factors[j]);out[i]=__dsub_rn(1.,p);
}
bool cuda_compute_available(std::size_t&bytes){int count=0;if(cudaGetDeviceCount(&count)!=cudaSuccess||!count){bytes=0;return false;}std::size_t total;return cudaMemGetInfo(&bytes,&total)==cudaSuccess;}
std::vector<double> cuda_reduce_absence(const ReductionBatch&b){
  std::vector<double> out(b.initial.size());if(out.empty())return out;
  DeviceBuffer<double> initial(out.size()),factors(b.factors.size()),result(out.size());DeviceBuffer<std::uint64_t> offsets(b.offsets.size());
  checked(cudaMemcpy(initial.ptr,b.initial.data(),out.size()*sizeof(double),cudaMemcpyHostToDevice));
  if(!b.factors.empty())checked(cudaMemcpy(factors.ptr,b.factors.data(),b.factors.size()*sizeof(double),cudaMemcpyHostToDevice));
  checked(cudaMemcpy(offsets.ptr,b.offsets.data(),b.offsets.size()*sizeof(std::uint64_t),cudaMemcpyHostToDevice));
  reduction<<<unsigned((out.size()+127)/128),128>>>(initial.ptr,factors.ptr,offsets.ptr,result.ptr,out.size());checked(cudaGetLastError());
  checked(cudaMemcpy(out.data(),result.ptr,out.size()*sizeof(double),cudaMemcpyDeviceToHost));return out;
}
}
