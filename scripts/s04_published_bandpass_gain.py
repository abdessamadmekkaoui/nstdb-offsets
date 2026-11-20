"""Step 4 - band-pass gain on the 12 published records, as published and with the per-segment offsets removed.

Clean = reference of MIT-BIH 118 / 119 (common.clean_reference). Noisy = published record read with ADC zero 0 (as nst
wrote it; this undoes the constant -5.12 mV header shift). Method = Kaiser FIR band-pass 0.5-150 Hz.
Score = SNR improvement, means removed, 5:00 to 10 s before the end.
Output: results/04_published_bandpass_gain.md
"""
import os

import numpy as np

import common as C

EV = slice(C.T0, C.N - 10 * C.FS)


def gain(clean, noisy):
    scale = 0.9 * 32767 / max(np.max(np.abs(noisy)), np.max(np.abs(clean)))
    x, c = np.round(noisy * scale), np.round(clean * scale)
    return C.snr_db(c[EV], C.kaiser_bpf(x)[EV]) - C.snr_db(c[EV], x[EV])


def main():
    em = C.channel0(C.nstdb("em")) / 200.0
    L = ["# 4. Kaiser band-pass gain on the 12 published records", "",
         "| record | as published (dB) | per-segment offsets removed (dB) |", "|---|---|---|"]
    a_all, b_all = [], []
    for rid in ("118", "119"):
        x0 = (C.channel0(C.mitdb(rid)) - 1024) / 200.0
        y = C.clean_reference(x0)
        for lv in C.LEVELS:
            e = C.channel0(C.nstdb(f"{rid}e{lv}")) / 200.0
            n = e - x0                                        # added noise (e-record read with ADC zero 0)
            dc, _ = C.fit_segment_offsets(n, em)
            a, b = gain(y, y + n), gain(y, y + n - dc)
            a_all.append(a)
            b_all.append(b)
            L.append(f"| {rid}e{lv} | {a:+.2f} | {b:+.2f} |")
            print(L[-1], flush=True)
    L += [f"| **mean** | **{np.mean(a_all):+.2f}** | **{np.mean(b_all):+.2f}** |"]
    open(os.path.join(C.RESULTS, "04_published_bandpass_gain.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
