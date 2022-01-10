"""
Created on Mon May 13 17:33:09 2019

@author: nleder
"""

# Load the Pandas libraries with alias 'pd'
import argparse
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def get_arguments():
    """
    Returns the given Function Parameters off the script-call

    @return Returns the parameters
    """
    parser = argparse.ArgumentParser(
        description='This script is used to plot an existing ICOc log-data.' +
        ' For standard the file log.hdf5 in the file order is used.')
    parser.add_argument('-i',
                        '--input',
                        metavar='Inputfile',
                        help='Chose another input file')
    args = parser.parse_args()

    if args.input is not None:
        filename = args.input
        print('INPUTFILE CHANGED')
    else:
        filename = 'log.hdf5'
    return filename


def main():
    """
    Main function of the ICOplotter
    """
    log_file = get_arguments()
    data = pd.read_hdf(log_file, key="acceleration")
    timestamps = data["timestamp"]
    n_points = len(timestamps)

    f_sample = n_points / \
        (timestamps.iloc[n_points-1]-timestamps.iloc[0])*1000000
    stats = data.describe()

    x_data = data.get('x')
    y_data = data.get('y')
    z_data = data.get('z')
    nr_of_axis = len(
        [True for axis in (x_data, y_data, z_data) if axis is not None])

    if nr_of_axis < 1 or nr_of_axis > 3:
        print(f"Error: Incorrect number of axis: “{nr_of_axis}”",
              file=sys.stderr)
        sys.exit(1)

    axes = [
        axis for axis, data in [('x', x_data), ('y', y_data), ('z', z_data)]
        if data is not None
    ]

    std_dev = stats.loc['std', axes]
    print(" ".join([
        f"Avg {axis.upper()}: {int(stats.loc['mean', [axis]])}"
        for axis in axes
    ]))

    snr = 20 * np.log10(std_dev / (np.power(2, 16) - 1))
    print(f"SNR of this file is : {min(snr):.2f} dB and {max(snr):.2f} dB "
          f"@ {f_sample / 1000:.2f} kHz")

    plt.subplots(2, 1, figsize=(20, 10))
    plt.subplot(211)
    for axis in axes:
        plt.plot(timestamps, data[axis])

    plt.subplot(212)
    for axis in axes:
        plt.psd(data[axis] - data[axis].mean(), 512, f_sample)
    plt.show()


if __name__ == "__main__":
    main()
