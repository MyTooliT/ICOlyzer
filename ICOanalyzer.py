"""
Created on Fri Mar 27 08:16:22 2020

@author: Clemens
"""
import argparse
import pandas as pd


class FileInformation():
    """
    This class contains the information about the to be analyzed log-file.
    """

    def __init__(self, filename):
        self.filename = filename
        self.packet_loss = 0
        self.packets = 0
        self.datapoints = 0
        self.out_of_range = 0


def get_arguments(element):
    """
    Returns the given Function Parameters off the script-call

    @return Returns the parameters
    """
    parser = argparse.ArgumentParser(
        description='This script is used to calculate the occurred packet loss of an ICOc log data. Additionally it can be used to get the percentage of sample points outside of a given range as long as a min or max is defined via additional parameters at the script call.')
    parser.add_argument('-m', '--min', metavar='MIN-Value',
                        help='Define a Min-Value')
    parser.add_argument('-v', '--value', metavar='MAX-Value',
                        help='Define a Max-Value')
    parser.add_argument('-i', '--input', metavar='Inputfile',
                        help='Chose another input file')
    parser.add_argument('-d', '--details', action='store_true',
                        help='Show more Information about Paketloss')
    args = parser.parse_args()

    check_values = False
    details_on = False

    if args.min is not None:
        test_value_min = float(args.min)
        check_values = True
    else:
        test_value_min = -1
    if args.value is not None:
        test_value_max = float(args.value)
        check_values = True
    else:
        test_value_max = 1
    if args.input is not None:
        element.filename = args.input
        print('INPUTFILE CHANGED')
    if args.details is True:
        details_on = True
        print('DETAILS ENABLED')
    else:
        details_on = False
    if check_values is True:
        print('VALUE-CHECK ENABLED')
    return element, test_value_min, test_value_max, check_values, details_on


def main():
    """
    Main function of the ICOanalyzer.
    """
    check_values = False
    details_on = False
    test_value_max = 1
    test_value_min = -1
    element = FileInformation('log.hdf5')

    element, test_value_min, test_value_max, check_values, details_on = get_arguments(
        element)

    print('Input file is: ' + element.filename)
    print("Starting ckeck of " + element.filename)
    data = pd.read_hdf(element.filename, key="acceleration")
    first_counter = data["counter"][0]
    for datapoint in data["counter"]:
        if (datapoint == first_counter+1) or (datapoint == 0 and first_counter == 255):
            element.packets = element.packets + 1
            first_counter = datapoint
        elif datapoint != first_counter:
            lost_packets = datapoint-first_counter - 1
            if details_on is True:
                if lost_packets < 0:
                    print(str(lost_packets+255+1)+" Packets lost")
                else:
                    print(str(lost_packets)+" Packets lost")
            if lost_packets < 0:
                lost_packets = lost_packets + 255
            first_counter = datapoint
            element.packets = element.packets + lost_packets + 1
            element.packet_loss = element.packet_loss + lost_packets
        while (element.datapoints) < (len(data["x"])):
            acc_data = data["x"][element.datapoints]
            element.datapoints = element.datapoints + 1
            if (acc_data > test_value_max) or (acc_data < test_value_min):
                element.out_of_range = element.out_of_range + 1
    print("Finished ckeck of " + element.filename)
    print("PACKETLOSS: " +
          str(round((element.packet_loss / element.packets)*100, 2)) + "%")
    if check_values is True:
        percent_overflow = (element.out_of_range /
                            element.datapoints)*100
        percent_overflow = round(percent_overflow, 2)
        print("DATAPOINTS: " + str(element.out_of_range) +
              " Samples were over " + str(test_value_max) +
              "g\u2080 or below " + str(test_value_min) +
              "g\u2080 ("+str(percent_overflow)+"%)")


if __name__ == "__main__":
    main()
