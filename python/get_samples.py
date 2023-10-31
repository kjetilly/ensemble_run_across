import sys
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import csv

sys.path.append('/home/kjetil/projects/sintef/across/ensemble_pavel/opm/opm/build/opm-common/python')
base_filename_grid = "/mnt/data_internal/kjetil/pavel/output/output/sleipner_decks/Coarse_Sleipner_ensemble/Coarse_Sleipner_ensemble_{ensemble_number:04d}/output/COARSE_SLEIPNER_ENSEMBLE_{ensemble_number:04d}.EGRID"

import opm
from opm.io.ecl import ESmry, EGrid,EclOutput,EclFile,ERft

base_filename = "/mnt/data_internal/kjetil/pavel/output/output/sleipner_decks/Coarse_Sleipner_ensemble/Coarse_Sleipner_ensemble_{ensemble_number:04d}/output/COARSE_SLEIPNER_ENSEMBLE_{ensemble_number:04d}.UNRST"
ensemble_numbers = list(range(1, 513))


qoi_functions = {
    "moveable_co2" : lambda ecl, egrid: np.mean(egrid.cellvolumes() * ecl['SGAS'] * (ecl['SGAS']>0.1)),
    "pressure": lambda ecl, egrid: np.mean(egrid.cellvolumes() * ecl['PRESSURE'])
}

for qoi_name, qoi_function in qoi_functions.items():
    qois = np.zeros(len(ensemble_numbers))
    for ensemble_number in tqdm(ensemble_numbers):
        ensemble_number_formatted = f'{ensemble_number:04d}'
        ecloutput = EclFile(base_filename.format(ensemble_number = ensemble_number))
        egrid = EGrid(base_filename_grid.format(ensemble_number=ensemble_number))
        qoi = qoi_function(ecloutput, egrid)#np.mean(cellvolums * ecloutput['SGAS'] * (ecloutput['SGAS']>0.1))
        qois[ensemble_number-1] = qoi
    plt.hist(qois)
    plt.xlabel(f"{qoi_name} across all grid cells")
    plt.ylabel("Occurences")
    plt.show()

    with open(f'{qoi_name}.csv', 'w', newline='') as csvfile:
        fieldnames = ['sample', qoi_name]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for n, qoi in enumerate(tqdm(qois)):
            writer.writerow({'sample' : n+1, qoi_name:qoi})