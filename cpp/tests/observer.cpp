#include "se/observer.hpp"

#include <cassert>
#include <cmath>
#include <atomic>
#include <thread>
#include <unordered_set>
#include "se/world.hpp"

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
    se::World a(4,4,1); a.initialize_multi({{1,1,'N',0,1,1}},{}); se::World b=a;
    auto a_channel=a.snapshot_channel(), b_channel=b.snapshot_channel(); assert(a_channel!=b_channel);
    a.set_body_state(1,2,1,'E'); assert(a_channel->latest()->bodies[0].x==2); assert(b_channel->latest()->bodies[0].x==1);
    b.set_body_state(1,1,2,'S'); assert(b_channel->latest()->bodies[0].y==2); assert(a_channel->latest()->bodies[0].y==1);
    return 0;
}
