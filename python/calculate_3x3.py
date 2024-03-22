import sys
sys.path.append(
    '/home/kjetil/projects/opm-clean/sources/opm/build/opm-common/python'
)

from calculate_qoi import calculate_qois
basepath = '/extradata/kjetil/pavel_ensemble/data_3x3_from_karolina/sleipner_ensemble_3x3/Coarse_Sleipner_ensemble'

calculate_qois(basepath, 'coarse_3x3')