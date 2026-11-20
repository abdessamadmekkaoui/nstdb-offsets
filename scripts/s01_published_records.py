"""Step 1 - the offsets are in the 12 published NSTDB records (118e24 ... 119e_6).

Every file is read twice: with wfdb-python and with the independent decoder in common.py. Checks:
  1. header fields and checksums;  2. both readers give identical samples;
  3. first 5 min (no noise): e-record minus MIT-BIH record;
  4. per 2-min segment from 5:00: least-squares fit (e-record - clean) = a*em + c;  c = the segment offset;
  5. offset share of the added-noise variance (5:00 to 10 s before the end).
Output: results/01_published_records.md, results/01_segment_offsets.csv
"""
import csv
import os

import numpy as np
import wfdb

import common as C


def cksum(x):
    v = int(np.sum(x)) & 0xFFFF
    return v - 65536 if v >= 32768 else v


def main():
    os.makedirs(C.RESULTS, exist_ok=True)
    names = ["118", "119"] + C.PUBLISHED + ["em"]
    path = {n: (C.mitdb(n) if n in ("118", "119") else C.nstdb(n)) for n in names}
    L = ["# 1. The offsets in the 12 published NSTDB records", "",
         f"Reader A = wfdb-python {wfdb.__version__}; reader B = independent format 212/16 decoder (`common.py`).", "",
         "## 1.1 Header fields, channel 0, and agreement of the two readers", "",
         "| record | format | gain (adu/mV) | baseline | ADC zero | checksums ok | readers identical (digital / physical) |",
         "|---|---|---|---|---|---|---|"]
    D = {}
    for n in names:
        h = C.parse_header(path[n])
        dB = C.decode(path[n], h)
        D[n] = dB
        s = h["sigs"][0]
        ok = all(cksum(dB[:, k]) == h["sigs"][k]["cksum"] for k in range(h["nsig"]))
        rA = wfdb.rdrecord(path[n], physical=False)
        rP = wfdb.rdrecord(path[n])
        same_d = np.array_equal(rA.d_signal.astype(np.int64), dB)
        physB = (dB - np.array([x["baseline"] for x in h["sigs"]])) / np.array([x["gain"] for x in h["sigs"]])
        same_p = np.allclose(rP.p_signal, physB, atol=1e-9)
        L.append(f"| {n} | {s['fmt']} | {s['gain']:g} | {s['baseline']} | {s['adczero']} | {'yes' if ok else 'NO'} | "
                 f"{'yes' if same_d else 'NO'} / {'yes' if same_p else 'NO'} |")

    em = D["em"][:C.N, 0].astype(float)
    seg_rows, rows = [], []
    for rid in ("118", "119"):
        m = D[rid][:C.N, 0]
        for lv in C.LEVELS:
            r = f"{rid}e{lv}"
            diff = (D[r][:C.N, 0] - m).astype(float)
            pre = diff[:C.T0]
            dc, fits = C.fit_segment_offsets(diff, em)
            for k, (a, c) in enumerate(fits):
                seg_rows.append(dict(record=r, segment=k, start_s=C.segment_starts()[k] // C.FS, noise_on=int(k % 2 == 0),
                                     em_gain=round(a, 4), offset_counts=round(c, 2),
                                     offset_mV_adc_zero_fixed=round((c + 1024) / 200.0, 3)))
            ev = slice(C.T0, C.N - 10 * C.FS)
            n_ = diff[ev] + 1024
            rows.append((r, pre.mean(), pre.std(), float(np.var(dc[ev]) / np.var(n_)),
                         min((c + 1024) / 200 for _, c in fits), max((c + 1024) / 200 for _, c in fits),
                         np.mean([a for k, (a, _) in enumerate(fits) if k % 2 == 0])))
    L += ["", "Physical value = (digital - baseline) / gain. The e-records keep baseline 1024 with ADC zero 0, while nst "
          "removed the ECG's ADC zero (1024): every WFDB reader shifts them by -5.12 mV (constant, no effect on any SNR "
          "improvement).", "",
          "## 1.2 First 5 minutes and per-segment offsets", "",
          "| record | first 5 min: mean / std of (e-record - clean), counts | em gain (noise segments) | segment offsets, min .. max (mV) | offset share of added-noise variance |",
          "|---|---|---|---|---|"]
    L += [f"| {r} | {mu:.3f} / {sd:.3f} | {g:.4f} | {lo:+.2f} .. {hi:+.2f} | {sh:.3f} |" for r, mu, sd, sh, lo, hi, g in rows]
    L += ["", "Full list of segment fits: `01_segment_offsets.csv` (offset in counts as read, and in mV after adding back "
          "the 1024-count ADC-zero shift)."]
    with open(os.path.join(C.RESULTS, "01_segment_offsets.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(seg_rows[0]))
        w.writeheader()
        w.writerows(seg_rows)
    open(os.path.join(C.RESULTS, "01_published_records.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
