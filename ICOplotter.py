"""
Created on Mon May 13 17:33:09 2019

@author: nleder
"""

# Load the Pandas libraries with alias 'pd'
import argparse
import pandas as pd

import matplotlib.pyplot as plt
import numpy as np


def get_arguments():
    """
    Returns the given Function Parameters off the script-call

    @return Returns the parameters
    """
    parser = argparse.ArgumentParser(
        description='This script is used to plot an existing ICOc log-data.' +
        ' For standard the file log.hdf5 in the file order is used.')
    parser.add_argument('-i', '--input', metavar='Inputfile',
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

    if nr_of_axis == 1:
        axis = ('x'
                if x_data is not None else 'y' if y_data is not None else 'z')
        std_dev = stats.loc['std', [axis]]
        snr = 20 * np.log10(std_dev / (np.power(2, 16) - 1))
        print("SNR of this file is : {:.2f} dB and {:.2f} dB @ {:.2f} kHz".
              format(min(snr), max(snr), f_sample / 1000))
    elif nr_of_axis == 3:
        std_dev = stats.loc['std', ['x', 'y', 'z']]
        print("Avg  X: %d Y: %d Z: %d" % (stats.loc['mean', ['x']],
                                          stats.loc['mean', ['y']],
                                          stats.loc['mean', ['z']]))
        snr = 20*np.log10(std_dev/(np.power(2, 16)-1))
        print("SNR of this file is : {:.2f} dB and {:.2f} dB @ {:.2f} kHz".format(
            min(snr), max(snr), f_sample/1000))
    elif nr_of_axis == 2:
        if x_data is None:
            std_dev = stats.loc['std', ['y', 'z']]
            print("Avg  Y: %d Z: %d " % (stats.loc['mean', ['y']],
                                         stats.loc['mean', ['z']]))
            snr = 20*np.log10(std_dev/(np.power(2, 16)-1))
            print("SNR of this file is : {:.2f} dB and {:.2f} dB @ {:.2f} kHz".format(
                min(snr), max(snr), f_sample/1000))
        elif y_data is None:
            std_dev = stats.loc['std', ['x', 'z']]
            print("Avg  X: %d Z: %d " % (stats.loc['mean', ['x']],
                                         stats.loc['mean', ['z']]))
            snr = 20*np.log10(std_dev/(np.power(2, 16)-1))
            print("SNR of this file is : {:.2f} dB and {:.2f} dB @ {:.2f} kHz".format(
                min(snr), max(snr), f_sample/1000))
        elif z_data is None:
            std_dev = stats.loc['std', ['x', 'y']]
            print("Avg  X: %d Y: %d " % (stats.loc['mean', ['x']],
                                         stats.loc['mean', ['y']]))
            snr = 20*np.log10(std_dev/(np.power(2, 16)-1))
            print("SNR of this file is : {:.2f} dB and {:.2f} dB @ {:.2f} kHz".format(
                min(snr), max(snr), f_sample/1000))
    else:
        print("ERROR: UNDEFINED NR OF AXIS")
    fig, axs = plt.subplots(2, 1, figsize=(20, 10))
    plt.subplot(211)
    if x_data is not None:
        plt.plot(timestamps, data["x"])
    if y_data is not None:
        plt.plot(timestamps, data["y"])
    if z_data is not None:
        plt.plot(timestamps, data["z"])
    plt.subplot(212)
    if x_data is not None:
        plt.psd(data["x"]-data["x"].mean(), 512, f_sample)
    if y_data is not None:
        plt.psd(data["y"]-data["y"].mean(), 512, f_sample)
    if z_data is not None:
        plt.psd(data["z"]-data["z"].mean(), 512, f_sample)
    plt.show()


if __name__ == "__main__":
    main()
