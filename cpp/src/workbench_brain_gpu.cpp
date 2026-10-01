#include "se/workbench_brain_gpu.hpp"
#include <SDL3/SDL.h>
#include <SDL3/SDL_opengl.h>
#include <imgui.h>
#include <stdexcept>
#include <vector>
namespace se {
class WorkbenchBrainGPU::Impl {
public:
  struct Vertex {
    float x, y, intensity, radius, type, composite;
  };
  GLuint program{}, vao{}, edges{}, nodes{};
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
  PFNGLDELETEBUFFERSPROC delete_buffers;
  PFNGLCREATESHADERPROC create_shader;
  PFNGLSHADERSOURCEPROC source;
  PFNGLCOMPILESHADERPROC compile;
  PFNGLGETSHADERIVPROC shader_info;
  PFNGLCREATEPROGRAMPROC create_program;
  PFNGLATTACHSHADERPROC attach;
  PFNGLLINKPROGRAMPROC link;
  PFNGLGETPROGRAMIVPROC program_info;
  PFNGLDELETESHADERPROC delete_shader;
  PFNGLDELETEPROGRAMPROC delete_program;
  PFNGLUSEPROGRAMPROC use;
  PFNGLGETUNIFORMLOCATIONPROC location;
  PFNGLUNIFORM2FPROC uniform2;
  PFNGLUNIFORM4FPROC uniform4;
  PFNGLUNIFORM1IPROC uniform1;
  PFNGLENABLEVERTEXATTRIBARRAYPROC enable;
  PFNGLVERTEXATTRIBPOINTERPROC attribute;
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
    GL(delete_buffers, "glDeleteBuffers");
    GL(create_shader, "glCreateShader");
    GL(source, "glShaderSource");
    GL(compile, "glCompileShader");
    GL(shader_info, "glGetShaderiv");
    GL(create_program, "glCreateProgram");
    GL(attach, "glAttachShader");
    GL(link, "glLinkProgram");
    GL(program_info, "glGetProgramiv");
    GL(delete_shader, "glDeleteShader");
    GL(delete_program, "glDeleteProgram");
    GL(use, "glUseProgram");
    GL(location, "glGetUniformLocation");
    GL(uniform2, "glUniform2f");
    GL(uniform4, "glUniform4f");
    GL(uniform1, "glUniform1i");
    GL(enable, "glEnableVertexAttribArray");
    GL(attribute, "glVertexAttribPointer");
#undef GL
    const char *vs =
        "#version 330 core\nlayout(location=0)in vec2 p;layout(location=1)in "
        "vec4 v;uniform vec2 screen;uniform vec4 pane;uniform vec4 camera;out "
        "vec4 state;void main(){vec2 "
        "q=pane.xy+pane.zw*.5+(p-pane.zw*.5)*camera.x+camera.yz;gl_Position="
        "vec4(q.x/screen.x*2-1,1-q.y/"
        "screen.y*2,0,1);gl_PointSize=v.y*2*camera.w;state=v;}";
    const char *fs =
        "#version 330 core\nin vec4 state;uniform int points;uniform int "
        "filter;out vec4 color;void "
        "main(){if(points==1){if(state.w<.5&&length(gl_PointCoord-vec2(.5))>.5)"
        "discard;color=vec4(.20+state.x*.29,.38+state.x*.45,.53+state.x*.46,1);"
        "}else{if((filter==1&&state.x<.4)||(filter==2&&int(state.z)!=5)||("
        "filter==3&&int(state.z)!=2))discard;vec3 "
        "c=int(state.z)==5?vec3(.72,.59,.36):vec3(.34,.56,.67);color=vec4(c,."
        "07+state.x*.43);}}";
    auto shader = [&](GLenum kind, const char *text) {
      auto id = create_shader(kind);
      source(id, 1, &text, nullptr);
      compile(id);
      GLint valid;
      shader_info(id, GL_COMPILE_STATUS, &valid);
      if (!valid) {
        delete_shader(id);
        throw std::runtime_error("Brain shader compilation failed");
      }
      return id;
    };
    auto v = shader(GL_VERTEX_SHADER, vs), f = shader(GL_FRAGMENT_SHADER, fs);
    program = create_program();
    attach(program, v);
    attach(program, f);
    link(program);
    delete_shader(v);
    delete_shader(f);
    GLint valid;
    program_info(program, GL_LINK_STATUS, &valid);
    if (!valid)
      throw std::runtime_error("Brain shader link failed");
    gen_va(1, &vao);
    gen(1, &edges);
    gen(1, &nodes);
  }
  ~Impl() {
    delete_buffers(1, &edges);
    delete_buffers(1, &nodes);
    delete_va(1, &vao);
    delete_program(program);
  }
  void vertices(GLuint buffer) {
    bind_va(vao);
    bind(GL_ARRAY_BUFFER, buffer);
    enable(0);
    attribute(0, 2, GL_FLOAT, GL_FALSE, sizeof(Vertex), nullptr);
    enable(1);
    attribute(1, 4, GL_FLOAT, GL_FALSE, sizeof(Vertex),
              reinterpret_cast<void *>(2 * sizeof(float)));
  }
  void render() {
    auto &io = ImGui::GetIO();
    auto scale = io.DisplayFramebufferScale;
    glScissor(int(origin.x * scale.x),
              int((io.DisplaySize.y - origin.y - size.y) * scale.y),
              int(size.x * scale.x), int(size.y * scale.y));
    glEnable(GL_SCISSOR_TEST);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glEnable(GL_PROGRAM_POINT_SIZE);
    use(program);
    uniform2(location(program, "screen"), io.DisplaySize.x, io.DisplaySize.y);
    uniform4(location(program, "pane"), origin.x, origin.y, size.x, size.y);
    uniform4(location(program, "camera"), zoom, pan_x, pan_y, scale.x);
    uniform1(location(program, "filter"), filter);
    uniform1(location(program, "points"), 0);
    vertices(edges);
    glDrawArrays(GL_LINES, 0, edge_count);
    uniform1(location(program, "points"), 1);
    vertices(nodes);
    glDrawArrays(GL_POINTS, 0, node_count);
    glDisable(GL_PROGRAM_POINT_SIZE);
  }
};
WorkbenchBrainGPU::WorkbenchBrainGPU() : impl_(std::make_unique<Impl>()) {}
WorkbenchBrainGPU::~WorkbenchBrainGPU() = default;
void WorkbenchBrainGPU::upload(const BrainDrawData &graph) {
  std::vector<Impl::Vertex> edges, nodes;
  edges.reserve(graph.edges.size() * 2);
  nodes.reserve(graph.nodes.size());
  for (auto const &e : graph.edges) {
    edges.push_back({e.x1, e.y1, e.intensity, 1, float(e.type), 0});
    edges.push_back({e.x2, e.y2, e.intensity, 1, float(e.type), 0});
  }
  for (auto const &n : graph.nodes)
    nodes.push_back({n.x, n.y, n.intensity, n.radius, 0, float(n.composite)});
  impl_->vertices(impl_->edges);
  impl_->data(GL_ARRAY_BUFFER, edges.size() * sizeof(Impl::Vertex),
              edges.data(), GL_DYNAMIC_DRAW);
  impl_->edge_count = GLsizei(edges.size());
  impl_->vertices(impl_->nodes);
  impl_->data(GL_ARRAY_BUFFER, nodes.size() * sizeof(Impl::Vertex),
              nodes.data(), GL_DYNAMIC_DRAW);
  impl_->node_count = GLsizei(nodes.size());
}
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
