add_executable(read_benchmark read_benchmark.cpp)
target_link_libraries(read_benchmark EDM4HEP::edm4hep podio::podioRootIO podio::podioSioIO ROOT::Tree)

add_executable(read_benchmark_lcio read_benchmark_lcio.cpp)
target_include_directories(read_benchmark_lcio PRIVATE ${LCIO_INCLUDE_DIRS})
target_link_libraries(read_benchmark_lcio ${LCIO_LIBRARIES} podio::podio ROOT::Tree)

install(TARGETS read_benchmark read_benchmark_lcio DESTINATION bin)
