#include "EVENT/LCEvent.h"
#include "EVENT/MCParticle.h"
#include "EVENT/ReconstructedParticle.h"
#include "UTIL/LCRelationNavigator.h"
#include "EVENT/Track.h"
#include "EVENT/Cluster.h"
#include "EVENT/LCCollection.h"
#include "IOIMPL/LCFactory.h"
#include "lcio.h"

#include "podio/BenchmarkRecorder.h"

#include <iostream>
#include <vector>
#include <string>

using ReadEventF = lcio::LCEvent*(lcio::LCReader::*)();
using OpenF = void(lcio::LCReader::*)(const std::string&);

using namespace podio::benchmark;

int main(int argc, char* argv[]) {
  if (argc < 2) {
    std::cerr << "usage: read_benchmark_lcio benchmark_file input_file" << std::endl;
    return 1;
  }

  podio::benchmark::BenchmarkRecorder benchmarkRecorder{argv[1]};
  auto& setupTree = benchmarkRecorder.addTree("setup_times",
                                              {"constructor", "open_file", "get_entries", "close_file", "destructor"});
  auto& eventTree = benchmarkRecorder.addTree("event_times",
                                              {"read_next_event"});

  // Doing this in this slightly cumbersome way, because it is quicker to write
  // than wrapping everything into the benchmarking functionality
  const auto constStart = podio::benchmark::ClockT::now();
  auto* lcReader = lcio::LCFactory::getInstance()->createLCReader();
  const auto constEnd = podio::benchmark::ClockT::now();
  setupTree.recordTime("constructor", constEnd - constStart);

  setupTree.recordTime("open_file",
                       run_void_member_timed<lcio::LCReader, OpenF, const std::string&>(*lcReader, &lcio::LCReader::open, argv[2]));
  const auto [nEvents, gevt_duration] = run_member_timed(*lcReader, &lcio::LCReader::getNumberOfEvents);
  setupTree.recordTime("get_entries", gevt_duration);

  std::cout << nEvents << std::endl;

  for (auto i = 0u; i < 17143; ++i) {
    const auto [evt, duration] = run_member_timed<lcio::LCReader, ReadEventF>(*lcReader, &lcio::LCReader::readNextEvent);
    eventTree.recordTime("read_next_event", duration);
    eventTree.Fill();

  }

  setupTree.recordTime("close_file", run_void_member_timed(*lcReader, &lcio::LCReader::close));
  const auto destStart = podio::benchmark::ClockT::now();
  delete lcReader;
  const auto destEnd = podio::benchmark::ClockT::now();
  setupTree.recordTime("destructor", destEnd - destStart);
  setupTree.Fill();

  return 0;
}
