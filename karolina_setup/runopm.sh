#!/bin/bash
source /scratch/project/dd-22-20/kjetilly/sleipner_ensemble/workflow_bash/karolina_modules.sh
mpirun -np ${1} /scratch/project/dd-22-20/kjetilly/sleipner_ensemble/installdir/src/opm-sources/opm-install/bin/flow \
	--output-dir=./output \
	--linear-solver=cprw \
	--cpr-reuse-setup=4 \
	--cpr-reuse-interval=200 \
	--linear-solver-reduction=0.001 \
	--min-strict-cnv-iter=10 \
	--time-step-control-target-newton-iterations=8 \
	$2


