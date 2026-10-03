cmake_minimum_required(VERSION 3.20)
project(synthetic_entity_cpp VERSION 0.9.3 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
option(SE_BUILD_OBSERVER "Build the optional native SDL3/OpenGL observer" OFF)
option(SE_ENABLE_CUDA "Build optional host numeric CUDA kernels" OFF)
add_library(se_engine src/world.cpp src/event_scheduler.cpp src/relation_store.cpp src/cognitive_graph.cpp src/activity_wave.cpp src/native_brain_engine.cpp src/native_brain_bridge.cpp src/neurodynamic_substrate.cpp src/neurodynamic_bridge.cpp)
target_include_directories(se_engine PUBLIC include)
target_sources(se_engine PRIVATE src/compute_runtime.cpp)
find_package(Threads REQUIRED)
target_link_libraries(se_engine PUBLIC Threads::Threads)
if(SE_ENABLE_CUDA)
  enable_language(CUDA)
  if(NOT CMAKE_CUDA_ARCHITECTURES)
    set(CMAKE_CUDA_ARCHITECTURES native)
  endif()
  find_package(CUDAToolkit REQUIRED)
  target_sources(se_engine PRIVATE src/compute_cuda.cu)
  target_compile_definitions(se_engine PRIVATE SE_WITH_CUDA=1)
  target_link_libraries(se_engine PUBLIC CUDA::cudart)
  set_target_properties(se_engine PROPERTIES CUDA_STANDARD 20 CUDA_STANDARD_REQUIRED ON CUDA_ARCHITECTURES "${CMAKE_CUDA_ARCHITECTURES}")
  target_compile_options(se_engine PRIVATE $<$<COMPILE_LANGUAGE:CUDA>:--fmad=false>)
endif()
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
execute_process(COMMAND ${Python_EXECUTABLE} -m pybind11 --cmakedir OUTPUT_VARIABLE PYBIND11_CMAKE_DIR OUTPUT_STRIP_TRAILING_WHITESPACE)
list(APPEND CMAKE_PREFIX_PATH ${PYBIND11_CMAKE_DIR})
find_package(pybind11 CONFIG REQUIRED)
pybind11_add_module(_native_brain src/bindings.cpp src/bindings_scheduler.cpp src/bindings_workbench.cpp)
target_link_libraries(_native_brain PRIVATE se_engine)
set(SE_NATIVE_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/../consciousness" CACHE PATH "Native module deployment directory")
set_target_properties(_native_brain PROPERTIES RUNTIME_OUTPUT_DIRECTORY_RELEASE ${SE_NATIVE_OUTPUT_DIRECTORY} LIBRARY_OUTPUT_DIRECTORY_RELEASE ${SE_NATIVE_OUTPUT_DIRECTORY})
add_executable(se_equivalence tests/equivalence.cpp)
target_link_libraries(se_equivalence PRIVATE se_engine)
enable_testing()
add_executable(se_compute_tests tests/compute.cpp)
target_link_libraries(se_compute_tests PRIVATE se_engine)
add_test(NAME se_compute_tests COMMAND se_compute_tests)
add_executable(se_compute_benchmark tests/compute_benchmark.cpp)
target_link_libraries(se_compute_benchmark PRIVATE se_engine)
add_executable(se_planner_benchmark tests/planner_benchmark.cpp)
target_link_libraries(se_planner_benchmark PRIVATE se_engine)
add_test(NAME se_equivalence COMMAND se_equivalence ${CMAKE_CURRENT_SOURCE_DIR}/fixtures/oracle_v051.txt)
add_executable(se_benchmark tests/benchmark.cpp)
target_link_libraries(se_benchmark PRIVATE se_engine)
if(WIN32)
  target_link_libraries(se_benchmark PRIVATE psapi)
endif()
if(SE_BUILD_OBSERVER)
  include(FetchContent)
  FetchContent_Declare(SDL3
    GIT_REPOSITORY https://github.com/libsdl-org/SDL.git
    GIT_TAG release-3.2.8
    GIT_SHALLOW TRUE)
  FetchContent_MakeAvailable(SDL3)
  FetchContent_Declare(imgui
    GIT_REPOSITORY https://github.com/ocornut/imgui.git
    GIT_TAG v1.91.9b
    GIT_SHALLOW TRUE)
  FetchContent_MakeAvailable(imgui)
  find_package(OpenGL REQUIRED)
  add_library(se_imgui STATIC ${imgui_SOURCE_DIR}/imgui.cpp ${imgui_SOURCE_DIR}/imgui_draw.cpp
    ${imgui_SOURCE_DIR}/imgui_tables.cpp ${imgui_SOURCE_DIR}/imgui_widgets.cpp
    ${imgui_SOURCE_DIR}/backends/imgui_impl_sdl3.cpp ${imgui_SOURCE_DIR}/backends/imgui_impl_opengl3.cpp)
  target_include_directories(se_imgui PUBLIC ${imgui_SOURCE_DIR} ${imgui_SOURCE_DIR}/backends)
  target_link_libraries(se_imgui PUBLIC SDL3::SDL3 OpenGL::GL)
  add_library(se_observer src/observer.cpp src/workbench_ui.cpp src/workbench_settings_ui.cpp src/workbench_style.cpp
    src/workbench_world_view.cpp src/workbench_brain_view.cpp src/workbench_brain_gpu.cpp src/workbench_status_view.cpp src/workbench_dialogue_view.cpp)
  target_include_directories(se_observer PUBLIC include)
  target_link_libraries(se_observer PUBLIC se_imgui)
  target_compile_definitions(se_observer PRIVATE SE_WORKBENCH_FONT="${imgui_SOURCE_DIR}/misc/fonts/Roboto-Medium.ttf")
  target_link_libraries(_native_brain PRIVATE se_observer)
  target_compile_definitions(_native_brain PRIVATE SE_WITH_OBSERVER=1)
  add_custom_command(TARGET _native_brain POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different $<TARGET_FILE:SDL3::SDL3> $<TARGET_FILE_DIR:_native_brain>)
  foreach(font_target _native_brain)
    add_custom_command(TARGET ${font_target} POST_BUILD
      COMMAND ${CMAKE_COMMAND} -E make_directory $<TARGET_FILE_DIR:${font_target}>/assets
      COMMAND ${CMAKE_COMMAND} -E copy_if_different ${imgui_SOURCE_DIR}/misc/fonts/Roboto-Medium.ttf $<TARGET_FILE_DIR:${font_target}>/assets/Roboto-Medium.ttf)
    add_custom_command(TARGET ${font_target} POST_BUILD
      COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CURRENT_SOURCE_DIR}/assets/fonts/LICENSE-Roboto.txt $<TARGET_FILE_DIR:${font_target}>/assets/LICENSE-Roboto.txt
      COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CURRENT_SOURCE_DIR}/assets/fonts/NOTICE-Roboto.txt $<TARGET_FILE_DIR:${font_target}>/assets/NOTICE-Roboto.txt
      COMMAND ${CMAKE_COMMAND} -E copy_if_different ${imgui_SOURCE_DIR}/LICENSE.txt $<TARGET_FILE_DIR:${font_target}>/assets/LICENSE-ImGui.txt)
  endforeach()

  add_executable(se_observer_demo tests/observer_demo.cpp)
  target_link_libraries(se_observer_demo PRIVATE se_observer)
  add_custom_command(TARGET se_observer_demo POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different $<TARGET_FILE:SDL3::SDL3> $<TARGET_FILE_DIR:se_observer_demo>)
  add_custom_command(TARGET se_observer_demo POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory $<TARGET_FILE_DIR:se_observer_demo>/assets
    COMMAND ${CMAKE_COMMAND} -E copy_if_different ${imgui_SOURCE_DIR}/misc/fonts/Roboto-Medium.ttf $<TARGET_FILE_DIR:se_observer_demo>/assets/Roboto-Medium.ttf)
  add_custom_command(TARGET se_observer_demo POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CURRENT_SOURCE_DIR}/assets/fonts/LICENSE-Roboto.txt $<TARGET_FILE_DIR:se_observer_demo>/assets/LICENSE-Roboto.txt
    COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CURRENT_SOURCE_DIR}/assets/fonts/NOTICE-Roboto.txt $<TARGET_FILE_DIR:se_observer_demo>/assets/NOTICE-Roboto.txt
    COMMAND ${CMAKE_COMMAND} -E copy_if_different ${imgui_SOURCE_DIR}/LICENSE.txt $<TARGET_FILE_DIR:se_observer_demo>/assets/LICENSE-ImGui.txt)

  add_executable(se_observer_tests tests/observer.cpp)
  target_link_libraries(se_observer_tests PRIVATE se_observer se_engine)
  add_custom_command(TARGET se_observer_tests POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different $<TARGET_FILE:SDL3::SDL3> $<TARGET_FILE_DIR:se_observer_tests>)
  add_test(NAME se_observer_tests COMMAND se_observer_tests)
  add_executable(se_presentation_gpu_tests tests/presentation_gpu.cpp)
  target_link_libraries(se_presentation_gpu_tests PRIVATE se_observer)
  add_custom_command(TARGET se_presentation_gpu_tests POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different $<TARGET_FILE:SDL3::SDL3> $<TARGET_FILE_DIR:se_presentation_gpu_tests>)
  # Requires an actual GL context; run explicitly on a graphics-equipped host.
endif()
