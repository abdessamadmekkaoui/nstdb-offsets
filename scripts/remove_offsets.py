"""Remove the nst per-segment offsets from a noise stress test record.

nst (WFDB) adds a continuity term at every noise on/off switch and holds it for the whole next segment. This tool fits,
in every segment from `start` on, (noisy - clean) = a*noise + c by least squares, per channel, and subtracts c.
The output is the same record with the offsets removed; it is also written with ADC zero 0 (as nst wrote the samples),
which undoes the constant -5.12 mV header shift of the published 118eXX / 119eXX records.

Example (the 12 published records):
    python remove_offsets.py --all-published --out ../results/offsets_removed
One record:
    python remove_offsets.py --noisy ../data/nstdb/118e06 --clean ../data/mitdb/118 --noise ../data/nstdb/em \
        --out ../results/offsets_removed
Records you made yourself with nst: give the same three records; change --start / --seg if your protocol differs from
nst's default (noise from 5:00, 2-minute segments).
"""
import argparse
import os

import numpy as np

import common as C


def remove_offsets(noisy, clean, noise, fs=360, start_s=300, seg_s=120):
    """noisy, clean, noise: 1-D arrays in the same units (clean with its ADC zero / baseline already removed).
    Returns (noisy with the per-segment constants removed, the constants per sample)."""
    n = min(len(noisy), len(clean), len(noise))
    added = noisy[:n] - clean[:n]
    dc = np.zeros(n)
    for a0 in range(start_s * fs, n, seg_s * fs):
        s = slice(a0, min(n, a0 + seg_s * fs))
        _, c = np.linalg.lstsq(np.c_[noise[s], np.ones(s.stop - a0)], added[s], rcond=None)[0]
        dc[s] = c
    return noisy[:n] - dc, dc


def process(noisy_path, clean_path, noise_path, out_dir, start_s, seg_s):
    import wfdb
    hn, hc = C.parse_header(noisy_path), C.parse_header(clean_path)
    dn, dcl, dno = C.decode(noisy_path, hn), C.decode(clean_path, hc), C.decode(noise_path)
    n = min(len(dn), len(dcl), len(dno))
    chans, offs = [], []
    for k in range(hn["nsig"]):
        clean = dcl[:n, k] - hc["sigs"][k]["adczero"]                 # nst removes the clean record's ADC zero
        fixed, dc = remove_offsets(dn[:n, k].astype(float), clean.astype(float), dno[:n, k % dno.shape[1]].astype(float),
                                   int(hn["fs"]), start_s, seg_s)
        chans.append(fixed / hn["sigs"][k]["gain"])                   # physical, ADC zero 0
        offs.append(dc / hn["sigs"][k]["gain"])
    os.makedirs(out_dir, exist_ok=True)
    name = hn["name"] + "_nooff"
    wfdb.wrsamp(name, fs=hn["fs"], units=["mV"] * hn["nsig"], sig_name=[s["desc"] or f"ch{k}" for k, s in enumerate(hn["sigs"])],
                p_signal=np.column_stack(chans), fmt=["16"] * hn["nsig"],
                adc_gain=[s["gain"] for s in hn["sigs"]], baseline=[0] * hn["nsig"], write_dir=out_dir,
                comments=[f"{hn['name']} with nst per-segment offsets removed (remove_offsets.py)"])
    o = np.column_stack(offs)
    seg0 = [o[a0, 0] for a0 in range(start_s * int(hn["fs"]), n, seg_s * int(hn["fs"]))]
    print(f"{hn['name']}: {len(seg0)} segments, channel 0 offsets {min(seg0):+.3f} .. {max(seg0):+.3f} mV -> "
          f"{os.path.join(out_dir, name)}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--noisy", help="WFDB record made by nst (path without extension)")
    p.add_argument("--clean", help="the clean record nst started from")
    p.add_argument("--noise", help="the NSTDB noise record nst added (em, ma or bw)")
    p.add_argument("--all-published", action="store_true", help="process the 12 published records 118eXX / 119eXX")
    p.add_argument("--out", default=os.path.join(C.RESULTS, "offsets_removed"))
    p.add_argument("--start", type=int, default=300, help="noise start (s), nst default 300")
    p.add_argument("--seg", type=int, default=120, help="segment length (s), nst default 120")
    a = p.parse_args()
    if a.all_published:
        for r in C.PUBLISHED:
            process(C.nstdb(r), C.mitdb(r[:3]), C.nstdb("em"), a.out, a.start, a.seg)
    elif a.noisy and a.clean and a.noise:
        process(a.noisy, a.clean, a.noise, a.out, a.start, a.seg)
    else:
        p.error("give --noisy, --clean and --noise, or --all-published")


if __name__ == "__main__":
    main()
