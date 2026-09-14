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
    static const std::array<std::uint8_t,7> fallback{31,17,2,4,0,4,0};
    static const std::unordered_map<char,std::array<std::uint8_t,7>> g={
      {'A',{14,17,17,31,17,17,17}},{'B',{30,17,17,30,17,17,30}},{'C',{14,17,16,16,16,17,14}},
      {'D',{30,17,17,17,17,17,30}},{'E',{31,16,16,30,16,16,31}},{'G',{14,17,16,23,17,17,15}},
      {'F',{31,16,16,30,16,16,16}},{'H',{17,17,17,31,17,17,17}},{'U',{17,17,17,17,17,17,14}},
      {'I',{31,4,4,4,4,4,31}},{'K',{17,18,20,24,20,18,17}},{'L',{16,16,16,16,16,16,31}},
      {'M',{17,27,21,21,17,17,17}},{'N',{17,25,21,19,17,17,17}},{'O',{14,17,17,17,17,17,14}},
      {'P',{30,17,17,30,16,16,16}},{'Q',{14,17,17,17,21,18,13}},{'R',{30,17,17,30,20,18,17}},{'S',{15,16,16,14,1,1,30}},{'T',{31,4,4,4,4,4,4}},
      {'V',{17,17,17,17,17,10,4}},{'W',{17,17,17,21,21,21,10}},{'X',{17,17,10,4,10,17,17}},{'Y',{17,17,10,4,4,4,4}},{'Z',{31,1,2,4,8,16,31}},
      {'0',{14,17,19,21,25,17,14}},{'1',{4,12,4,4,4,4,14}},{'2',{14,17,1,2,4,8,31}},
      {'3',{30,1,1,14,1,1,30}},{'4',{2,6,10,18,31,2,2}},{'5',{31,16,16,30,1,1,30}},
      {'6',{14,16,16,30,17,17,14}},{'7',{31,1,2,4,8,8,8}},{'8',{14,17,17,14,17,17,14}},
      {'9',{14,17,17,15,1,1,14}},{'.',{0,0,0,0,0,4,4}},{':',{0,4,4,0,4,4,0}},{'-',{0,0,0,31,0,0,0}},{'/',{1,2,2,4,8,8,16}},{'>',{16,8,4,2,4,8,16}}
    };auto it=g.find(c);if(it!=g.end())return it->second;if(c>='a'&&c<='z'){auto upper=g.find(char(c-'a'+'A'));if(upper!=g.end()){static thread_local std::array<std::uint8_t,7>lower;lower=upper->second;lower[6]|=1;return lower;}}return fallback;
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
    const std::size_t node_budget=std::clamp<std::size_t>(std::size_t(width)*std::size_t(height)/1800,128,512);
    const std::size_t node_count=std::min(node_budget,snapshot.nodes.size());
    std::unordered_map<std::uint32_t,std::pair<float,float>> positions;
    const float cx=width*.5f,cy=height*.5f,rx=std::max(8.f,width*.39f),ry=std::max(8.f,height*.38f);
    for(std::size_t index=0;index<node_count;++index){auto const&n=snapshot.nodes[index];
        std::uint32_t h=n.id*2654435761u+1013904223u;float angle=float(h%10000u)*.0006283185f;
        float ring=.38f+.58f*float((h>>16)%1000u)/999.f;float x=cx+std::cos(angle)*rx*ring,y=cy+std::sin(angle)*ry*ring;
        positions[n.id]={x,y};float active=std::clamp(float(n.activity),0.f,1.f);out.nodes.push_back({n.id,x,y,3.5f+active*3.f,.18f+active*.82f,n.composite,n.last_active_cognitive_tick==snapshot.cognitive_tick&&snapshot.cognitive_tick!=0});
    }
    const std::size_t edge_budget=std::min<std::size_t>(2048,node_budget*4);
    for(auto const&e:snapshot.edges){if(out.edges.size()>=edge_budget)break;auto a=positions.find(e.source),b=positions.find(e.target);if(a==positions.end()||b==positions.end())continue;out.edges.push_back({e.source,e.target,a->second.first,a->second.second,b->second.first,b->second.second,float(std::clamp(.2*e.confidence+.8*e.activation,0.,1.)),.5f+float(std::clamp(e.strength,0.,1.))*1.5f,e.relation_type});}
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
        load_gl();create_brain_gpu();
    }
    void shutdown() {
        destroy_brain_gpu();
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
    std::uint32_t max_seen_node_id{};bool saw_node{};
    std::shared_ptr<const BrainSnapshot> cached_snapshot;
    BrainDrawData cached_graph;
    int cached_brain_width{},cached_brain_height{};
    struct Vertex{float x,y,r,g,b,a,size,birth;};
    GLuint program{},vao{},edge_vbo{},node_vbo{};GLint screen_uniform{-1},points_uniform{-1},time_uniform{-1};GLsizei edge_vertices{},node_vertices{};
    PFNGLGENVERTEXARRAYSPROC GenVertexArrays{};PFNGLBINDVERTEXARRAYPROC BindVertexArray{};PFNGLDELETEVERTEXARRAYSPROC DeleteVertexArrays{};PFNGLGENBUFFERSPROC GenBuffers{};PFNGLBINDBUFFERPROC BindBuffer{};PFNGLBUFFERDATAPROC BufferData{};PFNGLDELETEBUFFERSPROC DeleteBuffers{};PFNGLCREATESHADERPROC CreateShader{};PFNGLSHADERSOURCEPROC ShaderSource{};PFNGLCOMPILESHADERPROC CompileShader{};PFNGLCREATEPROGRAMPROC CreateProgram{};PFNGLATTACHSHADERPROC AttachShader{};PFNGLLINKPROGRAMPROC LinkProgram{};PFNGLDELETESHADERPROC DeleteShader{};PFNGLDELETEPROGRAMPROC DeleteProgram{};PFNGLUSEPROGRAMPROC UseProgram{};PFNGLGETUNIFORMLOCATIONPROC GetUniformLocation{};PFNGLUNIFORM2FPROC Uniform2f{};PFNGLUNIFORM1IPROC Uniform1i{};PFNGLUNIFORM1FPROC Uniform1f{};PFNGLENABLEVERTEXATTRIBARRAYPROC EnableVertexAttribArray{};PFNGLVERTEXATTRIBPOINTERPROC VertexAttribPointer{};
    template<class T>void load(T&f,const char*n){f=reinterpret_cast<T>(SDL_GL_GetProcAddress(n));if(!f)throw std::runtime_error(std::string("OpenGL function unavailable: ")+n);}
    void load_gl(){load(GenVertexArrays,"glGenVertexArrays");load(BindVertexArray,"glBindVertexArray");load(DeleteVertexArrays,"glDeleteVertexArrays");load(GenBuffers,"glGenBuffers");load(BindBuffer,"glBindBuffer");load(BufferData,"glBufferData");load(DeleteBuffers,"glDeleteBuffers");load(CreateShader,"glCreateShader");load(ShaderSource,"glShaderSource");load(CompileShader,"glCompileShader");load(CreateProgram,"glCreateProgram");load(AttachShader,"glAttachShader");load(LinkProgram,"glLinkProgram");load(DeleteShader,"glDeleteShader");load(DeleteProgram,"glDeleteProgram");load(UseProgram,"glUseProgram");load(GetUniformLocation,"glGetUniformLocation");load(Uniform2f,"glUniform2f");load(Uniform1i,"glUniform1i");load(Uniform1f,"glUniform1f");load(EnableVertexAttribArray,"glEnableVertexAttribArray");load(VertexAttribPointer,"glVertexAttribPointer");}
    GLuint shader(GLenum kind,const char*source){GLuint s=CreateShader(kind);ShaderSource(s,1,&source,nullptr);CompileShader(s);return s;}
    void create_brain_gpu(){const char*vs="#version 330 core\nlayout(location=0)in vec2 p;layout(location=1)in vec4 c;layout(location=2)in float sz;layout(location=3)in float born;uniform vec2 screen;uniform float now;out vec4 color;out float age;void main(){gl_Position=vec4(p.x/screen.x*2-1,1-p.y/screen.y*2,0,1);gl_PointSize=sz;age=now-born;color=c;}";const char*fs="#version 330 core\nin vec4 color;in float age;uniform int points;out vec4 outc;void main(){if(points==1&&distance(gl_PointCoord,vec2(.5))>.5)discard;float birth=points==1?clamp(age/.45,.2,1.):1.;outc=vec4(color.rgb*birth,color.a);}";auto v=shader(GL_VERTEX_SHADER,vs),f=shader(GL_FRAGMENT_SHADER,fs);program=CreateProgram();AttachShader(program,v);AttachShader(program,f);LinkProgram(program);DeleteShader(v);DeleteShader(f);screen_uniform=GetUniformLocation(program,"screen");points_uniform=GetUniformLocation(program,"points");time_uniform=GetUniformLocation(program,"now");GenVertexArrays(1,&vao);GenBuffers(1,&edge_vbo);GenBuffers(1,&node_vbo);}
    void destroy_brain_gpu(){if(!context)return;if(edge_vbo)DeleteBuffers(1,&edge_vbo);if(node_vbo)DeleteBuffers(1,&node_vbo);if(vao)DeleteVertexArrays(1,&vao);if(program)DeleteProgram(program);edge_vbo=node_vbo=vao=program=0;}
    void bind_vertices(GLuint buffer){BindVertexArray(vao);BindBuffer(GL_ARRAY_BUFFER,buffer);EnableVertexAttribArray(0);VertexAttribPointer(0,2,GL_FLOAT,GL_FALSE,sizeof(Vertex),(void*)0);EnableVertexAttribArray(1);VertexAttribPointer(1,4,GL_FLOAT,GL_FALSE,sizeof(Vertex),(void*)(2*sizeof(float)));EnableVertexAttribArray(2);VertexAttribPointer(2,1,GL_FLOAT,GL_FALSE,sizeof(Vertex),(void*)(6*sizeof(float)));EnableVertexAttribArray(3);VertexAttribPointer(3,1,GL_FLOAT,GL_FALSE,sizeof(Vertex),(void*)(7*sizeof(float)));}
};

