"""
Created on Fri Mar 27 08:16:22 2020

@author: Clemens
"""


import argparse
import pandas as pd


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

    filepaths, test_value_min, test_value_max, details_on = get_arguments()

    for filepath in filepaths:
        print(f"Input: {filepath}")
        data = pd.read_hdf(filepath, key="acceleration")

        last_counter = data["counter"][0]
        packet_loss = 0
        packets = 0
        for counter in data["counter"]:
            if counter == last_counter:
                continue  # Skip packages with same counter value

            lost_packets = (counter - last_counter) % 256 - 1
            if lost_packets != 0 and details_on is True:
                print(f"{lost_packets} Packets lost")

            packet_loss += lost_packets
            packets += lost_packets + 1

            last_counter = counter

        out_of_range = {"x": 0, "y": 0, "z": 0}
        for axis in "xyz":
            acceleration_values = data.get(axis)
            if acceleration_values is None:
                continue
            for datapoint in acceleration_values:
                if datapoint > test_value_max or datapoint < test_value_min:
                    out_of_range[axis] += 1

        packet_loss = round((packet_loss / packets) * 100, 2)
        print(f"Packet Loss: {packet_loss}%")

        print("Data Points:")
        for axis in "xyz":
            acceleration_values = data.get(axis)
            if acceleration_values is None:
                continue

            percent_overflow = round(
                (out_of_range[axis] / len(acceleration_values)) * 100, 2
            )
            print(
                f"{axis.upper()}-Axis: {out_of_range[axis]} "
                f"Samples were over {test_value_max}g or below "
                f"{test_value_min}g ({percent_overflow}%)"
            )

        if len(data["timestamp"]) >= 2:
            # Accessing last element via `-1` raises `KeyError`
            runtime = data["timestamp"][len(data["timestamp"]) - 1] / 1_000_000
            print(f"Runtime: {runtime:.3} seconds")


if __name__ == "__main__":
    main()
