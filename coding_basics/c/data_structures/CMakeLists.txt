cmake_minimum_required(VERSION 3.10)

# Project name
project(data_structures)

# Use C11 standard
set(CMAKE_C_STANDARD 11)

# Build type: Debug
set(CMAKE_BUILD_TYPE Debug)

# Create executable
add_executable(tc_arrays ds_arrays.c)
add_executable(tc_linkedlist ds_linkedlist.c)
add_executable(tc_stacks ds_stacks.c)
add_executable(tc_queue ds_queue.c)
add_executable(tc_tree ds_tree.c)