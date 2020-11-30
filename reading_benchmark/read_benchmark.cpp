#include "edm4hep/MCParticleCollection.h"
#include "edm4hep/ReconstructedParticleCollection.h"
#include "edm4hep/MCRecoParticleAssociationCollection.h"
#include "edm4hep/RecoParticleRefCollection.h"
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

double doSomething(edm4hep::ConstRecoParticleRef part) {
  constexpr podio::ObjectID invalidObject = {podio::ObjectID::invalid, podio::ObjectID::invalid};
  if (part.getParticle().getObjectID() == invalidObject) {
    std::cout << "Reference without particle" << std::endl;
    return -1;
  }
  return part.getParticle().getEnergy();
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
                     podio::EventStore& store) {
  const auto& collection = store.get<CollectionT>(name);
  if (!collection.isValid()) {
    std::cerr << "ERROR: collection " << name << " not valid" << std::endl;
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
                         const std::vector<std::string>& collectionNames) {
  // NOTE: The names and decision logic here is necessarily tailored to what is
  // done in the write benchmarks that produces these input files via
  // k4SimDelphes
  for (const auto& name : collectionNames) {
    if (name == "Particle") {
      touchCollection<edm4hep::MCParticleCollection>(name, store);
    } else if (name == "Muon" || name == "Photon" || name == "Electron") {
      touchCollection<edm4hep::RecoParticleRefCollection>(name, store);
    } else if (name == "ReconstructedParticles" || name == "Jet" || name == "MissingET") {
      touchCollection<edm4hep::ReconstructedParticleCollection>(name, store);
    } else if (name == "EFlowTrack") {
      touchCollection<edm4hep::TrackCollection>(name, store);
    } else if (name == "EFlowPhoton" || name == "EFlowNeutralHadron") {
      touchCollection<edm4hep::ClusterCollection>(name, store);
    } else if (name == "MCRecoAssociations") {
      touchCollection<edm4hep::MCRecoParticleAssociationCollection>(name, store);
    } else if (name == "ScalarHT" || name == "ParticleIDs") {
      touchCollection<edm4hep::ParticleIDCollection>(name, store);
    } else {
      std::cerr << "ERROR: Unknown collection: \'" << name << "\'" << std::endl;
    }
  }

}

int main(int argc, char* argv[]) {
  if (argc < 3) {
    std::cerr << "usage: read_benchmark benchmark_file input_file" << std::endl;
    return 1;
  }

  podio::benchmark::BenchmarkRecorder benchmarkRecorder{argv[1]};
  auto reader = getReader(argv[2], benchmarkRecorder);
  reader->openFile(argv[2]);
  podio::EventStore store;
  store.setReader(reader.get());

  // NOTE: Nothing to benchmark here, since the reading of the collectionID
  // table is a call to the reader in any case and additionally it doesn't
  // happen in this step
  const auto& collectionNames = store.getCollectionIDTable()->names();

  const auto nEvents = reader->getEntries();
  for (unsigned i = 0; i < nEvents; ++i) {
    touchAllCollections(store, collectionNames);

    store.clear();
    reader->endOfEvent();
  }

  reader->closeFile();
  return 0;
}
