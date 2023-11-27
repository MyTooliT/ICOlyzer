"""Utility code for working with command line data"""

# -- Imports ------------------------------------------------------------------

from argparse import ArgumentTypeError
from pathlib import Path


# -- Functions ----------------------------------------------------------------


def file_exists(filepath: str) -> str:
    """Check if the given path points to an existing file

    Parameters
    ----------

    filepath:
        Path to the file

    Raises
    ------

    An argument type error in case the the filepath does not point to an
    existing file

    Returns
    -------

    The given filepath on success

    """

    if not Path(filepath).exists():
        raise ArgumentTypeError(f"“{filepath}” does not exist")

    if not Path(filepath).is_file():
        raise ArgumentTypeError(f"“{filepath}” does not point to a file")

    return filepath
