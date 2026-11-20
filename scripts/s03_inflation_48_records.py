"""Step 3 - how much do the nst offsets inflate denoising scores?  48 MIT-BIH records x em / ma / bw x 24 / 12 / 0 dB.

For each record (channel 0) and noise record (channel 0, as stored, mean not removed - nst does not remove it):
  gain g from the SNR rule S = A^2/8 (A = median QRS peak-to-peak of the clean reference), N = mean 1-s variance of
  the noise from 5:00 (common.qrs_amplitude / common.noise_power);
  three noisy versions (common.make_nst_noise):  nst = as nst makes it (with offsets),
  gated = same noise and on/off segments, no offsets,  cont = noise added continuously from 5:00, mean removed.
Score = SNR improvement against the clean reference, means removed, 5:00 to 10 s before the end, delay compensated.
Inflation = score(nst) - score(gated) = the part of the score that comes from the offsets only.
    python s03_inflation_48_records.py [nproc]       (results cached per record in results/03_per_record/)
Output: results/03_inflation.csv, results/03_inflation.md
"""
import csv
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

import common as C

NOISES = ("em", "ma", "bw")
LEVELS = (24, 12, 0)
VARIANTS = ("nst", "gated", "cont")
EV = slice(C.T0, C.N - 10 * C.FS)
CACHE = os.path.join(C.RESULTS, "03_per_record")


def score(clean, noisy):
    scale = 0.9 * 32767 / max(np.max(np.abs(noisy)), np.max(np.abs(clean)))   # 16-bit input, as a converter gives
    x = np.round(noisy * scale)
    c = np.round(clean * scale)
    base = C.snr_db(c[EV], x[EV])
    return {m: float(C.snr_db(c[EV], f(x)[EV]) - base) for m, (_, f) in C.METHODS.items()}


def worker(rec):
    out = os.path.join(CACHE, rec + ".json")
    if os.path.exists(out):
        return rec, "cached"
    import wfdb
    h = C.parse_header(C.mitdb(rec))
    x = (C.channel0(C.mitdb(rec)) - h["sigs"][0]["baseline"]) / h["sigs"][0]["gain"]
    y = C.clean_reference(x)
    ann = wfdb.rdann(C.mitdb(rec), "atr")
    A = C.qrs_amplitude(y, ann.sample, ann.symbol)
    rows = []
    for nn in NOISES:
        v = C.channel0(C.nstdb(nn)) / 200.0                       # mV (NSTDB noise: gain 200, ADC zero 0)
        vz = v - v[C.T0:].mean()
        vz[:C.T0] = 0
        pn = C.noise_power(vz)
        for lv in LEVELS:
            g = np.sqrt(A * A / 8 / (pn * 10 ** (lv / 10)))
            nz = C.make_nst_noise(v, g)
            off = nz["nst"] - nz["gated"]
            row = dict(record=rec, noise=nn, level=lv, gain=float(g),
                       offset_share_var=float(np.var(off[EV]) / np.var(nz["nst"][EV])),
                       offset_max_mV=float(np.max(np.abs(off[EV]))))
            for var in VARIANTS:
                for m, val in score(y, y + nz[var]).items():
                    row[f"{var}:{m}"] = val
            rows.append(row)
    os.makedirs(CACHE, exist_ok=True)
    json.dump(rows, open(out + ".tmp", "w"))
    os.replace(out + ".tmp", out)
    return rec, "done"


def table():
    rows = []
    for f in sorted(os.listdir(CACHE)):
        rows += json.load(open(os.path.join(CACHE, f)))
    with open(os.path.join(C.RESULTS, "03_inflation.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    recs = sorted({r["record"] for r in rows})
    M = list(C.METHODS)
    L = ["# 3. Inflation of the SNR improvement by the nst offsets", "",
         f"{len(recs)} MIT-BIH records x em / ma / bw x {LEVELS} dB, mean over records. Methods: " +
         "; ".join(f"{k} = {v[0]}" for k, v in C.METHODS.items()) + ".", "",
         "## 3.1 Inflation = score with nst offsets - score on the same noise without offsets (dB, mean (min .. max))", "",
         "| noise | level (dB) | offset share of noise variance | " + " | ".join(M) + " |", "|---|---|---|" + "---|" * len(M)]
    for nn in NOISES:
        for lv in LEVELS:
            R = [r for r in rows if r["noise"] == nn and r["level"] == lv]
            sh = np.mean([r["offset_share_var"] for r in R])
            cells = []
            for m in M:
                d = np.array([r[f"nst:{m}"] - r[f"gated:{m}"] for r in R])
                cells.append(f"{d.mean():+.2f} ({d.min():+.2f} .. {d.max():+.2f})")
            L.append(f"| {nn} | {lv} | {sh:.3f} | " + " | ".join(cells) + " |")
    L += ["", "## 3.2 Scores (dB, mean over records): nst-made / gated, no offsets / continuous", "",
          "| noise | level (dB) | " + " | ".join(M) + " |", "|---|---|" + "---|" * len(M)]
    for nn in NOISES:
        for lv in LEVELS:
            R = [r for r in rows if r["noise"] == nn and r["level"] == lv]
            cells = [" / ".join(f"{np.mean([r[f'{v}:{m}'] for r in R]):+.2f}" for v in VARIANTS) for m in M]
            L.append(f"| {nn} | {lv} | " + " | ".join(cells) + " |")
    open(os.path.join(C.RESULTS, "03_inflation.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    recs = C.mitdb_records()
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else os.cpu_count()) as pool:
        for i, (r, st) in enumerate(pool.imap_unordered(worker, recs)):
            print(f"[{i + 1}/{len(recs)}] {r} {st}", flush=True)
    table()
