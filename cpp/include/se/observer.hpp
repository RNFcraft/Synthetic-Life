#pragma once

#include "se/render_snapshot.hpp"
#include "se/brain_snapshot.hpp"
#include "se/dialogue_snapshot.hpp"

#include <memory>
#include <atomic>
#include <thread>
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
struct BrainNodeVisual { std::uint32_t id{};float x{},y{},radius{},intensity{};bool composite{},appearing{}; };
struct BrainEdgeVisual { std::uint32_t source{},target{};float x1{},y1{},x2{},y2{},intensity{},thickness{};std::uint8_t type{}; };
struct BrainDrawData { std::vector<BrainNodeVisual>nodes;std::vector<BrainEdgeVisual>edges; };

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
BrainDrawData prepare_brain_draw_data(const BrainSnapshot& snapshot,int width,int height);

class SnapshotSource {
public:
    virtual ~SnapshotSource() = default;
    virtual RenderSnapshot latest() const = 0;
};
class ChannelSnapshotSource final : public SnapshotSource {
public:
    explicit ChannelSnapshotSource(std::shared_ptr<RenderSnapshotChannel> channel):channel_(std::move(channel)){}
    RenderSnapshot latest() const override { auto value=channel_->latest(); return value ? *value : RenderSnapshot{}; }
private: std::shared_ptr<RenderSnapshotChannel> channel_;
};

// SDL/OpenGL ownership and the frame loop live behind this interface. It has no
// access to World and can only obtain value-owned snapshots from SnapshotSource.
class NativeObserver {
public:
    NativeObserver(int width = 960, int height = 720);
    explicit NativeObserver(std::shared_ptr<RenderSnapshotChannel> channel, std::shared_ptr<BrainSnapshotChannel> brain = {},std::shared_ptr<DialogueSnapshotChannel> dialogue = {}, int width = 1100, int height = 720);
    ~NativeObserver();
    NativeObserver(const NativeObserver&) = delete;
    NativeObserver& operator=(const NativeObserver&) = delete;
    NativeObserver(NativeObserver&&) = delete;
    NativeObserver& operator=(NativeObserver&&) = delete;

    bool is_open() const;
    bool pump_events();
    void render(const RenderSnapshot& snapshot);
    void run(const SnapshotSource& source);
    bool start();
    void stop();
    bool is_running() const noexcept;
    std::uint64_t frames_rendered() const noexcept;
    std::uint64_t last_snapshot_event_sequence() const noexcept;
    std::uint64_t brain_snapshot_rebuilds() const noexcept;
    RenderSnapshot latest_snapshot() const;
    BrainSnapshot latest_brain_snapshot() const;
    DialogueSnapshot latest_dialogue_snapshot() const;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
    std::shared_ptr<SnapshotSource> source_;
    std::shared_ptr<BrainSnapshotChannel> brain_;
    std::shared_ptr<DialogueSnapshotChannel> dialogue_;
    std::thread thread_;
    std::atomic<bool> running_{false};
    std::atomic<std::uint64_t> frames_{0};
    std::atomic<std::uint64_t> last_sequence_{0};
    std::atomic<std::uint64_t> brain_rebuilds_{0};
};

} // namespace se
