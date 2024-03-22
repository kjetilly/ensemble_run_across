from opm.io.ecl import ESmry, EGrid, EclOutput, EclFile, ERft
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import csv
import os


def calculate_all_co2(ecl, cellvolumes, initfile, summary, timestep):
    return np.sum(initfile["PORV"] * ecl["SGAS", timestep])


def calculate_real_mobile_co2(ecl, cellvolumes, initfile, summary,timestep):
    return np.sum(
        initfile["PORV"]
        * (ecl["SGAS", timestep] - 0.1)
        * (ecl["SGAS", timestep] > 0.10)
    )


def calculate_real_immobile_co2(ecl, cellvolumes, initfile, summary, timestep):
    all_co2 = calculate_all_co2(ecl, cellvolumes, initfile, summary, timestep)
    real_mobile_co2 = calculate_real_mobile_co2(ecl, cellvolumes, initfile, summary, timestep)
    return all_co2 - real_mobile_co2


def reportstep2timestep(timestep, times):
    dt = 365.242500
    timestep_days = dt * timestep
    index = np.argmin(abs(timestep_days - times))
    return index

def calculate_trapped_co2(ecl, cellvolumes, initfile, summary, timestep):
    # “Trapped CO2” is what we want to analyze, and define it as 
    # the fraction of injected CO2 that is “Capillary trapped or dissolved”. 
    # We can calculate it as follows:
    #
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
    surface_density = 1.98  # density of CO2 at surface pressure

    # TODO: Find corresponding timestep from summary["TIME"]
    # dt is 365.242500 days
    timestep_translated = reportstep2timestep(timestep, summary['TIME'])
    mass_in_gas_phase = summary["FGIPG"][timestep_translated] * surface_density
    real_immobile_co2 = calculate_real_immobile_co2(ecl, cellvolumes, initfile, summary, timestep)
    all_co2 = calculate_all_co2(ecl, cellvolumes, initfile, summary, timestep)
    immobile_fraction = real_immobile_co2 / all_co2
    mass_immobile = immobile_fraction * mass_in_gas_phase
    total_injected_mass = summary["FGIT"][timestep_translated] * surface_density
    mass_dissolved = summary["FGIPL"][timestep_translated] * surface_density
    trapped_co2 = (mass_dissolved + mass_immobile) / total_injected_mass

    return trapped_co2


def calculate_qois(basepath, output_dir_base, *, number_of_samples=1024, timesteps=215):
    base_filename_grid = os.path.join(
        basepath,
        "Coarse_Sleipner_ensemble_{ensemble_number:04d}/output/COARSE_SLEIPNER_ENSEMBLE_{ensemble_number:04d}.EGRID",
    )
    base_filename = os.path.join(
        basepath,
        "Coarse_Sleipner_ensemble_{ensemble_number:04d}/output/COARSE_SLEIPNER_ENSEMBLE_{ensemble_number:04d}.UNRST",
    )
    base_filename_init = os.path.join(
        basepath,
        "Coarse_Sleipner_ensemble_{ensemble_number:04d}/output/COARSE_SLEIPNER_ENSEMBLE_{ensemble_number:04d}.INIT",
    )

    base_filename_summary = os.path.join(
        basepath,
        "Coarse_Sleipner_ensemble_{ensemble_number:04d}/output/COARSE_SLEIPNER_ENSEMBLE_{ensemble_number:04d}.SMSPEC",
    )
    ensemble_numbers = list(range(1, number_of_samples + 1))
    qoi_functions = {
        "trapped_co2": calculate_trapped_co2,
        "real_immobile_co2": calculate_real_immobile_co2,
        "all_co2": calculate_all_co2,
        "mobile_co2": lambda ecl, cellvolumes, initfile, summary, timestep: np.sum(
            initfile["PORV"] * ecl["SGAS", timestep] * (ecl["SGAS", timestep] > 0.10)
        ),
        "real_mobile_co2": calculate_real_mobile_co2,
        "immobile_co2": lambda ecl, cellvolumes, initfile, summary, timestep: np.sum(
            initfile["PORV"] * ecl["SGAS", timestep] * (ecl["SGAS", timestep] <= 0.10)
        ),
        "pressure": lambda ecl, cellvolumes, initfile, summary, timestep: np.sum(
            cellvolumes * ecl["PRESSURE", timestep] / np.sum(cellvolumes)
        ),
    }

    for qoi_name, qoi_function in qoi_functions.items():
        print(f"Calculating for {qoi_name}")
        qois = np.zeros((timesteps, len(ensemble_numbers)))

        for ensemble_number in tqdm(ensemble_numbers):
            if not os.path.exists(
                base_filename.format(ensemble_number=ensemble_number)
            ):
                continue
            ecloutput = EclFile(base_filename.format(ensemble_number=ensemble_number))
            egrid = EGrid(base_filename_grid.format(ensemble_number=ensemble_number))
            summary = ESmry(base_filename_summary.format(ensemble_number=ensemble_number))
            cellvolumes = egrid.cellvolumes()
            initfile = EclFile(
                base_filename_init.format(ensemble_number=ensemble_number)
            )
            for timestep in range(timesteps):
                qoi = qoi_function(ecloutput, cellvolumes, initfile, summary, timestep)
                qois[timestep, ensemble_number - 1] = qoi
                
        output_dir = os.path.join(output_dir_base, qoi_name)
        os.makedirs(output_dir, exist_ok=True)

        for timestep in range(timesteps):
            with open(
                os.path.join(output_dir, f"{qoi_name}_{timestep}.csv"), "w", newline=""
            ) as csvfile:
                fieldnames = ["sample", qoi_name]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for n, qoi in enumerate(qois[timestep, :]):
                    writer.writerow({"sample": n + 1, qoi_name: qoi})

if __name__ =='__main__':
    import sys
    
    if len(sys.argv) != 3:
        print(f"Usage:\n\t{sys.executable} {sys.argv[0]} <base path to ensemble> <output_folder>\n\n")
        print("<base path to ensemble> should contain:")
        print("\tCoarse_Sleipner_ensemble_0001/output/COARSE_SLEIPNER_ENSEMBLE_0001.EGRID")
        print("\tCoarse_Sleipner_ensemble_0001/output/COARSE_SLEIPNER_ENSEMBLE_0001.INIT")
        print("\tCoarse_Sleipner_ensemble_0001/output/COARSE_SLEIPNER_ENSEMBLE_0001.UNRST")
        print("\t...")
        print("\tCoarse_Sleipner_ensemble_1024/output/COARSE_SLEIPNER_ENSEMBLE_1024.EGRID")
        print("\tCoarse_Sleipner_ensemble_1024/output/COARSE_SLEIPNER_ENSEMBLE_1024.INIT")
        print("\tCoarse_Sleipner_ensemble_1024/output/COARSE_SLEIPNER_ENSEMBLE_1024.UNRST")
        
        exit(1)
    basename = sys.argv[1]
    output_folder = sys.argv[2]
    calculate_qois(basename, output_folder)