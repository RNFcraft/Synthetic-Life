#include "se/observer.hpp"

#include <SDL3/SDL.h>
#include <SDL3/SDL_opengl.h>

#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <string>
#include <utility>

namespace se {
namespace {
constexpr float kPadding = 16.0f;

std::pair<float, float> direction_for(char orientation) {
    switch (orientation) {
    case 'N': case 'n': return {0.0f, -1.0f};
    case 'S': case 's': return {0.0f, 1.0f};
    case 'E': case 'e': return {1.0f, 0.0f};
    case 'W': case 'w': return {-1.0f, 0.0f};
    default: return {0.0f, -1.0f};
    }
}

void append_cell(std::vector<DrawPrimitive>& out, DrawPrimitiveKind kind,
                 const WorldFitTransform& fit, int x, int y, unsigned int id,
                 char orientation = 'N') {
    const float px = fit.origin_x + static_cast<float>(x) * fit.cell_size;
    const float py = fit.origin_y + static_cast<float>(y) * fit.cell_size;
    auto [dx, dy] = direction_for(orientation);
    out.push_back({kind, px, py, fit.cell_size, fit.cell_size, dx, dy, id});
}
} // namespace

WorldFitTransform fit_world_to_viewport(int world_width, int world_height,
                                        int viewport_width, int viewport_height) {
    if (world_width <= 0 || world_height <= 0 || viewport_width <= 0 || viewport_height <= 0) {
        return {};
    }
    const float available_w = std::max(1.0f, static_cast<float>(viewport_width) - 2.0f * kPadding);
    const float available_h = std::max(1.0f, static_cast<float>(viewport_height) - 2.0f * kPadding);
    const float cell = std::max(1.0f, std::min(available_w / world_width, available_h / world_height));
    const float grid_w = cell * world_width;
    const float grid_h = cell * world_height;
    return {(viewport_width - grid_w) * 0.5f, (viewport_height - grid_h) * 0.5f,
            cell, grid_w, grid_h};
}

std::vector<DrawPrimitive> prepare_draw_data(const RenderSnapshot& snapshot,
                                             int viewport_width, int viewport_height) {
    std::vector<DrawPrimitive> result;
    const auto fit = fit_world_to_viewport(snapshot.world_width, snapshot.world_height,
                                           viewport_width, viewport_height);
    if (fit.cell_size == 0.0f) return result;
    result.push_back({DrawPrimitiveKind::grid, fit.origin_x, fit.origin_y,
                      fit.grid_width, fit.grid_height, 0.0f, 0.0f, 0});
    for (const auto& object : snapshot.objects)
        append_cell(result, DrawPrimitiveKind::object, fit, object.x, object.y, object.id);
    for (const auto& body : snapshot.bodies) {
        append_cell(result, DrawPrimitiveKind::body, fit, body.x, body.y, body.id, body.orientation);
        append_cell(result, DrawPrimitiveKind::orientation, fit, body.x, body.y, body.id, body.orientation);
        if (body.held_object_id != 0)
            append_cell(result, DrawPrimitiveKind::held_object, fit, body.x, body.y,
                        body.held_object_id, body.orientation);
    }
    return result;
}

class NativeObserver::Impl {
public:
    Impl(int width, int height):width(width),height(height) {}
    void initialize() {
        if (!SDL_Init(SDL_INIT_VIDEO)) throw std::runtime_error(SDL_GetError());
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3);
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 3);
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE);
        window = SDL_CreateWindow("Synthetic-Life native observer", width, height,
                                  SDL_WINDOW_OPENGL | SDL_WINDOW_RESIZABLE);
        if (!window) throw std::runtime_error(SDL_GetError());
        context = SDL_GL_CreateContext(window);
        if (!context) throw std::runtime_error(SDL_GetError());
        SDL_GL_SetSwapInterval(1);
    }
    void shutdown() {
        if (context) SDL_GL_DestroyContext(context);
        if (window) SDL_DestroyWindow(window);
        context=nullptr; window=nullptr;
        SDL_Quit();
    }
    ~Impl() { shutdown(); }
    SDL_Window* window{};
    SDL_GLContext context{};
    bool open{true};
    int width, height;
};

NativeObserver::NativeObserver(int width, int height) : impl_(std::make_unique<Impl>(width, height)) { impl_->initialize(); }
NativeObserver::NativeObserver(std::shared_ptr<RenderSnapshotChannel> channel, int width, int height)
    : impl_(std::make_unique<Impl>(width, height)), source_(std::make_shared<ChannelSnapshotSource>(std::move(channel))) {}
