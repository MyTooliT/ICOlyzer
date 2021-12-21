# ICOtools
Contains the ICOtronic tools that can be used on the ICOtronic log files for later analyses of the recorded signals from the ICOc scripts.

## Version

This Readme is written for ICOtools v.1.0.0

## Tools

### IcoPlotter
- Measures a SNR value of the recording
- Opens a plotter with the recorded signal
- Plots the Power Spectral Density Graph for the recorded signal

### IcoAnalyzer
- Measures packetloss of the recorded signal
- Measures how many datapoints are outside of a given maximum and minimum

## Setup Instructions
To use the ICOtools you need to have Python installed. 

It could be possible that some libraries are needed for the system to run. they can be installed via "pip install LIBRARY-NAME" in the command line.

To setup the scripts you just need to clone the repository of ICOtools.

https://github.com/MyTooliT/ICOtools


## Using the tools
Open the command line in the folder of the scripts. Now you just have to run the script you want with "python SCRIPT-NAME" and maybe some parameter if you don't want to use the standard parameters.

### Using IcoPlotter

The IcoPlotter script looks for a log.txt file in the folder the scripts are as a default. After using the command: "python IcoPlotter.py" the script will run and after loading the file open the graph of the recording

<img src="assets/plotter_image.png" alt="plotter_image" style="zoom:40%;" />

The calculated SNR will be written in the command line.

![plotter_standard](assets/plotter_standard.png)

With closing the plotter the script will finish and the command line will be ready for a new command. For running the script with another input-file use the following parameter:

"-i datapath"

The datapath is the path to the ICOc-logfile you want to plot and can be given as a relative path or an absolute path.

Example:

![plotter-i](assets/plotter-i.png)

### Using IcoAnalyzer

The IcoAnalyzer script looks for ALL .txt files in the folder the script is run at as a default. You have to make sure that all .txt files in the analyzed folder are logfiles from the ICOc script or the IcoAnalyzer script will run into an error and not function. After using the command: "python IcoAnalyzer.py" the script will run and look at all .txt files in the folder. It will list them and then file for file check the paketloss and values outside of the given range. All values outside the defined values (default is 31500-35000) are deemed as outside and will be counted. After finishing looking through the files the script will print the results for all files in the command line.

![analyzer](assets/analyzer.png)

If you want to change the folder the script looks through or the minimum and maximum values you have to give the script some extra parameter. Using multiple parameters on one command is also possible.

#### IcoAnalyzer parameter

##### -i

With "-i FOLDERPATH" you can change the folder the script sees through. This path can be given as a relativ or an absolute path.

![analyzer-i](assets/analyzer-i.png)

##### -d

With "-d" you can activate a more detailed information about the packetloss. Not only will it show the percentage of the files, it will now also show how many packets were lost with each packetloss for each file.

![packetloss_details](assets/packetlossdetails.png)

##### -m

With "-m VALUE" you can change the minimal value for datapoints to be checked. All values below this parameter will be counted as out of the borders.

##### -v

With "-v VALUE" you can change the maximum value for datapoints to be checked. All values above this parameter will be counted as out of the borders.

![analyzer_parameters](assets/analyzer_parameters.png)
