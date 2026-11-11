"""Fetch DE441 heliocentric J2000-ecliptic vectors from JPL Horizons (public API, no login) for
calibrating the N-body mean-longitude drift (Newtonian integration lacks general relativity)."""
import json
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parents[1] / "data"
BODIES = {"emb": "3", "mercury": "199", "venus": "299", "mars": "4", "jupiter": "5", "saturn": "6"}
JD_J2000 = 2451545.0
# 15 epochs: ~9900 BCE .. 2000 CE every 850 years (as JD TDB)
EPOCH_JD = [JD_J2000 + 365.25 * y for y in range(-11900, 1, 850)]  # Horizons limit: 9999 BCE


def fetch(cmd, jds):
    mjds = " ".join(f"{jd - 2400000.5:.1f}" for jd in jds)  # TLIST values are read as MJD
    q = {"format": "text", "COMMAND": f"'{cmd}'", "OBJ_DATA": "'NO'", "MAKE_EPHEM": "'YES'", "EPHEM_TYPE": "'VECTORS'",
         "CENTER": "'500@10'", "REF_PLANE": "'ECLIPTIC'", "REF_SYSTEM": "'ICRF'", "VEC_TABLE": "'1'",
         "VEC_CORR": "'NONE'", "TIME_TYPE": "'TDB'", "CSV_FORMAT": "'YES'", "OUT_UNITS": "'AU-D'", "TLIST": f"'{mjds}'"}
    url = "https://ssd.jpl.nasa.gov/api/horizons.api?" + urllib.parse.urlencode(q)
    text = urllib.request.urlopen(url, timeout=120).read().decode()
    body = text.split("$$SOE")[1].split("$$EOE")[0]
    rows = []
    for line in body.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        rows.append([float(parts[0]), float(parts[2]), float(parts[3]), float(parts[4])])
    return rows


if __name__ == "__main__":
    out = {}
    for name, cmd in BODIES.items():
        out[name] = fetch(cmd, EPOCH_JD)
        print(name, len(out[name]), "rows; first JD", out[name][0][0])
    (DATA / "horizons_de441_helio.json").write_text(json.dumps(out, indent=1))
