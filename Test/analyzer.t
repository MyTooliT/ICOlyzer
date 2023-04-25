Setup

  $ . "$TESTDIR"/setup.sh
  $ cd "$TESTDIR/.."

Analyze example file

  $ icoanalyzer examples/log-x.hdf5
  Input: examples/log-x.hdf5
  Packet Loss: 0.61%
  Data Points:
    X-Axis: 127772 Samples were over 1g or below -1g (45.31%)
  Runtime: 29.996 seconds

Test detailed output

  $ icoanalyzer -d examples/log-x.hdf5
  Input: examples/log-x.hdf5
   64 Packets lost after  2.979 seconds - No values for   3 milliseconds
   64 Packets lost after  3.274 seconds - No values for   3 milliseconds
   64 Packets lost after  7.089 seconds - No values for   3 milliseconds
   64 Packets lost after 11.192 seconds - No values for   3 milliseconds
   64 Packets lost after 16.931 seconds - No values for   3 milliseconds
   64 Packets lost after 22.149 seconds - No values for   3 milliseconds
   64 Packets lost after 22.782 seconds - No values for   2 milliseconds
   64 Packets lost after 25.781 seconds - No values for   3 milliseconds
   64 Packets lost after 29.623 seconds - No values for   2 milliseconds
  Packet Loss: 0.61%
  Data Points:
    X-Axis: 127772 Samples were over 1g or below -1g (45.31%)
  Runtime: 29.996 seconds

Test data file containing data for multiple axes

  $ icoanalyzer -d examples/log-xyz.hdf5
  Input: examples/log-xyz.hdf5
  Packet Loss: 0.0%
  Data Points:
    X-Axis: 94564 Samples were over 1g or below -1g (99.79%)
    Y-Axis: 94767 Samples were over 1g or below -1g (100.0%)
    Z-Axis: 94767 Samples were over 1g or below -1g (100.0%)
  Runtime: 29.991 seconds
