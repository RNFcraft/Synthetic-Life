#pragma once
#include <cstdint>
#include <vector>

namespace se {
enum class ActionType : std::uint8_t { Idle=1, MoveUp, MoveDown, MoveLeft, MoveRight, GrabUp, GrabDown, GrabLeft, GrabRight, Release, InteractUp, InteractDown, InteractLeft, InteractRight, TurnLeft, TurnRight, Interact };
enum class ActionResult : std::uint8_t { Success=1, Blocked, Invalid };
enum class RelationType : std::uint8_t { Associative=1, Sequential, Causal, Inhibitory, SelfAction, Spatial };
enum class RelationStatus : std::uint8_t { Provisional=1, Consolidated };
struct SensoryCell { std::int16_t dx{},dy{}; bool occupied{},boundary{},self{}; std::int16_t state{},appearance{}; };
struct BodySense { bool up{},down{},left{},right{},holding{}; double resistance{}; };
struct SensoryFrame { std::uint64_t world_tick{}; std::vector<SensoryCell> cells; BodySense body; };
}
