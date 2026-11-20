# nstdb-offsets

Code and results for the paper **"Constant Offsets in the MIT-BIH Noise Stress Test Records Inflate ECG Denoising
Results"** (A. Mekkaoui, M. H. El Yousfi Alaoui; submitted to *Physiological Measurement*).

<!-- After the Zenodo release, paste the DOI badge here, e.g. [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX) -->

## The finding in one paragraph

The WFDB program `nst` makes the noise stress test records of the MIT-BIH Noise Stress Test Database (NSTDB): it adds
a noise record to a clean ECG in 2-minute segments, switched on and off from minute 5. To keep its output free of
jumps at each switch, nst adds a continuity term and **holds it constant for the whole next segment**. The records it
makes therefore carry a constant offset in every segment. These offsets carry **85-92 % of the added noise variance**.
Any denoising method that removes the band below 0.5 Hz removes them at no cost, and its SNR improvement rises by
**about 8 dB (em) to 11 dB (ma)**. On the 12 published records (118e24 ... 119e_6), a band-pass filter gains about
+10 dB as published and about +2 dB once the offsets are removed.

## Repository layout

| Path | Content |
|---|---|
| `scripts/common.py` | data paths, independent WFDB format 212/16 reader, nst noise model, offset fit, metric, methods |
| `scripts/download_data.py` | downloads NSTDB and the MIT-BIH Arrhythmia Database from PhysioNet into `data/` |
| `scripts/s01_published_records.py` | step 1: the offsets in the 12 published records (two independent readers) |
| `scripts/s02_nst_replay.py` | step 2: nst re-implemented from `app/nst.c`; rebuilds the published records |
| `scripts/s03_inflation_48_records.py` | step 3: inflation of the SNR improvement, 48 records x em/ma/bw x 24/12/0 dB, 4 methods |
| `scripts/s04_published_bandpass_gain.py` | step 4: band-pass gain on the published records, with and without offsets |
| `scripts/s05_sensors2026_reproduction.py` | step 5: re-run of the evaluation protocol of Hanzala et al., *Sensors* 2026 |
| `scripts/remove_offsets.py` | **tool**: removes the per-segment offsets from a record made by nst |
| `scripts/make_figures.py` | figures 1-3 of the paper |
| `results/` | outputs of steps 1-5 (Markdown and CSV) and the literature survey |
| `figures/` | figures 1-3 (PNG) |

## How to reproduce

Python 3.10 or newer.

```bash
pip install -r requirements.txt
cd scripts
python download_data.py                 # about 110 MB from PhysioNet into ../data
python s01_published_records.py         # seconds
python s02_nst_replay.py                # about 1 minute
python s03_inflation_48_records.py 8    # 8 processes; tens of minutes
python s04_published_bandpass_gain.py
python s05_sensors2026_reproduction.py
python make_figures.py
```

If you already have the databases, point to them instead of downloading:
`NSTDB_DIR=/path/to/nstdb MITDB_DIR=/path/to/mitdb python s01_published_records.py`
(on Windows PowerShell: `$env:NSTDB_DIR='...'; $env:MITDB_DIR='...'`).

## Removing the offsets from your own test data

```bash
cd scripts
python remove_offsets.py --all-published --out ../results/offsets_removed          # the 12 published records
python remove_offsets.py --noisy ../data/nstdb/118e06 --clean ../data/mitdb/118 --noise ../data/nstdb/em --out out_dir
```

For each 2-minute segment from 5:00 the tool fits `(noisy - clean) = a * noise + c` by least squares and subtracts
`c`. The output is a WFDB record (`<name>_nooff`) written with ADC zero 0, which also undoes the constant -5.12 mV
header shift of the published records. Use `--start` and `--seg` if your nst protocol differs from the default.

**Recommendation for benchmarks:** add the NSTDB noise records directly (continuous, or random segments scaled by a
constant). When the published records or nst must be used, remove one constant per segment and report results both
with and without the offsets.

## Methods scored (step 3)

| Key | Method |
|---|---|
| KA | linear-phase FIR band-pass 0.5-150 Hz, Kaiser window (beta for 50 dB), 1057 taps, delay compensated |
| HP | causal 2nd-order Butterworth high-pass, 0.5 Hz |
| MED | two-stage median baseline removal (200 ms, then 600 ms) |
| DWT | db4 wavelet, 4 levels, soft SURE threshold per band in blocks of 2048 samples; keeps the approximation band |

Score = SNR improvement against the clean reference (MIT-BIH record with two-stage median baseline removed and 60 /
120 Hz notches), means removed, from 5:00 to 10 s before the end. The noise gain follows a simplified form of nst's SNR
rule (median QRS amplitude and mean 1-s noise variance, where nst uses 5 % trimmed means); the inflation does not
depend on the level.

## Data and licences

- Data are **not** included. They come from PhysioNet: MIT-BIH Noise Stress Test Database 1.0.0
  (doi:10.13026/C2HS3T) and MIT-BIH Arrhythmia Database 1.0.0 (doi:10.13026/C2F305), Open Data Commons Attribution
  License v1.0. Please cite Moody, Muldrow and Mark (1984) and Goldberger et al. (2000) as PhysioNet asks.
- Code: MIT licence. Results and figures: CC BY 4.0. See `LICENSE`.

## How to cite

See `CITATION.cff` (GitHub shows a "Cite this repository" button). Please cite the paper and the Zenodo archive.
