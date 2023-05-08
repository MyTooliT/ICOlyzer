Setup

  $ cd "$TESTDIR/.."

Print help output

  $ icoplotter -h
  usage: icoplotter [-h] [-l] [-s] [-p] [input]
  
  Visualizes ICOc measurement data in HDF5 format
  
  positional arguments:
    input          measurement data in HDF5 format (default: log.hdf5)
  
  option.* (re)
    -h, --help     show this help message and exit
    -l, --loss     visualize time periods containing lost data (default: False)
    -s, --scatter  use scatter plot instead of line plot for sensor data
                   (default: False)
    -p, --print    store graphical output as PDF file (default: False)

Store standard plotter output as PDF

  $ icoplotter examples/log-x.hdf5 --print
  Avg X: 0
  SNR of this file is : -106.50 dB and -106.50 dB @ 9.40 kHz
  Stored plotter output in .+ (re)
  $ mv examples/log-x.pdf examples/log-x-without-highlight.pdf

Highlight time periods containing lost data

  $ icoplotter --loss examples/log-x.hdf5 --print
  Avg X: 0
  SNR of this file is : -106.50 dB and -106.50 dB @ 9.40 kHz
  Stored plotter output in .+ (re)

Files with and without highlight must be different for given data

  $ diff examples/log-x-without-highlight.pdf examples/log-x.hdf5 >/dev/null
  [1]

Store file using scatter plot

  $ icoplotter -ps examples/log-xy.hdf5
  Avg X: -2 Avg Y: -99
  SNR of this file is : -103.56 dB and -94.84 dB @ 3.54 kHz
  Stored plotter output in .+ (re)

  $ ls examples/*.pdf
  examples/log-x-without-highlight.pdf
  examples/log-x.pdf
  examples/log-xy.pdf

Cleanup

  $ rm examples/*.pdf
