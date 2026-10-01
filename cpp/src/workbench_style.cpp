#include "se/workbench_style.hpp"
#include <SDL3/SDL.h>
#include <filesystem>
#include <imgui.h>
#include <stdexcept>
namespace se {
void WorkbenchStyle::apply(float scale) {
  auto &s = ImGui::GetStyle();
  s = ImGuiStyle{};
  s.WindowRounding = 0;
  s.ChildRounding = 0;
  s.FrameRounding = 3;
  s.PopupRounding = 4;
  s.ScrollbarRounding = 3;
  s.GrabRounding = 3;
  s.TabRounding = 3;
  s.WindowBorderSize = 1;
  s.ChildBorderSize = 0;
  s.FrameBorderSize = 1;
  s.WindowPadding = {12, 12};
  s.FramePadding = {9, 5};
  s.ItemSpacing = {8, 8};
  s.ItemInnerSpacing = {6, 4};
  s.ScrollbarSize = 12;
  s.GrabMinSize = 10;
  auto &c = s.Colors;
  c[ImGuiCol_Text] = {.906f, .929f, .949f, 1};
  c[ImGuiCol_TextDisabled] = {.45f, .51f, .56f, 1};
  c[ImGuiCol_WindowBg] = {.078f, .102f, .125f, 1};
  c[ImGuiCol_ChildBg] = c[ImGuiCol_WindowBg];
  c[ImGuiCol_PopupBg] = {.102f, .133f, .165f, 1};
  c[ImGuiCol_Border] = {.165f, .204f, .243f, 1};
  c[ImGuiCol_FrameBg] = {.055f, .075f, .094f, 1};
  c[ImGuiCol_FrameBgHovered] = {.14f, .19f, .23f, 1};
  c[ImGuiCol_FrameBgActive] = {.16f, .23f, .28f, 1};
  c[ImGuiCol_Button] = {.12f, .16f, .20f, 1};
  c[ImGuiCol_ButtonHovered] = {.18f, .25f, .30f, 1};
  c[ImGuiCol_ButtonActive] = {.16f, .32f, .42f, 1};
  c[ImGuiCol_Header] = {.12f, .19f, .24f, 1};
  c[ImGuiCol_HeaderHovered] = {.18f, .28f, .34f, 1};
  c[ImGuiCol_HeaderActive] = {.18f, .34f, .44f, 1};
  c[ImGuiCol_Separator] = c[ImGuiCol_Border];
  c[ImGuiCol_SeparatorHovered] = {.25f, .49f, .61f, 1};
  c[ImGuiCol_SeparatorActive] = {.30f, .60f, .75f, 1};
  c[ImGuiCol_CheckMark] = {.49f, .83f, .99f, 1};
  c[ImGuiCol_SliderGrab] = {.18f, .62f, .85f, 1};
  c[ImGuiCol_SliderGrabActive] = {.49f, .83f, .99f, 1};
  c[ImGuiCol_ScrollbarBg] = {.065f, .085f, .10f, 1};
  c[ImGuiCol_ScrollbarGrab] = {.22f, .28f, .33f, 1};
  c[ImGuiCol_ScrollbarGrabHovered] = {.32f, .39f, .44f, 1};
  c[ImGuiCol_ScrollbarGrabActive] = {.38f, .46f, .52f, 1};
  c[ImGuiCol_Tab] = {.09f, .13f, .16f, 1};
  c[ImGuiCol_TabHovered] = {.17f, .28f, .35f, 1};
  c[ImGuiCol_TabSelected] = {.14f, .23f, .30f, 1};
  c[ImGuiCol_TitleBg] = c[ImGuiCol_WindowBg];
  c[ImGuiCol_TitleBgActive] = c[ImGuiCol_WindowBg];
  c[ImGuiCol_PlotHistogram] = {.18f, .62f, .85f, 1};
  c[ImGuiCol_NavCursor] = {.49f, .83f, .99f, 1};
  s.DisabledAlpha = .42f;
  s.ScaleAllSizes(scale);
}
void WorkbenchStyle::load_font(float scale) {
  auto &io = ImGui::GetIO();
  io.Fonts->Clear();
  std::filesystem::path paths[] = {
      std::filesystem::path(SDL_GetBasePath()) / "assets/Roboto-Medium.ttf",
      std::filesystem::path("consciousness/assets/Roboto-Medium.ttf"),
      SE_WORKBENCH_FONT};
  for (auto const &path : paths)
    if (std::filesystem::is_regular_file(path)) {
      ImFontConfig cfg;
      cfg.OversampleH = 2;
      cfg.OversampleV = 2;
      if (io.Fonts->AddFontFromFileTTF(path.string().c_str(), 16.f * scale,
                                       &cfg,
                                       io.Fonts->GetGlyphRangesCyrillic()))
        return;
    }
  throw std::runtime_error(
      "Workbench font asset missing: assets/Roboto-Medium.ttf");
}
} // namespace se
