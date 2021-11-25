# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 08:16:22 2020

@author: Clemens
"""

import os
import sys,getopt

# Load the Pandas libraries with alias 'pd' 
import pandas as pd 

class datei():
    def __init__(self,filename):
        self.filename = filename
        self.packet_loss = 0
        self.packets = 0
        self.datapoints = 0
        self.out_of_range = 0


def main(argv):
    dateien = []
    log_location = '.\\'
    check_values = True
    details_on = False
    hdf5_read = False
    test_value_max = 35000	#error bounds that cover abitray orientation but no artefacts
    test_value_min = 31500  #was 32000
    
	
    try:
        opts, args = getopt.getopt(argv, "hi:v:m:df",["ifolder=","value=","min=","details","hdf5"])
    except getopt.GetoptError:
        print('watch_simple_plot.py -i <inputfolder> -v <max_value> -m <minimum_value>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('watch_simple_plot.py -i <inputfolder> -v <max_value> -m <minimum_value>')
            sys.exit()
        elif opt in ("-i", "--ifolder"):
            log_location = arg 
        elif opt in ("-v", "--value"):
            test_value_max = int(arg)
            check_values = True
        elif opt in ("-m", "--min"):
            test_value_min = int(arg)
            check_values = True
        elif opt in ("-d", "--details"):
            details_on = True
        elif opt in ("-f", "--hdf5"):
            hdf5_read = True
    print('Input folder is: ' + log_location)
        
                
    lookup="Start"

    if hdf5_read == True:
        test_value_max = 1	#hdf5 is in g not absoulte
        test_value_min = -1  #hdf5 is in g not absoulte
        print("DATAS TO CHECK ARE:")
        for file in os.listdir(log_location):
            if file.endswith(".hdf5"):
                print(os.path.join(log_location,file))
                dateien.append(datei(file))            
        print("")
        for element in dateien:
            log_file = element.filename
            print("Starting ckeck of " + element.filename)
            data = pd.read_hdf(log_location +"\\"+ log_file, key="acceleration")
            
            counter = data["counter"]
            acc_datas = data["x"]
#            datalen=len(acc_datas)  #TESTING!!!!!!
            first_counter=counter[0]
            for datapoint in counter:
                if datapoint==first_counter:
                    continue
                elif (datapoint==first_counter+1) or (datapoint==0 and first_counter==255):
                    element.packets = element.packets + 1
                    first_counter = datapoint
                else:
                    lost_packets = datapoint-first_counter - 1
                    ##Next if/else is to see number of lost packets:
                    if details_on == True:
                        if lost_packets < 0:
                            print(str(lost_packets+255+1)+" Packets lost")
                        else:
                            print(str(lost_packets)+" Packets lost")
                    if lost_packets < 0 :
                        lost_packets = lost_packets + 255
                    first_counter = datapoint
                    element.packets = element.packets + lost_packets + 1
                    element.packet_loss = element.packet_loss + lost_packets
                while (element.datapoints) < (len(acc_datas)):
                    acc_data = acc_datas[element.datapoints]
                    element.datapoints = element.datapoints + 1
#                    print(str(element.datapoints)+"/"+str(datalen)+" : "+str(acc_data)) #TESTING!!!!!
                    if (acc_data > test_value_max) or (acc_data < test_value_min):
                        element.out_of_range = element.out_of_range + 1
            print("Finished ckeck of " + element.filename)
        print("Finished ckecking of all files")
        print("RESULTS PACKETLOSS:")
        for element in dateien:
            percent_packetloss = (element.packet_loss / element.packets)*100
            percent_packetloss = round(percent_packetloss,2)
            print(element.filename + " : " + str(percent_packetloss) + "%")
        if check_values == True:
            print("RESULTS OF DATAPOINTS:")
            for element in dateien:
                percent_overflow = (element.out_of_range / element.datapoints)*100
                percent_overflow = round(percent_overflow,2)
                print(element.filename + " : " + str(element.out_of_range) + " Samples were over " + str(test_value_max) + " or below "+ str(test_value_min) + " ("+str(percent_overflow)+"%)")
            
    
            
            

            








### OLD LOG FILES ###
    else:
        print("DATAS TO CHECK ARE:")
        for file in os.listdir(log_location):
            if file.endswith(".txt"):
                print(os.path.join(log_location,file))
                dateien.append(datei(file))            
        if check_values == True:
            print("CHECKING FOR RANGE " + str(test_value_min) + " TO " + str(test_value_max) + " ACTIVATED")
        print("")
        for element in dateien:
            log_file = element.filename
            print("Starting ckeck of " + element.filename)
        
    
    ### GETTING THE POINTS OF DATA ###
            skip=11 #if no "Start" or other lookup was found take line 11 as default
            with open(log_location +"\\"+ log_file) as myFile:
                for num, line in enumerate(myFile, 0):
                    if lookup in line:
                        #print('found at line:'+str(num))
                        skip=num+5
            myFile.close()
            
            # Read data from file 'filename.csv' 
            # (in the same directory that your python process is based)
            # Control delimiters, rows, column names with read_csv (see later) 
            data = pd.read_csv(log_location +"\\"+ log_file,header=None,sep='\(|ms\)|\s+|;',skiprows=skip, engine='python', skipfooter=50, error_bad_lines=False) 
            # Preview the first 5 lines of the loaded data 
            data.head()
            
            if skip > 10:   #as long as less than 8 holders are there the old ones are lesser then 10, new always about 40+
                try:
                    data_clean = data.drop([0,2,3,5,6,8,9,11,12,14,15,17],axis=1)
                    nr_of_axis=3
                except:
                    try:
                        data_clean = data.drop([0,2,3,5,6,8,9,11,12,14],axis=1)
                        nr_of_axis=2
                    except:
                        data_clean = data.drop([0,2,3,5,6,8,9,11],axis=1)
                        nr_of_axis=1
            
            #    data_clean = data.drop([0,2,3,5,6,8,9,11],axis=1)
            #    nr_of_axis=1
                data_clean.head()
                if(nr_of_axis==1):
                    col_names = ['time','msg_cnt','timestamp','acc']       
                elif(nr_of_axis==3):
                    col_names = ['time','msg_cnt','timestamp','accx','accy','accz']
                else:
                    col_names = ['time','msg_cnt','timestamp','acc1','acc2']
                #print(data_clean)
            #    col_names = ['time','msg_cnt','timestamp','acc']
            else:
                try:
                    data_clean = data.drop([0,2,3,5,6,8,9,11,12,14],axis=1)
                    nr_of_axis=3
                except:
                    try:
                        data_clean = data.drop([0,2,3,5,6,8,9,11],axis=1)
                        nr_of_axis=2
                    except:
                        data_clean = data.drop([0,2,3,5,6,8],axis=1)
                        nr_of_axis=1
                
                data_clean.head()
            
                if(nr_of_axis==1):
                    col_names = ['time','msg_cnt','acc']       
                elif(nr_of_axis==3):
                    col_names = ['time','msg_cnt','accx','accy','accz']
                else:
                    col_names = ['time','msg_cnt','acc1','acc2']
            
            
            
            
            data_clean.columns = col_names          
            
            counter=data_clean["msg_cnt"]
            first_counter=counter[0]
            for datapoint in counter:
                if datapoint==first_counter:
                    continue
                elif (datapoint==first_counter+1) or (datapoint==0 and first_counter==255):
                    element.packets = element.packets + 1
                    first_counter = datapoint
                else:
                    lost_packets = datapoint-first_counter - 1
                    ##Next if/else is to see number of lost packets:
                    if details_on == True:
                        if lost_packets < 0:
                            print(str(lost_packets+255+1)+" Packets lost")
                        else:
                            print(str(lost_packets)+" Packets lost")
                    if lost_packets < 0 :
                        lost_packets = lost_packets + 255
                    first_counter = datapoint
                    element.packets = element.packets + lost_packets + 1
                    element.packet_loss = element.packet_loss + lost_packets
            
            if check_values == True:
                if nr_of_axis == 1:
                    axisname = "acc"
                elif nr_of_axis == 3:
                    axisname = "accx"
                else:
                    axisname = "acc1"
                acc_datas = data_clean[axisname]
                for acc_data in acc_datas:
                    element.datapoints = element.datapoints + 1
                    if (acc_data > test_value_max) or (acc_data < test_value_min):
                        element.out_of_range = element.out_of_range + 1
            print("Finished ckeck of " + element.filename)
        print("Finished ckecking of all files")
        print("RESULTS PACKETLOSS:")
        for element in dateien:
            percent_packetloss = (element.packet_loss / element.packets)*100
            percent_packetloss = round(percent_packetloss,2)
            print(element.filename + " : " + str(percent_packetloss) + "%")
        if check_values == True:
            print("RESULTS OF DATAPOINTS:")
            for element in dateien:
                percent_overflow = (element.out_of_range / element.datapoints)*100
                percent_overflow = round(percent_overflow,2)
                print(element.filename + " : " + str(element.out_of_range) + " Samples were over " + str(test_value_max) + " or below "+ str(test_value_min) + " ("+str(percent_overflow)+"%)")
            
    


if __name__ == "__main__":
   main(sys.argv[1:])
                         