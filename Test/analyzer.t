Setup

  $ cd "$TESTDIR/.."

Analyze example file

  $ icoanalyzer examples/log-x.hdf5
  Input: examples/log-x.hdf5
  Packet Loss: 0.61%
  Data Points:
    X-Axis: 282021 Samples - 127772 Samples were over 1g or below -1g (45.31%)
  Measurement Date: 2021-12-20T11:00:21.489537
  Runtime: 29.996 seconds

Test detailed output

  $ icoanalyzer -d examples/log-x.hdf5
  Input: examples/log-x.hdf5
   64 Packets lost after  2.979 seconds - No values for 0.3 milliseconds
   64 Packets lost after  3.274 seconds - No values for 0.3 milliseconds
   64 Packets lost after  7.089 seconds - No values for 0.3 milliseconds
   64 Packets lost after 11.192 seconds - No values for 0.3 milliseconds
   64 Packets lost after 16.931 seconds - No values for 0.3 milliseconds
   64 Packets lost after 22.149 seconds - No values for 0.3 milliseconds
   64 Packets lost after 22.782 seconds - No values for 0.2 milliseconds
   64 Packets lost after 25.781 seconds - No values for 0.3 milliseconds
   64 Packets lost after 29.623 seconds - No values for 0.2 milliseconds
  Average Packets Lost: 64.0 Packets
  Packet Loss: 0.61%
  Data Points:
    X-Axis: 282021 Samples - 127772 Samples were over 1g or below -1g (45.31%)
  Measurement Date: 2021-12-20T11:00:21.489537
  Runtime: 29.996 seconds

Test data file containing data for multiple axes

  $ icoanalyzer -d examples/log-xyz.hdf5
  Input: examples/log-xyz.hdf5
  Average Packets Lost: 0 Packets
  Packet Loss: 0.0%
  Data Points:
    X-Axis: 94767 Samples - 94564 Samples were over 1g or below -1g (99.79%)
    Y-Axis: 94767 Samples - 94767 Samples were over 1g or below -1g (100.0%)
    Z-Axis: 94767 Samples - 94767 Samples were over 1g or below -1g (100.0%)
  Measurement Date: 2021-12-27T09:28:12.636001
  Runtime: 29.991 seconds

Test data file containing broken data (non-monotonic timestamps)

  $ icoanalyzer -d examples/broken.hdf5 >/dev/null
  Latest data at 0.000000 seconds is older than data before at 4.858067 seconds
  Latest data at 0.000000 seconds is older than data before at 4.855696 seconds
  Latest data at 0.000000 seconds is older than data before at 0.858623 seconds
  Latest data at 0.000000 seconds is older than data before at 0.820173 seconds

Test average value and sigma output (single axis)

  $ icoanalyzer -s examples/log-x.hdf5
  Input: examples/log-x.hdf5
  Packet Loss: 0.61%
  Data Points:
    X-Axis: 282021 Samples - 127772 Samples were over 1g or below -1g (45.31%)
  The average value of the x axis was: -0.96g
  The standard deviation(σ²) of the x axis was: 0.0962528
  Measurement Date: 2021-12-20T11:00:21.489537
  Runtime: 29.996 seconds

Test average value and sigma output (multiple axis)

  $ icoanalyzer -s examples/log-xyz.hdf5
  Input: examples/log-xyz.hdf5
  Packet Loss: 0.0%
  Data Points:
    X-Axis: 94767 Samples - 94564 Samples were over 1g or below -1g (99.79%)
  The average value of the x axis was: -2.12g
  The standard deviation(σ²) of the x axis was: 0.4838315
    Y-Axis: 94767 Samples - 94767 Samples were over 1g or below -1g (100.0%)
  The average value of the y axis was: -99.96g
  The standard deviation(σ²) of the y axis was: 3.2213167
    Z-Axis: 94767 Samples - 94767 Samples were over 1g or below -1g (100.0%)
  The average value of the z axis was: -99.25g
  The standard deviation(σ²) of the z axis was: 0.2494332
  Measurement Date: 2021-12-27T09:28:12.636001
  Runtime: 29.991 seconds
