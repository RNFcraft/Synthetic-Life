#include "se/observer.hpp"

#include <SDL3/SDL.h>
#include <SDL3/SDL_opengl.h>

#include <algorithm>
#include <array>
#include <cmath>
#include <stdexcept>
#include <string>
#include <utility>
#include <unordered_map>
#include <sstream>
#include <iomanip>

namespace se {
namespace {
constexpr float kPadding = 16.0f;

const std::array<std::uint8_t,7>& glyph(char c){
    static const std::array<std::uint8_t,7> blank{};
    static const std::unordered_map<char,std::array<std::uint8_t,7>> g={
      {'A',{14,17,17,31,17,17,17}},{'B',{30,17,17,30,17,17,30}},{'C',{14,17,16,16,16,17,14}},
      {'D',{30,17,17,17,17,17,30}},{'E',{31,16,16,30,16,16,31}},{'G',{14,17,16,23,17,17,15}},
      {'F',{31,16,16,30,16,16,16}},{'H',{17,17,17,31,17,17,17}},{'U',{17,17,17,17,17,17,14}},
      {'I',{31,4,4,4,4,4,31}},{'K',{17,18,20,24,20,18,17}},{'L',{16,16,16,16,16,16,31}},
      {'M',{17,27,21,21,17,17,17}},{'N',{17,25,21,19,17,17,17}},{'O',{14,17,17,17,17,17,14}},
      {'R',{30,17,17,30,20,18,17}},{'S',{15,16,16,14,1,1,30}},{'T',{31,4,4,4,4,4,4}},
      {'V',{17,17,17,17,17,10,4}},{'W',{17,17,17,21,21,21,10}},{'Y',{17,17,10,4,4,4,4}},
      {'0',{14,17,19,21,25,17,14}},{'1',{4,12,4,4,4,4,14}},{'2',{14,17,1,2,4,8,31}},
      {'3',{30,1,1,14,1,1,30}},{'4',{2,6,10,18,31,2,2}},{'5',{31,16,16,30,1,1,30}},
      {'6',{14,16,16,30,17,17,14}},{'7',{31,1,2,4,8,8,8}},{'8',{14,17,17,14,17,17,14}},
      {'9',{14,17,17,15,1,1,14}},{'.',{0,0,0,0,0,4,4}},{':',{0,4,4,0,4,4,0}},{'-',{0,0,0,31,0,0,0}}
    };auto it=g.find(c);return it==g.end()?blank:it->second;
}

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

BrainDrawData prepare_brain_draw_data(const BrainSnapshot& snapshot,int width,int height) {
    BrainDrawData out;if(width<=0||height<=0)return out;
    std::unordered_map<std::uint32_t,std::pair<float,float>> positions;
    const float cx=width*.5f,cy=height*.5f,rx=std::max(8.f,width*.39f),ry=std::max(8.f,height*.38f);
    for(auto const&n:snapshot.nodes){
        std::uint32_t h=n.id*2654435761u+1013904223u;float angle=float(h%10000u)*.0006283185f;
        float ring=.38f+.58f*float((h>>16)%1000u)/999.f;float x=cx+std::cos(angle)*rx*ring,y=cy+std::sin(angle)*ry*ring;
        positions[n.id]={x,y};float active=std::clamp(float(n.activity),0.f,1.f);out.nodes.push_back({n.id,x,y,3.5f+active*3.f,.18f+active*.82f,n.composite,n.last_active_cognitive_tick==snapshot.cognitive_tick&&snapshot.cognitive_tick!=0});
    }
    for(auto const&e:snapshot.edges){auto a=positions.find(e.source),b=positions.find(e.target);if(a==positions.end()||b==positions.end())continue;out.edges.push_back({e.source,e.target,a->second.first,a->second.second,b->second.first,b->second.second,float(std::clamp(.2*e.confidence+.8*e.activation,0.,1.)),.5f+float(std::clamp(e.strength,0.,1.))*1.5f,e.relation_type});}
    return out;
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
    std::unordered_map<std::uint32_t,double> node_birth_time;
};

NativeObserver::NativeObserver(int width, int height) : impl_(std::make_unique<Impl>(width, height)) { impl_->initialize(); }
NativeObserver::NativeObserver(std::shared_ptr<RenderSnapshotChannel> channel, std::shared_ptr<BrainSnapshotChannel> brain, int width, int height)
    : impl_(std::make_unique<Impl>(width, height)), source_(std::make_shared<ChannelSnapshotSource>(std::move(channel))), brain_(std::move(brain)) {}
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
    const int dashboard=std::clamp(int(width*.28f),240,std::max(240,width-240));const int world_width=std::max(1,width-dashboard);
    const auto draw_data = prepare_draw_data(snapshot, world_width, height);
    glEnable(GL_SCISSOR_TEST);
    auto rect=[&](int x,int y,int w,int h,float r,float g,float b){if(w<=0||h<=0)return;glScissor(x,height-y-h,w,h);glClearColor(r,g,b,1);glClear(GL_COLOR_BUFFER_BIT);};
    auto text=[&](int x,int y,const std::string&s,int scale,float r,float g,float b){int pen=x;for(char c:s){if(c==' '){pen+=6*scale;continue;}auto const&bits=glyph(c);for(int row=0;row<7;++row)for(int col=0;col<5;++col)if(bits[row]&(1<<(4-col)))rect(pen+col*scale,y+row*scale,scale,scale,r,g,b);pen+=6*scale;}};
    rect(8,8,world_width-16,height-16,.075f,.10f,.13f);rect(world_width+8,8,dashboard-16,height-16,.07f,.09f,.115f);
    const int brain_x=world_width+20,brain_y=22,brain_w=dashboard-40,brain_h=std::max(120,int(height*.62f));rect(brain_x,brain_y,brain_w,brain_h,.045f,.065f,.09f);rect(brain_x,brain_y+brain_h+14,brain_w,std::max(20,height-brain_h-58),.055f,.075f,.095f);
    for (const auto& primitive : draw_data) {
        if (primitive.kind == DrawPrimitiveKind::grid) {
            glScissor(static_cast<int>(primitive.x),
                      height - static_cast<int>(primitive.y + primitive.height),
                      static_cast<int>(primitive.width), static_cast<int>(primitive.height));
            glClearColor(0.12f, 0.16f, 0.20f, 1.0f);
            glClear(GL_COLOR_BUFFER_BIT);
            glClearColor(0.19f, 0.24f, 0.29f, 1.0f);
            const auto fit = fit_world_to_viewport(snapshot.world_width, snapshot.world_height, world_width, height);
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
    if(brain_){auto brain=brain_->latest();if(brain){auto graph=prepare_brain_draw_data(*brain,brain_w,brain_h);auto edge_color=[](std::uint8_t t){switch(t){case 1:return std::array<float,3>{.35f,.62f,.78f};case 2:return std::array<float,3>{.45f,.72f,.50f};case 3:return std::array<float,3>{.76f,.38f,.42f};case 4:return std::array<float,3>{.72f,.55f,.30f};default:return std::array<float,3>{.48f,.52f,.64f};}};
        for(auto const&e:graph.edges){auto c=edge_color(e.type);int steps=std::max(2,int(std::hypot(e.x2-e.x1,e.y2-e.y1)));for(int i=0;i<=steps;++i){float t=float(i)/steps;int x=brain_x+int(e.x1+(e.x2-e.x1)*t);int y=brain_y+int(e.y1+(e.y2-e.y1)*t);int s=std::max(1,int(e.thickness));rect(x,y,s,s,c[0]*(.35f+.65f*e.intensity),c[1]*(.35f+.65f*e.intensity),c[2]*(.35f+.65f*e.intensity));}}
        const double visual_now=double(SDL_GetTicks())/1000.;
        for(auto const&n:graph.nodes){auto [birth,_]=impl_->node_birth_time.emplace(n.id,visual_now);double age=visual_now-birth->second;float appearance=std::clamp(float(age/.45),.18f,1.f);float pulse=age<.8?float((1.-age/.8)*.35):0.f;float intensity=std::clamp(n.intensity+pulse,0.f,1.f);int glow=int((n.radius+4*intensity)*appearance);rect(brain_x+int(n.x)-glow,brain_y+int(n.y)-glow,glow*2,glow*2,.06f+.08f*intensity,.12f+.16f*intensity,.18f+.22f*intensity);int r=std::max(2,int(n.radius*appearance));rect(brain_x+int(n.x)-r,brain_y+int(n.y)-r,r*2,r*2,.25f+.45f*intensity,.48f+.40f*intensity,.62f+.35f*intensity);if(n.composite)rect(brain_x+int(n.x)-1,brain_y+int(n.y)-1,3,3,.93f,.88f,.65f);}
        int sy=brain_y+brain_h+28;int tx=brain_x+12;std::ostringstream wt;wt<<std::fixed<<std::setprecision(3)<<snapshot.world_time;
        text(brain_x+10,brain_y+10,"BRAIN",2,.55f,.74f,.86f);text(tx,sy,"STATUS",2,.50f,.68f,.78f);sy+=28;
        text(tx,sy,"WORLD TIME: "+wt.str(),1,.66f,.74f,.78f);sy+=15;text(tx,sy,"EVENT: "+std::to_string(snapshot.event_sequence),1,.66f,.74f,.78f);sy+=15;
        text(tx,sy,"TICK: "+std::to_string(brain->cognitive_tick),1,.66f,.74f,.78f);sy+=15;text(tx,sy,"GEN: "+std::to_string(brain->cognition_generation),1,.66f,.74f,.78f);sy+=15;
        text(tx,sy,"COGNITS: "+std::to_string(brain->nodes.size()),1,.66f,.74f,.78f);sy+=15;text(tx,sy,"RELATIONS: "+std::to_string(brain->edges.size()),1,.66f,.74f,.78f);sy+=15;
        auto active=std::count_if(brain->nodes.begin(),brain->nodes.end(),[&](auto const&n){return n.last_active_cognitive_tick==brain->cognitive_tick&&brain->cognitive_tick;});text(tx,sy,"ACTIVE: "+std::to_string(active),1,.66f,.74f,.78f);
    }}
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
BrainSnapshot NativeObserver::latest_brain_snapshot() const { auto value=brain_?brain_->latest():nullptr;return value?*value:BrainSnapshot{}; }

} // namespace se
