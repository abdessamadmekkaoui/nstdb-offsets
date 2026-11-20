"""Download the two PhysioNet databases used here into <repo>/data (about 110 MB in total).
    MIT-BIH Noise Stress Test Database 1.0.0  -> data/nstdb   (doi:10.13026/C2HS3T)
    MIT-BIH Arrhythmia Database 1.0.0          -> data/mitdb   (doi:10.13026/C2F305)
Both are open (Open Data Commons Attribution License v1.0); please cite them as PhysioNet asks.
"""
import os

import wfdb

import common as C

if __name__ == "__main__":
    for db, d in (("nstdb", C.NSTDB), ("mitdb", C.MITDB)):
        os.makedirs(d, exist_ok=True)
        print(f"downloading {db} -> {d}")
        wfdb.dl_database(db, dl_dir=d)
    print("done")
