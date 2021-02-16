# Benchmark results
## System info
- CPU: `Intel(R) Core(TM) i7-9750H CPU @ 2.60GHz`
- Total available memory: `15991820 kB`
- ROOT version: `6.22/06`
- ROOT features `cxx17 asimage builtin_afterimage builtin_clang builtin_llvm dataframe davix exceptions gdml gsl_shared imt mathmore mlp minuit2 opengl pyroot pythia8 r roofit root7 rpath shared soversion sqlite ssl tmva tmva-rmva unuran vc vmc vdt x11 xml xrootd`

## write

### sio
Results from 10 benchmark runs with 17143 events each

#### Wall times
| min [s]  | mean [s] |  max [s] |
|----------|----------|----------|
|    23.20 |    24.67 |    25.72 |

#### I/O times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total [s]                |    6.590 |    6.853 |    7.029 |
#### Setup times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total setup [ms]         |    3.590 |    4.233 |    7.994 |
| constructor [ms]         |    2.085 |    2.734 |    6.318 |
| finish [ms]              |    1.412 |    1.485 |    1.652 |
#### Per event times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| median [us]              |    386.6 |    397.7 |    405.1 |
| min [us]                 |    84.48 |    85.69 |    87.41 |
| max [us]                 |     1815 |     2837 |     3670 |
| 90 percentile [us]       |    527.0 |    550.8 |    569.4 |
| 99 percentile [us]       |    673.9 |    779.7 |    861.8 |

### root
Results from 10 benchmark runs with 17143 events each

#### Wall times
| min [s]  | mean [s] |  max [s] |
|----------|----------|----------|
|    27.47 |    29.05 |    31.77 |

#### I/O times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total [s]                |    10.48 |    11.05 |    12.17 |
#### Setup times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total setup [ms]         |    446.3 |    465.7 |    496.5 |
| constructor [ms]         |    24.82 |    28.10 |    37.38 |
| finish [ms]              |    417.1 |    437.6 |    471.7 |
#### Per event times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| median [us]              |    459.0 |    467.0 |    493.0 |
| min [us]                 |    403.8 |    415.9 |    425.6 |
| max [us]                 | 6.31e+05 | 6.82e+05 | 7.16e+05 |
| 90 percentile [us]       |    528.2 |    612.3 |    783.2 |
| 99 percentile [us]       |     2488 |     2613 |     2851 |

### per-event comparison plot

![per event distribution for write](per_event_write.png)

## read

### sio
Results from 10 benchmark runs with 17143 events each

#### Wall times
| min [s]  | mean [s] |  max [s] |
|----------|----------|----------|
|    3.374 |    3.569 |    3.863 |

#### I/O times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total [s]                |    1.962 |    2.074 |    2.232 |
#### Setup times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total setup [ms]         |    2.412 |    3.329 |    7.013 |
| open file [ms]           |    0.391 |    0.503 |    1.184 |
| read collection ids [us] |    0.155 |    0.243 |    0.543 |
| close file [us]          |    7.113 |    8.505 |    10.90 |
| constructor [us]         |     2011 |     2816 |     5818 |
#### Per event times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| median [us]              |    116.1 |    120.5 |    125.8 |
| min [us]                 |    32.56 |    33.97 |    35.70 |
| max [us]                 |     1042 |     1553 |     3674 |
| 90 percentile [us]       |    145.7 |    155.8 |    171.3 |
| 99 percentile [us]       |    186.4 |    230.9 |    297.3 |

### root
Results from 10 benchmark runs with 17143 events each

#### Wall times
| min [s]  | mean [s] |  max [s] |
|----------|----------|----------|
|    11.71 |    12.25 |    13.79 |

#### I/O times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total [s]                |    10.22 |    10.70 |    12.05 |
#### Setup times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total setup [ms]         |    435.5 |    458.4 |    509.1 |
| open file [ms]           |    426.8 |    448.7 |    497.8 |
| read collection ids [us] |    0.334 |    0.489 |    0.653 |
| close file [us]          |     8090 |     9687 | 1.13e+04 |
| constructor [us]         |    0.323 |    0.373 |    0.667 |
#### Per event times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| median [us]              |    511.3 |    527.1 |    552.8 |
| min [us]                 |    410.8 |    427.9 |    438.8 |
| max [us]                 | 2.97e+05 | 3.08e+05 | 3.31e+05 |
| 90 percentile [us]       |    580.2 |    639.5 |    899.3 |
| 99 percentile [us]       |     1192 |     1390 |     1732 |

### per-event comparison plot

![per event distribution for read](per_event_read.png)
