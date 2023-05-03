"""
Created on Mon May 13 17:33:09 2019

@author: nleder
"""

import argparse
import sys

from argparse import ArgumentDefaultsHelpFormatter, Namespace
from datetime import datetime
from dateutil.parser import isoparse
from pathlib import Path
from sys import stderr

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.pyplot import plot, scatter
from matplotlib.ticker import FuncFormatter
from pandas import DataFrame, read_hdf
from tables import open_file

from icotools.cli import file_exists
from .iftlibrary import IFTLibrary, IFTLibraryException


def get_arguments() -> Namespace:
    """Parse command line arguments

    Returns
    -------

    An object that contains the given command line arguments

    """

    parser = argparse.ArgumentParser(
        description="Visualizes ICOc measurement data in HDF5 format",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "input",
        default="log.hdf5",
        type=file_exists,
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


def sample_rate(data: DataFrame) -> float:
    """Calculate sample rate of measurement data

    Parameters
    ----------

    data: Measurement data

    Returns
    -------

    Overall sample rate for all axes in Hz

    """

    timestamps = data["timestamp"]

    return (
        len(timestamps)
        / (timestamps.iloc[-1] - timestamps.iloc[0])
        * 1_000_000
    )


def print_info(data: DataFrame) -> None:
    """Print information about measurement data"""

    stats = data.describe()

    axes = [axis for axis in "xyz" if axis in data.keys()]
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
        f"@ {sample_rate(data) / 1000:.2f} kHz"
    )


def plot_data(data: DataFrame, args: Namespace, log_file: Path) -> None:
    """Visualize measurement data"""

    with open_file(log_file, mode="r") as file:
        timestamp_start = isoparse(
            file.get_node("/acceleration").attrs["Start_Time"]
        ).timestamp()

    ift_values = {}
    axes = [axis for axis in "xyz" if axis in data.keys()]
    # Convert timestamps (in μs since start) to absolute timestamps
    timestamps = (data["timestamp"] / 1_000_000) + timestamp_start
    f_sample = sample_rate(data)
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

    figure, _ = plt.subplots(plots, 1, figsize=(20, 10))
    figure.canvas.manager.set_window_title("Acceleration Measurement")
    figure.suptitle(
        datetime.fromtimestamp(timestamp_start).strftime("%c"), fontsize=20
    )
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


# -- Main ---------------------------------------------------------------------


def main():
    args = get_arguments()
    log_file = Path(args.input)

    data = read_hdf(log_file, key="acceleration")

    print_info(data)
    plot_data(data, args, log_file)


if __name__ == "__main__":
    main()
