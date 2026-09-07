#pragma once
#include "cognitive_graph.hpp"
namespace se { struct WaveResult{std::vector<std::uint32_t> active;double energy{};std::uint32_t steps{};std::uint64_t relations_traversed{};double transmitted_energy{};}; WaveResult propagate(CognitiveGraph&,std::span<const std::uint32_t>,std::uint64_t cognitive_tick,std::uint32_t max_steps=8,double retention=.72,double refractory_attenuation=.2); }
