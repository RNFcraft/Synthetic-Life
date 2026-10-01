#include "se/workbench_ui.hpp"
#include <algorithm>
#include <cstring>
#include <imgui.h>
namespace se {
void draw_dialogue_view(WorkbenchUIState &ui, const DialogueSnapshot *s,
                        WorkbenchCommandChannel *commands) {
  float reserved = ImGui::GetFrameHeightWithSpacing() +
                   ImGui::GetTextLineHeightWithSpacing() * 2;
  ImGui::BeginChild(
      "Transcript",
      {0, std::max(1.f, ImGui::GetContentRegionAvail().y - reserved)});
  bool at_bottom = ImGui::GetScrollY() >= ImGui::GetScrollMaxY() - 2;
  if (!s || s->lines.empty()) {
    ImGui::TextDisabled("No dialogue yet");
    ImGui::Spacing();
    ImGui::TextWrapped("Send an explicit utterance to the organism. Responses "
                       "appear only when produced by its language system.");
  } else
    for (auto const &line : s->lines) {
      ImGui::PushID(static_cast<int>(line.sequence));
      ImGui::TextColored(
          line.role == DialogueRole::External ? ImVec4{.58f, .64f, .69f, 1}
                                              : ImVec4{.49f, .83f, .99f, 1},
          "%s", line.role == DialogueRole::External ? "EXTERNAL" : "ENTITY");
      ImGui::SameLine();
      ImGui::TextDisabled("%s", format_world_time(line.world_time).c_str());
      ImGui::PushTextWrapPos(0);
      ImGui::TextUnformatted(line.text.c_str());
      ImGui::PopTextWrapPos();
      ImGui::Spacing();
      ImGui::Separator();
      ImGui::Spacing();
      ImGui::PopID();
    }
  if (s && s->revision != ui.dialogue_revision) {
    if (at_bottom)
      ImGui::SetScrollHereY(1.f);
    ui.dialogue_revision = s->revision;
  }
  ImGui::EndChild();
  ImGui::Separator();
  ImGui::BeginDisabled(!commands);
  float send_width =
      ImGui::CalcTextSize("Send").x + ImGui::GetStyle().FramePadding.x * 2;
  ImGui::SetNextItemWidth(std::max(1.f, ImGui::GetContentRegionAvail().x -
                                            send_width -
                                            ImGui::GetStyle().ItemSpacing.x));
  bool enter = ImGui::InputTextWithHint("##message", "Message...",
                                        ui.input.data(), ui.input.size(),
                                        ImGuiInputTextFlags_EnterReturnsTrue);
  ImGui::SameLine();
  bool send = ImGui::Button("Send");
  if ((enter || send) && commands) {
    std::string text = ui.input.data();
    if (text.find_first_not_of(" \t\r\n") != std::string::npos) {
      if (commands->submit(WorkbenchCommandKind::SendDialogue, 0, 0, 0, text)) {
        ui.input[0] = 0;
        ui.input_error.clear();
      } else
        ui.input_error = "Queue full; message retained";
    }
  }
  ImGui::EndDisabled();
  if (ui.input_error.empty())
    ImGui::TextWrapped("Enter: send / external causal input");
  else
    ImGui::TextWrapped("%s", ui.input_error.c_str());
}
} // namespace se