NativeObserver::~NativeObserver() { stop(); }
bool NativeObserver::is_open() const { return impl_ && impl_->open; }

bool NativeObserver::pump_events() {
    SDL_Event event;
    while (SDL_PollEvent(&event)) {
        if (event.type == SDL_EVENT_QUIT || event.type == SDL_EVENT_WINDOW_CLOSE_REQUESTED)
            impl_->open = false;
    }
    return impl_->open;
}

void NativeObserver::render(const RenderSnapshot& snapshot) {
    int width = 0, height = 0;
    SDL_GetWindowSizeInPixels(impl_->window, &width, &height);
    glViewport(0, 0, width, height);
    glClearColor(0.055f, 0.075f, 0.10f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT);
    const auto draw_data = prepare_draw_data(snapshot, width, height);
    glEnable(GL_SCISSOR_TEST);
    for (const auto& primitive : draw_data) {
        if (primitive.kind == DrawPrimitiveKind::grid) {
            glScissor(static_cast<int>(primitive.x),
                      height - static_cast<int>(primitive.y + primitive.height),
                      static_cast<int>(primitive.width), static_cast<int>(primitive.height));
            glClearColor(0.12f, 0.16f, 0.20f, 1.0f);
            glClear(GL_COLOR_BUFFER_BIT);
            glClearColor(0.19f, 0.24f, 0.29f, 1.0f);
            const auto fit = fit_world_to_viewport(snapshot.world_width, snapshot.world_height, width, height);
            for (int x = 0; x <= snapshot.world_width; ++x) {
                const int line_x = static_cast<int>(fit.origin_x + x * fit.cell_size);
                glScissor(line_x, height - static_cast<int>(fit.origin_y + fit.grid_height),
                          1, static_cast<int>(fit.grid_height));
                glClear(GL_COLOR_BUFFER_BIT);
            }
            for (int y = 0; y <= snapshot.world_height; ++y) {
                const int line_y = height - static_cast<int>(fit.origin_y + y * fit.cell_size);
                glScissor(static_cast<int>(fit.origin_x), line_y,
                          static_cast<int>(fit.grid_width), 1);
                glClear(GL_COLOR_BUFFER_BIT);
            }
            continue;
        }
        float x = primitive.x + 2.0f;
        float y = primitive.y + 2.0f;
        float side = std::max(1.0f, primitive.width - 4.0f);
        if (primitive.kind == DrawPrimitiveKind::object) glClearColor(0.95f, 0.65f, 0.18f, 1.0f);
        else if (primitive.kind == DrawPrimitiveKind::body) glClearColor(0.18f, 0.70f, 0.95f, 1.0f);
        else if (primitive.kind == DrawPrimitiveKind::orientation) {
            const float marker = std::max(2.0f, side * 0.25f);
            x += (primitive.direction_x + 1.0f) * 0.5f * (side - marker);
            y += (primitive.direction_y + 1.0f) * 0.5f * (side - marker);
            side = marker;
            glClearColor(0.98f, 0.98f, 0.98f, 1.0f);
        } else { // held-object marker
            const float marker = std::max(2.0f, side * 0.20f);
            x += side - marker;
            side = marker;
            glClearColor(0.85f, 0.25f, 0.75f, 1.0f);
        }
        glScissor(static_cast<int>(x), height - static_cast<int>(y + side),
                  static_cast<int>(side), static_cast<int>(side));
        glClear(GL_COLOR_BUFFER_BIT);
    }
    glDisable(GL_SCISSOR_TEST);
    SDL_GL_SwapWindow(impl_->window);
}

void NativeObserver::run(const SnapshotSource& source) {
    while (pump_events()) render(source.latest());
}

bool NativeObserver::start() {
    if (!source_ || running_.exchange(true)) return false;
    thread_ = std::thread([this] {
        try {
            impl_->initialize();
            while (running_ && pump_events()) {
                auto snapshot=source_->latest();render(snapshot);last_sequence_=snapshot.event_sequence;++frames_;
            }
            impl_->shutdown();
        } catch (...) { impl_->shutdown(); }
        running_=false;
    });
    return true;
}
void NativeObserver::stop() { running_ = false; if (thread_.joinable()) thread_.join(); }
bool NativeObserver::is_running() const noexcept { return running_; }
std::uint64_t NativeObserver::frames_rendered() const noexcept { return frames_; }
std::uint64_t NativeObserver::last_snapshot_event_sequence() const noexcept { return last_sequence_; }
RenderSnapshot NativeObserver::latest_snapshot() const { return source_ ? source_->latest() : RenderSnapshot{}; }

} // namespace se
