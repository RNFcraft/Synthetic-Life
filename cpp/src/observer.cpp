#include "se/observer.hpp"
#include "se/workbench_style.hpp"
#include "se/workbench_ui.hpp"
#include <SDL3/SDL.h>
#include <SDL3/SDL_opengl.h>
#include <algorithm>
#include <cstdio>
#include <imgui.h>
#include <imgui_impl_opengl3.h>
#include <imgui_impl_sdl3.h>
#include <stdexcept>
namespace se {
class NativeObserver::Impl {
public:
  Impl(int w, int h) : width(w), height(h) {}
  ~Impl() { shutdown(); }
  void initialize() {
    if (!SDL_Init(SDL_INIT_VIDEO))
      throw std::runtime_error(SDL_GetError());
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 3);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK,
                        SDL_GL_CONTEXT_PROFILE_CORE);
    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1);
    window = SDL_CreateWindow("Synthetic-Life | Experimental Workbench", width,
                              height,
                              SDL_WINDOW_OPENGL | SDL_WINDOW_RESIZABLE |
                                  SDL_WINDOW_HIGH_PIXEL_DENSITY);
    if (!window)
      throw std::runtime_error(SDL_GetError());
    SDL_SetWindowMinimumSize(window, 1100, 700);
    context = SDL_GL_CreateContext(window);
    if (!context)
      throw std::runtime_error(SDL_GetError());
    SDL_GL_SetSwapInterval(1);
    IMGUI_CHECKVERSION();
    imgui = ImGui::CreateContext();
    ImGui::SetCurrentContext(imgui);
    ImGui::GetIO().IniFilename = nullptr;
    ImGui::GetIO().LogFilename = nullptr;
    scale = std::clamp(SDL_GetWindowDisplayScale(window), 1.f, 2.5f);
    WorkbenchStyle::apply(scale);
    WorkbenchStyle::load_font(scale);
    if (!ImGui_ImplSDL3_InitForOpenGL(window, context))
      throw std::runtime_error("ImGui SDL initialization failed");
    sdl_backend = true;
    if (!ImGui_ImplOpenGL3_Init("#version 330 core"))
      throw std::runtime_error("ImGui GL initialization failed");
    gl_backend = true;
    open = true;
  }
  void shutdown() {
    ui.brain_gpu.reset();
    if (imgui) {
      ImGui::SetCurrentContext(imgui);
      if (gl_backend)
        ImGui_ImplOpenGL3_Shutdown();
      if (sdl_backend)
        ImGui_ImplSDL3_Shutdown();
      ImGui::DestroyContext(imgui);
      imgui = nullptr;
    }
    gl_backend = sdl_backend = false;
    if (context)
      SDL_GL_DestroyContext(context);
    context = nullptr;
    if (window)
      SDL_DestroyWindow(window);
    window = nullptr;
    SDL_Quit();
  }
  SDL_Window *window{};
  SDL_GLContext context{};
  ImGuiContext *imgui{};
  bool open{true}, sdl_backend{}, gl_backend{};
  int width, height;
  float scale{1.f};
  WorkbenchUIState ui;
  std::string capture_path;
  std::uint64_t capture_min_frames{3};
};
NativeObserver::NativeObserver(int width, int height)
    : impl_(std::make_unique<Impl>(width, height)) {
  impl_->initialize();
}
NativeObserver::NativeObserver(
    std::shared_ptr<RenderSnapshotChannel> channel,
    std::shared_ptr<BrainSnapshotChannel> brain,
    std::shared_ptr<DialogueSnapshotChannel> dialogue, int width, int height)
    : impl_(std::make_unique<Impl>(width, height)),
      source_(std::make_shared<ChannelSnapshotSource>(std::move(channel))),
      brain_(std::move(brain)), dialogue_(std::move(dialogue)) {}
