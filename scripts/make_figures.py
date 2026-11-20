"""Figures of the paper, from the data (fig. 1) and from the results of steps 3 and 5.
  figures/fig1_offsets_mechanism.png  (a) 118e06: added noise and fitted per-segment offset; (b) the 7:00 switch
  figures/fig2_inflation_by_noise.png score with nst offsets / same noise without offsets / continuous noise, 12 dB
  figures/fig3_sensors2026_repro.png  reported SWT gain vs the 0.5 Hz pre-filter alone (as published / offsets removed)
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import common as C  # noqa: E402

C_NST, C_GATED, C_CONT, C_PAPER = "#c0392b", "#2471a3", "0.6", "0.15"
plt.rcParams.update({"font.size": 8, "font.family": "serif", "savefig.dpi": 300, "axes.spines.top": False,
                     "axes.spines.right": False})
METH = [("KA", "Kaiser BPF"), ("HP", "0.5 Hz IIR HP"), ("MED", "median baseline"), ("DWT", "db4 J4 DWT")]


def fig1():
    em = C.channel0(C.nstdb("em")) / 200.0
    m = C.channel0(C.mitdb("118")) - 1024
    n = (C.channel0(C.nstdb("118e06")) - m) / 200.0                # added noise, mV (ADC zero 0)
    dc, _ = C.fit_segment_offsets(n, em)
    N, FS, SEG, T0 = C.N, C.FS, C.SEG, C.T0
    t = np.arange(N) / FS / 60
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 2.3), gridspec_kw={"width_ratios": [1.6, 1]})
    for k, a in enumerate(C.segment_starts()):
        if k % 2 == 0:
            a1.axvspan(a / FS / 60, min(N, a + SEG) / FS / 60, color="0.93", lw=0, zorder=0)
    a1.plot(t[::4], n[::4], lw=0.35, color="0.45", label="added noise = record $-$ clean ECG")
    a1.plot(t, dc, lw=1.3, color=C_NST, label="per-segment offset (fitted)")
    a1.axhline(0, color="k", lw=0.4)
    a1.set(xlabel="time (min)", ylabel="mV", xlim=(0, 30.2))
    a1.legend(fontsize=6.5, frameon=False, loc="upper left")
    a1.set_title("(a) 118e06: noise on (shaded) / off every 2 min from 5:00", fontsize=8, loc="left")
    sw = T0 + SEG
    z = slice(sw - 3 * FS, sw + 3 * FS)
    tz = (np.arange(N)[z] - sw) / FS
    a2.plot(tz, n[z], lw=0.6, color="0.45")
    a2.plot(tz, dc[z], lw=1.3, color=C_NST)
    a2.axvline(0, color="k", lw=0.5, ls=":")
    a2.axhline(0, color="k", lw=0.4)
    a2.annotate("noise switched off,\noffset held for 2 min", xy=(1.5, dc[sw + int(1.5 * FS)]),
                xytext=(0.25, 1.6), fontsize=6.5, arrowprops=dict(arrowstyle="->", lw=0.6))
    a2.set_xlabel("time from the 7:00 switch (s)")
    a2.set_title("(b) nst keeps the output continuous", fontsize=8, loc="left")
    fig.tight_layout()
    fig.savefig(os.path.join(C.FIGURES, "fig1_offsets_mechanism.png"))
    plt.close(fig)


def fig2(level="12"):
    rows = list(csv.DictReader(open(os.path.join(C.RESULTS, "03_inflation.csv"))))
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.6))
    for ax, nn in zip(axes, ("em", "ma", "bw")):
        R = [r for r in rows if r["noise"] == nn and r["level"] == level]
        x = np.arange(len(METH))
        w = 0.27
        for j, (var, col, lab) in enumerate((("nst", C_NST, "nst-made (with offsets)"),
                                             ("gated", C_GATED, "same noise, no offsets"),
                                             ("cont", C_CONT, "noise added continuously"))):
            ax.bar(x + (j - 1) * w, [np.mean([float(r[f"{var}:{m}"]) for r in R]) for m, _ in METH], w, color=col, label=lab)
        ax.axhline(0, color="k", lw=0.4)
        ax.set_xticks(x)
        ax.set_xticklabels([l for _, l in METH], rotation=35, ha="right", fontsize=6.5)
        sh = np.mean([float(r["offset_share_var"]) for r in R])
        ax.set_title(f"{nn}, {level} dB: offsets = {100 * sh:.0f} % of noise var.", fontsize=7, loc="left")
    axes[0].set_ylabel("SNR improvement (dB)")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, fontsize=6.5, frameon=False, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(os.path.join(C.FIGURES, "fig2_inflation_by_noise.png"))
    plt.close(fig)


def fig3():
    rows = []
    for line in open(os.path.join(C.RESULTS, "05_sensors2026_reproduction.md"), encoding="utf-8"):
        p = [x.strip() for x in line.split("|")]
        if len(p) > 7 and p[1][:3] in ("118", "119"):
            f = lambda s: float(s.replace("+", ""))  # noqa: E731
            rows.append(dict(rec=p[1], paper_gain=f(p[5]), pre_pub=f(p[6].split("/")[0]), pre_nooff=f(p[7].split("/")[0])))
    x = np.arange(len(rows))
    w = 0.27
    fig, ax = plt.subplots(figsize=(3.5, 2.8))
    ax.bar(x - w, [r["paper_gain"] for r in rows], w, color=C_PAPER, label="reported (SWT, best config.)")
    ax.bar(x, [r["pre_pub"] for r in rows], w, color=C_NST, label="their 0.5 Hz pre-filter alone")
    ax.bar(x + w, [r["pre_nooff"] for r in rows], w, color=C_GATED, label="pre-filter alone, offsets removed")
    ax.axhline(0, color="k", lw=0.4)
    ax.set_xticks(x)
    ax.set_xticklabels([r["rec"] for r in rows], rotation=60, fontsize=6)
    ax.set_ylabel("SNR change (dB), 300-310 s")
    h, l = ax.get_legend_handles_labels()
    fig.legend(h, l, fontsize=6, frameon=False, loc="upper center", ncol=1, bbox_to_anchor=(0.55, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    fig.savefig(os.path.join(C.FIGURES, "fig3_sensors2026_repro.png"))
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(C.FIGURES, exist_ok=True)
    fig1()
    fig2()
    fig3()
    print("figures written to", C.FIGURES)
