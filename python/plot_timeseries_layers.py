import csv
import collections
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import os


def plot_timeseries(foldername, errorevery=10):

    plot_folder = os.path.join(os.path.dirname(foldername), "img")
    os.makedirs(plot_folder, exist_ok=True)

    qois_dict = collections.defaultdict(lambda: collections.defaultdict(list))

    timesteps = 215
    latex_names = {
        "real_mobile_co2": "\\mathrm{Real\\;Mobile\\;CO_2}",
        "mobile_co2": "\\mathrm{Mobile\\;CO_2}",
        "all_co2": "\\mathrm{All\\;CO_2}",
        "immobile_co2": "\\mathrm{Immobile\\;CO_2}",
        "all_co2_mass": "\\mathrm{Mass\\;of\\;All\\;CO_2}",
        "trapped_co2": "\\mathrm{Trapped\\;CO_2}",
        "trapped_co2_mass": "\\mathrm{Mass\\;of\\;Trapped\\;CO_2}",
        "pressure": "p",
    }
    latex_names["diff"] = f"{latex_names['all_co2']}-{latex_names['real_mobile_co2']}"
    for qoi_name in [
        # "real_mobile_co2",
        # "mobile_co2",
        "all_co2",
        "all_co2_mass",
        # "immobile_co2",
        "trapped_co2_mass",
        "trapped_co2",
        # "pressure",
    ]:
        for layer in range(1, 10):
            latex_name = latex_names[qoi_name]
            filename_for = os.path.join(
                foldername, "{qoi_name}/{qoi_name}_{timestep}.csv"
            )
            all_qois = collections.defaultdict(list)

            for ts in tqdm(range(timesteps)):
                with open(
                    filename_for.format(timestep=ts, qoi_name=qoi_name, layer=layer)
                ) as f:
                    reader = csv.DictReader(f)

                    for row in reader:
                        qoi = float(row[qoi_name])
                        qois_dict[qoi_name][ts].append(qoi)
                        if qoi == 0.0:
                            continue
                        all_qois[ts].append(qoi)

            statistics_qoi = collections.defaultdict(list)
            for ts in range(timesteps):
                try:
                    statistics_qoi["mean"].append(np.mean(all_qois[ts]))
                    statistics_qoi["std"].append(np.std(all_qois[ts]))
                    statistics_qoi["min"].append(np.min(all_qois[ts]))
                    statistics_qoi["max"].append(np.max(all_qois[ts]))
                except:
                    print(f"{ts=}")

            t = np.arange(0, timesteps)
            plt.errorbar(
                t,
                statistics_qoi["mean"],
                yerr=statistics_qoi["std"],
                errorevery=errorevery,
                label=f"layer = {layer}",
            )
            # plt.fill_between(
            #     t, statistics_qoi["min"], statistics_qoi["max"], alpha=0.6, color="salmon"
            # )
            plt.ylabel(f"$\\mathbb{{E}}({latex_name})$")
            plt.xlabel("Time [years]")
            plt.legend()
            plt.tight_layout()
        plt.savefig(os.path.join(plot_folder, f"evolution_{qoi_name}.png"), dpi=300)
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
