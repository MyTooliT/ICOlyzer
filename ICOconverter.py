"""
Created on Wed Mar 30 08:54:27 2022

@author: Clemens
"""
import argparse
import glob
import pandas as pd
from pathlib import Path


def get_arguments():
    """
    Returns the given Function Parameters off the script-call

    @return Returns the parameters
    """
    parser = argparse.ArgumentParser(
        description='This script is used to convert hdf5 into other file types.' +
        ' For standard the file log.hdf5 in the file order is used and converted into csv.')
    parser.add_argument('-i',
                        '--input',
                        metavar='Inputfile',
                        help='Chose another input file')
    parser.add_argument('-e',
                        '--excel',
                        action='store_true',
                        help='Convert to excel instead of csv')
    args = parser.parse_args()

    excel = False

    if args.input is not None:
        filename = args.input
        print('INPUTFILE CHANGED')
    else:
        filename = 'log.hdf5'
    if args.excel is True:
        excel = True
    return filename, excel


def main():
    """
    Main function of the ICOconverter.
    """
    getfolder = False
    log_file, convertexcel = get_arguments()
    if Path(log_file).is_dir():
        getfolder = True
    if convertexcel is True:
        print('Conversion to .xlsx')
    if convertexcel is False:
        print('Conversion to .csv')
    print('Starting the conversion process')
    if getfolder is False:
        loaded_file = pd.read_hdf(log_file, key="acceleration")
        print('Starting the conversion of: ' + log_file)
        if convertexcel is True:
            loaded_file.to_excel(Path(log_file).with_suffix('.xlsx'),
                                 index=False,
                                 header=True)
        if convertexcel is False:
            loaded_file.to_csv(Path(log_file).with_suffix('.csv'),
                               index=False,
                               header=True)
    if getfolder is True:
        for file_path in glob.glob(f"{log_file}/*.hdf5"):
            print('Starting the conversion of: ' + file_path)
            loaded_file = pd.read_hdf(file_path, key="acceleration")
            if convertexcel is True:
                loaded_file.to_excel(Path(file_path).with_suffix('.xlsx'),
                                     index=False,
                                     header=True)
            if convertexcel is False:
                loaded_file.to_csv(Path(file_path).with_suffix('.csv'),
                                   index=False,
                                   header=True)

    print('Finished the conversion process')


if __name__ == "__main__":
    main()
