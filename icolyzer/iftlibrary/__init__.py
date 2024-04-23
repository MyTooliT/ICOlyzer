"""Python bindings for the Figure of Merit (FOM) library from the IFT"""

# -- Version ------------------------------------------------------------------

__version__ = "0.1.0"

# -- Exports ------------------------------------------------------------------

from .ift import (
    IFTLibrary,
    IFTLibraryException,
    IFTLibraryNotAvailable,
    IFTValueException,
)

ift_value = IFTLibrary.ift_value
