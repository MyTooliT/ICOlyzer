Setup

  $ . "$TESTDIR"/setup.sh
  $ cd "$TESTDIR/.."

Analyze example file

  $ icoanalyzer examples/log-x.hdf5
  Input file is: examples/log-x.hdf5
  PACKETLOSS:
  0.61%
  DATAPOINTS:
  X-AXIS: 127772 Samples were over 1g or below -1g (45.31%)

  $ icoanalyzer -d examples/log-x.hdf5
  Input file is: examples/log-x.hdf5
  64 Packets lost
  64 Packets lost
  64 Packets lost
  64 Packets lost
  64 Packets lost
  64 Packets lost
  64 Packets lost
  64 Packets lost
  64 Packets lost
  PACKETLOSS:
  0.61%
  DATAPOINTS:
  X-AXIS: 127772 Samples were over 1g or below -1g (45.31%)
