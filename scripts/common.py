"""Shared helpers: data paths, a WFDB format 212/16 reader, the nst protocol constants, the per-segment offset fit,
the clean reference, the SNR improvement metric and the methods scored in the paper.

Data locations (PhysioNet, see download_data.py):
    NSTDB_DIR  MIT-BIH Noise Stress Test Database 1.0.0   (default: <repo>/data/nstdb)
    MITDB_DIR  MIT-BIH Arrhythmia Database 1.0.0          (default: <repo>/data/mitdb)
Both can be overridden with environment variables of the same name.
"""
import os

import numpy as np
import pywt
from scipy.ndimage import median_filter
from scipy.signal import butter, filtfilt, firwin, iirnotch, kaiser_beta, lfilter, oaconvolve

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NSTDB = os.environ.get("NSTDB_DIR", os.path.join(REPO, "data", "nstdb"))
MITDB = os.environ.get("MITDB_DIR", os.path.join(REPO, "data", "mitdb"))
RESULTS = os.path.join(REPO, "results")
FIGURES = os.path.join(REPO, "figures")

FS = 360                      # Hz
N = 650000                    # samples per record (30:05)
SEG = 120 * FS                # nst protocol: 2-minute segments
T0 = 300 * FS                 # noise starts at 5:00
LEVELS = ("24", "18", "12", "06", "00", "_6")     # published records 118eXX / 119eXX
PUBLISHED = [f"{r}e{lv}" for r in ("118", "119") for lv in LEVELS]


# ---------------------------------------------------------------- reading (independent of wfdb-python)
def parse_header(path):
    """Minimal WFDB header(5) parser for single-segment records."""
    lines = [l for l in open(path + ".hea").read().splitlines() if l.strip() and not l.startswith("#")]
    rec = lines[0].split()
    sigs = []
    for l in lines[1:1 + int(rec[1])]:
        f = l.split()
        g = f[2]
        base = None
        if "(" in g:
            g, base = g.split("(")
            base = int(base.rstrip(")").split(")")[0])
        gain = float(g.split("/")[0]) if g else 200.0
        adczero = int(f[4])
        sigs.append(dict(file=f[0], fmt=int(f[1]), gain=gain if gain else 200.0, res=int(f[3]), adczero=adczero,
                         baseline=adczero if base is None else base, init=int(f[5]), cksum=int(f[6]),
                         desc=" ".join(f[8:])))
    return dict(name=rec[0], nsig=int(rec[1]), fs=float(rec[2]), n=int(rec[3]), sigs=sigs)


