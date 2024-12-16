# Defining the project name
project(projTemplate_TEST)



# Set shared compiler options
add_compile_options(-w -m64 -Wall -Wextra -Wpedantic -g -gcodeview --coverage -fprofile-arcs)
add_compile_options(
    $<$<COMPILE_LANGUAGE:C>:-std=c11>
    )
add_compile_options(
    $<$<COMPILE_LANGUAGE:CXX>:-std=c++20>
    )
add_link_options(-fuse-ld=lld -g -Wl,--pdb= --coverage)



# Set compiler definitions
add_compile_definitions(WIN32)



# Specify source files
file(GLOB_RECURSE LOCAL_SOURCES      ${CMAKE_CURRENT_SOURCE_DIR}/*.cpp)
file(GLOB_RECURSE SOURCES            ${CMAKE_SOURCE_DIR}/src/*.cpp)



# Specify include directories
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/src

    # Add external include directories if needed
    )



# Specified linker precompiled static libraries (.lib or .a for Windows)
link_libraries(
    # System stuffs
    ws2_32
    libgtest.a
    libgmock.a

    # Add external libraries if needed
    )



# Add source to this project's executable.
add_executable(${PROJECT_NAME} ${LOCAL_SOURCES} ${SOURCES})



# Dependency on top-level code clean-up 
add_dependencies(${PROJECT_NAME} clang_format)
