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
        description='This script is used to plot an existing ICOc log-data. For standard the file log.hdf5 in the file order is used.')
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
    log_file = get_arguments()
    data = pd.read_hdf(log_file, key="acceleration")
    timestamps = data["timestamp"]
    n_points = len(data["timestamp"])

    f_sample = n_points / \
        (timestamps.iloc[n_points-1]-timestamps.iloc[0])*1000000
    stats = data.describe()

    nr_of_axis = 0
    x = None
    y = None
    z = None
    try:
        x = data["x"]
        nr_of_axis = nr_of_axis + 1
    except:
        pass
    try:
        y = data["y"]
        nr_of_axis = nr_of_axis + 1
    except:
        pass
    try:
        z = data["z"]
        nr_of_axis = nr_of_axis + 1
    except:
        pass

    if(nr_of_axis == 1):
        std_dev = stats.loc['std', ['x']]
        SNR = 20*np.log10(std_dev/(np.power(2, 16)-1))
        print("SNR of this file is : {:.2f} dB and {:.2f} dB @ {:.2f} kHz".format(
            min(SNR), max(SNR), f_sample/1000))

    elif(nr_of_axis == 3):
        std_dev = stats.loc['std', ['x', 'y', 'z']]
        print("Avg  X: %d Y: %d Z: %d" % (stats.loc['mean', ['x']],
                                          stats.loc['mean', ['y']],
                                          stats.loc['mean', ['z']]))
        SNR = 20*np.log10(std_dev/(np.power(2, 16)-1))
        print("SNR of this file is : {:.2f} dB and {:.2f} dB @ {:.2f} kHz".format(
            min(SNR), max(SNR), f_sample/1000))
    elif(nr_of_axis == 2):
        if x is None:
            std_dev = stats.loc['std', ['y', 'z']]
            print("Avg  Y: %d Z: %d " % (stats.loc['mean', ['y']],
                                         stats.loc['mean', ['z']]))
            SNR = 20*np.log10(std_dev/(np.power(2, 16)-1))
            print("SNR of this file is : {:.2f} dB and {:.2f} dB @ {:.2f} kHz".format(
                min(SNR), max(SNR), f_sample/1000))
        elif y is None:
            std_dev = stats.loc['std', ['x', 'z']]
            print("Avg  X: %d Z: %d " % (stats.loc['mean', ['x']],
                                         stats.loc['mean', ['z']]))
            SNR = 20*np.log10(std_dev/(np.power(2, 16)-1))
            print("SNR of this file is : {:.2f} dB and {:.2f} dB @ {:.2f} kHz".format(
                min(SNR), max(SNR), f_sample/1000))
        elif z is None:
            std_dev = stats.loc['std', ['x', 'y']]
            print("Avg  X: %d Y: %d " % (stats.loc['mean', ['x']],
                                         stats.loc['mean', ['y']]))
            SNR = 20*np.log10(std_dev/(np.power(2, 16)-1))
            print("SNR of this file is : {:.2f} dB and {:.2f} dB @ {:.2f} kHz".format(
                min(SNR), max(SNR), f_sample/1000))
    else:
        print("ERROR: UNDEFINED NR OF AXIS")

    if(nr_of_axis == 1):
        f, axs = plt.subplots(2, 1, figsize=(20, 10))
        plt.subplot(211)
        plt.plot(timestamps, data["x"])
        plt.subplot(212)
        plt.psd(data["x"]-data["x"].mean(), 512, f_sample)
        plt.show()
    elif(nr_of_axis == 3):
        f, axs = plt.subplots(2, 1, figsize=(20, 10))
        plt.subplot(211)
        plt.plot(timestamps, data[['x', 'y', 'z']])
        plt.subplot(212)
        plt.psd(data['x']-data['x'].mean(), 512, f_sample)
        plt.show()
    elif(nr_of_axis == 2):
        if x is None:
            f, axs = plt.subplots(2, 1, figsize=(20, 10))
            plt.subplot(211)
            plt.plot(timestamps, data[['y', 'z']])
            plt.subplot(212)
            plt.psd(data['y']-data['y'].mean(), 512, f_sample)
            plt.show()
        elif y is None:
            f, axs = plt.subplots(2, 1, figsize=(20, 10))
            plt.subplot(211)
            plt.plot(timestamps, data[['x', 'z']])
            plt.subplot(212)
            plt.psd(data['x']-data['x'].mean(), 512, f_sample)
            plt.show()
        elif z is None:
            f, axs = plt.subplots(2, 1, figsize=(20, 10))
            plt.subplot(211)
            plt.plot(timestamps, data[['x', 'y']])
            plt.subplot(212)
            plt.psd(data['x']-data['x'].mean(), 512, f_sample)
            plt.show()


if __name__ == "__main__":
    main()
