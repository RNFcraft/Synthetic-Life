#include "se/event_scheduler.hpp"
#include <algorithm>
#include <cmath>
#include <stdexcept>
namespace se {
std::uint64_t EventScheduler::schedule(double time,RuntimeEventType type,std::uint64_t payload){if(!std::isfinite(time)||time<now_)throw std::invalid_argument("event time precedes WorldTime");auto id=next_id_++;queue_.push({time,id,type,payload});return id;}
std::vector<RuntimeEvent> EventScheduler::pop_ready(double through){if(!std::isfinite(through)||through<now_)throw std::invalid_argument("WorldTime must be monotonic");std::vector<RuntimeEvent>out;while(!queue_.empty()&&queue_.top().time<=through){now_=queue_.top().time;out.push_back(queue_.top());queue_.pop();}now_=through;return out;}
std::vector<RuntimeEvent> EventScheduler::snapshot()const{auto copy=queue_;std::vector<RuntimeEvent>out;while(!copy.empty()){out.push_back(copy.top());copy.pop();}return out;}
void EventScheduler::restore(double now,std::uint64_t next,const std::vector<RuntimeEvent>&events){if(!std::isfinite(now)||next<1)throw std::invalid_argument("invalid scheduler state");now_=now;next_id_=next;queue_={};for(auto&e:events){if(!std::isfinite(e.time)||e.time<now_||e.id>=next_id_)throw std::invalid_argument("invalid pending event");queue_.push(e);}}
}
