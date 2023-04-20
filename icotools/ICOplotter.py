"""
Created on Mon May 13 17:33:09 2019

@author: nleder
"""

import argparse
import sys

from argparse import ArgumentDefaultsHelpFormatter
from ctypes import CDLL, c_double, c_size_t, POINTER, sizeof
from pathlib import Path
from platform import machine, system
from sys import stderr
from typing import Collection, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd  # Load the Pandas libraries with alias 'pd'

from numpy import array_split


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


class IFTLibrary:
    """Wrapper for IFT figure of merit (FOM) library"""

    class IFTValueException(Exception):
        """Raised if there are any problems with the IFT value calculation"""

    basename_library = (
        "libift.so"
        if system() == "Linux"
        else "libift.dylib" if system() == "Darwin" else "ift.dll"
    )
    filepath_library = (Path(__file__).parent / basename_library).as_posix()

    try:
        library = CDLL(filepath_library)
        ift_value_function = library.ift_value
        ift_value_function.argtypes = [
            POINTER(c_double),  # double samples[]
            c_size_t,  # size_t sample_size
            c_double,  # double window_length
            c_double,  # double sampling_frequency
            c_double,  # A2
            c_double,  # A3
            c_double,  # A4
            c_double,  # A5
            POINTER(c_double),  # double output[]
        ]
        available = True
    except OSError:
        available = False

    @classmethod
    def ift_value(
        cls,
        samples: Collection[float],
        sampling_frequency: float,
        window_length: float = 0.05,
    ) -> List[float]:
        """Calculate the IFT value for the given input

        Preconditions
        -------------

        Please note, that you have to provide samples for 0.6 seconds or more,
        i.e. `len(samples) >= 0.6 * sampling_frequency` has to be true

        Arguments
        ---------

        samples:
            The sample values for which the IFT value should be calculated

        sampling_frequency:
            The frequency used to capture the input samples. If you specify a
            value that is below `200`, then the default frequency of `9524` Hz
            will be used instead.

        window_length:
            Possible values are between 0.005 and 1 second. If you
            specify a value out of this range, then the function will use a
            default window length of 0.05 seconds (50 ms). This default
            value will also be used, if the amount of samples for the given
            window length (=`floor(window_length*sampling_frequency)`) is
            larger than (or equal to) the sample size.

        Returns
        -------

        A list containing the calculated IFT values for the given input samples

        Example
        -------

        Calculate the IFT values for 0.6 seconds of sample data

        >>> samples = range(600)
        >>> values = IFTLibrary.ift_value(samples=samples,
        ...                               sampling_frequency=1000,
        ...                               window_length=0.005)
        >>> values # doctest:+ELLIPSIS
        [3.5, 3.5, ..., 3.5, 3.5]
        >>> len(values) == len(samples)
        True

        Calculating the IFT value for less than 0.6 s of sample data fails

        >>> IFTLibrary.ift_value(
        ...     samples=range(599), sampling_frequency=1000,
        ...     window_length=0.005) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        IFTValueException: Sample size too small

        """

        size_t_max = 2 ** (sizeof(c_size_t) * 8) - 1
        len_samples = len(samples)

        # In the unlikely case that we want to retrieve the IFT value for more
        # than `size_t` values we split the input into equal parts.
        #
        # We want large parts (“close” to `size_t`), since otherwise we
        # might feed with arrays below the minimum size.
        parts = len_samples // (size_t_max - 1) + 1

        output: List[float] = []
        for samples_part_array in array_split(list(samples), parts):
            samples_part = list(samples_part_array)
            len_samples_part = len(samples_part)
            samples_arg = (c_double * len_samples_part)(*samples_part)
            output_part = (c_double * len_samples_part)()

            status = cls.ift_value_function(
                samples_arg,
                len_samples_part,
                window_length,
                sampling_frequency,
                0,
                0,
                0,
                0,
                output_part,
            )

            if status != 0:
                message = "Sample size too "
                message += "large" if status == -1 else "small"
                raise IFTLibrary.IFTValueException(message)

            output.extend(output_part)

        return list(output)


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

    if not IFTLibrary.available:
        print(
            "Warning: IFT library not available for current architecture",
            file=stderr,
        )
        plots = 2
    else:
        plots = 3

    plt.subplots(plots, 1, figsize=(20, 10))
    plt.subplot(plots, 1, 1)
    for axis in axes:
        plt.plot(timestamps, data[axis], label=axis)
        plt.xlabel("Time")
        plt.ylabel("Raw Sensor Data")
    plt.legend()

    plt.subplot(plots, 1, 2)
    if n_points < 0.6 * f_sample:
        print(
            (
                "Warning: At least 0.6 seconds of samples required to "
                "calculate IFT value"
            ),
            file=stderr,
        )
    elif IFTLibrary.available:
        for axis in axes:
            samples = data[axis]
            ift_values = IFTLibrary.ift_value(samples, f_sample)
            plt.plot(timestamps, ift_values, label=axis)
            plt.xlabel("Time")
            plt.ylabel("IFT Value")
        plt.legend()
        plt.subplot(plots, 1, 3)
    else:
        print(
            (
                "Warning: IFT value calculation is not available on your\n"
                f"• OS: “{system()}” or\n"
                f"• CPU architecture: “{machine()}”"
            ),
            file=stderr,
        )

    for axis in axes:
        plt.psd(data[axis] - data[axis].mean(), 512, f_sample, label=axis)
    plt.legend()

    plt.show()


if __name__ == "__main__":
    main()
