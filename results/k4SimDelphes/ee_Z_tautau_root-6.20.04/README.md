# Benchmark results
## System info
- CPU: `Intel(R) Core(TM) i7-9750H CPU @ 2.60GHz`
- Total available memory: `15991820 kB`
- ROOT version: `6.20/04`
- ROOT features `cxx17 asimage builtin_afterimage builtin_clang builtin_llvm dataframe davix exceptions gdml gsl_shared imt mathmore mlp minuit2 opengl pyroot pythia8 r roofit root7 rpath shared soversion sqlite ssl tmva unuran vc vmc vdt x11 xml xrootd`

## write

### sio
Results from 10 benchmark runs with 100000 events each

#### Wall times
| min [s]  | mean [s] |  max [s] |
|----------|----------|----------|
|     1284 |     1362 |     1553 |

#### I/O times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total [s]                |    12.52 |    15.01 |    22.77 |
#### Setup times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total setup [ms]         |    10.51 |    14.50 |    24.40 |
| constructor [ms]         |    1.974 |    4.819 |    15.10 |
| finish [ms]              |    8.381 |    9.671 |    13.89 |
#### Per event times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| median [us]              |    120.6 |    138.4 |    192.3 |
| min [us]                 |    70.24 |    77.42 |    106.3 |
| max [us]                 |     1969 | 1.12e+04 | 2.66e+04 |
| 90 percentile [us]       |    146.1 |    194.4 |    351.0 |
| 99 percentile [us]       |    228.5 |    332.5 |    575.6 |

### root
Results from 10 benchmark runs with 100000 events each

#### Wall times
| min [s]  | mean [s] |  max [s] |
|----------|----------|----------|
|     1283 |     1368 |     1493 |

#### I/O times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total [s]                |    18.02 |    27.61 |    46.38 |
#### Setup times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total setup [ms]         |    691.4 |    749.0 |     1045 |
| constructor [ms]         |    29.47 |    36.60 |    58.18 |
| finish [ms]              |    660.3 |    712.4 |     1005 |
#### Per event times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| median [us]              |    134.3 |    185.3 |    312.0 |
| min [us]                 |    119.4 |    128.2 |    136.4 |
| max [us]                 | 7.81e+05 | 8.30e+05 | 9.95e+05 |
| 90 percentile [us]       |    166.1 |    381.3 |    787.0 |
| 99 percentile [us]       |    539.3 |     1078 |     1848 |

### per-event comparison plot

![per event distribution for write](per_event_write.png)

## read

### sio
Results from 10 benchmark runs with 100000 events each

#### Wall times
| min [s]  | mean [s] |  max [s] |
|----------|----------|----------|
|    6.998 |    7.831 |    10.23 |

#### I/O times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total [s]                |    4.289 |    4.784 |    6.138 |
#### Setup times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total setup [ms]         |    4.063 |    4.623 |    6.715 |
| read collection ids [us] |    0.163 |    0.222 |    0.469 |
| open file [ms]           |    2.045 |    2.161 |    2.587 |
| close file [us]          |    5.889 |    11.89 |    34.91 |
| constructor [us]         |     1999 |     2449 |     4541 |
#### Per event times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| median [us]              |    42.71 |    46.01 |    53.35 |
| min [us]                 |    27.59 |    29.23 |    31.25 |
| max [us]                 |    938.7 |     1294 |     2265 |
| 90 percentile [us]       |    48.44 |    57.44 |    86.50 |
| 99 percentile [us]       |    78.89 |    102.3 |    188.0 |

### root
Results from 10 benchmark runs with 100000 events each

#### Wall times
| min [s]  | mean [s] |  max [s] |
|----------|----------|----------|
|    17.67 |    19.07 |    22.34 |

#### I/O times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total [s]                |    14.79 |    15.99 |    18.69 |
#### Setup times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total setup [ms]         |    396.8 |    462.6 |    656.6 |
| read collection ids [us] |    0.391 |    0.767 |    2.844 |
| open file [ms]           |    388.4 |    454.0 |    645.5 |
| close file [us]          |     7538 |     8599 | 1.11e+04 |
| constructor [us]         |    0.317 |    0.386 |    0.819 |
#### Per event times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| median [us]              |    129.9 |    137.8 |    150.2 |
| min [us]                 |    110.6 |    117.9 |    127.6 |
| max [us]                 | 2.55e+05 | 2.73e+05 | 3.37e+05 |
| 90 percentile [us]       |    139.6 |    161.2 |    220.1 |
| 99 percentile [us]       |    253.5 |    317.7 |    428.4 |

### per-event comparison plot

![per event distribution for read](per_event_read.png)
