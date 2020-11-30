# PODIO benchmarking

# Requirements

## python for analyzing
Python3

- `uproot4`
- `awkward1`
- `pandas` (only used internally for easier handling of some row-wise summary
  statistics)
- `numpy`

``` sh
pip install uproot4 awkward1
```


## podio
[podio](https://github.com/AIDASoft/podio) with the changes from
[podio#155](https://github.com/AIDASoft/podio/pull/155) merged in order to have
the `TimedWriter` and `TimedReader` available.

<!-- ## EDM4HEP -->
<!-- [EDM4HEP](https://github.com/key4hep/EDM4HEP) installed. -->

## k4SimDelphes
[`k4SimDelphes`](https://github.com/key4hep/k4SimDelphes) has to be built from
source, because some changes are necessary to instrument the Delphes readers to
actually use the `TimedWriter` to produce the benchmark output for the writing
case.

### Necessary changes
To instrument the readers from `k4SimDelphes` the `podioWriter` has to be a
`TimedWriter`. I.e.

```cpp
WriterT podioWriter(outputFile, &eventStore);
```
has to be replaced with

``` cpp
podio::benchmark::BenchmarkRecorder benchmarkRecorder(outputFile + ".bench.root");
podio::TimedWriter<WriterT> podioWriter(benchmarkRecorder, outputFile, &eventStore);
```

Where here the output file of the benchmark recorder is simply reusing the
original ouput file name. After compilation all the available standalone readers
will produce the edm4hep output and an additional root file with the benchmark
output.