NativeObserver::NativeObserver(int width, int height) : impl_(std::make_unique<Impl>(width, height)) { impl_->initialize(); }
NativeObserver::NativeObserver(std::shared_ptr<RenderSnapshotChannel> channel, std::shared_ptr<BrainSnapshotChannel> brain,std::shared_ptr<DialogueSnapshotChannel> dialogue, int width, int height)
    : impl_(std::make_unique<Impl>(width, height)), source_(std::make_shared<ChannelSnapshotSource>(std::move(channel))), brain_(std::move(brain)),dialogue_(std::move(dialogue)) {}
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
    const int dialogue_width=std::clamp(int(width*.21f),120,std::max(120,width-480));const int dashboard=std::clamp(int(width*.27f),220,std::max(220,width-dialogue_width-240));const int world_width=std::max(1,width-dialogue_width-dashboard);
    const auto draw_data = prepare_draw_data(snapshot, world_width, height);
    glEnable(GL_SCISSOR_TEST);
    auto rect=[&](int x,int y,int w,int h,float r,float g,float b){if(w<=0||h<=0)return;glScissor(x,height-y-h,w,h);glClearColor(r,g,b,1);glClear(GL_COLOR_BUFFER_BIT);};
    auto text=[&](int x,int y,const std::string&s,int scale,float r,float g,float b){int pen=x;for(char c:s){if(c==' '){pen+=6*scale;continue;}auto const&bits=glyph(c);for(int row=0;row<7;++row)for(int col=0;col<5;++col)if(bits[row]&(1<<(4-col)))rect(pen+col*scale,y+row*scale,scale,scale,r,g,b);pen+=6*scale;}};
    rect(8,8,dialogue_width-16,height-16,.055f,.075f,.095f);rect(dialogue_width+8,8,world_width-16,height-16,.075f,.10f,.13f);rect(dialogue_width+world_width+8,8,dashboard-16,height-16,.07f,.09f,.115f);
    const int brain_x=dialogue_width+world_width+20,brain_y=22,brain_w=dashboard-40,brain_h=std::max(120,int(height*.62f));rect(brain_x,brain_y,brain_w,brain_h,.045f,.065f,.09f);rect(brain_x,brain_y+brain_h+14,brain_w,std::max(20,height-brain_h-58),.055f,.075f,.095f);
    text(18,20,"DIALOGUE",2,.55f,.74f,.86f);
    if(dialogue_){auto dialogue=dialogue_->latest();if(dialogue){int line_h=15,max_lines=std::max(0,(height-62)/line_h),shown=std::min<int>(max_lines,dialogue->lines.size()),y=height-24-shown*line_h,max_chars=std::max(1,(dialogue_width-34)/6);for(auto it=dialogue->lines.end()-shown;it!=dialogue->lines.end();++it){std::string line=(it->role==DialogueRole::External?"> ":"E> ")+it->text;if((int)line.size()>max_chars)line.resize(max_chars);text(18,y,line,1,it->role==DialogueRole::External?.72f:.48f,it->role==DialogueRole::External?.78f:.82f,it->role==DialogueRole::External?.82f:.65f);y+=line_h;}}}
    for (const auto& primitive : draw_data) {
        if (primitive.kind == DrawPrimitiveKind::grid) {
            glScissor(dialogue_width+static_cast<int>(primitive.x),
                      height - static_cast<int>(primitive.y + primitive.height),
                      static_cast<int>(primitive.width), static_cast<int>(primitive.height));
            glClearColor(0.12f, 0.16f, 0.20f, 1.0f);
            glClear(GL_COLOR_BUFFER_BIT);
            glClearColor(0.19f, 0.24f, 0.29f, 1.0f);
            const auto fit = fit_world_to_viewport(snapshot.world_width, snapshot.world_height, world_width, height);
            for (int x = 0; x <= snapshot.world_width; ++x) {
                const int line_x = dialogue_width+static_cast<int>(fit.origin_x + x * fit.cell_size);
                glScissor(line_x, height - static_cast<int>(fit.origin_y + fit.grid_height),
                          1, static_cast<int>(fit.grid_height));
                glClear(GL_COLOR_BUFFER_BIT);
            }
            for (int y = 0; y <= snapshot.world_height; ++y) {
                const int line_y = height - static_cast<int>(fit.origin_y + y * fit.cell_size);
                glScissor(dialogue_width+static_cast<int>(fit.origin_x), line_y,
                          static_cast<int>(fit.grid_width), 1);
                glClear(GL_COLOR_BUFFER_BIT);
            }
            continue;
        }
        float x = dialogue_width+primitive.x + 2.0f;
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
    if(brain_){auto brain=brain_->latest();if(brain){auto edge_color=[](std::uint8_t t){switch(t){case 1:return std::array<float,3>{.35f,.62f,.78f};case 2:return std::array<float,3>{.45f,.72f,.50f};case 3:return std::array<float,3>{.76f,.38f,.42f};case 4:return std::array<float,3>{.72f,.55f,.30f};default:return std::array<float,3>{.48f,.52f,.64f};}};
        if(brain!=impl_->cached_snapshot||brain_w!=impl_->cached_brain_width||brain_h!=impl_->cached_brain_height){impl_->cached_graph=prepare_brain_draw_data(*brain,brain_w,brain_h);impl_->cached_snapshot=brain;impl_->cached_brain_width=brain_w;impl_->cached_brain_height=brain_h;++brain_rebuilds_;const float now=float(SDL_GetTicks())/1000.f;std::vector<Impl::Vertex>ev,nv;ev.reserve(impl_->cached_graph.edges.size()*2);nv.reserve(impl_->cached_graph.nodes.size());for(auto const&e:impl_->cached_graph.edges){auto c=edge_color(e.type);float light=.35f+.65f*e.intensity;Impl::Vertex a{brain_x+e.x1,brain_y+e.y1,c[0]*light,c[1]*light,c[2]*light,.8f,1,0},b=a;b.x=brain_x+e.x2;b.y=brain_y+e.y2;ev.push_back(a);ev.push_back(b);}for(auto const&n:impl_->cached_graph.nodes){bool known=impl_->saw_node&&n.id<=impl_->max_seen_node_id;float born=known?0.f:now;impl_->max_seen_node_id=impl_->saw_node?std::max(impl_->max_seen_node_id,n.id):n.id;impl_->saw_node=true;float intensity=n.intensity;nv.push_back({brain_x+n.x,brain_y+n.y,.25f+.45f*intensity,.48f+.4f*intensity,.62f+.35f*intensity,1.f,n.radius*2.2f,born});}impl_->bind_vertices(impl_->edge_vbo);impl_->BufferData(GL_ARRAY_BUFFER,ev.size()*sizeof(Impl::Vertex),ev.data(),GL_DYNAMIC_DRAW);impl_->edge_vertices=GLsizei(ev.size());impl_->bind_vertices(impl_->node_vbo);impl_->BufferData(GL_ARRAY_BUFFER,nv.size()*sizeof(Impl::Vertex),nv.data(),GL_DYNAMIC_DRAW);impl_->node_vertices=GLsizei(nv.size());}
        auto const&graph=impl_->cached_graph;glDisable(GL_SCISSOR_TEST);glEnable(GL_BLEND);glEnable(GL_PROGRAM_POINT_SIZE);glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);impl_->UseProgram(impl_->program);impl_->Uniform2f(impl_->screen_uniform,float(width),float(height));impl_->Uniform1f(impl_->time_uniform,float(SDL_GetTicks())/1000.f);impl_->Uniform1i(impl_->points_uniform,0);impl_->bind_vertices(impl_->edge_vbo);glDrawArrays(GL_LINES,0,impl_->edge_vertices);impl_->Uniform1i(impl_->points_uniform,1);impl_->bind_vertices(impl_->node_vbo);glDrawArrays(GL_POINTS,0,impl_->node_vertices);impl_->UseProgram(0);glDisable(GL_PROGRAM_POINT_SIZE);glDisable(GL_BLEND);glEnable(GL_SCISSOR_TEST);
        int sy=brain_y+brain_h+28;int tx=brain_x+12;std::ostringstream wt;wt<<std::fixed<<std::setprecision(3)<<snapshot.world_time;
        text(brain_x+10,brain_y+10,"BRAIN",2,.55f,.74f,.86f);text(tx,sy,"STATUS",2,.50f,.68f,.78f);sy+=28;
        text(tx,sy,"WORLD TIME: "+wt.str(),1,.66f,.74f,.78f);sy+=15;text(tx,sy,"EVENT: "+std::to_string(snapshot.event_sequence),1,.66f,.74f,.78f);sy+=15;
        text(tx,sy,"TICK: "+std::to_string(brain->cognitive_tick),1,.66f,.74f,.78f);sy+=15;text(tx,sy,"GEN: "+std::to_string(brain->cognition_generation),1,.66f,.74f,.78f);sy+=15;
        text(tx,sy,"COGNITS: "+std::to_string(graph.nodes.size())+" / "+std::to_string(brain->total_cognits),1,.66f,.74f,.78f);sy+=15;text(tx,sy,"RELATIONS: "+std::to_string(graph.edges.size())+" / "+std::to_string(brain->total_relations),1,.66f,.74f,.78f);sy+=15;
        text(tx,sy,"ACTIVE: "+std::to_string(brain->active_cognits),1,.66f,.74f,.78f);
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
std::uint64_t NativeObserver::brain_snapshot_rebuilds() const noexcept { return brain_rebuilds_; }
RenderSnapshot NativeObserver::latest_snapshot() const { return source_ ? source_->latest() : RenderSnapshot{}; }
BrainSnapshot NativeObserver::latest_brain_snapshot() const { auto value=brain_?brain_->latest():nullptr;return value?*value:BrainSnapshot{}; }
DialogueSnapshot NativeObserver::latest_dialogue_snapshot() const { auto value=dialogue_?dialogue_->latest():nullptr;return value?*value:DialogueSnapshot{}; }

} // namespace se
