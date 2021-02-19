#!/usr/bin/env bash
set -euo pipefail

MACRO=${HOME}/work/k4SimDelphes/examples/higgs_recoil_plots.C

for f in k4simdelphes_stdhep_output.?.${1}; do
    bench_file=higgs_recoil_bench.$(echo $f | awk -F'.' '{print $2}').root
    root -q -b "${MACRO}(\"${f}\", \"${bench_file}\")"
done

rm recoil_plots.pdf
