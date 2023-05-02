Setup

  $ cd "$TESTDIR/.."

Print help output

  $ icoplotter -h
  usage: icoplotter [-h] [-s] [-p] [input]
  
  Visualizes ICOc measurement data in HDF5 format
  
  positional arguments:
    input          measurement data in HDF5 format (default: log.hdf5)
  
  option.+ (re)
    -h, --help     show this help message and exit
    -s, --scatter  use scatter plot instead of line plot for sensor data
                   (default: False)
    -p, --print    store graphical output as PDF file (default: False)

Store plotter output as PDF

  $ icoplotter examples/log-x.hdf5 --print
  Avg X: 0
  SNR of this file is : -106.50 dB and -106.50 dB @ 9.40 kHz
  Stored plotter output in .+ (re)

Store file using scatter plot

  $ icoplotter -ps examples/log-xy.hdf5
  Avg X: -2 Avg Y: -99
  SNR of this file is : -103.56 dB and -94.84 dB @ 3.54 kHz
  Stored plotter output in .+ (re)

  $ ls examples/*.pdf
  examples/log-x.pdf
  examples/log-xy.pdf

Cleanup

  $ rm examples/*.pdf
