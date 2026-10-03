#ifdef NDEBUG
#undef NDEBUG
#endif
#include "se/workbench_brain_gpu.hpp"
#include <SDL3/SDL.h>
#include <SDL3/SDL_opengl.h>
#include <imgui.h>
#include <cassert>
#include <cmath>
#include <iostream>
int main(){
  assert(SDL_Init(SDL_INIT_VIDEO));
  SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION,3);SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION,3);
  SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK,SDL_GL_CONTEXT_PROFILE_CORE);
  auto*w=SDL_CreateWindow("GPU presentation contract",640,480,SDL_WINDOW_OPENGL|SDL_WINDOW_HIDDEN);
  assert(w);auto context=SDL_GL_CreateContext(w);assert(context);
  ImGui::CreateContext();ImGui::GetIO().DisplaySize={640,480};ImGui::GetIO().DisplayFramebufferScale={1,1};
  ImGui::GetIO().IniFilename=nullptr;ImGui::GetIO().Fonts->Build();
  {
    se::WorkbenchBrainGPU renderer;
    se::BrainSnapshot s;s.nodes={{0,.7,.3,.8,false,true,1},{1,.9,.3,.8,false,true,1}};
    s.edges={{0,1,2,.8,.8,.8}};
    renderer.upload(s,128,512);auto initial=renderer.telemetry();
    renderer.upload(s,128,512);assert(renderer.telemetry().uploaded_bytes==initial.uploaded_bytes);
    s.nodes[1].activity=.2;renderer.upload(s,128,512);assert(renderer.telemetry().uploaded_bytes>initial.uploaded_bytes);
    for(auto size:{ImVec2{640,480},ImVec2{320,240}}){
      ImGui::GetIO().DisplaySize=size;
      ImGui::NewFrame();ImGui::Begin("test");
      renderer.enqueue(ImGui::GetWindowDrawList(),{0,0},size,1,0,0,0);
      for(auto id:{0u,1u}){
        auto hash=id*2654435761u+1013904223u;float angle=float(hash%10000)*.0006283185f,ring=.38f+.58f*float((hash>>16)%1000)/999.f;
        float x=size.x*.5f+std::cos(angle)*std::max(8.f,size.x*.39f)*ring;
        float y=size.y*.5f+std::sin(angle)*std::max(8.f,size.y*.38f)*ring;
        assert(renderer.pick(x,y)==id);
      }
      assert(renderer.pick(1,1)==UINT32_MAX);
      ImGui::End();ImGui::EndFrame();
    }
    assert(renderer.telemetry().picks==6);
  }
  ImGui::DestroyContext();SDL_GL_DestroyContext(context);SDL_DestroyWindow(w);SDL_Quit();
  std::cout<<"GPU ID layout/picking/resize/delta-upload exact PASS\n";
}
