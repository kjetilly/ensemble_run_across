#!/bin/bash
PYTHONPATH=$PYTHONPATH:/home/kjetil/opm/opm/build/opm-common/python python python/plot_timeseries.py all_data
PYTHONPATH=$PYTHONPATH:/home/kjetil/opm/opm/build/opm-common/python python python/plot_timeseries_convergence.py all_data
PYTHONPATH=$PYTHONPATH:/home/kjetil/opm/opm/build/opm-common/python python python/convergence_sobol_sensitivity.py all_data
