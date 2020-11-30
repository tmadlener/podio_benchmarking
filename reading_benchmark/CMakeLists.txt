add_executable(read_benchmark read_benchmark.cpp)
target_link_libraries(read_benchmark EDM4HEP::edm4hep podio::podioRootIO podio::podioSioIO ROOT::Tree)
