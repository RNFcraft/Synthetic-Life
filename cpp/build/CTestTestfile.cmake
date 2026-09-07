# CMake generated Testfile for 
# Source directory: D:/projects/aiagent/synth_life/cpp
# Build directory: D:/projects/aiagent/synth_life/cpp/build
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
if(CTEST_CONFIGURATION_TYPE MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
  add_test([=[se_equivalence]=] "D:/projects/aiagent/synth_life/cpp/build/Debug/se_equivalence.exe" "D:/projects/aiagent/synth_life/cpp/fixtures/oracle_v051.txt")
  set_tests_properties([=[se_equivalence]=] PROPERTIES  _BACKTRACE_TRIPLES "D:/projects/aiagent/synth_life/cpp/CMakeLists.txt;17;add_test;D:/projects/aiagent/synth_life/cpp/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
  add_test([=[se_equivalence]=] "D:/projects/aiagent/synth_life/cpp/build/Release/se_equivalence.exe" "D:/projects/aiagent/synth_life/cpp/fixtures/oracle_v051.txt")
  set_tests_properties([=[se_equivalence]=] PROPERTIES  _BACKTRACE_TRIPLES "D:/projects/aiagent/synth_life/cpp/CMakeLists.txt;17;add_test;D:/projects/aiagent/synth_life/cpp/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Mm][Ii][Nn][Ss][Ii][Zz][Ee][Rr][Ee][Ll])$")
  add_test([=[se_equivalence]=] "D:/projects/aiagent/synth_life/cpp/build/MinSizeRel/se_equivalence.exe" "D:/projects/aiagent/synth_life/cpp/fixtures/oracle_v051.txt")
  set_tests_properties([=[se_equivalence]=] PROPERTIES  _BACKTRACE_TRIPLES "D:/projects/aiagent/synth_life/cpp/CMakeLists.txt;17;add_test;D:/projects/aiagent/synth_life/cpp/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Rr][Ee][Ll][Ww][Ii][Tt][Hh][Dd][Ee][Bb][Ii][Nn][Ff][Oo])$")
  add_test([=[se_equivalence]=] "D:/projects/aiagent/synth_life/cpp/build/RelWithDebInfo/se_equivalence.exe" "D:/projects/aiagent/synth_life/cpp/fixtures/oracle_v051.txt")
  set_tests_properties([=[se_equivalence]=] PROPERTIES  _BACKTRACE_TRIPLES "D:/projects/aiagent/synth_life/cpp/CMakeLists.txt;17;add_test;D:/projects/aiagent/synth_life/cpp/CMakeLists.txt;0;")
else()
  add_test([=[se_equivalence]=] NOT_AVAILABLE)
endif()
