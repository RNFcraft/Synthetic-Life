#include "se/workbench_brain_gpu.hpp"
#include <SDL3/SDL.h>
#include <SDL3/SDL_opengl.h>
#include <imgui.h>
#include <stdexcept>
#include <vector>
#include <unordered_set>
#include <algorithm>
#include <cstring>
#include <chrono>
namespace se {
class WorkbenchBrainGPU::Impl {
public:
  struct Vertex {
    std::uint32_t id, pad;
    float intensity, radius, type, composite;
  };
  GLuint program{}, vao{}, edges{}, nodes{}, pick_fbo{}, pick_texture{};
  int pick_width{},pick_height{};
  bool picking{};
  GLuint queries[4]{};bool query_pending[4]{};unsigned query_cursor{};
  PFNGLGENQUERIESPROC gen_queries;PFNGLDELETEQUERIESPROC delete_queries;
  PFNGLBEGINQUERYPROC begin_query;PFNGLENDQUERYPROC end_query;
  PFNGLGETQUERYOBJECTIVPROC query_ready;PFNGLGETQUERYOBJECTUI64VPROC query_value;
  GLsizei edge_count{}, node_count{};
  ImVec2 origin, size;
  float zoom{}, pan_x{}, pan_y{};
  int filter{};
  PFNGLGENVERTEXARRAYSPROC gen_va;
  PFNGLBINDVERTEXARRAYPROC bind_va;
  PFNGLDELETEVERTEXARRAYSPROC delete_va;
  PFNGLGENBUFFERSPROC gen;
  PFNGLBINDBUFFERPROC bind;
  PFNGLBUFFERDATAPROC data;
  PFNGLBUFFERSUBDATAPROC subdata;
  std::vector<Vertex> edge_cache,node_cache;
  std::size_t edge_capacity{},node_capacity{};
  BrainGPUTelemetry telemetry;
  PFNGLDELETEBUFFERSPROC delete_buffers;
  PFNGLCREATESHADERPROC create_shader;
  PFNGLSHADERSOURCEPROC source;
  PFNGLCOMPILESHADERPROC compile;
  PFNGLGETSHADERIVPROC shader_info;
  PFNGLGETSHADERINFOLOGPROC shader_log;
  PFNGLCREATEPROGRAMPROC create_program;
  PFNGLATTACHSHADERPROC attach;
  PFNGLLINKPROGRAMPROC link;
  PFNGLGETPROGRAMIVPROC program_info;
  PFNGLGETPROGRAMINFOLOGPROC program_log;
  PFNGLDELETESHADERPROC delete_shader;
  PFNGLDELETEPROGRAMPROC delete_program;
  PFNGLUSEPROGRAMPROC use;
  PFNGLGETUNIFORMLOCATIONPROC location;
  PFNGLUNIFORM2FPROC uniform2;
  PFNGLUNIFORM4FPROC uniform4;
  PFNGLUNIFORM1IPROC uniform1;
  PFNGLENABLEVERTEXATTRIBARRAYPROC enable;
  PFNGLVERTEXATTRIBPOINTERPROC attribute;
  PFNGLVERTEXATTRIBIPOINTERPROC integer_attribute;
  PFNGLGENFRAMEBUFFERSPROC gen_framebuffers;
  PFNGLBINDFRAMEBUFFERPROC bind_framebuffer;
  PFNGLFRAMEBUFFERTEXTURE2DPROC framebuffer_texture;
  PFNGLDELETEFRAMEBUFFERSPROC delete_framebuffers;
  PFNGLCHECKFRAMEBUFFERSTATUSPROC framebuffer_status;
  template <class T> void load(T &f, const char *name) {
    f = reinterpret_cast<T>(SDL_GL_GetProcAddress(name));
    if (!f)
      throw std::runtime_error(name);
  }
  Impl() {
#define GL(member, name) load(member, name)
    GL(gen_va, "glGenVertexArrays");
    GL(bind_va, "glBindVertexArray");
    GL(delete_va, "glDeleteVertexArrays");
    GL(gen, "glGenBuffers");
    GL(bind, "glBindBuffer");
    GL(data, "glBufferData");
    GL(subdata,"glBufferSubData");
    GL(delete_buffers, "glDeleteBuffers");
    GL(create_shader, "glCreateShader");
    GL(source, "glShaderSource");
    GL(compile, "glCompileShader");
    GL(shader_info, "glGetShaderiv");
    GL(shader_log, "glGetShaderInfoLog");
    GL(create_program, "glCreateProgram");
    GL(attach, "glAttachShader");
    GL(link, "glLinkProgram");
    GL(program_info, "glGetProgramiv");
    GL(program_log, "glGetProgramInfoLog");
    GL(delete_shader, "glDeleteShader");
    GL(delete_program, "glDeleteProgram");
    GL(use, "glUseProgram");
    GL(location, "glGetUniformLocation");
    GL(uniform2, "glUniform2f");
    GL(uniform4, "glUniform4f");
    GL(uniform1, "glUniform1i");
    GL(enable, "glEnableVertexAttribArray");
    GL(attribute, "glVertexAttribPointer");
    GL(integer_attribute, "glVertexAttribIPointer");
    GL(gen_framebuffers,"glGenFramebuffers");
    GL(bind_framebuffer,"glBindFramebuffer");
    GL(framebuffer_texture,"glFramebufferTexture2D");
    GL(delete_framebuffers,"glDeleteFramebuffers");
    GL(framebuffer_status,"glCheckFramebufferStatus");
    GL(gen_queries,"glGenQueries");GL(delete_queries,"glDeleteQueries");
    GL(begin_query,"glBeginQuery");GL(end_query,"glEndQuery");
    GL(query_ready,"glGetQueryObjectiv");GL(query_value,"glGetQueryObjectui64v");
#undef GL
    const char *vs = R"GLSL(#version 330 core
layout(location=0)in uint node_id;
layout(location=1)in vec4 v;
uniform vec2 screen;uniform vec4 pane;uniform vec4 camera;
out vec4 state;flat out uint identity;
void main(){
 uint h=node_id*2654435761u+1013904223u;
 float angle=float(h%10000u)*.0006283185;
 float ring=.38+.58*float((h>>16)%1000u)/999.;
 vec2 p=pane.zw*.5+vec2(cos(angle)*max(8.,pane.z*.39),sin(angle)*max(8.,pane.w*.38))*ring;
 vec2 q=pane.xy+pane.zw*.5+(p-pane.zw*.5)*camera.x+camera.yz;
 gl_Position=vec4(q.x/screen.x*2.-1.,1.-q.y/screen.y*2.,0.,1.);
 gl_PointSize=v.y*2.*camera.w;state=v;identity=node_id;
})GLSL";
    const char *fs =
        "#version 330 core\nin vec4 state;uniform int points;uniform int "
        "edge_filter;uniform int picking;flat in uint identity;out vec4 color;void "
        "main(){if(points==1){if(state.w<.5&&length(gl_PointCoord-vec2(.5))>.5)"
        "discard;if(picking==1){uint id=identity+1u;color=vec4(float(id&255u),float((id>>8)&255u),float((id>>16)&255u),float((id>>24)&255u))/255.;}else color=vec4(.20+state.x*.29,.38+state.x*.45,.53+state.x*.46,1);"
        "}else{if((edge_filter==1&&state.x<.4)||(edge_filter==2&&int(state.z)!=5)||("
        "edge_filter==3&&int(state.z)!=2))discard;vec3 "
        "c=int(state.z)==5?vec3(.72,.59,.36):vec3(.34,.56,.67);color=vec4(c,."
        "07+state.x*.43);}}";
    auto shader = [&](GLenum kind, const char *text) {
      auto id = create_shader(kind);
      source(id, 1, &text, nullptr);
      compile(id);
      GLint valid;
      shader_info(id, GL_COMPILE_STATUS, &valid);
      if (!valid) {
        GLint length = 0;
        shader_info(id, GL_INFO_LOG_LENGTH, &length);
        std::vector<char> log(length > 0 ? length : 1, '\0');
        shader_log(id, GLsizei(log.size()), nullptr, log.data());
        delete_shader(id);
        throw std::runtime_error(std::string("Brain ") +
                                 (kind == GL_VERTEX_SHADER ? "vertex" : "fragment") +
                                 " shader compilation failed: " + log.data());
      }
      return id;
    };
    auto v = shader(GL_VERTEX_SHADER, vs);
    GLuint f;
    try {
      f = shader(GL_FRAGMENT_SHADER, fs);
    } catch (...) {
      delete_shader(v);
      throw;
    }
    program = create_program();
    attach(program, v);
    attach(program, f);
    link(program);
    delete_shader(v);
    delete_shader(f);
    GLint valid;
    program_info(program, GL_LINK_STATUS, &valid);
    if (!valid) {
      GLint length = 0;
      program_info(program, GL_INFO_LOG_LENGTH, &length);
      std::vector<char> log(length > 0 ? length : 1, '\0');
      program_log(program, GLsizei(log.size()), nullptr, log.data());
      delete_program(program);
      program = 0;
      throw std::runtime_error(std::string("Brain shader link failed: ") + log.data());
    }
    gen_queries(4,queries);
    gen_va(1, &vao);
    gen(1, &edges);
    gen(1, &nodes);
  }
  ~Impl() {
    delete_queries(4,queries);
    if(pick_fbo)delete_framebuffers(1,&pick_fbo);
    if(pick_texture)glDeleteTextures(1,&pick_texture);
    delete_buffers(1, &edges);
    delete_buffers(1, &nodes);
    delete_va(1, &vao);
    delete_program(program);
  }
  void update(GLuint buffer,const std::vector<Vertex>&next,std::vector<Vertex>&cache,std::size_t&capacity){
    auto start=std::chrono::steady_clock::now();
    bind(GL_ARRAY_BUFFER,buffer);
    if(next.size()>capacity){
      capacity=std::max(next.size(),capacity*2);
      data(GL_ARRAY_BUFFER,capacity*sizeof(Vertex),nullptr,GL_DYNAMIC_DRAW);
      cache.clear();++telemetry.buffer_rebuilds;
    }
    std::size_t i=0;
    while(i<next.size()){
      if(i<cache.size() && std::memcmp(&next[i],&cache[i],sizeof(Vertex))==0){++i;continue;}
      auto first=i++;
      while(i<next.size() && (i>=cache.size()||std::memcmp(&next[i],&cache[i],sizeof(Vertex))!=0))++i;
      subdata(GL_ARRAY_BUFFER,first*sizeof(Vertex),(i-first)*sizeof(Vertex),next.data()+first);
      telemetry.uploaded_bytes+=(i-first)*sizeof(Vertex);++telemetry.delta_updates;
    }
    cache=next;
    telemetry.upload_cpu_us=std::chrono::duration<double,std::micro>(std::chrono::steady_clock::now()-start).count();
  }
  void vertices(GLuint buffer) {
    bind_va(vao);
    bind(GL_ARRAY_BUFFER, buffer);
    enable(0);
    integer_attribute(0, 1, GL_UNSIGNED_INT, sizeof(Vertex), nullptr);
    enable(1);
    attribute(1, 4, GL_FLOAT, GL_FALSE, sizeof(Vertex),
              reinterpret_cast<void *>(2 * sizeof(float)));
  }
  void render() {
    auto slot=query_cursor++%4;bool timed=false;
    if(!picking){
      if(query_pending[slot]){GLint ready=0;query_ready(queries[slot],GL_QUERY_RESULT_AVAILABLE,&ready);
        if(ready){GLuint64 ns=0;query_value(queries[slot],GL_QUERY_RESULT,&ns);telemetry.gpu_draw_us=double(ns)/1000.;++telemetry.gpu_samples;query_pending[slot]=false;}}
      if(!query_pending[slot]){begin_query(GL_TIME_ELAPSED,queries[slot]);timed=true;}
    }
    auto &io = ImGui::GetIO();
    auto scale = io.DisplayFramebufferScale;
    glScissor(int(origin.x * scale.x),
              int((io.DisplaySize.y - origin.y - size.y) * scale.y),
              int(size.x * scale.x), int(size.y * scale.y));
    glEnable(GL_SCISSOR_TEST);
    if(picking)glDisable(GL_BLEND);else glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glEnable(GL_PROGRAM_POINT_SIZE);
    use(program);
    uniform2(location(program, "screen"), io.DisplaySize.x, io.DisplaySize.y);
    uniform4(location(program, "pane"), origin.x, origin.y, size.x, size.y);
    uniform4(location(program, "camera"), zoom, pan_x, pan_y, scale.x);
    uniform1(location(program, "edge_filter"), filter);
    uniform1(location(program, "picking"), picking?1:0);
    uniform1(location(program, "points"), 0);
    vertices(edges);
    if(!picking)glDrawArrays(GL_LINES, 0, edge_count);
    uniform1(location(program, "points"), 1);
    vertices(nodes);
    glDrawArrays(GL_POINTS, 0, node_count);
    glDisable(GL_PROGRAM_POINT_SIZE);
    if(timed){end_query(GL_TIME_ELAPSED);query_pending[slot]=true;}
  }
  std::uint32_t pick(float x,float y){
    auto&io=ImGui::GetIO();auto scale=io.DisplayFramebufferScale;
    int w=std::max(1,int(io.DisplaySize.x*scale.x)),h=std::max(1,int(io.DisplaySize.y*scale.y));
    GLint old_fbo,old_texture,old_viewport[4];glGetIntegerv(GL_FRAMEBUFFER_BINDING,&old_fbo);glGetIntegerv(GL_TEXTURE_BINDING_2D,&old_texture);glGetIntegerv(GL_VIEWPORT,old_viewport);
    bool dither=glIsEnabled(GL_DITHER);glDisable(GL_DITHER);
    if(!pick_fbo){gen_framebuffers(1,&pick_fbo);glGenTextures(1,&pick_texture);}
    bind_framebuffer(GL_FRAMEBUFFER,pick_fbo);
    if(w!=pick_width||h!=pick_height){
      glBindTexture(GL_TEXTURE_2D,pick_texture);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST);
      glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA8,w,h,0,GL_RGBA,GL_UNSIGNED_BYTE,nullptr);
      framebuffer_texture(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,pick_texture,0);pick_width=w;pick_height=h;
    }
    if(framebuffer_status(GL_FRAMEBUFFER)!=GL_FRAMEBUFFER_COMPLETE){bind_framebuffer(GL_FRAMEBUFFER,old_fbo);throw std::runtime_error("Brain picking framebuffer incomplete");}
    glViewport(0,0,w,h);glDisable(GL_SCISSOR_TEST);glClearColor(0,0,0,0);glClear(GL_COLOR_BUFFER_BIT);
    picking=true;render();picking=false;
    unsigned char pixel[4]{};glReadPixels(std::clamp(int(x*scale.x),0,w-1),std::clamp(h-1-int(y*scale.y),0,h-1),1,1,GL_RGBA,GL_UNSIGNED_BYTE,pixel);
    bind_framebuffer(GL_FRAMEBUFFER,old_fbo);glBindTexture(GL_TEXTURE_2D,old_texture);glViewport(old_viewport[0],old_viewport[1],old_viewport[2],old_viewport[3]);if(dither)glEnable(GL_DITHER);
    std::uint32_t id=std::uint32_t(pixel[0])|(std::uint32_t(pixel[1])<<8)|(std::uint32_t(pixel[2])<<16)|(std::uint32_t(pixel[3])<<24);
    return id?id-1:UINT32_MAX;
  }
};
WorkbenchBrainGPU::WorkbenchBrainGPU() : impl_(std::make_unique<Impl>()) {}
WorkbenchBrainGPU::~WorkbenchBrainGPU() = default;
void WorkbenchBrainGPU::upload(const BrainSnapshot &graph, std::size_t node_budget, std::size_t edge_budget) {
  std::vector<Impl::Vertex> edges, nodes;
  std::unordered_set<std::uint32_t> visible;
  auto count=std::min(node_budget,graph.nodes.size());
  nodes.reserve(count);
  for(std::size_t i=0;i<count;++i){const auto&n=graph.nodes[i];visible.insert(n.id);
    float active=std::clamp(float(n.activity),0.f,1.f);
    nodes.push_back({n.id,0,.18f+active*.82f,3.5f+active*3,0,float(n.composite)});
  }
  for(const auto&e:graph.edges){
    if(edges.size()/2>=edge_budget)break;
    if(!visible.contains(e.source)||!visible.contains(e.target))continue;
    auto intensity=float(std::clamp(.2*e.confidence+.8*e.activation,0.,1.));
    edges.push_back({e.source,0,intensity,1,float(e.relation_type),0});
    edges.push_back({e.target,0,intensity,1,float(e.relation_type),0});
  }
  impl_->vertices(impl_->edges);
  impl_->update(impl_->edges,edges,impl_->edge_cache,impl_->edge_capacity);
  impl_->edge_count=GLsizei(edges.size());
  impl_->vertices(impl_->nodes);
  impl_->update(impl_->nodes,nodes,impl_->node_cache,impl_->node_capacity);
  impl_->node_count=GLsizei(nodes.size());
  impl_->telemetry.buffer_bytes=(impl_->node_capacity+impl_->edge_capacity)*sizeof(Impl::Vertex);
}
BrainGPUTelemetry WorkbenchBrainGPU::telemetry() const{return impl_->telemetry;}
std::uint32_t WorkbenchBrainGPU::pick(float x,float y){++impl_->telemetry.picks;return impl_->pick(x,y);}
void WorkbenchBrainGPU::enqueue(ImDrawList *draw, const ImVec2 &origin,
                                const ImVec2 &size, float zoom, float x,
                                float y, int filter) {
  impl_->origin = origin;
  impl_->size = size;
  impl_->zoom = zoom;
  impl_->pan_x = x;
  impl_->pan_y = y;
  impl_->filter = filter;
  draw->AddCallback(
      [](const ImDrawList *, const ImDrawCmd *cmd) {
        static_cast<Impl *>(cmd->UserCallbackData)->render();
      },
      impl_.get());
  draw->AddCallback(ImDrawCallback_ResetRenderState, nullptr);
}
} // namespace se
