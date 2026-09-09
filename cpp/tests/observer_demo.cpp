#include "se/observer.hpp"

namespace {
class DemoSource final : public se::SnapshotSource {
public:
    se::RenderSnapshot latest() const override {
        se::RenderSnapshot snapshot;
        snapshot.world_width = 16;
        snapshot.world_height = 10;
        snapshot.bodies = {{1, 3, 4, 'E', 0, 8}, {2, 11, 6, 'N', 0, 0}};
        snapshot.objects = {{8, 4, 4, 0}, {9, 12, 2, 0}};
        return snapshot;
    }
};
}

int main() {
    DemoSource source;
    se::NativeObserver observer;
    observer.run(source);
    return 0;
}
