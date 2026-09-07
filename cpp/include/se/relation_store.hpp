#pragma once
#include "types.hpp"
#include <array>
#include <cstdint>
#include <limits>
#include <vector>
namespace se {
constexpr std::uint32_t no_slot=std::numeric_limits<std::uint32_t>::max();
struct RelationHandle{std::uint32_t page{},slot{},generation{};};
struct ProvisionalData{std::uint32_t support{};double lift{1},contradiction{},usefulness{};std::uint32_t confirmations{};std::uint64_t last_evidence_world_tick{};};
struct ConsolidatedData{std::uint32_t support{},confirmations{};double contradiction{},usefulness{},lift{1};std::uint64_t last_evidence_world_tick{};};
struct Edge{std::uint32_t target{};double strength{.2},confidence{.3},prediction{};RelationType type{RelationType::Associative};std::uint32_t action{};RelationStatus status{RelationStatus::Provisional};std::uint32_t payload{},generation{1};std::uint64_t last_used_cognitive_tick{};bool alive{true};};
struct PersistedRelation{std::uint32_t source{},target{},support{},confirmations{};double strength{},confidence{},prediction{},lift{1},contradiction{},usefulness{};std::uint64_t last_used_cognitive_tick{},last_evidence_world_tick{};std::uint8_t type{},status{};std::uint32_t action{};};
class RelationStore{
 static constexpr std::uint32_t page_size=256;struct Slot{Edge edge{};std::uint32_t source{},next{no_slot};};struct Page{std::array<Slot,page_size>slots;};
public:
 void resize_nodes(std::size_t n){heads_.resize(n,no_slot);tails_.resize(n,no_slot);}
 std::pair<Edge&,RelationHandle> connect(std::uint32_t source,std::uint32_t target,RelationType type,std::uint32_t action=0);
 bool erase(RelationHandle);bool valid(RelationHandle)const;Edge* get(RelationHandle);const Edge* get(RelationHandle)const;
 template<class F>void for_each(std::uint32_t source,F&&f){for(auto x=heads_.at(source);x!=no_slot;x=slot(x).next){auto&s=slot(x);if(s.edge.alive)f(s.edge,handle(x,s.edge.generation));}}
 template<class F>void for_each(std::uint32_t source,F&&f)const{for(auto x=heads_.at(source);x!=no_slot;x=slot(x).next){auto&s=slot(x);if(s.edge.alive)f(s.edge,handle(x,s.edge.generation));}}
 ProvisionalData& provisional(Edge&e){return provisional_.at(e.payload);}const ProvisionalData& provisional(const Edge&e)const{return provisional_.at(e.payload);}
 ConsolidatedData& consolidated(Edge&e){return consolidated_.at(e.payload);}const ConsolidatedData& consolidated(const Edge&e)const{return consolidated_.at(e.payload);}
 std::uint32_t support(const Edge&e)const{return e.status==RelationStatus::Provisional?provisional_[e.payload].support:consolidated_[e.payload].support;}std::uint64_t last_evidence(const Edge&e)const{return e.status==RelationStatus::Provisional?provisional_[e.payload].last_evidence_world_tick:consolidated_[e.payload].last_evidence_world_tick;}
 void consolidate(RelationHandle);std::size_t size()const{return live_;}std::size_t provisional_count()const{return provisional_live_;}std::size_t consolidated_count()const{return consolidated_live_;}std::size_t reserved_bytes()const;std::size_t logical_bytes()const;
 std::vector<PersistedRelation> snapshot()const;std::vector<RelationHandle> handles()const;void restore(std::size_t node_count,const std::vector<PersistedRelation>&);
 PersistedRelation state(std::uint32_t source,RelationHandle)const;void update(RelationHandle,const PersistedRelation&);
 void make_provisional(RelationHandle);
 static constexpr std::size_t provisional_record_bytes(){return sizeof(Edge)+sizeof(ProvisionalData)+sizeof(std::uint32_t)*2;}static constexpr std::size_t consolidated_record_bytes(){return sizeof(Edge)+sizeof(ConsolidatedData)+sizeof(std::uint32_t)*2;}
private:
 std::vector<std::uint32_t>heads_,tails_,free_;std::vector<Page>pages_;std::vector<ProvisionalData>provisional_;std::vector<ConsolidatedData>consolidated_;std::uint32_t allocated_{};std::size_t live_{},provisional_live_{},consolidated_live_{};
 Slot&slot(std::uint32_t i){return pages_[i/page_size].slots[i%page_size];}const Slot&slot(std::uint32_t i)const{return pages_[i/page_size].slots[i%page_size];}static RelationHandle handle(std::uint32_t i,std::uint32_t g){return{i/page_size,i%page_size,g};}static std::uint32_t index(RelationHandle h){return h.page*page_size+h.slot;}
};
}
