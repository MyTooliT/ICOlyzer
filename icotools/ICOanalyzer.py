"""
Created on Fri Mar 27 08:16:22 2020

@author: Clemens
"""
import argparse
import pandas as pd


class FileInformation:
    """
    This class contains the information about the to be analyzed log-file.
    """

    def __init__(self, filename):
        self.filename = filename
        self.packet_loss = 0
        self.packets = 0
        self.datapoints = 0
        self.out_of_range = 0
        self.out_of_range2 = 0
        self.out_of_range3 = 0


def get_arguments(element):
    """
    Returns the given Function Parameters off the script-call

    @return Returns the parameters
    """
    parser = argparse.ArgumentParser(
        description="This script is used to calculate the occurred packet "
        + "loss of an ICOc log data. Additionally it can be used to get "
        + "the % of sample points outside of a given range"
        + " as long as a min or max is defined via additional "
        + "parameters at the script call."
    )
    parser.add_argument(
        "-m", "--min", metavar="MIN-Value", help="Define a Min-Value"
    )
    parser.add_argument(
        "-v", "--value", metavar="MAX-Value", help="Define a Max-Value"
    )
    parser.add_argument(
        "-i", "--input", metavar="Inputfile", help="Chose another input file"
    )
    parser.add_argument(
        "-d",
        "--details",
        action="store_true",
        help="Show more Information about Paketloss",
    )
    args = parser.parse_args()
    details_on = False

    if args.min is not None:
        test_value_min = float(args.min)
        print("MINIMUM CHANGED")
    else:
        test_value_min = -1
    if args.value is not None:
        test_value_max = float(args.value)
        print("MAXIMUM CHANGED")
    else:
        test_value_max = 1
    if args.input is not None:
        element.filename = args.input
        print("INPUTFILE CHANGED")
    if args.details is True:
        details_on = True
        print("DETAILS ENABLED")
    else:
        details_on = False
    return element, test_value_min, test_value_max, details_on


def main():
    """
    Main function of the ICOanalyzer.
    """
    details_on = False
    test_value_max = 1
    test_value_min = -1
    element = FileInformation("log.hdf5")

    element, test_value_min, test_value_max, details_on = get_arguments(
        element
    )

    print("Input file is: " + element.filename)
    data = pd.read_hdf(element.filename, key="acceleration")

    first_counter = data["counter"][0]
    for datapoint in data["counter"]:
        if (datapoint == first_counter + 1) or (
            datapoint == 0 and first_counter == 255
        ):
            element.packets = element.packets + 1
            first_counter = datapoint
        elif datapoint != first_counter:
            lost_packets = datapoint - first_counter - 1
            if details_on is True:
                if lost_packets < 0:
                    print(str(lost_packets + 255 + 1) + " Packets lost")
                else:
                    print(str(lost_packets) + " Packets lost")
            if lost_packets < 0:
                lost_packets = lost_packets + 255
            first_counter = datapoint
            element.packets = element.packets + lost_packets + 1
            element.packet_loss = element.packet_loss + lost_packets
    x_data = None
    y_data = None
    z_data = None
    try:
        x_data = data["x"]
    except KeyError:
        pass
    try:
        y_data = data["y"]
    except KeyError:
        pass
    try:
        z_data = data["z"]
    except KeyError:
        pass

    while (element.datapoints) < (len(data["timestamp"])):
        if x_data is not None:
            acc_data = x_data[element.datapoints]
            if (acc_data > test_value_max) or (acc_data < test_value_min):
                element.out_of_range = element.out_of_range + 1
        if y_data is not None:
            acc_data2 = y_data[element.datapoints]
            if (acc_data2 > test_value_max) or (acc_data2 < test_value_min):
                element.out_of_range2 = element.out_of_range2 + 1
        if z_data is not None:
            acc_data3 = z_data[element.datapoints]
            if (acc_data3 > test_value_max) or (acc_data3 < test_value_min):
                element.out_of_range3 = element.out_of_range3 + 1
        element.datapoints = element.datapoints + 1
    print("PACKETLOSS:")
    print(str(round((element.packet_loss / element.packets) * 100, 2)) + "%")
    print("DATAPOINTS:")
    if x_data is not None:
        percent_overflow = (element.out_of_range / element.datapoints) * 100
        percent_overflow = round(percent_overflow, 2)
        print(
            "X-AXIS: "
            + str(element.out_of_range)
            + " Samples were over "
            + str(test_value_max)
            + "g or below "
            + str(test_value_min)
            + "g ("
            + str(percent_overflow)
            + "%)"
        )
    if y_data is not None:
        percent_overflow2 = (element.out_of_range2 / element.datapoints) * 100
        percent_overflow2 = round(percent_overflow2, 2)
        print(
            "Y-AXIS: "
            + str(element.out_of_range2)
            + " Samples were over "
            + str(test_value_max)
            + "g or below "
            + str(test_value_min)
            + "g ("
            + str(percent_overflow2)
            + "%)"
        )
    if z_data is not None:
        percent_overflow3 = (element.out_of_range3 / element.datapoints) * 100
        percent_overflow3 = round(percent_overflow3, 2)
        print(
            "Z-AXIS: "
            + str(element.out_of_range3)
            + " Samples were over "
            + str(test_value_max)
            + "g or below "
            + str(test_value_min)
            + "g ("
            + str(percent_overflow3)
            + "%)"
        )


if __name__ == "__main__":
    main()
