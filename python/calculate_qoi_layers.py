from calculate_qoi import calculate_qois
import os.path
import numpy as np
import multiprocessing


class ProcessLayer:
    def __init__(self, *, output_folder, layer_name, layer_data, layer_offset, basename):
        self.output_folder = output_folder
        self.layer_name = layer_name
        self.layer_data = layer_data
        self.layer_offset = layer_offset
        self.basename = basename

    def __call__(self, layer):
        output_folder_with_layer = os.path.join(
            self.output_folder, f"{self.layer_name}_{layer}"
        )
        layer_mask = self.layer_data == (layer + self.layer_offset)
        calculate_qois(basename, output_folder_with_layer, layer_mask=layer_mask)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 5:
        print(
            f"Usage:\n\t{sys.executable} {sys.argv[0]} <base path to ensemble> <layer_map.csv> <feeder_map.csv> <output_folder>\n\n"
        )
        print("<base path to ensemble> should contain:")
        print(
            "\tCoarse_Sleipner_ensemble_0001/output/COARSE_SLEIPNER_ENSEMBLE_0001.EGRID"
        )
        print(
            "\tCoarse_Sleipner_ensemble_0001/output/COARSE_SLEIPNER_ENSEMBLE_0001.INIT"
        )
        print(
            "\tCoarse_Sleipner_ensemble_0001/output/COARSE_SLEIPNER_ENSEMBLE_0001.UNRST"
        )
        print("\t...")
        print(
            "\tCoarse_Sleipner_ensemble_1024/output/COARSE_SLEIPNER_ENSEMBLE_1024.EGRID"
        )
        print(
            "\tCoarse_Sleipner_ensemble_1024/output/COARSE_SLEIPNER_ENSEMBLE_1024.INIT"
        )
        print(
            "\tCoarse_Sleipner_ensemble_1024/output/COARSE_SLEIPNER_ENSEMBLE_1024.UNRST"
        )

        exit(1)
    basename = sys.argv[1]
    output_folder = sys.argv[4]
    layer_file = sys.argv[2]
    feeder_file = sys.argv[3]
    layer_normal = np.loadtxt(layer_file)

    os.makedirs(output_folder, exist_ok=True)
    layers = {
        "sand": layer_normal,
        "shale" : layer_normal
        # "feeder" : np.readtxt(feeder_file),
    }

    layer_offsets = {
        "sand": 0,
        "shale" : 100
    }

    for layer_name, layer_data in layers.items():
        processlayer = ProcessLayer(
            output_folder=output_folder,
            layer_name=layer_name,
            layer_data=layer_data,
            layer_offset=layer_offsets[layer_name],
            basename=basename,
        )
        with multiprocessing.Pool(16) as p:
            p.map(processlayer, range(1, 10))
