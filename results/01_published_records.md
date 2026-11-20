# 1. The offsets in the 12 published NSTDB records

Reader A = wfdb-python 4.3.1; reader B = independent format 212/16 decoder (`common.py`).

## 1.1 Header fields, channel 0, and agreement of the two readers

| record | format | gain (adu/mV) | baseline | ADC zero | checksums ok | readers identical (digital / physical) |
|---|---|---|---|---|---|---|
| 118 | 212 | 200 | 1024 | 1024 | yes | yes / yes |
| 119 | 212 | 200 | 1024 | 1024 | yes | yes / yes |
| 118e24 | 212 | 200 | 1024 | 0 | yes | yes / yes |
| 118e18 | 212 | 200 | 1024 | 0 | yes | yes / yes |
| 118e12 | 212 | 200 | 1024 | 0 | yes | yes / yes |
| 118e06 | 212 | 200 | 1024 | 0 | yes | yes / yes |
| 118e00 | 16 | 200 | 1024 | 0 | yes | yes / yes |
| 118e_6 | 16 | 200 | 1024 | 0 | yes | yes / yes |
| 119e24 | 212 | 200 | 1024 | 0 | yes | yes / yes |
| 119e18 | 212 | 200 | 1024 | 0 | yes | yes / yes |
| 119e12 | 212 | 200 | 1024 | 0 | yes | yes / yes |
| 119e06 | 212 | 200 | 1024 | 0 | yes | yes / yes |
| 119e00 | 16 | 200 | 1024 | 0 | yes | yes / yes |
| 119e_6 | 16 | 200 | 1024 | 0 | yes | yes / yes |
| em | 212 | 200 | 0 | 0 | yes | yes / yes |

Physical value = (digital - baseline) / gain. The e-records keep baseline 1024 with ADC zero 0, while nst removed the ECG's ADC zero (1024): every WFDB reader shifts them by -5.12 mV (constant, no effect on any SNR improvement).

## 1.2 First 5 minutes and per-segment offsets

| record | first 5 min: mean / std of (e-record - clean), counts | em gain (noise segments) | segment offsets, min .. max (mV) | offset share of added-noise variance |
|---|---|---|---|---|
| 118e24 | -1024.000 / 0.000 | 0.1867 | -0.29 .. +0.54 | 0.850 |
| 118e18 | -1024.000 / 0.000 | 0.3722 | -0.60 .. +1.04 | 0.847 |
| 118e12 | -1024.000 / 0.000 | 0.7432 | -1.20 .. +2.08 | 0.848 |
| 118e06 | -1024.000 / 0.000 | 1.4834 | -2.41 .. +4.12 | 0.847 |
| 118e00 | -1024.000 / 0.000 | 2.9608 | -4.82 .. +8.23 | 0.847 |
| 118e_6 | -1024.000 / 0.000 | 5.9090 | -9.62 .. +16.42 | 0.847 |
| 119e24 | -1024.000 / 0.000 | 0.1617 | -0.25 .. +0.46 | 0.847 |
| 119e18 | -1024.000 / 0.000 | 0.3224 | -0.52 .. +0.90 | 0.847 |
| 119e12 | -1024.000 / 0.000 | 0.6434 | -1.04 .. +1.80 | 0.847 |
| 119e06 | -1024.000 / 0.000 | 1.2842 | -2.09 .. +3.57 | 0.847 |
| 119e00 | -1024.000 / 0.000 | 2.5633 | -4.17 .. +7.13 | 0.847 |
| 119e_6 | -1024.000 / 0.000 | 5.1159 | -8.33 .. +14.23 | 0.847 |

Full list of segment fits: `01_segment_offsets.csv` (offset in counts as read, and in mV after adding back the 1024-count ADC-zero shift).
