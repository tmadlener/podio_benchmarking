cmake_minimum_required(VERSION 3.12)

project(PODIO_BENCHMARKING)

# Always build with c++17
set(CMAKE_CXX_STANDARD 17)

find_package(podio REQUIRED HINTS $ENV{PODIO})

if(NOT SIO IN_LIST PODIO_IO_HANDLERS)
  message(FATAL_ERROR "Need podio built with the SIO backend")
endif()

find_package(ROOT REQUIRED COMPONENTS RIO Tree)
find_package(EDM4HEP)
find_package(LCIO)

add_subdirectory(reading_benchmark)
