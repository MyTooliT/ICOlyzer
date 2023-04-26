Setup

  $ cd "$TESTDIR/.."

Print help output

  $ icoplotter -h
  usage: icoplotter [-h] [-p] [input]
  
  Visualizes ICOc measurement data in HDF5 format
  
  positional arguments:
    input        measurement data in HDF5 format (default: log.hdf5)
  
  options:
    -h, --help   show this help message and exit
    -p, --print  store graphical output as PDF file (default: False)

Store plotter output as PDF

  $ icoplotter examples/log-x.hdf5 --print
  Avg X: 0
  SNR of this file is : -106.50 dB and -106.50 dB @ 9.40 kHz
  Stored plotter output in .* (re)

  $ ls examples/log-x.pdf
  examples/log-x.pdf

  $ rm examples/log-x.pdf
