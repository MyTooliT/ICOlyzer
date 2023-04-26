"""
Created on Mon May 13 17:33:09 2019

@author: nleder
"""

import argparse
import sys

from argparse import ArgumentDefaultsHelpFormatter
from pathlib import Path
from sys import stderr

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd  # Load the Pandas libraries with alias 'pd'

from .iftlibrary import IFTLibrary, IFTLibraryException


def get_arguments():
    """
    Returns the given Function Parameters off the script-call

    @return Returns the parameters
    """
    parser = argparse.ArgumentParser(
        description="Visualizes ICOc measurement data in HDF5 format",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "input",
        default="log.hdf5",
        nargs="?",
        help="measurement data in HDF5 format",
    )
    args = parser.parse_args()

    return args.input


def main():
    """
    Main function of the ICOplotter
    """
    log_file = Path(get_arguments()).resolve()

    error_message = ""
    if not log_file.exists():
        error_message = f"“{log_file}” does not exist"
    elif log_file.is_dir():
        error_message = f"“{log_file}” is a directory, not an HDF5 file"
    elif not log_file.is_file():
        error_message = f"“{log_file}” is not a file"
    if error_message != "":
        print(error_message, file=stderr)
        return

    data = pd.read_hdf(log_file, key="acceleration")
    timestamps = data["timestamp"]
    n_points = len(timestamps)

    f_sample = (
        n_points
        / (timestamps.iloc[n_points - 1] - timestamps.iloc[0])
        * 1000000
    )
    stats = data.describe()

    axes = [axis for axis in ("x", "y", "z") if data.get(axis) is not None]
    nr_of_axis = len(axes)

    if nr_of_axis <= 0:
        print("Error: No axis data available", file=sys.stderr)
        sys.exit(1)

    print(
        " ".join(
            [
                f"Avg {axis.upper()}: {int(stats.loc['mean'][axis])}"
                for axis in axes
            ]
        )
    )

    std_dev = stats.loc["std", axes]
    snr = 20 * np.log10(std_dev / (np.power(2, 16) - 1))
    print(
        f"SNR of this file is : {min(snr):.2f} dB and {max(snr):.2f} dB "
        f"@ {f_sample / 1000:.2f} kHz"
    )

    ift_values = {}
    try:
        plots = 3
        for axis in axes:
            samples = data[axis]
            ift_values[axis] = IFTLibrary.ift_value(samples, f_sample)
    except IFTLibraryException as error:
        plots = 2
        print(f"Unable to calculate IFT value: {error}", file=stderr)

    plt.subplots(plots, 1, figsize=(20, 10))
    plt.subplot(plots, 1, 1)
    for axis in axes:
        plt.plot(timestamps, data[axis], label=axis)
        plt.xlabel("Time")
        plt.ylabel("Raw Sensor Data")
    plt.legend()

    plt.subplot(plots, 1, 2)

    if ift_values:
        for axis in axes:
            plt.plot(timestamps, ift_values[axis], label=axis)
            plt.xlabel("Time")
            plt.ylabel("IFT Value")
        plt.legend()
        plt.subplot(plots, 1, 3)

    for axis in axes:
        plt.psd(data[axis] - data[axis].mean(), 512, f_sample, label=axis)
    plt.legend()

    plt.show()


if __name__ == "__main__":
    main()