NativeObserver::~NativeObserver() { stop(); }
void NativeObserver::attach_workbench(
    std::shared_ptr<WorkbenchStatusChannel> status,
    std::shared_ptr<WorkbenchCommandChannel> commands) {
  if (running_)
    throw std::runtime_error("attach workbench before starting observer");
  status_ = std::move(status);
  commands_ = std::move(commands);
}
void NativeObserver::capture_next_frame(std::string path, bool scenario_popup) {
  if (running_)
    throw std::runtime_error("request capture before starting observer");
  impl_->capture_path = std::move(path);
  impl_->ui.open_scenario_popup = scenario_popup;
  impl_->capture_min_frames = scenario_popup ? 6 : 3;
}
bool NativeObserver::is_open() const { return impl_ && impl_->open; }
bool NativeObserver::pump_events() {
  ImGui::SetCurrentContext(impl_->imgui);
  SDL_Event event;
  while (SDL_PollEvent(&event)) {
    ImGui_ImplSDL3_ProcessEvent(&event);
    if (event.type == SDL_EVENT_QUIT ||
        event.type == SDL_EVENT_WINDOW_CLOSE_REQUESTED)
      impl_->open = false;
  }
  return impl_->open;
}
void NativeObserver::render(const RenderSnapshot &snapshot) {
  ImGui::SetCurrentContext(impl_->imgui);
  auto scale = std::clamp(SDL_GetWindowDisplayScale(impl_->window), 1.f, 2.5f);
  if (scale != impl_->scale) {
    impl_->scale = scale;
    WorkbenchStyle::apply(scale);
    ImGui_ImplOpenGL3_DestroyFontsTexture();
    WorkbenchStyle::load_font(scale);
  }
  ImGui_ImplOpenGL3_NewFrame();
  ImGui_ImplSDL3_NewFrame();
  ImGui::NewFrame();
  draw_workbench(impl_->ui, snapshot, brain_ ? brain_->latest() : nullptr,
                 dialogue_ ? dialogue_->latest() : nullptr,
                 status_ ? status_->latest() : nullptr, commands_.get(),
                 impl_->scale);
  brain_rebuilds_ = impl_->ui.brain_rebuilds;
  ImGui::Render();
  int width, height;
  SDL_GetWindowSizeInPixels(impl_->window, &width, &height);
  glViewport(0, 0, width, height);
  glClearColor(.055f, .075f, .094f, 1);
  glClear(GL_COLOR_BUFFER_BIT);
  ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());
  if (!impl_->capture_path.empty() && frames_ >= impl_->capture_min_frames) {
    std::vector<unsigned char> pixels(std::size_t(width) * height * 4);
    glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE, pixels.data());
    for (int y = 0; y < height / 2; ++y)
      for (int x = 0; x < width * 4; ++x)
        std::swap(pixels[std::size_t(y) * width * 4 + x],
                  pixels[std::size_t(height - 1 - y) * width * 4 + x]);
    auto surface = SDL_CreateSurfaceFrom(width, height, SDL_PIXELFORMAT_RGBA32,
                                         pixels.data(), width * 4);
    if (!surface || !SDL_SaveBMP(surface, impl_->capture_path.c_str()))
      throw std::runtime_error(SDL_GetError());
    SDL_DestroySurface(surface);
    impl_->capture_path.clear();
  }
  SDL_GL_SwapWindow(impl_->window);
}
void NativeObserver::run(const SnapshotSource &source) {
  while (pump_events())
    render(source.latest());
}
bool NativeObserver::start() {
  if (!source_ || running_.exchange(true))
    return false;
  if (thread_.joinable())
    thread_.join();
  thread_ = std::thread([this] {
    try {
      impl_->initialize();
      while (running_ && pump_events()) {
        auto snapshot = source_->latest();
        render(snapshot);
        last_sequence_ = snapshot.event_sequence;
        ++frames_;
      }
      impl_->shutdown();
    } catch (const std::exception &error) {
      std::fprintf(stderr, "Workbench observer failed: %s\n", error.what());
      impl_->shutdown();
    } catch (...) {
      std::fprintf(stderr, "Workbench observer failed: unknown error\n");
      impl_->shutdown();
    }
    running_ = false;
  });
  return true;
}
void NativeObserver::stop() {
  running_ = false;
  if (thread_.joinable())
    thread_.join();
}
bool NativeObserver::is_running() const noexcept { return running_; }
std::uint64_t NativeObserver::frames_rendered() const noexcept {
  return frames_;
}
std::uint64_t NativeObserver::last_snapshot_event_sequence() const noexcept {
  return last_sequence_;
}
std::uint64_t NativeObserver::brain_snapshot_rebuilds() const noexcept {
  return brain_rebuilds_;
}
RenderSnapshot NativeObserver::latest_snapshot() const {
  return source_ ? source_->latest() : RenderSnapshot{};
}
BrainSnapshot NativeObserver::latest_brain_snapshot() const {
  auto v = brain_ ? brain_->latest() : nullptr;
  return v ? *v : BrainSnapshot{};
}
DialogueSnapshot NativeObserver::latest_dialogue_snapshot() const {
  auto v = dialogue_ ? dialogue_->latest() : nullptr;
  return v ? *v : DialogueSnapshot{};
}
} // namespace se
