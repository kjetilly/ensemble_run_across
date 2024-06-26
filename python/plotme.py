import csv
import collections
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import os
import scipy.stats
from SALib.analyze.sobol import analyze
from SALib.sample.sobol import sample
from SALib.test_functions import Ishigami
import copy
import traceback


def plot_timeseries(foldername, errorevery=10):
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

        for ts in tqdm(range(timesteps)):
            with open(filename_for.format(timestep=ts, qoi_name=qoi_name)) as f:
                reader = csv.DictReader(f)

                for row in reader:
                    qoi = float(row[qoi_name])
                    qois_dict[qoi_name][ts].append(qoi)
                    if qoi == 0.0:
                        continue
                    all_qois[ts].append(qoi)

        statistics_qoi = collections.defaultdict(list)
        ts_for_corr = []
        for ts in range(timesteps):
            # statistics_qoi['mean'].append(np.mean(all_qois[ts]))
            # statistics_qoi['std'].append(np.std(all_qois[ts]))
            # statistics_qoi['min'].append(np.min(all_qois[ts]))
            # statistics_qoi['max'].append(np.max(all_qois[ts]))
            if np.prod(all_qois[ts]) < 2:
                continue
            ts_for_corr.append(ts)
            for i in range(len(all_parameter_names)):
                M = len(all_qois[ts])
                statistics_qoi[f"corr_{all_parameter_names[i]}"].append(
                    scipy.stats.pearsonr(parameters[:M, i], all_qois[ts]).statistic
                )

            try:
                Si = analyze(problem, np.array(all_qois[ts]))
            except Exception as e:
                print(e)
                print(traceback.format_exc())
                Si = {
                    "S1": np.zeros(len(all_parameter_names)),
                    "S2": np.zeros(len(all_parameter_names)),
                    "ST": np.zeros(len(all_parameter_names)),
                }
            for i in range(len(all_parameter_names)):
                for k in ["S1", "ST"]:
                    statistics_qoi[f"{k}_{all_parameter_names[i]}"].append(Si[k][i])

        t = np.arange(0, timesteps)
        for i in range(len(all_parameter_names)):
            plt.plot(
                ts_for_corr,
                statistics_qoi[f"corr_{all_parameter_names[i]}"],
                label=f"{all_parameter_names[i]}",
            )
        plt.ylabel(f"Correlation")
        plt.xlabel("Time [years]")
        plt.title(f"Correlation for ${latex_names[qoi_name]}$")
        plt.text(
            50,
            0,
            "DRAFT!",
            fontsize=100,
            color="grey",
            rotation=45,
            ha="center",
            va="center",
            alpha=0.5,
        )
        plt.legend()
        plt.tight_layout()

        plt.savefig(os.path.join(plot_folder, f"correlation_{qoi_name}.png"), dpi=300)
        plt.close("all")


        for i in range(len(all_parameter_names)):
            #print(f"{parameters[:M, i].shape=}\n{all_qois[ts_for_corr[-1]]=}\n{all_qois=}")
            plt.scatter(parameters[:M, i], all_qois[ts_for_corr[-1]])
            plt.xlabel(all_parameter_names[i])
            plt.ylabel(qoi_name)
            plt.savefig(os.path.join(plot_folder, f"scatter_{qoi_name}_{all_parameter_names[i]}.png"), dpi=300)
            plt.close('all')

        for k in ["S1", "ST"]:
            if f"{k}_{all_parameter_names[i]}" in statistics_qoi.keys():
                t = np.arange(
                    0,
                    min(
                        timesteps, len(statistics_qoi[f"{k}_{all_parameter_names[i]}"])
                    ),
                )
                for i in range(len(all_parameter_names)):
                    plt.plot(
                        t,
                        statistics_qoi[f"{k}_{all_parameter_names[i]}"],
                        label=f"{all_parameter_names[i]}",
                    )
                    print(
                        f"{k} ({qoi_name}) ({all_parameter_names[i]})= {statistics_qoi[f'{k}_{all_parameter_names[i]}'][-1]}"
                    )
                plt.ylabel(f"Sobol {k}")
                plt.xlabel("Time [years]")
                plt.title(f"Sobol {k} ${latex_names[qoi_name]}$")
                plt.text(
                    100,
                    0,
                    "DRAFT!",
                    fontsize=80,
                    color="grey",
                    rotation=30,
                    ha="center",
                    va="center",
                    alpha=0.5,
                )
                plt.legend()
                plt.tight_layout()

                plt.savefig(
                    os.path.join(plot_folder, f"sobol_{k}_{qoi_name}.png"), dpi=300
                )
                plt.close("all")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print(
            f"Usage:\n\t{sys.executable} {sys.argv[0]} <path to folder containing QoI folders>\n\n"
        )
        exit(1)
    foldername = sys.argv[1]
    plot_timeseries(foldername)
