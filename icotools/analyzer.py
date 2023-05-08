"""
Created on Fri Mar 27 08:16:22 2020

@author: Clemens
"""


import argparse
from pathlib import Path
from sys import stderr

import pandas as pd
from tables import open_file


def get_arguments():
    """
    Returns the given Function Parameters off the script-call

    @return Returns the parameters
    """

    parser = argparse.ArgumentParser(
        description=(
            "Calculate packet loss, values outside of given range, and "
            "runtime for HDF5 input files"
        )
    )
    parser.add_argument(
        "-m",
        "--min",
        default=-1,
        type=float,
        help="minimum value for data range (default: -1)",
    )
    parser.add_argument(
        "-v",
        "--max",
        default=1,
        type=float,
        help="maximum value for data range (default: 1)",
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
        help="Show additional information about paket loss (default: false)",
    )
    args = parser.parse_args()

    return args.inputs, args.min, args.max, args.details


def main():
    """
    Main function of the ICOanalyzer.
    """

    filepaths, test_value_min, test_value_max, details_on = get_arguments()

    for filepath in filepaths:
        # Flush standard output to keep order with standard error output.
        # This means that the output about the current file and the warnings
        # about missing measurement data should be in the correct order. This
        # is helpful if we analyze multiple files at once (e.g. using
        # `find … -exec`)
        print(f"Input: {filepath}", flush=True)
        if not Path(filepath).exists():
            print(f"Skipping non-existent file “{filepath}”", file=stderr)
            continue

        data = pd.read_hdf(filepath, key="acceleration")

        last_counter = data["counter"][0]
        last_timestamp = data["timestamp"][0]
        packet_loss = 0
        packets = 0
        for counter, timestamp in zip(data["counter"], data["timestamp"]):
            if counter == last_counter:
                continue  # Skip packages with same counter value

            lost_packets = (counter - last_counter) % 256 - 1
            duration_last_packet_ms = (timestamp - last_timestamp) / 1000
            loss_timestamp_s = last_timestamp / 1_000_000

            if duration_last_packet_ms > 1000:
                duration_last_packet_s = duration_last_packet_ms / 1000
                print(
                    (
                        "No measurement data for "
                        f"{duration_last_packet_s:.3f} seconds after "
                        f"{loss_timestamp_s} seconds"
                    ),
                    file=stderr,
                )

            if lost_packets != 0 and details_on is True:
                print(
                    f"{lost_packets:3} Packets lost after "
                    f"{loss_timestamp_s:6.3f} seconds - No values for "
                    f"{duration_last_packet_ms:3.1f} milliseconds"
                )

            packet_loss += lost_packets
            packets += lost_packets + 1

            last_timestamp = timestamp
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
            indent = " " * 2
            print(
                f"{indent}{axis.upper()}-Axis: {len(data.get(axis))} Samples "
                f"- {out_of_range[axis]} Samples were over {test_value_max}g "
                f"or below {test_value_min}g ({percent_overflow}%)"
            )

        with open_file(filepath, mode="r") as file:
            start_time = file.get_node("/acceleration").attrs["Start_Time"]

        print(f"Measurement Date: {start_time}")

        if len(data["timestamp"]) >= 2:
            runtime = data["timestamp"].iloc[-1] / 1_000_000
            print(f"Runtime: {runtime:.3f} seconds")


if __name__ == "__main__":
    main()
