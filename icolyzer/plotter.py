"""
Created on Mon May 13 17:33:09 2019

@author: nleder
"""

import argparse
import sys

from argparse import ArgumentDefaultsHelpFormatter, Namespace
from datetime import datetime
from pathlib import Path
from sys import stderr

from numpy import log10, power
from matplotlib.collections import LineCollection
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.pyplot import show, subplots
from matplotlib.ticker import FuncFormatter
from pandas import read_hdf
from tables import open_file

from icolyzer.cli import file_exists
from icolyzer.iftlibrary import IFTLibrary, IFTLibraryException


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
        "-n",
        "--no-loss",
        action="store_true",
        default=False,
        help="visualize time periods containing lost data",
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


# pylint: disable=too-many-instance-attributes


class Plotter:
    """Visualize HDF5 ICOtronic measurement data"""

    def __init__(self, args: Namespace) -> None:
        """Initialize plotter object using given arguments

        Parameters
        ----------

        args:
            Parsed command line arguments

        """

        filepath = Path(args.input)
        self.args = args
        self.output_filepath = filepath.with_suffix(".pdf")
        self.data = read_hdf(filepath, key="acceleration")

        # Convert timestamps (in μs since start) to absolute timestamps
        with open_file(filepath, mode="r") as file:
            timestamp_start = datetime.fromisoformat(
                file.get_node("/acceleration").attrs["Start_Time"]
            ).timestamp()
        self.timestamps = (
            self.data["timestamp"] / 1_000_000
        ) + timestamp_start

        self.sample_rate = len(self.timestamps) / (
            self.timestamps.iloc[-1] - self.timestamps.iloc[0]
        )

        self.axes = [axis for axis in "xyz" if axis in self.data.keys()]

        self.ift_values = {}
        plots = 3
        try:
            for axis in self.axes:
                samples = self.data[axis]
                self.ift_values[axis] = IFTLibrary.ift_value(
                    samples, self.sample_rate / len(self.axes)
                )
        except IFTLibraryException as error:
            plots = 2
            print(f"Unable to calculate IFT value: {error}", file=stderr)

        figure, self.figure_axes = subplots(plots, 1, figsize=(20, 10))
        assert figure.canvas.manager is not None
        figure.canvas.manager.set_window_title("Acceleration Measurement")
        figure.suptitle(
            datetime.fromtimestamp(timestamp_start).strftime("%c"),
            fontsize=20,
        )

        # Used to skip to next subplot
        self.current_plot = 0
        self.subplot = self.figure_axes[self.current_plot]

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
        snr = 20 * log10(std_dev / (power(2, 16) - 1))
        print("SNR:")
        indent = " " * 2
        for axis in self.axes:
            print(
                f"{indent}{axis.upper()}: {snr[axis]:.2f} dB @ "
                f"{self.sample_rate / 1000:.2f} kHz"
            )
        if len(snr) >= 2:
            print(f"{indent}Minimum: {min(snr):.2f} dB")
            print(f"{indent}Maximum: {max(snr):.2f} dB")

    def _next_plot(self):
        """Activate next subplot"""

        if self.current_plot + 1 < len(self.figure_axes):
            self.current_plot += 1
            self.subplot = self.figure_axes[self.current_plot]

    def _plot_time(self, data, ylabel: str) -> None:
        """Plot time based data"""

        self.subplot.xaxis.set_major_formatter(
            FuncFormatter(
                lambda x, position: datetime.fromtimestamp(x).strftime(
                    "%H:%M:%S.%f"
                )
            )
        )
        plotter_function = (
            self.subplot.scatter if self.args.scatter else self.subplot.plot
        )

        for axis in self.axes:
            plotter_function(self.timestamps, data[axis], label=axis)
            self.subplot.set_xlabel("Time")
            self.subplot.set_ylabel(ylabel)

        if not self.args.no_loss:
            lost_data_lines: dict[
                str, list[tuple[tuple[int, int], tuple[int, int]]]
            ] = {axis: [] for axis in self.axes}
            for axis in self.axes:
                last_timestamp = self.timestamps[0]
                last_value = data[axis][0]
                last_counter = self.data["counter"][0]
                for counter, timestamp, value in zip(
                    self.data["counter"], self.timestamps, data[axis]
                ):
                    if counter != last_counter:
                        lost_packets = (counter - last_counter) % 256 - 1

                        if lost_packets > 0:
                            lost_data_lines[axis].append(
                                (
                                    (last_timestamp, last_value),
                                    (timestamp, value),
                                )
                            )

                    last_counter = counter
                    last_timestamp = timestamp
                    last_value = value

            for axis, lines in lost_data_lines.items():
                if len(lines) <= 0:
                    continue

                self.subplot.add_collection(LineCollection(lines, color="red"))

        self.subplot.legend()

        self._next_plot()

    def _plot_psd(self) -> None:
        "Plot power spectral density data"

        for axis in self.axes:
            self.subplot.psd(
                self.data[axis] - self.data[axis].mean(),
                512,
                self.sample_rate,
                label=axis,
            )
        self.subplot.legend()

        self._next_plot()

    def plot(self) -> None:
        """Visualize measurement data"""

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
            show()


# pylint: enable=too-many-instance-attributes


# -- Main ---------------------------------------------------------------------


def main():
    """Print information about and visualize ICOtronic HDF measurement data"""

    try:
        plotter = Plotter(get_arguments())
        plotter.print_info()
        plotter.plot()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
