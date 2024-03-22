#!/bin/bash
hq=/scratch/project/dd-22-20/kjetilly/sleipner_ensemble/hq/hq
opmcommand=/scratch/project/dd-22-20/kjetilly/run_3x3_sleipner/runopm.sh
CPUS=4

for datafile in /scratch/project/dd-22-20/kjetilly/sleipner_ensemble_3x3/Coarse_Sleipner_ensemble/Coarse_Sleipner_ensemble_*/COARSE_SLEIPNER_ENSEMBLE_*.DATA
do
    submission_name=$(basename $datafile)
    submission_name=${submission_name//COARSE_SLEIPNER_ENSEMBLE/}
    submission_name=${submission_name//.DATA/}
    submission_name="sample${submission_name}"
    rundir=$(dirname $datafile)
    ${hq} submit --pin taskset --cwd=${rundir} --name=${submission_name} --cpus $((2*${CPUS})) ${opmcommand} ${CPUS} $(basename $datafile)
done
