import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.append('/home/kjetil/projects/across/ensemble_pavel/opm/opm/build/opm-common/python')
import opm
from opm.io.ecl import ESmry, EGrid,EclOutput,EclFile,ERft

base_filename = "/home/kjetil/projects/across/ensemble_pavel/mrst/mrst-bitbucket/mrst-core/output/sleipner_decks/Coarse_Sleipner_ensemble/Coarse_Sleipner_ensemble_{ensemble_number}/mpi/14/dev.5/COARSE_SLEIPNER_ENSEMBLE_{ensemble_number}.UNRST"
ensemble_numbers = list(range(1, 513))
qois = np.zeros(len(ensemble_numbers))
for ensemble_number in ensemble_numbers:
    ensemble_number_formatted = f'{ensemble_number:04d}'
    ecloutput = EclFile(base_filename.format(ensemble_number = ensemble_number_formatted))
    sgasmean = np.mean(ecloutput['PRESSURE'])
    qois[ensemble_number-1] = sgasmean
plt.hist(qois)
plt.xlabel("mean of PRESSURE across all grid cells")
plt.ylabel("Occurences")
                        
    