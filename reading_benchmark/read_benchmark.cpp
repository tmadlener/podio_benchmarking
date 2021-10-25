#include "edm4hep/MCParticleCollection.h"
#include "edm4hep/ReconstructedParticleCollection.h"
#include "edm4hep/MCRecoParticleAssociationCollection.h"
#include "edm4hep/TrackCollection.h"
#include "edm4hep/ClusterCollection.h"
#include "edm4hep/ParticleIDCollection.h"

#include "podio/TimedReader.h"
#include "podio/ROOTReader.h"
#include "podio/SIOReader.h"
#include "podio/BenchmarkRecorder.h"

#include <iostream>
#include <memory>
#include <string_view>
#include <vector>
#include <string>

std::string_view getFileEnding(const char* filename) {
  const auto festart = std::string_view(filename).rfind('.');
  return std::string_view(filename).substr(festart);
}

/**
 * Get the correct timed input reader for the given file-ending of the input
 * file
 */
std::unique_ptr<podio::IReader> getReader(const char* filename, podio::benchmark::BenchmarkRecorder& recorder) {
  if (getFileEnding(filename) == ".root") {
    return std::make_unique<podio::TimedReader<podio::ROOTReader>>(recorder);
  } else {
    return std::make_unique<podio::TimedReader<podio::SIOReader>>(recorder);
  }
}

// List of small functions touching on a given element to simulate "real world usage"
double doSomething(edm4hep::ConstMCParticle part) {
  double parentEnergy = 0;
  for (const auto& parent : part.getParents()) {
    parentEnergy += parent.getEnergy();
  }
  return parentEnergy;
}

double doSomething(edm4hep::ConstReconstructedParticle part) {
  double constituentEnergy = 0;
  for (const auto cluster : part.getParticles()) {
    constituentEnergy += cluster.getEnergy();
  }
 
  return constituentEnergy;
}

double doSomething(edm4hep::ConstTrack track) {
  return track.getTrackStates(0).covMatrix[0];
}

double doSomething(edm4hep::ConstCluster cluster) {
  return cluster.getEnergy();
}

double doSomething(edm4hep::ConstMCRecoParticleAssociation assoc) {
  return assoc.getRec().getEnergy() - assoc.getSim().getEnergy();
}

double doSomething(edm4hep::ConstParticleID part) {
  return part.getLikelihood();
}

/**
 * Loop over all elements and run the doSomething function on each element in
 * order to simulate some dummy usage. The benchmarked part is actually in the
 * EventStore::get call, but at least touching each element of the collection
 * potentially leads to a "more realistic" memory access pattern for the next
 * collection, which might not be as easily cached this way.
 */
template<typename CollectionT>
void touchCollection(const std::string& name,
                     podio::EventStore& store,
                     podio::benchmark::BenchmarkRecorderTree& sizeRecorder) {
  const auto& collection = store.get<CollectionT>(name);
  if (!collection.isValid()) {
    std::cerr << "ERROR: collection " << name << " not valid" << std::endl;
  }

  // have t slightly cheat here to be able to easily use the
  // BenchmarkRecorderTree since it only accepts std::chrono::duration
  sizeRecorder.recordTime(name + "_size", std::chrono::nanoseconds(collection.size()));

  // If we have a jet collection, we do some more data collecting
  if constexpr (std::is_same_v<CollectionT, edm4hep::ReconstructedParticleCollection>) {
    if (name == "Jet") {
      size_t nTracks{0}, nClusters{0};
      for (const auto jet : collection) {
        for (const auto constituent : jet.getParticles()) {
          nTracks += constituent.getTracks().size();
          nClusters += constituent.getClusters().size();
        }
      }

      sizeRecorder.recordTime(name + "_Tracks_size", std::chrono::nanoseconds(nTracks));
      sizeRecorder.recordTime(name + "_Clusters_size", std::chrono::nanoseconds(nClusters));
    }
  }
 
  double tmp = 0;
  for (const auto elem : collection) {
    tmp += doSomething(elem);
  }
}

/**
 * "touch" all collections, to ensure that all collections that are present in
 * an event are also actually read from file, even if they are lazily read.
 */
