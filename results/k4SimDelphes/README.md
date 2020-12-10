# podio I/O benchmarking results using k4SimDelphes

In order to produce some output files (and simultaneously benchmark the writing
performance of the two available I/O backends of podio) `k4SimDelphes` is used
on a few physics use cases. The output files are then used to benchmark the
reading performance using the
[`read_benchmark`](../../reading_benchmark/read_benchmark.cpp) utility from this
repository.

To facilitate the benchmarking some helper scripts are present that run the
different benchmark cases several times, before the results are analyzed and an
automated report in markdown format is generated and placed in the directory of
the corresponding physics case.

## Inputs and physics cases

All cases here use standard Delphes cards, which are just copied here for
convenience. The only additional change that is made is to fix the `RandomSeed`
in order to guarantee reproducibility. The `edm4hep_output_config.tcl` is also
copied here for convenience and remains unchanged. Other physics case specific
inputs are placed in the respective directories. 

The diff between the shipped and the used delphes card are the following
``` diff
--- $DELPHES_DIR/cards/delphes_card_IDEA.tcl	2020-10-20 15:16:29.000000000 +0200
+++ delphes_card_IDEA.tcl	2020-12-02 19:08:30.892729950 +0100
@@ -11,8 +11,6 @@
 # Order of execution of various modules
 #######################################
 
+set RandomSeed 31415
+
 set ExecutionPath {
   ParticlePropagator
```

## Running `ee_Z_tautau` or the `ee_Z_bbbar` benchmark

To run the `ee_Z_tautau` or the `ee_Z_bbbar` benchmark do the following

``` sh
export CASE=ee_Z_tautau # change to ee_Z_bbbar to run it

python run_benchmarks.py pythia \
    --outdir ${CASE} \
    --nruns 10 \
    delphes_card_IDEA.tcl \
    edm4hep_output_config.tcl \
    ${CASE}/${CASE}.cmd
```

This will run each case 10 times for each of the two backends: `sio` and `root`.
It will produce separate folders with the output files as well as with the
results of the benchmarks, which still have to be analyzed. By default
`run_benchmarks.py` will remove the output files of the converter again directly
after it has run a complete set of read and write and only keep the files
containing the benchmark results. If you want to keep the output files add the
`--keep-outputs` flag to the command above. To have a look at one or more
benchmark results it is possible to use the `analyze_write.py` and
`analyze_read.py` scripts that come with this repository. A complete report can
be generated with the `make_benchmark_report.py` script and the yaml
[`report_config.yaml`](report_config.yaml) configuration.

``` sh
python ../../python/make_benchmark_report.py report_config.yaml ${CASE}
```

(assuming the `export CASE` has not changed from above)

## Running a Higgs recoil @ ILD example

For this we use a slightly adapted version of the standard ILD card, again
simply fixing the `RandomSeed`. The diff with the version shipped with Delhpes
is

``` diff
--- $DELPHES_DIR/cards/delphes_card_ILD.tcl	2020-06-02 13:41:05.000000000 +0200
+++ Higgs_recoil_at_ILD/delphes_card_ILD.tcl	2020-12-03 15:35:36.396219719 +0100
@@ -4,6 +4,8 @@
 # Order of execution of various modules
 #######################################
 
+set RandomSeed 27182
+
 set ExecutionPath {
   ParticlePropagator
```

In this case we are using a stdhep input file, which we can get via:

``` sh
wget -P Higgs_recoil_at_ILD/ http://osggridftp02.slac.stanford.edu:8080/sdf/group/lcddata/ilc/prod/ilc/mc-dbd/generated/250-TDR_ws/higgs/E250-TDR_ws.Pe2e2h.Gwhizard-1_95.eL.pR.I106479.001.stdhep
```

Running this benchmark and generating a report can be done via

``` sh
    python run_benchmarks.py stdhep \
    --outdir Higgs_recoil_at_ILD \
    --nruns 10 \
    Higgs_recoil_at_ILD/delphes_card_ILD.tcl \
    edm4hep_output_config.tcl \
    Higgs_recoil_at_ILD/E250-TDR_ws.Pe2e2h.Gwhizard-1_95.eL.pR.I106479.001.stdhep
    
python ../../python/make_benchmark_report.py report_config.yaml Higgs_recoil_at_ILD
```

### The 'root zlib compression' case
At the HSF WLCG workshop some results were presented for the benchmarks and
there we were using the same compression for `sio` and `root`. These have been
added as the *root zlib compression* case in this example.
