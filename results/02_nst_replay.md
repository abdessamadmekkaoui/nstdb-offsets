# 2. nst re-implemented: rebuilding the 12 published records

Compared from 5:00 to the second-to-last sample (the last sample differs by ~1000 counts in every record, an end-of-record artefact of nst). Best rounding variant per record shown.

| record | fitted g | rounding (sample / z) | identical | within +-1 | within +-3 | max abs diff (counts) |
|---|---|---|---|---|---|---|
| 118e24 | 0.18669 | trunc / float | 64.6 % | 100.00 % | 100.000 % | 2 |
| 118e18 | 0.37230 | trunc / float | 43.0 % | 99.98 % | 100.000 % | 2 |
| 118e12 | 0.74322 | trunc / trunc | 23.9 % | 98.32 % | 100.000 % | 2 |
| 118e06 | 1.48338 | trunc / float | 67.1 % | 99.90 % | 100.000 % | 2 |
| 118e00 | 2.96083 | trunc / float | 47.5 % | 88.67 % | 100.000 % | 3 |
| 118e_6 | 5.90896 | trunc / trunc | 56.5 % | 97.69 % | 100.000 % | 3 |
| 119e24 | 0.16175 | trunc / trunc | 99.3 % | 100.00 % | 100.000 % | 1 |
| 119e18 | 0.32245 | trunc / trunc | 97.3 % | 100.00 % | 100.000 % | 1 |
| 119e12 | 0.64350 | trunc / trunc | 31.9 % | 98.56 % | 100.000 % | 2 |
| 119e06 | 1.28419 | trunc / float | 55.9 % | 95.64 % | 100.000 % | 3 |
| 119e00 | 2.56333 | trunc / trunc | 85.7 % | 99.23 % | 100.000 % | 2 |
| 119e_6 | 5.11588 | trunc / float | 58.7 % | 89.93 % | 100.000 % | 3 |

The residual 1-3 counts come from the fitted gain and nst's unknown rounding; the offsets themselves (up to thousands of counts, step 1) are rebuilt exactly by the continuity rule.
