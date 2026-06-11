cmake_minimum_required(VERSION 3.16)
project(simukit C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

add_compile_options(-Wall -Wextra -Wpedantic -O2)

set(SIMUKIT_LIB_SOURCES
    src/util.c
    src/cp2k_out.c
    src/cp2k_run.c
    src/sdc.c
)

add_library(simukit STATIC ${SIMUKIT_LIB_SOURCES})
target_include_directories(simukit PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)

add_executable(simukit-sdc src/main_sdc.c)
target_link_libraries(simukit-sdc PRIVATE simukit m)

add_executable(simukit-run src/main_run.c)
target_link_libraries(simukit-run PRIVATE simukit)

install(TARGETS simukit simukit-sdc simukit-run
        RUNTIME DESTINATION bin
        ARCHIVE DESTINATION lib)
install(DIRECTORY include/simukit DESTINATION include)
