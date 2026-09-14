#pragma once
#include <atomic>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

namespace se {
inline constexpr std::size_t kMaxDialogueLines=64;
enum class DialogueRole:std::uint8_t { External=1,Entity=2 };
struct DialogueLine { std::uint64_t sequence{};double world_time{};DialogueRole role{DialogueRole::External};std::string text; };
struct DialogueSnapshot { std::uint64_t revision{};std::vector<DialogueLine> lines; };
class DialogueSnapshotChannel {
public:
  void publish(double world_time,DialogueRole role,std::string text){auto previous=latest();DialogueSnapshot next;next.revision=previous?previous->revision+1:1;if(previous)next.lines=previous->lines;next.lines.push_back({next.revision,world_time,role,std::move(text)});if(next.lines.size()>kMaxDialogueLines)next.lines.erase(next.lines.begin(),next.lines.begin()+(next.lines.size()-kMaxDialogueLines));latest_.store(std::make_shared<const DialogueSnapshot>(std::move(next)),std::memory_order_release);}
  std::shared_ptr<const DialogueSnapshot> latest()const{return latest_.load(std::memory_order_acquire);}
private:std::atomic<std::shared_ptr<const DialogueSnapshot>>latest_;
};
}
