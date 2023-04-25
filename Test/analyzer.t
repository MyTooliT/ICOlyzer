Setup

  $ . "$TESTDIR"/setup.sh
  $ cd "$TESTDIR/.."

Analyze example file

  $ icoanalyzer examples/log-x.hdf5
  Input: examples/log-x.hdf5
  Packet Loss: 0.61%
  Data Points:
    X-Axis: 127772 Samples were over 1g or below -1g (45.31%)
  Runtime: 30.0 seconds

Test detailed output

  $ icoanalyzer -d examples/log-x.hdf5
  Input: examples/log-x.hdf5
  64 Packets lost
  64 Packets lost
  64 Packets lost
  64 Packets lost
  64 Packets lost
  64 Packets lost
  64 Packets lost
  64 Packets lost
  64 Packets lost
  Packet Loss: 0.61%
  Data Points:
    X-Axis: 127772 Samples were over 1g or below -1g (45.31%)
  Runtime: 30.0 seconds

Test data file containing data for multiple axes

  $ icoanalyzer -d examples/log-xyz.hdf5
  Input: examples/log-xyz.hdf5
  Packet Loss: 0.0%
  Data Points:
    X-Axis: 94564 Samples were over 1g or below -1g (99.79%)
    Y-Axis: 94767 Samples were over 1g or below -1g (100.0%)
    Z-Axis: 94767 Samples were over 1g or below -1g (100.0%)
  Runtime: 30.0 seconds
