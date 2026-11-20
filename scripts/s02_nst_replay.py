"""Step 2 - re-implement nst (WFDB app/nst.c) and rebuild the 12 published records from MIT-BIH 118/119 and 'em'.

nst logic (app/nst.c): the ECG's ADC zero is removed; at every protocol switch (from 5:00, every 2 min, the noise gain
toggles g <-> 0) the continuity term z = vin + g_new*noise - vout is evaluated on the previous sample, so the output
does not jump; every sample vout = vin + g*noise - z. z is therefore constant over each segment = the offset.
nst's protocol file was not distributed, so the gain g of each record is fitted by least squares (one g over all
noise segments, one free constant per segment). Rounding inside nst is unknown: four variants are tried.
Output: results/02_nst_replay.md
"""
import os

import numpy as np

import common as C


def fit_gain(d, em):
    on = [a for k, a in enumerate(C.segment_starts()) if k % 2 == 0]
    sl = [slice(a, min(C.N, a + C.SEG)) for a in on]
    n_tot = sum(s.stop - s.start for s in sl)
    A = np.zeros((n_tot, 1 + len(sl)))
    y = np.zeros(n_tot)
    p = 0
    for j, s in enumerate(sl):
        L = s.stop - s.start
        A[p:p + L, 0], A[p:p + L, 1 + j], y[p:p + L] = em[s], 1, d[s]
        p += L
    return np.linalg.lstsq(A, y, rcond=None)[0][0]


def replay(ecg, em, g, rnd, zint=None):
    vin = ecg.astype(float)
    out = np.empty(C.N)
    out[:C.T0] = vin[:C.T0]
    gn, z, k = 0.0, 0.0, -1
    bounds = set(C.segment_starts())
    for t in range(C.T0, C.N):
        if t in bounds:
            k += 1
            gn = g if k % 2 == 0 else 0.0
            z = vin[t - 1] + gn * em[t - 1] - out[t - 1]
            if zint is not None:
                z = zint(z)
        out[t] = rnd(vin[t] + gn * em[t] - z)
    return out


def main():
    em = C.channel0(C.nstdb("em")).astype(float)
    L = ["# 2. nst re-implemented: rebuilding the 12 published records", "",
         "Compared from 5:00 to the second-to-last sample (the last sample differs by ~1000 counts in every record, an "
         "end-of-record artefact of nst). Best rounding variant per record shown.", "",
         "| record | fitted g | rounding (sample / z) | identical | within +-1 | within +-3 | max abs diff (counts) |",
         "|---|---|---|---|---|---|---|"]
    ev = slice(C.T0, C.N - 1)
    for rid in ("118", "119"):
        ecg = C.channel0(C.mitdb(rid)) - 1024
        for lv in C.LEVELS:
            pub = C.channel0(C.nstdb(f"{rid}e{lv}")).astype(float)
            g = fit_gain(pub - ecg, em)
            best = None
            for name, rnd, zi in (("trunc / float", np.trunc, None), ("trunc / trunc", np.trunc, np.trunc),
                                  ("round / float", np.round, None), ("round / round", np.round, np.round)):
                d = (replay(ecg, em, g, rnd, zi) - pub)[ev]
                res = (name, np.mean(d == 0), np.mean(np.abs(d) <= 1), np.mean(np.abs(d) <= 3), np.max(np.abs(d)))
                if best is None or res[2] > best[2]:
                    best = res
            L.append(f"| {rid}e{lv} | {g:.5f} | {best[0]} | {100 * best[1]:.1f} % | {100 * best[2]:.2f} % | "
                     f"{100 * best[3]:.3f} % | {best[4]:.0f} |")
            print(L[-1], flush=True)
    L += ["", "The residual 1-3 counts come from the fitted gain and nst's unknown rounding; the offsets themselves "
          "(up to thousands of counts, step 1) are rebuilt exactly by the continuity rule."]
    open(os.path.join(C.RESULTS, "02_nst_replay.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
