cmake_minimum_required(VERSION 3.10)

# Project name
project(demo)

# Use C11 standard
set(CMAKE_C_STANDARD 11)

# Build type: Debug (includes -g flag for gdb)
set(CMAKE_BUILD_TYPE Debug)

# Create executable called "demo" from demo.c
add_executable(demo demo.c)