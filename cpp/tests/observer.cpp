#include "se/observer.hpp"

#include <cassert>
#include <cmath>
#include <atomic>
#include <thread>
#include <unordered_set>
#include <numeric>
#include "se/world.hpp"
#include "se/native_brain_engine.hpp"

int main() {
    se::RenderSnapshot snapshot;
    snapshot.world_width = 8;
    snapshot.world_height = 4;
    snapshot.bodies.push_back({1, 2, 1, 'E', 0, 9});
    snapshot.objects.push_back({7, 6, 3, 0});
    const auto draws = se::prepare_draw_data(snapshot, 800, 400);
    assert(draws.size() == 5); // grid, free object, body, orientation, held marker
    assert(draws[0].kind == se::DrawPrimitiveKind::grid);
    assert(draws[1].kind == se::DrawPrimitiveKind::object);
    assert(draws[2].kind == se::DrawPrimitiveKind::body);
    assert(draws[3].direction_x == 1.0f && draws[3].direction_y == 0.0f);
    assert(draws[4].id == 9);
    const auto fit = se::fit_world_to_viewport(8, 4, 800, 400);
    assert(std::isfinite(fit.cell_size) && fit.cell_size > 0.0f);
    assert(fit.grid_width <= 800.0f && fit.grid_height <= 400.0f);
    assert(std::abs(fit.grid_width / fit.grid_height - 2.0f) < 0.001f);
    assert(se::prepare_draw_data({}, 800, 400).empty());
    const auto before = snapshot;
    snapshot.objects.clear();
    const auto changed = se::prepare_draw_data(snapshot, 800, 400);
    assert(changed.size() == 4);
    assert(before.objects.size() == 1); // draw preparation never writes its input.
    se::RenderSnapshotChannel channel;
    se::RenderSnapshot retained;
    retained.world_width=3; retained.world_height=2; retained.event_sequence=1;
    channel.publish(retained);
    auto old=channel.latest();
    std::atomic<bool> done{false};
    std::thread writer([&]{ for(std::uint64_t n=2;n<2000;++n){ se::RenderSnapshot value; value.world_width=3;value.world_height=2;value.world_time=double(n);value.event_sequence=n;value.bodies.push_back({1,1,1,'N',1,0});channel.publish(std::move(value)); } done=true; });
    std::thread reader([&]{ std::uint64_t previous=0; while(!done){auto value=channel.latest();if(value){assert(value->world_width>0&&value->world_height>0);assert(std::isfinite(value->world_time));assert(value->event_sequence>=previous);previous=value->event_sequence;std::unordered_set<unsigned> ids;for(auto const& body:value->bodies)assert(ids.insert(body.id).second);}} });
    writer.join(); reader.join();
    assert(old->event_sequence==1); // retained immutable snapshots survive publication.
    auto latest=channel.latest(); assert(latest->event_sequence==1999); // no consumption is required.
    se::BrainSnapshotChannel brains;se::BrainSnapshot first;first.cognitive_tick=1;first.nodes.push_back({1,.2,.3,.4,false,true,1});brains.publish(first);auto retained_brain=brains.latest();
    for(std::uint64_t n=2;n<100;++n){se::BrainSnapshot value;value.cognitive_tick=n;value.nodes.push_back({std::uint32_t(n),.8,.3,.7,false,true,n});brains.publish(std::move(value));}
    assert(retained_brain->cognitive_tick==1&&retained_brain->nodes[0].activity==.2);assert(brains.latest()->cognitive_tick==99);
    std::atomic<bool> brain_done{false};std::thread brain_writer([&]{for(std::uint64_t n=100;n<2000;++n){se::BrainSnapshot v;v.cognitive_tick=n;v.nodes.push_back({unsigned(n),.5,.2,.6,false,true,n});brains.publish(std::move(v));}brain_done=true;});std::thread brain_reader([&]{std::uint64_t previous=0;while(!brain_done){auto v=brains.latest();if(v){assert(v->cognitive_tick>=previous);previous=v->cognitive_tick;assert(v->nodes.size()==1);}}});brain_writer.join();brain_reader.join();assert(brains.latest()->cognitive_tick==1999);
    se::NativeBrainEngine engine;engine.add_cognits(3);engine.set_activity(1,.9);engine.add_relation(0,1,se::RelationType::Sequential,0,.8,.7,0);std::uint32_t active[]={1};engine.publish_brain_snapshot(2.5,7,4,active);auto graph=engine.brain_snapshot_channel()->latest();assert(graph->nodes.size()==3&&graph->edges.size()==1&&graph->nodes[1].activity==.9&&graph->edges[0].source==0&&graph->edges[0].target==1);
    auto graph_draw=se::prepare_brain_draw_data(*graph,300,240);assert(graph_draw.nodes.size()==3&&graph_draw.edges.size()==1);
    se::NativeBrainEngine large;large.add_cognits(10000);for(std::uint32_t i=0;i<50000;++i){auto source=i%10000,target=(source+(i/10000)+1)%10000;large.add_relation(source,target,se::RelationType::Associative,0,double(i%100)/100.,.6,0);}for(std::uint32_t i=0;i<20;++i)large.set_activity(i,.9-double(i)*.01);std::vector<std::uint32_t> hot(20);std::iota(hot.begin(),hot.end(),0);large.publish_brain_snapshot(1.,42,3,hot);auto bounded=large.brain_snapshot_channel()->latest();assert(bounded->total_cognits==10000&&bounded->total_relations==50000&&bounded->nodes.size()==se::kMaxBrainSnapshotNodes&&bounded->edges.size()<=se::kMaxBrainSnapshotEdges&&bounded->active_cognits==20&&bounded->truncated);for(std::uint32_t i=0;i<20;++i)assert(bounded->nodes[i].id==i);auto first_ids=bounded->nodes;large.publish_brain_snapshot(1.,42,3,hot);auto repeat=large.brain_snapshot_channel()->latest();for(std::size_t i=0;i<first_ids.size();++i)assert(first_ids[i].id==repeat->nodes[i].id);auto lod=se::prepare_brain_draw_data(*bounded,300,400);assert(lod.nodes.size()<=128&&lod.edges.size()<=512);
    se::World a(4,4,1); a.initialize_multi({{1,1,'N',0,1,1}},{}); se::World b=a;
    auto a_channel=a.snapshot_channel(), b_channel=b.snapshot_channel(); assert(a_channel!=b_channel);
    a.set_body_state(1,2,1,'E'); assert(a_channel->latest()->bodies[0].x==2); assert(b_channel->latest()->bodies[0].x==1);
    b.set_body_state(1,1,2,'S'); assert(b_channel->latest()->bodies[0].y==2); assert(a_channel->latest()->bodies[0].y==1);
    se::World direct(4,4,1);direct.initialize_multi({{1,1,'N',0,1,0}},{});auto direct_channel=direct.snapshot_channel();auto direct_before=direct_channel->latest();auto direct_sequence=direct.event_sequence();direct.apply(se::ActionType::MoveRight,0);auto direct_after=direct_channel->latest();assert(direct_after->bodies[0].x==2&&direct_after->bodies[0].y==1);assert(direct_before->bodies[0].x==1&&direct_before->bodies[0].y==1);assert(direct.event_sequence()==direct_sequence&&direct_after->event_sequence==direct_sequence);
    se::World batch(5,3,1);batch.initialize_multi({{0,1,'E',0,1,0},{4,1,'W',0,1,1}},{});auto batch_channel=batch.snapshot_channel();auto batch_before=batch_channel->latest();std::uint32_t ids[]={0,1};std::uint8_t actions[]={static_cast<std::uint8_t>(se::ActionType::MoveRight),static_cast<std::uint8_t>(se::ActionType::MoveLeft)};batch.resolve_intents(ids,actions);auto batch_after=batch_channel->latest();assert(batch.bodies()[0].x==1&&batch.bodies()[1].x==3);assert(batch_after->bodies[0].x==1&&batch_after->bodies[1].x==3);assert(batch_before->bodies[0].x==0&&batch_before->bodies[1].x==4);assert(batch_after->event_sequence==batch.event_sequence());
    return 0;
}
