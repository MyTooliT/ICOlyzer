"""Support code for calculating the IFT value"""

# -- Imports ------------------------------------------------------------------

from ctypes import CDLL, c_double, c_size_t, POINTER, sizeof
from pathlib import Path
from platform import machine, system
from typing import Collection, List

from numpy import array_split

# -- Classes ------------------------------------------------------------------


class IFTLibraryException(Exception):
    """Raised if there are any problems concerning the IFT library"""


class IFTLibraryNotAvailable(IFTLibraryException):
    """Raised if there are any problems loading the IFT library"""


class IFTValueException(IFTLibraryException):
    """Raised if there are any problems with the IFT value calculation"""


# pylint: disable=too-few-public-methods


class IFTLibrary:
    """Wrapper for IFT figure of merit (FOM) library"""

    system_machine_to_lib = {
        "Linux": {
            "aarch64": "libift-arm64.so",
            "armv7l": "libift-armv7l.so",
            "x86_64": "libift-x64.so",
        },
        "Darwin": {"arm64": "libift.dylib", "x86_64": "libift.dylib"},
        "Windows": {"AMD64": "ift.dll"},
    }
    exception = None

    try:
        basename_library = system_machine_to_lib[system()][machine()]
    except KeyError:
        exception = IFTLibraryNotAvailable(
            f"IFT library not available for system “{system()} ({machine()})”"
        )

    if exception is None:
        filepath_library = (
            Path(__file__).parent / "lib" / basename_library
        ).as_posix()

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
        except OSError:
            exception = IFTLibraryNotAvailable("Unable to load IFT library")

    @classmethod
    def ift_value(
        cls,
        samples: Collection[float],
        sampling_frequency: float = 9524,
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

        if cls.exception is not None:
            raise cls.exception

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
                raise IFTValueException(message)

            output.extend(output_part)

        return list(output)


# pylint: enable=too-few-public-methods
