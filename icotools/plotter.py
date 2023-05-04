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
        filepath = Path(args.input)
        self.args = args
        self.output_filepath = filepath.with_suffix(".pdf")
        self.data = read_hdf(filepath, key="acceleration")

        # Convert timestamps (in μs since start) to absolute timestamps
        with open_file(filepath, mode="r") as file:
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

        self.ift_values = {}
        self.plots = 3
        try:
            for axis in self.axes:
                samples = self.data[axis]
                self.ift_values[axis] = IFTLibrary.ift_value(
                    samples, self.sample_rate / len(self.axes)
                )
        except IFTLibraryException as error:
            self.plots = 2
            print(f"Unable to calculate IFT value: {error}", file=stderr)
        self.current_plot = 0

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

    def _init_plot(self) -> None:
        """Initialize graphical output"""

        figure, self.figure_axes = plt.subplots(
            self.plots, 1, figsize=(20, 10)
        )
        figure.canvas.manager.set_window_title("Acceleration Measurement")
        figure.suptitle(
            datetime.fromtimestamp(self.timestamp_start).strftime("%c"),
            fontsize=20,
        )

    def _plot_time(self, data, ylabel: str) -> None:
        """Plot time based data"""

        subplot = self.figure_axes[self.current_plot]
        subplot.xaxis.set_major_formatter(
            FuncFormatter(
                lambda x, position: datetime.fromtimestamp(x).strftime(
                    "%H:%M:%S.%f"
                )
            )
        )
        plotter_function = (
            subplot.scatter if self.args.scatter else subplot.plot
        )
        for axis in self.axes:
            plotter_function(self.timestamps, data[axis], label=axis)
            subplot.set_xlabel("Time")
            subplot.set_ylabel(ylabel)
        subplot.legend()

        self.current_plot += 1

    def _plot_psd(self) -> None:
        "Plot power spectral density data"

        subplot = self.figure_axes[self.current_plot]
        for axis in self.axes:
            subplot.psd(
                self.data[axis] - self.data[axis].mean(),
                512,
                self.sample_rate,
                label=axis,
            )
        subplot.legend()
        self.current_plot += 1

    def plot(self) -> None:
        """Visualize measurement data"""

        self._init_plot()
        self._plot_time(self.data, "Acceleration Data (g)")
        if self.ift_values:
            self._plot_time(self.ift_values, "IFT Value")
        self._plot_psd()

        if self.args.print:
            pdf = PdfPages(self.output_filepath)
            pdf.savefig()
            pdf.close()
            print(f"Stored plotter output in “{self.output_filepath}”")
        else:
            plt.show()


# -- Main ---------------------------------------------------------------------


def main():
    plotter = Plotter(get_arguments())
    plotter.print_info()
    plotter.plot()


if __name__ == "__main__":
    main()
