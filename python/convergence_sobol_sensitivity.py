import csv
import collections
import matplotlib.pyplot as plt
plt.rc('text', usetex=True)
plt.rc('text.latex', preamble=r'\usepackage{amsmath}')
import numpy as np
import scipy.linalg
from tqdm import tqdm
import os
import scipy.stats
from SALib.analyze.sobol import analyze
from SALib.sample.sobol import sample
from SALib.test_functions import Ishigami
import copy
import traceback


def plot_timeseries(foldername, errorevery=10,timestep_numbers=[214//2, 214], sample_factors=[0.5, 1.0]):
    plot_folder = os.path.join(foldername, "img")
    os.makedirs(plot_folder, exist_ok=True)

    qois_dict = collections.defaultdict(lambda: collections.defaultdict(list))

    timesteps = 215
    all_parameter_names = [
        "tegrad",
        "pesand",
        "peshale",
        "pefeeder",
        "posand",
        "totopsur",
        "dummy",
    ]
    latex_names = {
        "real_mobile_co2": "\\mathrm{Real\\;Mobile\\;CO_2}",
        "mobile_co2": "\\mathrm{Mobile\\;CO_2}",
        "all_co2": "\\mathrm{All\\;CO_2}",
        "immobile_co2": "\\mathrm{Immobile\\;CO_2}",
        "trapped_co2": "\\mathrm{Trapped\\;CO_2}",
        "pressure": "p",
        "dissolved_co2_mass": "\\mathrm{Mass\\;of\\;Dissolved\\;CO_2}",
        "cap_trapped_co2_mass": "\\mathrm{Mass\\;of\\;Cap\\;Trapped\\;CO_2}",
    }

    problem = {
        "num_vars": 7,
        "names": copy.deepcopy(all_parameter_names),
        "bounds": [
            [30, 40],
            [1100, 5000],
            [0.00075, 0.0015],
            [1100, 5000],
            [0.27, 0.4],
            [-10, 10],
            [0.0, 1.0],
        ],
    }

    parameters = []
    with open(os.path.join(foldername, "parameters.csv")) as f:
        reader = csv.DictReader(f)
        for row in reader:
            parameters.append([float(row[k]) for k in all_parameter_names])

    parameters = np.array(parameters)

    latex_names["diff"] = f"{latex_names['all_co2']}-{latex_names['real_mobile_co2']}"
    latex_names = {
        "real_mobile_co2": "\\mathrm{Real\\;Mobile\\;CO_2}",
        "mobile_co2": "\\mathrm{Mobile\\;CO_2}",
        "all_co2": "\\mathrm{All\\;CO_2}",
        "all_co2_mass": "\\mathrm{Mass\\;of\\;All\\;CO_2}",
        "immobile_co2": "\\mathrm{Immobile\\;CO_2}",
        "trapped_co2": "\\mathrm{Secondary\\;Trapped\\;CO_2}",
        "trapped_co2_mass": "\\mathrm{Mass\\;of\\;Secondary\\;Trapped\\;CO_2}",
        "pressure": "p",
        "dissolved_co2_mass" : "\\mathrm{Mass\\;of\\;Dissolved\\;CO_2}",
        "cap_trapped_co2_mass" : "\\mathrm{Mass\\;of\\;Cap\\;Trapped\\;CO_2}",
    }
    trapped_sum = None
    for qoi_name in [
        "dissolved_co2_mass",
        "cap_trapped_co2_mass",
        "real_mobile_co2",
        "mobile_co2",
        "all_co2",
        "immobile_co2",
        "trapped_co2",
        "pressure",
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
        

        statistics_qoi = collections.defaultdict(lambda: collections.defaultdict(list))
        for ts in timestep_numbers:
            for number_of_samples in sample_numbers:
                problem = {
                    "num_vars": 7,
                    "names": copy.deepcopy(all_parameter_names),
                    "bounds": [
                        [30, 40],
                        [1100, 5000],
                        [0.00075, 0.0015],
                        [1100, 5000],
                        [0.27, 0.4],
                        [-10, 10],
                        [0.0, 1.0],
                    ],
                }
                print (number_of_samples)
                Si = analyze(problem, np.array(all_qois[ts])[:number_of_samples])
                for i in range(len(all_parameter_names)):
                    for k in ["S1", "ST"]:
                        statistics_qoi[f"{k}_{all_parameter_names[i]}"][ts].append(Si[k][i])
        markers = ['-o', '-*']

        for k in ["S1", "ST"]:
            for i, parameter_name in enumerate(all_parameter_names):
                for marker, ts in zip(markers, timestep_numbers):

                    v = np.array(statistics_qoi[f"{k}_{all_parameter_names[i]}"][ts])
                    errors = abs(v[1:] - v[:-1])
                    samples = sample_numbers[1:]
                    plt.loglog(samples, errors, marker, label=f'$t={ts}$ years')
                    poly = np.polyfit(np.log(samples), np.log(errors), 1)
                    plt.loglog(samples, np.exp(poly[1])*samples**poly[0], '--', label=f'$\\mathcal{{O}}(M^{{{poly[0]:0.1f}}})$')
                    plt.xlabel("Number of samples ($M$)")
                    plt.ylabel("Cauchy difference ($|q^M-q^{M/2}|$)")
                    plt.title(f"Cauchy convergence of {k}({qoi_name}) against {parameter_name}")
                plt.xscale("log", base=2)
                plt.yscale("log", base=2)
                plt.legend()
                plt.grid(True)
                plt.savefig(os.path.join(plot_folder, f"cauchy_convergence_sobol_{k}_{qoi_name}_{all_parameter_names[i]}.png"), dpi=300)
                plt.close('all')
        
        for k in ["S1", "ST"]:
            for i, parameter_name in enumerate(all_parameter_names):
                for marker, ts in zip(markers, timestep_numbers):

                    v = np.array(statistics_qoi[f"{k}_{all_parameter_names[i]}"][ts])
                    errors = abs(v[:-1] - v[-1])
                    samples = sample_numbers[:-1]
                    plt.loglog(samples, errors, marker, label=f'$t={ts}$ years')
                    poly = np.polyfit(np.log(samples), np.log(errors), 1)
                    plt.loglog(samples, np.exp(poly[1])*samples**poly[0], '--', label=f'$\\mathcal{{O}}(M^{{{poly[0]:0.1f}}})$')
                    plt.xlabel("Number of samples ($M$)")
                    plt.ylabel(f"Difference ($|q^M-q^{{{sample_numbers[-1]}}}|$)")
                plt.title(f"Convergence {k}({qoi_name}) against {parameter_name}\nagainst reference solution ({sample_numbers[-1]} samples)\nfor  {k}({qoi_name})")
                plt.xscale("log", base=2)
                plt.yscale("log", base=2)
                plt.legend()
                plt.grid(True)
                plt.savefig(os.path.join(plot_folder, f"convergence_sobol_{k}_{qoi_name}_{all_parameter_names[i]}.png"), dpi=300)
                plt.close('all')
        
        for k in ["S1", "ST"]:
            errors_for_all_variables = collections.defaultdict(lambda: np.zeros(len(all_parameter_names), len(sample_numbers)-1))
            for i, parameter_name in enumerate(all_parameter_names):
                
                for marker, ts in zip(markers, timestep_numbers):

                    v = np.array(statistics_qoi[f"{k}_{all_parameter_names[i]}"][ts])
                    errors = abs(v[:-1] - v[-1])
                    errors_for_all_variables[ts][i,:] = errors
                    samples = sample_numbers[:-1]
            norms = {
                "\\ell^\\infty" : (lambda x : scipy.linalg.norm(x, ord=np.inf)),
                "\\ell^2" : (lambda x : scipy.linalg.norm(x, ord=2)),
                "\\ell^1" : (lambda x : scipy.linalg.norm(x, ord=1)),
                
            }
            qoi_full_name = latex_names[qoi_name]
            for norm_name, norm_func in norms.items():
                norm_name_alphanum = filter(str.isalnum, norm_name)
                for marker, ts in zip(markers, timestep_numbers):
                    samples = sample_numbers[:-1]
                    errors = norm_func(errors_for_all_variables[ts])
                    plt.loglog(samples, errors, marker, label=f'$t={ts}$ years')
                    poly = np.polyfit(np.log(samples), np.log(errors), 1)
                    plt.loglog(samples, np.exp(poly[1])*samples**poly[0], '--', label=f'$\\mathcal{{O}}(M^{{{poly[0]:0.1f}}})$')
                    plt.xlabel("Number of samples ($M$)")
                    plt.ylabel(f"Difference ($\\|q^M-q^{{{sample_numbers[-1]}}}\\|_{{{norm_name}}}$)")
                plt.title(f"Convergence of {k} for {qoi_full_name} in ${norm_name} over all parameters\nagainst reference solution ({sample_numbers[-1]} samples)\nfor  {k}({qoi_name})")
                plt.xscale("log", base=2)
                plt.yscale("log", base=2)
                plt.legend()
                plt.grid(True)
                plt.savefig(os.path.join(plot_folder, f"convergence_sobol_normed_{k}_{qoi_name}_{norm_name_alphanum}.png"), dpi=300)
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
