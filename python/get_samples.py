import sys
sys.path.append(
    '/run/media/kjetil/external/kjetil/ensemble_pavel/opm/opm/build/opm-common/python')
from opm.io.ecl import ESmry, EGrid, EclOutput, EclFile, ERft
import opm
import sys
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import csv
import os


base_filename_grid = "/run/media/kjetil/external/kjetil/ensemble_pavel/mrst/mrst-bitbucket/mrst-core/output/sleipner_decks/Coarse_Sleipner_ensemble/Coarse_Sleipner_ensemble_{ensemble_number:04d}/output/COARSE_SLEIPNER_ENSEMBLE_{ensemble_number:04d}.EGRID"


base_filename = "/run/media/kjetil/external/kjetil/ensemble_pavel/mrst/mrst-bitbucket/mrst-core/output/sleipner_decks/Coarse_Sleipner_ensemble/Coarse_Sleipner_ensemble_{ensemble_number:04d}/output/COARSE_SLEIPNER_ENSEMBLE_{ensemble_number:04d}.UNRST"
ensemble_numbers = list(range(1, 10))#25))


qoi_functions = {
    # "moveable_co2": lambda ecl, egrid: np.sum(egrid.cellvolumes() * ecl['SGAS', 14] * (ecl['SGAS', 14] > 0.1)),
    "all_co2": lambda ecl, egrid, timestep: np.sum(egrid.cellvolumes() * ecl['SGAS', timestep]),
    "pressure": lambda ecl, egrid, timestep: np.sum(egrid.cellvolumes() * ecl['PRESSURE', timestep]/np.sum(egrid.cellvolumes()))
}

with open("summaryfile.txt", "w") as f:
    pass

timesteps = 15
for qoi_name, qoi_function in qoi_functions.items():
    qois = np.zeros((timesteps, len(ensemble_numbers)))
    for ensemble_number in tqdm(ensemble_numbers):
        ensemble_number_formatted = f'{ensemble_number:04d}'
        ecloutput = EclFile(base_filename.format(
            ensemble_number=ensemble_number))
        egrid = EGrid(base_filename_grid.format(
            ensemble_number=ensemble_number))
    
        for timestep in range(timesteps):
            # np.mean(cellvolums * ecloutput['SGAS'] * (ecloutput['SGAS']>0.1))
            qoi = qoi_function(ecloutput, egrid, timestep)
            qois[timestep, ensemble_number-1] = qoi

        with open("summaryfile.txt", "a") as f:
            f.write(f"{qoi} {np.sum(egrid.cellvolumes())}\n")

    plt.hist(qois)
    plt.xlabel(f"{qoi_name} across all grid cells")
    plt.ylabel("Occurences")
    plt.show()
    
    os.makedirs("data_output", exist_ok = True)
    for timestep in range(timesteps):
        with open(f'{qoi_name}_{timestep}.csv', 'w', newline='') as csvfile:
            fieldnames = ['sample', qoi_name]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for n, qoi in enumerate(tqdm(qois[timestep,:])):
                writer.writerow({'sample': n+1, qoi_name: qoi})
