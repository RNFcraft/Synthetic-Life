#include "se/workbench_ui.hpp"
#include <algorithm>
#include <cmath>
#include <imgui.h>
namespace se {
namespace {
std::pair<float, float> direction(char c) {
  switch (c) {
  case 'S':
    return {0.f, 1.f};
  case 'E':
    return {1.f, 0.f};
  case 'W':
    return {-1.f, 0.f};
  default:
    return {0.f, -1.f};
  }
}
ImU32 color(PresentationKind kind) {
  switch (kind) {
  case PresentationKind::Food:
    return IM_COL32(255, 122, 26, 255);
  case PresentationKind::Water:
    return IM_COL32(66, 184, 216, 255);
  case PresentationKind::OtherResource:
    return IM_COL32(223, 175, 75, 255);
  default:
    return IM_COL32(148, 162, 174, 255);
  }
}
} // namespace
WorldFitTransform fit_world_to_viewport(int ww, int wh, int w, int h) {
  if (ww <= 0 || wh <= 0 || w <= 0 || h <= 0)
    return {};
  auto cell =
      std::min(std::max(1.f, w - 32.f) / ww, std::max(1.f, h - 32.f) / wh);
  return {(w - cell * ww) * .5f, (h - cell * wh) * .5f, cell, cell * ww,
          cell * wh};
}
std::vector<DrawPrimitive> prepare_draw_data(const RenderSnapshot &s, int w,
                                             int h) {
  std::vector<DrawPrimitive> out;
  auto f = fit_world_to_viewport(s.world_width, s.world_height, w, h);
  if (!f.cell_size)
    return out;
  out.push_back({DrawPrimitiveKind::grid, f.origin_x, f.origin_y, f.grid_width,
                 f.grid_height});
  auto add = [&](DrawPrimitiveKind kind, int x, int y, unsigned id,
                 char c = 'N') {
    auto [dx, dy] = direction(c);
    out.push_back({kind, f.origin_x + x * f.cell_size,
                   f.origin_y + y * f.cell_size, f.cell_size, f.cell_size, dx,
                   dy, id});
  };
  for (auto const &o : s.objects)
    add(DrawPrimitiveKind::object, o.x, o.y, o.id);
  for (auto const &b : s.bodies) {
    add(DrawPrimitiveKind::body, b.x, b.y, b.id, b.orientation);
    add(DrawPrimitiveKind::orientation, b.x, b.y, b.id, b.orientation);
    if (b.held_object_id)
      add(DrawPrimitiveKind::held_object, b.x, b.y, b.held_object_id,
          b.orientation);
  }
  return out;
}
void draw_world_view(WorkbenchUIState &ui, const RenderSnapshot &s,
                     WorkbenchCommandChannel *commands) {
  auto origin = ImGui::GetCursorScreenPos(),
       size = ImGui::GetContentRegionAvail();
  size.x = std::max(1.f, size.x);
  size.y = std::max(1.f, size.y);
  ImGui::InvisibleButton("WorldCanvas", size,
                         ImGuiButtonFlags_MouseButtonLeft |
                             ImGuiButtonFlags_MouseButtonMiddle |
                             ImGuiButtonFlags_MouseButtonRight);
  auto *d = ImGui::GetWindowDrawList();
  d->PushClipRect(origin, {origin.x + size.x, origin.y + size.y}, true);
  d->AddRectFilled(origin, {origin.x + size.x, origin.y + size.y},
                   IM_COL32(14, 19, 24, 255));
  if (s.world_width <= 0 || s.world_height <= 0) {
    d->AddText({origin.x + 20, origin.y + 20}, IM_COL32(148, 162, 174, 255),
               "Waiting for world snapshot");
    d->PopClipRect();
    return;
  }
  bool hover = ImGui::IsItemHovered();
  auto &io = ImGui::GetIO();
  if (hover && io.MouseWheel)
    ui.world_zoom =
        std::clamp(ui.world_zoom * std::pow(1.12f, io.MouseWheel), .4f, 8.f);
  if (hover && (ImGui::IsMouseDragging(ImGuiMouseButton_Middle) ||
                ImGui::IsMouseDragging(ImGuiMouseButton_Right))) {
    ui.world_pan_x += io.MouseDelta.x;
    ui.world_pan_y += io.MouseDelta.y;
  }
  auto fit = fit_world_to_viewport(s.world_width, s.world_height, int(size.x),
                                   int(size.y));
  float cell = fit.cell_size * ui.world_zoom;
  ImVec2 base{origin.x + (size.x - cell * s.world_width) * .5f + ui.world_pan_x,
              origin.y + (size.y - cell * s.world_height) * .5f +
                  ui.world_pan_y};
  auto at = [&](int x, int y) {
    return ImVec2{base.x + x * cell, base.y + y * cell};
  };
  d->AddRectFilled(base, at(s.world_width, s.world_height),
                   IM_COL32(20, 27, 33, 255));
  if (ui.show_grid) for (int x = 0; x <= s.world_width; ++x)
    d->AddLine(at(x, 0), at(x, s.world_height), IM_COL32(37, 47, 56, 255));
  if (ui.show_grid) for (int y = 0; y <= s.world_height; ++y)
    d->AddLine(at(0, y), at(s.world_width, y), IM_COL32(37, 47, 56, 255));
  d->AddRect(base, at(s.world_width, s.world_height),
             IM_COL32(76, 92, 106, 255));
  for (auto const &o : s.objects) {
    auto p = at(o.x, o.y);
    float pad = cell * .20f;
    d->AddRectFilled({p.x + pad, p.y + pad},
                     {p.x + cell - pad, p.y + cell - pad},
                     color(o.presentation_kind), 2);
    d->AddLine({p.x + pad + 1, p.y + pad + 1},
               {p.x + cell - pad - 1, p.y + pad + 1},
               IM_COL32(255, 255, 255, 45));
  }
  for (auto const &b : s.bodies) {
    auto p = at(b.x, b.y);
    ImVec2 center{p.x + cell * .5f, p.y + cell * .5f};
    d->AddCircleFilled(center, cell * .30f, IM_COL32(47, 158, 216, 255), 32);
    auto [dx, dy] = direction(b.orientation);
    d->AddLine(center,
               {center.x + dx * cell * .27f, center.y + dy * cell * .27f},
               IM_COL32(231, 237, 242, 255), 2.f);
    for (auto const &held : s.held_objects)
      if (held.owner_body_id == b.id) {
        ImVec2 q{center.x + dx * cell * .36f, center.y + dy * cell * .36f};
        d->AddRectFilled({q.x - cell * .09f, q.y - cell * .09f},
                         {q.x + cell * .09f, q.y + cell * .09f},
                         color(held.presentation_kind), 1);
      }
  }
  int x = int(std::floor((io.MousePos.x - base.x) / cell)),
      y = int(std::floor((io.MousePos.y - base.y) / cell));
  bool valid =
      hover && x >= 0 && y >= 0 && x < s.world_width && y < s.world_height;
  if (valid) {
    auto p = at(x, y);
    d->AddRectFilled(p, {p.x + cell, p.y + cell}, IM_COL32(125, 211, 252, 18));
    d->AddRect(p, {p.x + cell, p.y + cell}, IM_COL32(125, 211, 252, 100));
    auto object = std::find_if(s.objects.begin(), s.objects.end(),
                               [&](auto &o) { return o.x == x && o.y == y; });
    auto body = std::find_if(s.bodies.begin(), s.bodies.end(),
                             [&](auto &b) { return b.x == x && b.y == y; });
    if (ImGui::IsMouseClicked(ImGuiMouseButton_Left)) {
      ui.selected_x = x;
      ui.selected_y = y;
      if (ui.tool == 0) {
        ui.selected_object = object == s.objects.end() ? 0 : object->id;
        ui.body_selected = body != s.bodies.end();
        if (ui.body_selected)
          ui.selected_body = body->id;
      } else if (commands) {
        WorkbenchCommandKind kinds[] = {WorkbenchCommandKind::PlaceFood,
                                        WorkbenchCommandKind::PlaceWater,
                                        WorkbenchCommandKind::PlaceObject,
                                        WorkbenchCommandKind::RemoveObject};
        if (ui.tool != 4 || object != s.objects.end()) {
          auto id =
              commands->submit(kinds[ui.tool - 1], x, y,
                               object == s.objects.end() ? 0 : object->id);
          if (!id)
            ui.workbench_notice = "Editor command queue full";
          else
            ui.workbench_notice.clear();
        }
      }
    }
    if (object != s.objects.end() &&
        ImGui::IsItemHovered(ImGuiHoveredFlags_DelayShort)) {
      if (ui.show_tooltips) {
      ImGui::BeginTooltip();
      ImGui::Text("Object #%u / cell %d, %d", object->id, x, y);
      ImGui::Text("Appearance %d", object->state);
      ImGui::Text("Nutrients %.1f / hydration %.1f", object->nutrients,
                  object->hydration);
      ImGui::EndTooltip();
      }
    }
  }
  if (ui.selected_x >= 0 && ui.selected_y >= 0) {
    auto p = at(ui.selected_x, ui.selected_y);
    d->AddRect(p, {p.x + cell, p.y + cell}, IM_COL32(125, 211, 252, 220), 0, 0,
               2);
  }
  d->PopClipRect();
}
} // namespace se
