#include "se/neurodynamic_substrate.hpp"
#include <algorithm>
#include <stdexcept>
namespace se {
std::vector<AssemblyBridgeEvent> NeurodynamicSubstrate::assembly_bridge_events_after(std::uint64_t cursor, std::size_t limit) const {
  if (!limit)
    return {};
  if (!bridge_events_.empty() && cursor + 1 < bridge_events_.front().sequence)
    throw std::runtime_error("assembly bridge cursor fell behind bounded event log");
  std::vector<AssemblyBridgeEvent> out;
  out.reserve(std::min(limit, bridge_events_.size()));
  for (auto const &e : bridge_events_)
    if (e.sequence > cursor) {
      out.push_back(e);
      if (out.size() == limit)
        break;
    }
  return out;
}
}
