#include "se/observer.hpp"

#include <cassert>
#include <cmath>

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
    return 0;
}
