#!/usr/bin/env bash
set -euo pipefail

N_RUNS=10

# FCC Z decay cases
for CASE in tautau bbbar; do
    outdir=chep_final_ee_Z_${CASE}
    pythia_cmd=ee_Z_${CASE}/ee_Z_${CASE}.cmd

    rm -r ${outdir}
 
    python run_benchmarks.py pythia --keep-outputs \
        --nruns ${N_RUNS} \
        --outdir ${outdir} \
        delphes_card_IDEA.tcl \
        edm4hep_output_config.tcl \
        ${pythia_cmd}
done

rm -r chep_final_Higgs_recoil

python run_benchmarks.py stdhep --keep-outputs \
    --nruns ${N_RUNS} \
    --outdir chep_final_Higgs_recoil \
    Higgs_recoil_at_ILD/delphes_card_ILD.tcl \
    edm4hep_output_config.tcl \
    Higgs_recoil_at_ILD/E250-TDR_ws.Pe2e2h.Gwhizard-1_95.eL.pR.I106479.001.stdhep

python vchep_2021/make_plots.py
