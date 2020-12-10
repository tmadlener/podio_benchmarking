# Benchmark results
## System info
- CPU: `Intel(R) Core(TM) i7-9750H CPU @ 2.60GHz`
- Total available memory: `15992388 kB`

## write

### sio
Results from 10 benchmark runs with 17143 events each
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total [s]                |    13.22 |    13.90 |    14.55 |
#### Setup times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total setup [ms]         |    4.927 |    6.059 |    10.03 |
| constructor [ms]         |    2.400 |    3.462 |    7.409 |
| finish [ms]              |    2.439 |    2.567 |    2.742 |
#### Per event times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| median [us]              |    785.3 |    827.2 |    861.5 |
| min [us]                 |    147.2 |    154.7 |    158.6 |
| max [us]                 |     2032 |     2440 |     3002 |
| 90 percentile [us]       |     1069 |     1123 |     1180 |
| 99 percentile [us]       |     1318 |     1383 |     1482 |

### root
Results from 10 benchmark runs with 17143 events each
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total [s]                |    6.833 |    7.372 |    8.072 |
#### Setup times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total setup [ms]         |    824.7 |    876.5 |    975.2 |
| constructor [ms]         |    28.59 |    31.31 |    41.44 |
| finish [ms]              |    794.9 |    845.2 |    946.4 |
#### Per event times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| median [us]              |    212.5 |    227.1 |    246.8 |
| min [us]                 |    143.7 |    149.6 |    155.2 |
| max [us]                 | 9.39e+05 | 9.88e+05 | 1.07e+06 |
| 90 percentile [us]       |    273.7 |    333.0 |    470.3 |
| 99 percentile [us]       |     2732 |     2907 |     3119 |

### root zlib compression
Results from 10 benchmark runs with 17143 events each
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total [s]                |    11.36 |    11.83 |    13.22 |
#### Setup times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total setup [ms]         |     1153 |     1178 |     1204 |
| constructor [ms]         |    28.99 |    31.19 |    41.90 |
| finish [ms]              |     1123 |     1147 |     1173 |
#### Per event times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| median [us]              |    215.9 |    227.7 |    243.5 |
| min [us]                 |    143.4 |    150.7 |    159.2 |
| max [us]                 | 2.42e+06 | 2.51e+06 | 2.93e+06 |
| 90 percentile [us]       |    327.6 |    377.2 |    542.9 |
| 99 percentile [us]       |     5517 |     5661 |     5850 |

### per-event comparison plot

![per event distribution for write](per_event_write.png)

## read

### sio
Results from 10 benchmark runs with 17143 events each
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total [s]                |    4.589 |    4.713 |    4.940 |
#### Setup times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total setup [ms]         |    2.924 |    3.412 |    6.736 |
| open file [ms]           |    0.573 |    0.640 |    0.888 |
| constructor [us]         |     2329 |     2763 |     5838 |
| close file [us]          |    6.536 |    8.609 |    18.21 |
| read collection ids [us] |    0.155 |    0.201 |    0.416 |
#### Per event times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| median [us]              |    271.7 |    279.2 |    291.9 |
| min [us]                 |    102.6 |    105.9 |    108.8 |
| max [us]                 |    732.6 |    865.1 |     1114 |
| 90 percentile [us]       |    337.4 |    346.5 |    364.9 |
| 99 percentile [us]       |    412.2 |    422.5 |    442.3 |

### root
Results from 10 benchmark runs with 17143 events each
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total [s]                |    6.047 |    6.315 |    6.714 |
#### Setup times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total setup [ms]         |    202.5 |    215.3 |    255.6 |
| open file [ms]           |    195.6 |    208.1 |    249.0 |
| constructor [us]         |    0.371 |    0.488 |    1.160 |
| close file [us]          |     6518 |     7193 |     7808 |
| read collection ids [us] |    0.387 |    0.426 |    0.499 |
#### Per event times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| median [us]              |    283.5 |    296.9 |    316.7 |
| min [us]                 |    190.0 |    197.9 |    208.9 |
| max [us]                 | 3.81e+05 | 3.89e+05 | 4.05e+05 |
| 90 percentile [us]       |    338.8 |    354.6 |    371.3 |
| 99 percentile [us]       |     1012 |     1066 |     1139 |

### root zlib compression
Results from 10 benchmark runs with 17143 events each
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total [s]                |    6.200 |    6.417 |    6.656 |
#### Setup times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| total setup [ms]         |    208.8 |    213.2 |    221.8 |
| open file [ms]           |    200.7 |    204.7 |    213.4 |
| constructor [us]         |    0.378 |    0.435 |    0.805 |
| close file [us]          |     8102 |     8442 |     9379 |
| read collection ids [us] |    0.406 |    2.249 |    17.14 |
#### Per event times
|                          |   min    |   mean   |   max    |
|--------------------------|----------|----------|----------|
| median [us]              |    286.9 |    297.5 |    311.0 |
| min [us]                 |    192.8 |    199.9 |    211.7 |
| max [us]                 | 4.64e+05 | 4.73e+05 | 4.83e+05 |
| 90 percentile [us]       |    349.3 |    363.8 |    381.0 |
| 99 percentile [us]       |     1071 |     1101 |     1137 |

### per-event comparison plot

![per event distribution for read](per_event_read.png)
