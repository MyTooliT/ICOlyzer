"""
Created on Wed Mar 30 08:54:27 2022

@author: Clemens
"""

import argparse
import glob
from pathlib import Path
from sys import stderr

import pandas as pd


def get_arguments():
    """
    Returns the given Function Parameters off the script-call

    @return Returns the parameters
    """
    parser = argparse.ArgumentParser(
        description=(
            "This script is used to convert hdf5 into other file types. "
            "For standard the file log.hdf5 in the file order is used and "
            "converted into csv."
        )
    )
    parser.add_argument(
        "inputs",
        metavar="Inputfiles",
        default=["log.hdf5"],
        nargs="*",
        help="Chosen input files (default: log.hdf5)",
    )
    parser.add_argument(
        "-e",
        "--excel",
        action=argparse.BooleanOptionalAction,
        help="Convert to excel instead of csv",
    )
    args = parser.parse_args()

    return args.inputs, args.excel


def main():
    """
    Main function of the ICOconverter.
    """

    inputs, convertexcel = get_arguments()
    filepaths = []

    # Collect files
    for filepath in inputs:
        path = Path(filepath)
        if path.is_dir():
            filepaths.extend(glob.glob(f"{filepath}/*.hdf5"))
        elif path.is_file():
            filepaths.append(filepath)
        elif not path.is_file():
            print(f"Skipping non existing file “{filepath}”", file=stderr)
        else:
            print(
                f"Skipping “{filepath}” since it is "
                "neither a directory nor a file",
                file=stderr,
            )

    print("Starting the conversion process")
    for log_file in filepaths:
        loaded_file = pd.read_hdf(log_file, key="acceleration")
        export_file = Path(log_file).with_suffix(
            ".xlsx" if convertexcel else ".csv"
        )
        print(f"Converting “{log_file}” to “{export_file}”")
        conversion_method = (
            loaded_file.to_excel if convertexcel else loaded_file.to_csv
        )
        conversion_method(export_file, index=False, header=True)

    print("Finished the conversion process")


if __name__ == "__main__":
    main()
