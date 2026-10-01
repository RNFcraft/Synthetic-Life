#include "se/observer.hpp"

#ifdef NDEBUG
#undef NDEBUG
#endif
#include "se/native_brain_engine.hpp"
#include "se/workbench_style.hpp"
#include "se/workbench_ui.hpp"
#include "se/world.hpp"
#include <atomic>
#include <cassert>
#include <cmath>
#include <imgui.h>
#include <numeric>
#include <thread>
#include <unordered_set>

int main() {
  ImGui::CreateContext();
  auto &io = ImGui::GetIO();
  io.IniFilename = nullptr;
  io.DisplaySize = {1440, 900};
  for (float scale : {1.f, 1.5f, 2.f}) {
    se::WorkbenchStyle::apply(scale);
    se::WorkbenchStyle::load_font(scale);
    assert(io.Fonts->Build());
    assert(std::abs(io.Fonts->Fonts[0]->FontSize - 16.f * scale) < .01f);
    assert(io.Fonts->Fonts[0]->FindGlyphNoFallback(0x042f)); // Cyrillic Ya
  }
  se::WorkbenchStyle::apply(1);
  se::WorkbenchStyle::load_font(1);
  assert(io.Fonts->Build());
  se::WorkbenchUIState interaction;
  se::WorkbenchCommandChannel inputs;
  auto status = std::make_shared<se::WorkbenchStatusSnapshot>();
  status->paused = true;
  status->food_payload = status->water_payload = 20;
  se::RenderSnapshot world;
  world.world_width = world.world_height = 8;
  auto frame = [&] {
    ImGui::NewFrame();
    se::draw_workbench(interaction, world, nullptr, nullptr, status, &inputs,
                       1);
    ImGui::Render();
  };
  frame();
  io.AddKeyEvent(ImGuiKey_2, true);
  frame();
  assert(interaction.tool == 1);
  io.AddKeyEvent(ImGuiKey_2, false);
  frame();
  io.AddMousePosEvent(700, 400);
  frame();
  io.AddMouseButtonEvent(0, true);
  frame();
  auto placed = inputs.drain();
  assert(placed.size() == 1 &&
         placed[0].kind == se::WorkbenchCommandKind::PlaceFood);
  assert(placed[0].x >= 0 && placed[0].x < 8 && placed[0].y >= 0 &&
         placed[0].y < 8);
  io.AddMouseButtonEvent(0, false);
  frame();
  io.AddKeyEvent(ImGuiKey_Space, true);
  frame();
  auto resumed = inputs.drain();
  assert(resumed.size() == 1 &&
         resumed[0].kind == se::WorkbenchCommandKind::Resume);
  io.AddKeyEvent(ImGuiKey_Space, false);
  frame();
  io.AddKeyEvent(ImGuiKey_N, true);
  frame();
  auto stepped = inputs.drain();
  assert(stepped.size() == 1 &&
         stepped[0].kind == se::WorkbenchCommandKind::Step);
  io.AddKeyEvent(ImGuiKey_N, false);
  frame();
  io.AddMousePosEvent(60, 835);
  frame();
  io.AddMouseButtonEvent(0, true);
  frame();
  io.AddMouseButtonEvent(0, false);
  frame();
  assert(io.WantTextInput);
  io.AddInputCharactersUTF8("dax");
  io.AddKeyEvent(ImGuiKey_5, true);
  frame();
  assert(interaction.tool == 1 && inputs.drain().empty());
  io.AddKeyEvent(ImGuiKey_5, false);
  io.AddKeyEvent(ImGuiKey_Space, true);
  frame();
  assert(inputs.drain().empty()); // Space must not resume while typing.
  io.AddKeyEvent(ImGuiKey_Space, false);
  io.AddKeyEvent(ImGuiKey_Enter, true);
  frame();
  auto dialogue_input = inputs.drain();
  assert(dialogue_input.size() == 1 &&
         dialogue_input[0].kind == se::WorkbenchCommandKind::SendDialogue &&
         dialogue_input[0].text == "dax");
  ImGui::DestroyContext();
  for (auto [w, h] :
       std::vector<std::pair<int, int>>{{1100, 700}, {1440, 900}, {1920, 1080}})
    for (float scale : {1.f, 1.5f, 2.f}) {
      auto layout = se::workbench_layout(float(w), float(h), scale);
      for (auto r : {layout.toolbar, layout.dialogue, layout.world,
                     layout.brain, layout.status}) {
        assert(r.width > 0 && r.height > 0);
        assert(r.x >= 0 && r.y >= 0 && r.x + r.width <= w + .01 &&
               r.y + r.height <= h + .01);
      }
      assert(layout.dialogue.x + layout.dialogue.width <= layout.world.x);
      assert(layout.world.x + layout.world.width <= layout.brain.x);
      assert(layout.brain.y + layout.brain.height <= layout.status.y);
    }
  se::WorkbenchCommandChannel commands;
  for (unsigned n = 1; n <= 256; ++n)
    assert(commands.submit(se::WorkbenchCommandKind::Pause) == n);
  assert(commands.submit(se::WorkbenchCommandKind::Pause) == 0);
  auto messages = commands.drain();
  assert(messages.size() == 256 && messages.back().id == 256);
  commands.close();
  assert(commands.submit(se::WorkbenchCommandKind::Resume) == 0);
  se::WorkbenchStatusChannel statuses;
  se::WorkbenchStatusSnapshot physical;
  physical.energy = 72;
  physical.bins = {5, 3, 6};
  statuses.publish(physical);
  auto retained_status = statuses.latest();
  physical.energy = 10;
  statuses.publish(physical);
  assert(retained_status->energy == 72 && statuses.latest()->energy == 10);
  se::RenderSnapshot snapshot;
  snapshot.world_width = 8;
  snapshot.world_height = 4;
  snapshot.bodies.push_back({1, 2, 1, 'E', 0, 9});
  snapshot.objects.push_back({7, 6, 3, 0});
  const auto draws = se::prepare_draw_data(snapshot, 800, 400);
  assert(draws.size() ==
         5); // grid, free object, body, orientation, held marker
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
  assert(before.objects.size() ==
         1); // draw preparation never writes its input.
  se::RenderSnapshotChannel channel;
  se::RenderSnapshot retained;
  retained.world_width = 3;
  retained.world_height = 2;
  retained.event_sequence = 1;
  channel.publish(retained);
  auto old = channel.latest();
  std::atomic<bool> done{false};
  std::thread writer([&] {
    for (std::uint64_t n = 2; n < 2000; ++n) {
      se::RenderSnapshot value;
      value.world_width = 3;
      value.world_height = 2;
      value.world_time = double(n);
      value.event_sequence = n;
      value.bodies.push_back({1, 1, 1, 'N', 1, 0});
      channel.publish(std::move(value));
    }
    done = true;
  });
  std::thread reader([&] {
    std::uint64_t previous = 0;
    while (!done) {
      auto value = channel.latest();
      if (value) {
        assert(value->world_width > 0 && value->world_height > 0);
        assert(std::isfinite(value->world_time));
        assert(value->event_sequence >= previous);
        previous = value->event_sequence;
        std::unordered_set<unsigned> ids;
        for (auto const &body : value->bodies)
          assert(ids.insert(body.id).second);
      }
    }
  });
  writer.join();
  reader.join();
  assert(old->event_sequence ==
         1); // retained immutable snapshots survive publication.
  auto latest = channel.latest();
  assert(latest->event_sequence == 1999); // no consumption is required.
  se::BrainSnapshotChannel brains;
  se::BrainSnapshot first;
  first.cognitive_tick = 1;
  first.nodes.push_back({1, .2, .3, .4, false, true, 1});
  brains.publish(first);
  auto retained_brain = brains.latest();
  for (std::uint64_t n = 2; n < 100; ++n) {
    se::BrainSnapshot value;
    value.cognitive_tick = n;
    value.nodes.push_back({std::uint32_t(n), .8, .3, .7, false, true, n});
    brains.publish(std::move(value));
  }
  assert(retained_brain->cognitive_tick == 1 &&
         retained_brain->nodes[0].activity == .2);
  assert(brains.latest()->cognitive_tick == 99);
  std::atomic<bool> brain_done{false};
  std::thread brain_writer([&] {
    for (std::uint64_t n = 100; n < 2000; ++n) {
      se::BrainSnapshot v;
      v.cognitive_tick = n;
      v.nodes.push_back({unsigned(n), .5, .2, .6, false, true, n});
      brains.publish(std::move(v));
    }
    brain_done = true;
  });
  std::thread brain_reader([&] {
    std::uint64_t previous = 0;
    while (!brain_done) {
      auto v = brains.latest();
      if (v) {
        assert(v->cognitive_tick >= previous);
        previous = v->cognitive_tick;
        assert(v->nodes.size() == 1);
      }
    }
  });
  brain_writer.join();
  brain_reader.join();
  assert(brains.latest()->cognitive_tick == 1999);
  se::DialogueSnapshotChannel dialogue;
  dialogue.publish(1.25, se::DialogueRole::External, "dax");
  auto retained_dialogue = dialogue.latest();
  dialogue.publish(1.5, se::DialogueRole::Entity, "future-output");
  assert(retained_dialogue->revision == 1 &&
         retained_dialogue->lines.size() == 1 &&
         retained_dialogue->lines[0].text == "dax" &&
         retained_dialogue->lines[0].role == se::DialogueRole::External);
  for (int n = 0; n < 100; ++n)
    dialogue.publish(2. + n, se::DialogueRole::External,
                     "line-" + std::to_string(n));
  auto bounded_dialogue = dialogue.latest();
  assert(bounded_dialogue->lines.size() == se::kMaxDialogueLines &&
         bounded_dialogue->lines.front().sequence <
             bounded_dialogue->lines.back().sequence &&
         bounded_dialogue->lines.back().text == "line-99");
  se::NativeBrainEngine engine;
  engine.add_cognits(3);
  engine.set_activity(1, .9);
  engine.add_relation(0, 1, se::RelationType::Sequential, 0, .8, .7, 0);
  std::uint32_t active[] = {1};
  engine.publish_brain_snapshot(2.5, 7, 4, active);
  auto graph = engine.brain_snapshot_channel()->latest();
  assert(graph->nodes.size() == 3 && graph->edges.size() == 1 &&
         graph->nodes[0].id == 1 && graph->nodes[0].activity == .9 && graph->edges[0].source == 0 &&
         graph->edges[0].target == 1);
  auto graph_draw = se::prepare_brain_draw_data(*graph, 300, 240);
  assert(graph_draw.nodes.size() == 3 && graph_draw.edges.size() == 1);
  auto graph_repeat = se::prepare_brain_draw_data(*graph, 300, 240);
  for (std::size_t n = 0; n < graph_draw.nodes.size(); ++n)
    assert(graph_draw.nodes[n].x == graph_repeat.nodes[n].x &&
           graph_draw.nodes[n].y == graph_repeat.nodes[n].y);
  se::NativeBrainEngine large;
  large.add_cognits(10000);
  for (std::uint32_t i = 0; i < 50000; ++i) {
    auto source = i % 10000, target = (source + (i / 10000) + 1) % 10000;
    large.add_relation(source, target, se::RelationType::Associative, 0,
                       double(i % 100) / 100., .6, 0);
  }
  for (std::uint32_t i = 0; i < 20; ++i)
    large.set_activity(i, .9 - double(i) * .01);
  std::vector<std::uint32_t> hot(20);
  std::iota(hot.begin(), hot.end(), 0);
  large.publish_brain_snapshot(1., 42, 3, hot);
  auto bounded = large.brain_snapshot_channel()->latest();
  assert(bounded->total_cognits == 10000 && bounded->total_relations == 50000 &&
         bounded->nodes.size() == se::kMaxBrainSnapshotNodes &&
         bounded->edges.size() <= se::kMaxBrainSnapshotEdges &&
         bounded->active_cognits == 20 && bounded->truncated);
  for (std::uint32_t i = 0; i < 20; ++i)
    assert(bounded->nodes[i].id == i);
  auto first_ids = bounded->nodes;
  large.publish_brain_snapshot(1., 42, 3, hot);
  auto repeat = large.brain_snapshot_channel()->latest();
  for (std::size_t i = 0; i < first_ids.size(); ++i)
    assert(first_ids[i].id == repeat->nodes[i].id);
  auto lod = se::prepare_brain_draw_data(*bounded, 300, 400);
  assert(lod.nodes.size() <= 128 && lod.edges.size() <= 512);
  se::World a(4, 4, 1);
  a.initialize_multi({{1, 1, 'N', 0, 1, 1}}, {});
  se::World b = a;
  auto a_channel = a.snapshot_channel(), b_channel = b.snapshot_channel();
  assert(a_channel != b_channel);
  a.set_body_state(1, 2, 1, 'E');
  assert(a_channel->latest()->bodies[0].x == 2);
  assert(b_channel->latest()->bodies[0].x == 1);
  b.set_body_state(1, 1, 2, 'S');
  assert(b_channel->latest()->bodies[0].y == 2);
  assert(a_channel->latest()->bodies[0].y == 1);
  se::World direct(4, 4, 1);
  direct.initialize_multi({{1, 1, 'N', 0, 1, 0}}, {});
  auto direct_channel = direct.snapshot_channel();
  auto direct_before = direct_channel->latest();
  auto direct_sequence = direct.event_sequence();
  direct.apply(se::ActionType::MoveRight, 0);
  auto direct_after = direct_channel->latest();
  assert(direct_after->bodies[0].x == 2 && direct_after->bodies[0].y == 1);
  assert(direct_before->bodies[0].x == 1 && direct_before->bodies[0].y == 1);
  assert(direct.event_sequence() == direct_sequence &&
         direct_after->event_sequence == direct_sequence);
  se::World batch(5, 3, 1);
  batch.initialize_multi({{0, 1, 'E', 0, 1, 0}, {4, 1, 'W', 0, 1, 1}}, {});
  auto batch_channel = batch.snapshot_channel();
  auto batch_before = batch_channel->latest();
  std::uint32_t ids[] = {0, 1};
  std::uint8_t actions[] = {
      static_cast<std::uint8_t>(se::ActionType::MoveRight),
      static_cast<std::uint8_t>(se::ActionType::MoveLeft)};
  batch.resolve_intents(ids, actions);
  auto batch_after = batch_channel->latest();
  assert(batch.bodies()[0].x == 1 && batch.bodies()[1].x == 3);
  assert(batch_after->bodies[0].x == 1 && batch_after->bodies[1].x == 3);
  assert(batch_before->bodies[0].x == 0 && batch_before->bodies[1].x == 4);
  assert(batch_after->event_sequence == batch.event_sequence());
  return 0;
}
