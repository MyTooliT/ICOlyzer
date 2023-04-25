"""
Created on Fri Mar 27 08:16:22 2020

@author: Clemens
"""


import argparse
import pandas as pd


class FileInformation:
    """
    This class contains the information about the to be analyzed log-file.
    """

    def __init__(self, filename):
        self.filename = filename
        self.packet_loss = 0
        self.packets = 0
        self.datapoints = 0
        self.out_of_range = 0
        self.out_of_range2 = 0
        self.out_of_range3 = 0


def get_arguments():
    """
    Returns the given Function Parameters off the script-call

    @return Returns the parameters
    """
    parser = argparse.ArgumentParser(
        description="This script is used to calculate the occurred packet "
        + "loss of an ICOc log data. Additionally it can be used to get "
        + "the % of sample points outside of a given range"
        + " as long as a min or max is defined via additional "
        + "parameters at the script call.",
    )
    parser.add_argument(
        "-m",
        "--min",
        default=-1,
        type=float,
        metavar="MIN-Value",
        help="Define a Min-Value (default: -1)",
    )
    parser.add_argument(
        "-v",
        "--max",
        default=1,
        type=float,
        metavar="MAX-Value",
        help="Define a Max-Value (default: 1)",
    )
    parser.add_argument(
        "inputs",
        default=["log.hdf5"],
        nargs="*",
        help="measurement data in HDF5 format (default: log.hdf5)",
    )

    parser.add_argument(
        "-d",
        "--details",
        action="store_true",
        help="Show more Information about Paketloss (default: false)",
    )
    args = parser.parse_args()

    return args.inputs, args.min, args.max, args.details


def main():
    """
    Main function of the ICOanalyzer.
    """
    details_on = False
    test_value_max = 1
    test_value_min = -1

    filepaths, test_value_min, test_value_max, details_on = get_arguments()

    for filepath in filepaths:
        element = FileInformation(filepath)
        print("Input file is: " + element.filename)
        data = pd.read_hdf(element.filename, key="acceleration")

        first_counter = data["counter"][0]
        for datapoint in data["counter"]:
            if datapoint == first_counter:
                continue  # Skip packages with same counter value

            lost_packets = (datapoint - first_counter) % 256 - 1
            element.packets = element.packets + lost_packets + 1
            element.packet_loss = element.packet_loss + lost_packets

            if lost_packets != 0 and details_on is True:
                print(f"{lost_packets} Packets lost")

            first_counter = datapoint

        x_data = data.get("x")
        y_data = data.get("y")
        z_data = data.get("z")

        out_of_range = {"x": 0, "y": 0, "z": 0}
        for axis, acceleration_values in zip("xyz", (x_data, y_data, z_data)):
            if acceleration_values is None:
                continue
            element.datapoints = len(acceleration_values)
            for datapoint in acceleration_values:
                if datapoint > test_value_max or datapoint < test_value_min:
                    out_of_range[axis] += 1

        element.out_of_range += out_of_range["x"]
        element.out_of_range2 += out_of_range["y"]
        element.out_of_range3 += out_of_range["z"]

        print("PACKETLOSS:")
        print(
            str(round((element.packet_loss / element.packets) * 100, 2)) + "%"
        )
        print("DATAPOINTS:")
        for axis, acceleration_values in zip("xyz", (x_data, y_data, z_data)):
            if acceleration_values is None:
                continue

            percent_overflow = (out_of_range[axis] / element.datapoints) * 100
            percent_overflow = round(percent_overflow, 2)
            print(
                f"{axis.upper()}-AXIS: {out_of_range[axis]} "
                f"Samples were over {test_value_max}g or below "
                f"{test_value_min}g ({percent_overflow}%)"
            )

        if len(data["timestamp"]) >= 2:
            # Accessing last element via `-1` raises `KeyError`
            runtime = data["timestamp"][len(data["timestamp"]) - 1] / 1_000_000
            print(f"Runtime: {runtime:.3} seconds")


if __name__ == "__main__":
    main()