def decode(path, h=None):
    """Digital samples (n x nsig, int64) of a format 212 or 16 record, written from the WFDB signal(5) spec."""
    h = h or parse_header(path)
    raw = np.fromfile(os.path.join(os.path.dirname(path), h["sigs"][0]["file"]), dtype=np.uint8)
    fmt, ns = h["sigs"][0]["fmt"], h["nsig"]
    if fmt == 16:
        d = raw.view("<i2").astype(np.int64).reshape(-1, ns)
    elif fmt == 212:
        b = raw[: len(raw) // 3 * 3].reshape(-1, 3).astype(np.int64)
        s0 = b[:, 0] | ((b[:, 1] & 0x0F) << 8)
        s1 = b[:, 2] | ((b[:, 1] & 0xF0) << 4)
        s = np.empty(2 * len(b), np.int64)
        s[0::2], s[1::2] = s0, s1
        s = np.where(s >= 2048, s - 4096, s)
        d = s.reshape(-1, ns)
    else:
        raise ValueError(f"format {fmt} not supported")
    return d[: h["n"]]


def channel0(path):
    """Channel 0 (MLII for MIT-BIH, noise channel 1 for NSTDB), first N samples, digital counts."""
    return decode(path)[:N, 0]


def nstdb(name):
    return os.path.join(NSTDB, name)


def mitdb(name):
    return os.path.join(MITDB, name)


def mitdb_records():
    return sorted(f[:-4] for f in os.listdir(MITDB) if f.endswith(".dat"))


# ---------------------------------------------------------------- the offsets
def segment_starts():
    return list(range(T0, N, SEG))


def fit_segment_offsets(added, noise):
    """Per 2-minute segment from 5:00: least-squares fit added = a*noise + c. Returns (c per sample, list of (a, c))."""
    dc = np.zeros(len(added))
    fits = []
    for a0 in segment_starts():
        s = slice(a0, min(len(added), a0 + SEG))
        a, c = np.linalg.lstsq(np.c_[noise[s], np.ones(s.stop - a0)], added[s], rcond=None)[0]
        dc[s] = c
        fits.append((float(a), float(c)))
    return dc, fits


def make_nst_noise(v, g):
    """Noise exactly as nst adds it (app/nst.c): gain g on from 5:00 for 2 min, 0 for 2 min, ...; at each switch the
    continuity term z is updated on the previous sample with the new gain and then held for the whole segment.
    Returns dict(nst = g_k*v - z_k, gated = g_k*v (same on/off, no offsets), cont = g*(v - mean) from 5:00)."""
    A, B = np.zeros(N), np.zeros(N)
    z, gk = 0.0, 0.0
    for k, a0 in enumerate(segment_starts()):
        s = slice(a0, min(N, a0 + SEG))
        gn = g if k % 2 == 0 else 0.0
        z = z + (gn - gk) * v[a0 - 1]
        gk = gn
        A[s] = gn * v[s] - z
        B[s] = gn * v[s]
    C = np.zeros(N)
    C[T0:] = g * (v[T0:] - v[T0:].mean())
    return {"nst": A, "gated": B, "cont": C}


# ---------------------------------------------------------------- reference, SNR rule, metric
def baseline_two_median(x):
    """Two-stage median baseline (200 ms then 600 ms)."""
    b = median_filter(x, size=int(0.2 * FS) | 1, mode="nearest")
    return median_filter(b, size=int(0.6 * FS) | 1, mode="nearest")


def clean_reference(x_mV):
    """Clean reference of a MIT-BIH record: two-stage median baseline removed, then 60 and 120 Hz notches (Q 35,
    zero phase)."""
    y = x_mV - baseline_two_median(x_mV)
    for f0 in (60.0, 120.0):
        b, a = iirnotch(f0, 35.0, FS)
        y = filtfilt(b, a, y)
    return y


BEATS = set("NLRBAaJSVrFejnE/fQ?")


def qrs_amplitude(x, ann_samples, ann_symbols):
    """Median QRS peak-to-peak amplitude, +-50 ms around each beat annotation (simplified form of nst's rule, which
    uses a 5 % trimmed mean of the first 300 normal beats)."""
    h = int(0.05 * FS)
    return float(np.median([np.ptp(x[max(0, s - h):s + h + 1]) for s, y in zip(ann_samples, ann_symbols)
                            if y in BEATS and h <= s < N - h]))


def noise_power(v):
    """Mean 1-second variance of the noise from 5:00 (simplified form of nst's 5 % trimmed mean of 1-s RMS)."""
    w = v[T0:T0 + (N - T0) // FS * FS].reshape(-1, FS)
    return float(np.mean(np.var(w, axis=1)))


def snr_db(clean, test):
    """SNR of test against clean, both mean-removed."""
    c, t = clean - clean.mean(), test - test.mean()
    return 10 * np.log10(np.sum(c ** 2) / np.sum((c - t) ** 2))


# ---------------------------------------------------------------- methods
KAISER_TAPS, KAISER_DELAY = 1057, 528
_H_KAISER = firwin(KAISER_TAPS, (0.5, 150.0), window=("kaiser", kaiser_beta(50.0)), pass_zero=False, fs=FS)
_BHP = butter(2, 0.5 / (FS / 2), "high")


def kaiser_bpf(x):
    """Linear-phase FIR band-pass 0.5-150 Hz, Kaiser window (beta for 50 dB), 1057 taps; delay compensated."""
    y = oaconvolve(np.asarray(x, float), _H_KAISER)[:len(x)]
    return np.concatenate([y[KAISER_DELAY:], np.zeros(KAISER_DELAY)])


def butter_hp(x):
    """Causal 2nd-order Butterworth high-pass, 0.5 Hz."""
    return lfilter(*_BHP, np.asarray(x, float))


def median_baseline(x):
    x = np.asarray(x, float)
    return x - baseline_two_median(x)


def _rigrsure(v):
    n = len(v)
    s = np.sort(v * v)
    k = np.arange(1, n + 1)
    risk = (n - 2 * k + np.cumsum(s) + (n - k) * s) / n
    return float(np.sqrt(s[int(np.argmin(risk))]))


def dwt_sure(x, wavelet="db4", J=4, block=2048, min_win=16):
    """DWT denoiser: wavedec (symmetric), soft SURE threshold per detail band D1..DJ, estimated in time blocks of
    `block` samples, noise sigma = MAD/0.6745 of the band in the block; the approximation band is KEPT."""
    x = np.asarray(x, float)
    c = pywt.wavedec(x, wavelet, level=J, mode="symmetric")
    for j in range(1, J + 1):
        d = c[-j]
        w = max(block >> j, min_win)
        out = np.empty_like(d)
        t = 0.0
        for a0 in range(0, len(d), w):
            seg = d[a0:a0 + w]
            if len(seg) >= min_win or a0 == 0:
                sigma = np.median(np.abs(seg)) / 0.6745
                t = sigma * _rigrsure(seg / sigma) if sigma > 0 else 0.0
            out[a0:a0 + w] = np.sign(seg) * np.maximum(np.abs(seg) - t, 0.0)
        c[-j] = out
    return pywt.waverec(c, wavelet, mode="symmetric")[:len(x)]


METHODS = {
    "KA": ("Kaiser FIR band-pass 0.5-150 Hz", kaiser_bpf),
    "HP": ("Butterworth high-pass 0.5 Hz", butter_hp),
    "MED": ("two-stage median baseline", median_baseline),
    "DWT": ("db4 J4 SURE wavelet (keeps approximation)", dwt_sure),
}
