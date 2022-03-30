"""
Created on Wed Mar 30 08:54:27 2022

@author: Clemens
"""
import argparse
import pandas as pd
import os


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
    parser.add_argument('-f',
                        '--folder',
                        action='store_true',
                        help='Fileinput is a folder and not a file')
    parser.add_argument('-e',
                        '--excel',
                        action='store_true',
                        help='Convert to excel instead of csv')
    args = parser.parse_args()

    folder_selected = False
    excel = False

    if args.input is not None:
        filename = args.input
        print('INPUTFILE CHANGED')
    else:
        filename = 'log.hdf5'
    if args.folder is True:
        folder_selected = True
        if filename == 'log.hdf5':
            filename = '.'
    if args.excel is True:
        excel = True
    return filename, folder_selected, excel


def main():
    """
    Main function of the ICOconverter.
    """

    log_file, getfolder, convertexcel = get_arguments()
    print('Starting the conversion process')
    if getfolder is False:
        loaded_file = pd.read_hdf(log_file, key="acceleration")
        if convertexcel is True:
            name = log_file[:-5]
            name = name + '.xlsx'
            loaded_file.to_excel(name, index=False, header=True)
        if convertexcel is False:
            name = log_file[:-5]
            name = name + '.csv'
            loaded_file.to_csv(name, index=False, header=True)
    if getfolder is True:
        for file in os.listdir(log_file):
            if file.endswith(".hdf5"):
                print('Starting the conversion of: '+file)
                file_path = os.path.join(log_file, file)
                loaded_file = pd.read_hdf(file_path, key="acceleration")
                if convertexcel is True:
                    name = file_path[:-5]
                    name = name + '.xlsx'
                    loaded_file.to_excel(name, index=False, header=True)
                if convertexcel is False:
                    name = file_path[:-5]
                    name = name + '.csv'
                    loaded_file.to_csv(name, index=False, header=True)

    print('Finished the conversion process')


if __name__ == "__main__":
    main()
