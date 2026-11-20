"""Step 5 - re-run of the evaluation protocol of Hanzala et al., Sensors 2026, 26(22):7098 (doi 10.3390/s26227098) on
the 12 published records.

Their protocol (sec. 2.3): channel MLII; whole-record mean removal of noisy and clean; lag by normalized cross-correlation
within +-5 s (zero here: the published records are sample-aligned with 118 / 119, step 1); reference fitted a*clean + b
by least squares over the whole record, separately for the noisy input and for each output; metrics on 300-310 s;
before the wavelet stage, a 4th-order Butterworth high-pass at 0.5 Hz and a 50 Hz notch on the noisy signal.
Here: (1) their measured input SNR; (2) input SNR with the per-segment offsets removed; (3) SNR change of their
pre-filter ALONE (no wavelet), as published and with the offsets removed. Notch Q = 30 assumed; zero-phase and causal
filtering both shown (not stated in the paper).
Output: results/05_sensors2026_reproduction.md
"""
import os

import numpy as np
from scipy.signal import butter, filtfilt, iirnotch, lfilter

import common as C

W = slice(300 * C.FS, 310 * C.FS + 1)
REPORTED = {  # record: (reported input SNR, reported SNR change of the best SWT configuration), dB
    "119e24": (14.17, -4.17), "118e24": (9.23, -0.07), "119e18": (8.16, 1.14), "118e18": (3.36, 3.79),
    "119e12": (2.17, 4.95), "118e12": (-2.65, 5.87), "119e06": (-3.75, 6.69), "118e06": (-8.69, 6.78),
    "119e00": (-9.81, 8.01), "118e00": (-14.92, 7.01), "119e_6": (-15.88, 7.33), "118e_6": (-21.34, 7.42)}


def snr(ref, x):
    return 10 * np.log10(np.sum(ref[W] ** 2) / np.sum((x[W] - ref[W]) ** 2))


def fitted(xc, xy):
    a, b = np.linalg.lstsq(np.c_[xc, np.ones(len(xc))], xy, rcond=None)[0]
    return a * xc + b


def prefilter(x, zero_phase):
    bh, ah = butter(4, 0.5 / (C.FS / 2), "high")
    bn, an = iirnotch(50, 30, C.FS)
    f = filtfilt if zero_phase else lfilter
    return f(bn, an, f(bh, ah, x))


def main():
    em = C.channel0(C.nstdb("em")).astype(float)
    L = ["# 5. Protocol of Hanzala et al. (Sensors 2026) re-run on the 12 published records", "",
         "SNR values in dB on 300-310 s. 'Offsets removed' = the per-segment constants of step 1 subtracted. Pre-filter "
         "values: zero-phase / causal.", "",
         "| record | input SNR reported | input SNR reproduced | input SNR, offsets removed | SNR change reported (SWT) | "
         "pre-filter alone | pre-filter alone, offsets removed |", "|---|---|---|---|---|---|---|"]
    diffs = []
    for rid in ("118", "119"):
        xc0 = (C.channel0(C.mitdb(rid)) - 1024) / 200.0
        for lv in C.LEVELS:
            r = f"{rid}e{lv}"
            e = C.channel0(C.nstdb(r)).astype(float)
            dc, _ = C.fit_segment_offsets(e - xc0 * 200.0, em)
            out = []
            for xy_counts in (e, e - dc):
                xy = (xy_counts - 1024) / 200.0              # physical, as WFDB reads it (header baseline 1024)
                xy = xy - xy.mean()
                xc = xc0 - xc0.mean()
                s_in = snr(fitted(xc, xy), xy)
                g = []
                for zp in (True, False):
                    y = prefilter(xy, zp)
                    g.append(snr(fitted(xc, y), y) - s_in)
                out.append((s_in, g))
            p_in, p_ch = REPORTED[r]
            (a_in, a_g), (b_in, b_g) = out
            diffs.append(abs(a_g[0] - p_ch))
            L.append(f"| {r} | {p_in:+.2f} | {a_in:+.2f} | {b_in:+.2f} | {p_ch:+.2f} | {a_g[0]:+.2f} / {a_g[1]:+.2f} | "
                     f"{b_g[0]:+.2f} / {b_g[1]:+.2f} |")
            print(L[-1], flush=True)
    d = np.array(diffs)
    L += ["", f"|reported SWT change - pre-filter alone (zero-phase)|: <= 0.2 dB in {int(np.sum(d <= 0.2))} of 12 records, "
          f"<= 0.3 dB in {int(np.sum(d <= 0.3))} of 12, max {d.max():.2f} dB."]
    open(os.path.join(C.RESULTS, "05_sensors2026_reproduction.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
