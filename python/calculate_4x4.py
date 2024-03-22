import sys
sys.path.append(
    '/home/kjetil/projects/opm-clean/sources/opm/build/opm-common/python'
)

from calculate_qoi import calculate_qois
basepath = '/extradata/kjetil/pavel_ensemble/data_from_karolina/to_karolina'

calculate_qois(basepath, 'coarse_4x4')