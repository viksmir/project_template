cmake_minimum_required(VERSION 3.12)



project("projTemplate")



###########################################################################################################################
###  SHARED PARAMETERS ####################################################################################################
###########################################################################################################################




###########################################################################################################################
###  TARGET PROCEDURES  ###################################################################################################
###########################################################################################################################



# Define a code-formatting target
file(GLOB_RECURSE HEADERS            ${CMAKE_SOURCE_DIR}/src/*.hpp)
file(GLOB_RECURSE SOURCES            ${CMAKE_SOURCE_DIR}/src/*.cpp)
file(GLOB_RECURSE EXE_HEADERS        ${CMAKE_SOURCE_DIR}/projTemplate_EXE/*.hpp)
file(GLOB_RECURSE EXE_SOURCES        ${CMAKE_SOURCE_DIR}/projTemplate_EXE/*.cpp)
file(GLOB_RECURSE DLL_HEADERS        ${CMAKE_SOURCE_DIR}/projTemplate_DLL/*.hpp)
file(GLOB_RECURSE DLL_SOURCES        ${CMAKE_SOURCE_DIR}/projTemplate_DLL/*.cpp)
file(GLOB_RECURSE TEST_HEADERS       ${CMAKE_SOURCE_DIR}/projTemplate_TEST/*.hpp)
file(GLOB_RECURSE TEST_SOURCES       ${CMAKE_SOURCE_DIR}/projTemplate_TEST/*.cpp)
add_custom_target(
    clang_format
    COMMAND clang-format
        -style=file:${CMAKE_SOURCE_DIR}/.clang-format
        -i
        ${HEADERS}
        ${SOURCES}    
        ${EXE_HEADERS} 
        ${EXE_SOURCES} 
        ${DLL_HEADERS} 
        ${DLL_SOURCES} 
        ${TEST_HEADERS}
        ${TEST_SOURCES}
    )



# Define a custom target to build all subprojects
add_subdirectory("projTemplate_EXE")
add_subdirectory("projTemplate_DLL")
add_subdirectory("projTemplate_TEST")
add_custom_target(
    build_all
    DEPENDS projTemplate_EXE
    DEPENDS projTemplate_DLL
    DEPENDS projTemplate_TEST
    )



# Add custom post-build command to the 'build-all' target
set(BUILD_OUTPUT_DIR    ${CMAKE_SOURCE_DIR}/out/bin/${CMAKE_SYSTEM_NAME}/${CMAKE_SYSTEM_PROCESSOR}/${CMAKE_BUILD_TYPE} CACHE STRING "Final output directory of the binaries")
add_custom_command(
    TARGET build_all
    POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E env python ${CMAKE_SOURCE_DIR}/tools/post_build_tasks.py -o=${BUILD_OUTPUT_DIR} -b=${CMAKE_CURRENT_BINARY_DIR} -c -p=projTemplate_EXE,projTemplate_DLL -t=projTemplate_TEST
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    )
add_custom_target(run_all ALL DEPENDS build_all)