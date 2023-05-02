"""
Created on Mon May 13 17:33:09 2019

@author: nleder
"""

import argparse
import sys

from argparse import ArgumentDefaultsHelpFormatter
from datetime import datetime
from dateutil.parser import isoparse
from pathlib import Path
from sys import stderr

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.pyplot import plot, scatter
from matplotlib.ticker import FuncFormatter
from pandas import read_hdf
from tables import open_file

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
    parser.add_argument(
        "-s",
        "--scatter",
        action="store_true",
        help="use scatter plot instead of line plot for sensor data",
    )
    parser.add_argument(
        "-p",
        "--print",
        action="store_true",
        help="store graphical output as PDF file",
    )

    return parser.parse_args()


def main():
    """
    Main function of the ICOplotter
    """

    args = get_arguments()
    log_file = Path(args.input)

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

    data = read_hdf(log_file, key="acceleration")
    with open_file(log_file, mode="r") as file:
        timestamp_start = isoparse(
            file.get_node("/acceleration").attrs["Start_Time"]
        ).timestamp()

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
    # Convert timestamps (in μs since start) to absolute timestamps
    timestamps = (data["timestamp"] / 1_000_000) + timestamp_start
    try:
        plots = 3
        for axis in axes:
            samples = data[axis]
            ift_values[axis] = IFTLibrary.ift_value(samples, f_sample)
    except IFTLibraryException as error:
        plots = 2
        print(f"Unable to calculate IFT value: {error}", file=stderr)

    x_axis_format = FuncFormatter(
        lambda x, position: datetime.fromtimestamp(x).strftime("%H:%M:%S.%f")
    )

    plt.subplots(plots, 1, figsize=(20, 10))
    subplot = plt.subplot(plots, 1, 1)
    subplot.xaxis.set_major_formatter(x_axis_format)
    plotter_function = scatter if args.scatter else plot
    for axis in axes:
        plotter_function(timestamps, data[axis], label=axis)
        plt.xlabel("Time")
        plt.ylabel("Raw Sensor Data")
    plt.legend()

    subplot = plt.subplot(plots, 1, 2)

    if ift_values:
        for axis in axes:
            plotter_function(timestamps, ift_values[axis], label=axis)
            plt.xlabel("Time")
            plt.ylabel("IFT Value")
        plt.legend()
        subplot.xaxis.set_major_formatter(x_axis_format)

        plt.subplot(plots, 1, 3)

    for axis in axes:
        plt.psd(data[axis] - data[axis].mean(), 512, f_sample, label=axis)
    plt.legend()

    if args.print:
        output_filepath = log_file.with_suffix(".pdf")
        pdf = PdfPages(output_filepath)
        pdf.savefig()
        pdf.close()
        print(f"Stored plotter output in “{output_filepath}”")
    else:
        plt.show()


if __name__ == "__main__":
    main()
