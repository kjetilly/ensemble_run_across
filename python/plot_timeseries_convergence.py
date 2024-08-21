import csv
import collections
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import os


def plot_timeseries(foldername, timestep_numbers=[214//2, 214], sample_factors=[0.125/8, 0.125/4, 0.125/2, 0.125, 0.5, 1.0]):
    plot_folder = os.path.join(foldername, "img")
    os.makedirs(plot_folder, exist_ok=True)

    qois_dict = collections.defaultdict(lambda: collections.defaultdict(list))

    timesteps = 215
    latex_names = {
        "real_mobile_co2": "\\mathrm{Real\\;Mobile\\;CO_2}",
        "mobile_co2": "\\mathrm{Mobile\\;CO_2}",
        "all_co2": "\\mathrm{All\\;CO_2}",
        "all_co2_mass": "\\mathrm{Mass\\;of\\;All\\;CO_2}",
        "immobile_co2": "\\mathrm{Immobile\\;CO_2}",
        "trapped_co2": "\\mathrm{Trapped\\;CO_2}",
        "trapped_co2_mass": "\\mathrm{Mass\\;of\\;Trapped\\;CO_2}",
        "pressure": "p",
        "dissolved_co2_mass" : "\\mathrm{Mass\\;of\\;Dissolved\\;CO_2}",
        "cap_trapped_co2_mass" : "\\mathrm{Mass\\;of\\;Cap\\;Trapped\\;CO_2}",
    }
    latex_names["diff"] = f"{latex_names['all_co2']}-{latex_names['real_mobile_co2']}"
    for qoi_name in [
        #"dissolved_co2_mass",
        #"cap_trapped_co2_mass",
        # "real_mobile_co2",
        # "mobile_co2",
        #"all_co2",
        # "immobile_co2",
        #"trapped_co2_mass",
        "trapped_co2",
        # "pressure",
    ]:
        latex_name = latex_names[qoi_name]
        filename_for = os.path.join(foldername, "{qoi_name}/{qoi_name}_{timestep}.csv")
        all_qois = collections.defaultdict(list)
        for ts in tqdm(timestep_numbers):
            with open(filename_for.format(timestep=ts, qoi_name=qoi_name)) as f:
                reader = csv.DictReader(f)

                for row in reader:
                    qoi = float(row[qoi_name])
                    qois_dict[qoi_name][ts].append(qoi)
                    if qoi == 0.0:
                        continue
                    all_qois[ts].append(qoi)
        sample_numbers = (np.array(sample_factors) * len(all_qois[timestep_numbers[0]])).astype(int)
        sample_numbers = sample_numbers.tolist()
        sample_numbers.append(1024)
        sample_numbers.append(512)
        sample_numbers.append(256)
        sample_numbers.append(128)
        sample_numbers.append(2048)
        sample_numbers = np.array(sorted(list(set(sample_numbers))))
        
        print(sample_numbers)
        markers = ['-o', '-*']
        statistics_qoi = collections.defaultdict(lambda: collections.defaultdict(list))
        for marker, ts in zip(markers, timestep_numbers):
            
            for number_of_samples in sample_numbers:
                statistics_qoi["mean"][ts].append(np.mean(all_qois[ts][:number_of_samples]))
                statistics_qoi["std"][ts].append(np.std(all_qois[ts][:number_of_samples]))
                statistics_qoi["min"][ts].append(np.min(all_qois[ts][:number_of_samples]))
                statistics_qoi["max"][ts].append(np.max(all_qois[ts][:number_of_samples]))
        for k in ['mean', 'std', 'min', 'max']:
            for marker, ts in zip(markers, timestep_numbers):
                v = np.array(statistics_qoi[k][ts])
                print(v)
                errors = abs(v[1:] - v[:-1])
                samples = sample_numbers[1:]
                print(samples)
                plt.loglog(samples, errors, marker, label=f'$t={ts}$ years')
                poly = np.polyfit(np.log(samples), np.log(errors), 1)
                plt.loglog(samples, np.exp(poly[1])*samples**poly[0], '--', label=f'$\\mathcal{{O}}(M^{{{poly[0]:0.1f}}})$')
                plt.xlabel("Number of samples ($M$)")
                plt.ylabel("Cauchy difference ($|q^M-q^{M/2}|$)")
                plt.title(f"Cauchy convergence of {k}({qoi_name})")
            plt.xscale("log", base=2)
            plt.yscale("log", base=2)
            plt.legend()
            plt.grid(True)
            plt.savefig(os.path.join(plot_folder, f"cauchy_convergence_{k}_{qoi_name}.png"), dpi=300)
            plt.close('all')

        for k in ['mean', 'std', 'min', 'max']:
            for marker, ts in zip(markers, timestep_numbers):
                v = np.array(statistics_qoi[k][ts])
                errors = abs(v[:-1] - v[-1])
                samples = sample_numbers[:-1]
                plt.loglog(samples, errors, marker, label=f'$t={ts}$ years')
                poly = np.polyfit(np.log(samples), np.log(errors), 1)
                plt.loglog(samples, np.exp(poly[1])*samples**poly[0], '--', label=f'$\\mathcal{{O}}(M^{{{poly[0]:0.1f}}})$')
                plt.xlabel("Number of samples ($M$)")
                plt.ylabel(f"Difference ($|q^M-q^{{{sample_numbers[-1]}}}|$)")
                plt.title(f"Convergence against reference solution ({sample_numbers[-1]} samples)\nfor  {k}({qoi_name})")
            plt.xscale("log", base=2)
            plt.yscale("log", base=2)
            plt.legend()
            plt.grid(True)
            plt.savefig(os.path.join(plot_folder, f"convergence_{k}_{qoi_name}.png"), dpi=300)
            plt.close('all')

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print(
            f"Usage:\n\t{sys.executable} {sys.argv[0]} <path to folder containing QoI folders>\n\n"
        )
        exit(1)
    foldername = sys.argv[1]
    plot_timeseries(foldername)
