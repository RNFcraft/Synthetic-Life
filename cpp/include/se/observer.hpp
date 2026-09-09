#pragma once

#include "se/render_snapshot.hpp"

#include <memory>
#include <vector>

namespace se {

struct WorldFitTransform {
    float origin_x{};
    float origin_y{};
    float cell_size{};
    float grid_width{};
    float grid_height{};
};

enum class DrawPrimitiveKind { grid, object, body, orientation, held_object };

struct DrawPrimitive {
    DrawPrimitiveKind kind{};
    float x{};
    float y{};
    float width{};
    float height{};
    float direction_x{};
    float direction_y{};
    unsigned int id{};
};

// Pure presentation helpers. Coordinates are pixel coordinates in the viewport.
WorldFitTransform fit_world_to_viewport(int world_width, int world_height,
                                        int viewport_width, int viewport_height);
std::vector<DrawPrimitive> prepare_draw_data(const RenderSnapshot& snapshot,
                                             int viewport_width, int viewport_height);

class SnapshotSource {
public:
    virtual ~SnapshotSource() = default;
    virtual RenderSnapshot latest() const = 0;
};

// SDL/OpenGL ownership and the frame loop live behind this interface. It has no
// access to World and can only obtain value-owned snapshots from SnapshotSource.
class NativeObserver {
public:
    NativeObserver(int width = 960, int height = 720);
    ~NativeObserver();
    NativeObserver(const NativeObserver&) = delete;
    NativeObserver& operator=(const NativeObserver&) = delete;
    NativeObserver(NativeObserver&&) noexcept;
    NativeObserver& operator=(NativeObserver&&) noexcept;

    bool is_open() const;
    bool pump_events();
    void render(const RenderSnapshot& snapshot);
    void run(const SnapshotSource& source);

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace se
