cmake_minimum_required(VERSION 3.5)
project (Histogram VERSION 1.0.0 LANGUAGES CXX )

#=== SETTING VARIABLES ===#
# Compiling flags
set( GCC_COMPILE_FLAGS "-Wall -g" )
set( CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} ${GCC_COMPILE_FLAGS}" )

#=== main  target ===

file(GLOB SOURCE src/histogram.cpp)
add_executable(histogram ${SOURCE})

target_link_libraries(histogram)

#define C++17 as the standard.
set_property(TARGET histogram PROPERTY CXX_STANDARD 17)