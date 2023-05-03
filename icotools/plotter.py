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
from pandas import read_hdf
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


class Plotter:
    def __init__(self, args: Namespace):
        self.args = args
        self.log_file = Path(args.input)
        self.data = read_hdf(self.log_file, key="acceleration")

        # Convert timestamps (in μs since start) to absolute timestamps
        with open_file(self.log_file, mode="r") as file:
            self.timestamp_start = isoparse(
                file.get_node("/acceleration").attrs["Start_Time"]
            ).timestamp()
        self.timestamps = (
            self.data["timestamp"] / 1_000_000
        ) + self.timestamp_start

        self.sample_rate = len(self.timestamps) / (
            self.timestamps.iloc[-1] - self.timestamps.iloc[0]
        )

        self.axes = [axis for axis in "xyz" if axis in self.data.keys()]

    def print_info(self) -> None:
        """Print information about measurement data"""

        stats = self.data.describe()

        if len(self.axes) <= 0:
            print("Error: No axis data available", file=sys.stderr)
            sys.exit(1)

        print(
            " ".join(
                [
                    f"Avg {axis.upper()}: {int(stats.loc['mean'][axis])}"
                    for axis in self.axes
                ]
            )
        )

        std_dev = stats.loc["std", self.axes]
        snr = 20 * np.log10(std_dev / (np.power(2, 16) - 1))
        print(
            f"SNR of this file is : {min(snr):.2f} dB and {max(snr):.2f} dB "
            f"@ {self.sample_rate / 1000:.2f} kHz"
        )

    def plot(self) -> None:
        """Visualize measurement data"""

        ift_values = {}

        f_sample = self.sample_rate / len(self.axes)
        try:
            plots = 3
            for axis in self.axes:
                samples = self.data[axis]
                ift_values[axis] = IFTLibrary.ift_value(samples, f_sample)
        except IFTLibraryException as error:
            plots = 2
            print(f"Unable to calculate IFT value: {error}", file=stderr)

        x_axis_format = FuncFormatter(
            lambda x, position: datetime.fromtimestamp(x).strftime(
                "%H:%M:%S.%f"
            )
        )

        figure, _ = plt.subplots(plots, 1, figsize=(20, 10))
        figure.canvas.manager.set_window_title("Acceleration Measurement")
        figure.suptitle(
            datetime.fromtimestamp(self.timestamp_start).strftime("%c"),
            fontsize=20,
        )
        subplot = plt.subplot(plots, 1, 1)
        subplot.xaxis.set_major_formatter(x_axis_format)
        plotter_function = scatter if self.args.scatter else plot
        for axis in self.axes:
            plotter_function(self.timestamps, self.data[axis], label=axis)
            plt.xlabel("Time")
            plt.ylabel("Raw Sensor Data")
        plt.legend()

        subplot = plt.subplot(plots, 1, 2)

        if ift_values:
            for axis in self.axes:
                plotter_function(self.timestamps, ift_values[axis], label=axis)
                plt.xlabel("Time")
                plt.ylabel("IFT Value")
            plt.legend()
            subplot.xaxis.set_major_formatter(x_axis_format)

            plt.subplot(plots, 1, 3)

        for axis in self.axes:
            plt.psd(
                self.data[axis] - self.data[axis].mean(),
                512,
                f_sample,
                label=axis,
            )
        plt.legend()

        if self.args.print:
            output_filepath = self.log_file.with_suffix(".pdf")
            pdf = PdfPages(output_filepath)
            pdf.savefig()
            pdf.close()
            print(f"Stored plotter output in “{output_filepath}”")
        else:
            plt.show()


# -- Main ---------------------------------------------------------------------


def main():
    plotter = Plotter(get_arguments())
    plotter.print_info()
    plotter.plot()


if __name__ == "__main__":
    main()
