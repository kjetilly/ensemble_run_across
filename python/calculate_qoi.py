
from opm.io.ecl import ESmry, EGrid, EclOutput, EclFile, ERft
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import csv
import os

def calculate_trapped_co2(ecl, egrid, initfile, timestep):
    # No formulerer eg det slik at “Trapped CO2” er det vi vil analysere, 
    # og definerer det som fraksjonen av injisert CO2 som er “Capillary trapped or dissolved”.
    # Det kan vi rekne ut slik: 
    #    “Trapped CO2” = (mass dissolved + mass immobile)/total injected mass.
    #  
    #     Mass dissolved = FGIPL * surface density (1.98 kg/m^3?). 
    #
    #     Total injected mass = FGIT * surface density. 
    #     
    #     Mass immobile = immobile fraction * mass in gas phase. 
    #     
    #     Immobile fraction = “real immobile co2"/“all_co2”. 
    # 
    #     Mass in gas phase = FGIPG * surface density.
    #

    mass_in_gas_phase = ecl['FGIPG', timestep] * 

def calculate_qois(basepath, output_dir_base, *, number_of_samples=1024, timesteps=215):
    base_filename_grid = os.path.join(basepath, "Coarse_Sleipner_ensemble_{ensemble_number:04d}/output/COARSE_SLEIPNER_ENSEMBLE_{ensemble_number:04d}.EGRID")
    base_filename = os.path.join(basepath, "Coarse_Sleipner_ensemble_{ensemble_number:04d}/output/COARSE_SLEIPNER_ENSEMBLE_{ensemble_number:04d}.UNRST")
    base_filename_init = os.path.join(basepath, "Coarse_Sleipner_ensemble_{ensemble_number:04d}/output/COARSE_SLEIPNER_ENSEMBLE_{ensemble_number:04d}.INIT")
    ensemble_numbers = list(range(1, number_of_samples + 1))
    qoi_functions = {
        "all_co2": lambda ecl, egrid, initfile, timestep: np.sum(initfile["PORV"] * ecl['SGAS', timestep]),
        "mobile_co2": lambda ecl, egrid, initfile, timestep: np.sum(initfile["PORV"] * ecl['SGAS', timestep] * (ecl['SGAS', timestep] > 0.10)),
        "real_mobile_co2": lambda ecl, egrid, initfile, timestep: np.sum(initfile["PORV"] * (ecl['SGAS', timestep] - 0.1) * (ecl['SGAS', timestep] > 0.10)),
        "immobile_co2": lambda ecl, egrid, initfile, timestep: np.sum(initfile["PORV"] * ecl['SGAS', timestep] * (ecl['SGAS', timestep] <= 0.10)),
        "pressure": lambda ecl, egrid, initfile, timestep: np.sum(egrid.cellvolumes() * ecl['PRESSURE', timestep]/np.sum(egrid.cellvolumes()))
    }

    for qoi_name, qoi_function in qoi_functions.items():
        print(f"Calculating for {qoi_name}")
        qois = np.zeros((timesteps, len(ensemble_numbers)))

        for ensemble_number in tqdm(ensemble_numbers):
            if not os.path.exists(base_filename.format(ensemble_number=ensemble_number)):
                continue
            ecloutput = EclFile(base_filename.format(
                ensemble_number=ensemble_number))
            egrid = EGrid(base_filename_grid.format(
                ensemble_number=ensemble_number))
            initfile = EclFile(base_filename_init.format(ensemble_number=ensemble_number))
            for timestep in range(timesteps):
                try:
                    qoi = qoi_function(ecloutput, egrid, initfile, timestep)
                    qois[timestep, ensemble_number-1] = qoi
                except:
                    pass
        output_dir = os.path.join(output_dir_base, qoi_name)
        os.makedirs(output_dir, exist_ok = True)

        for timestep in range(timesteps):
            with open(os.path.join(output_dir, f'{qoi_name}_{timestep}.csv'), 'w', newline='') as csvfile:
                fieldnames = ['sample', qoi_name]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for n, qoi in enumerate(qois[timestep,:]):
                    writer.writerow({'sample': n+1, qoi_name: qoi})