void touchAllCollections(podio::EventStore& store,
                         const std::vector<std::string>& collectionNames,
                         podio::benchmark::BenchmarkRecorderTree& sizeRecorder) {
  // NOTE: The names and decision logic here is necessarily tailored to what is
  // done in the write benchmarks that produces these input files via
  // k4SimDelphes
  for (const auto& name : collectionNames) {
    if (name == "Particle") {
      touchCollection<edm4hep::MCParticleCollection>(name, store, sizeRecorder);
    } else if (name == "Muon" || name == "Photon" || name == "Electron") {
      touchCollection<edm4hep::ReconstructedParticleCollection>(name, store, sizeRecorder);
    } else if (name == "ReconstructedParticles" || name == "Jet" || name == "MissingET") {
      touchCollection<edm4hep::ReconstructedParticleCollection>(name, store, sizeRecorder);
    } else if (name == "EFlowTrack") {
      touchCollection<edm4hep::TrackCollection>(name, store, sizeRecorder);
    } else if (name == "EFlowPhoton" || name == "EFlowNeutralHadron") {
      touchCollection<edm4hep::ClusterCollection>(name, store, sizeRecorder);
    } else if (name == "MCRecoAssociations") {
      touchCollection<edm4hep::MCRecoParticleAssociationCollection>(name, store, sizeRecorder);
    } else if (name == "ScalarHT" || name == "ParticleIDs") {
      touchCollection<edm4hep::ParticleIDCollection>(name, store, sizeRecorder);
    } else {
      std::cerr << "ERROR: Unknown collection: \'" << name << "\'" << std::endl;
    }
  }

}


auto getSizeRecorderBranchNames(std::vector<std::string> collNames) {
  // For jets also record the number of associated Tracks and Clusters to get a
  // grip on the number of jet constituents
  if (std::find(collNames.begin(), collNames.end(), "Jet") != collNames.end()) {
    collNames.push_back("Jet_Tracks");
    collNames.push_back("Jet_Clusters");
  }

  for (auto& n : collNames) {
    n += "_size";
  }

  return collNames;
}

constexpr auto helpmessage = R"help(
Small program to touch different collections in the input_file to benchmark read performance.

Args:
    benchmark_file: File into which the benchmark results are written
    input_file:     File to use for the read benchmark. Either .root or .sio, the proper reader
                    will be instantiated automatically
    collections:    List of collection names that should be 'touched'. If none are passed, all
                    collections that are present in the input file will be touched.
)help";


int main(int argc, char* argv[]) {
  std::vector<std::string> collectionsToTouch;

  if (argc < 3) {
    std::cerr << "usage: read_benchmark benchmark_file input_file [collections]" << std::endl;

    if (argc == 2 && (argv[1] == std::string("-h") || argv[1] == std::string("--help"))) {
      std::cout << helpmessage << std::endl;
    }
    return 1;
  }

  if (argc > 3) {
    for (int i = 3; i < argc; ++i) {
      collectionsToTouch.push_back(argv[i]);
    }
  }

  const bool touchAll = collectionsToTouch.empty();

  podio::benchmark::BenchmarkRecorder benchmarkRecorder{argv[1]};
  auto reader = getReader(argv[2], benchmarkRecorder);
  reader->openFile(argv[2]);
  podio::EventStore store;
  store.setReader(reader.get());

  // NOTE: Nothing to benchmark here, since the reading of the collectionID
  // table is a call to the reader in any case and additionally it doesn't
  // happen in this step
  const auto& collectionNames = store.getCollectionIDTable()->names();

  // clean the collections to touch to not break things
  for (auto it = collectionsToTouch.begin(); it != collectionsToTouch.end();) {
    if (std::find(collectionNames.begin(), collectionNames.end(), *it) == collectionNames.end()) {
      std::cerr << "WARNING: Requesting to touch collection \'" << *it << "\' which is not present in the input file. Ignoring it" << std::endl;
      it = collectionsToTouch.erase(it);
    } else {
      ++it;
    }
  }

  // Set up another BenchmarkRecorderTree to also record the sizes of some
  // collections to see if these are correlated to some of the times
  auto& sizeRecorderTree = benchmarkRecorder.addTree("collection_sizes",
                                                     getSizeRecorderBranchNames(touchAll ? collectionNames : collectionsToTouch));

  const auto nEvents = reader->getEntries();
  for (unsigned i = 0; i < nEvents; ++i) {

    if (touchAll) {
      touchAllCollections(store, collectionNames, sizeRecorderTree);
    } else {
      touchAllCollections(store, collectionsToTouch, sizeRecorderTree);
    }

    store.clear();
    reader->endOfEvent();
    sizeRecorderTree.Fill();
  }

  reader->closeFile();
  return 0;
}
