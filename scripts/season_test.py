"""Precession test of the month-season pairings that survive in the Critical Edition.

Pairings (CE present): Ayodhya 2.3.4 Caitra with blossoming groves; Kishkindha 4.25.12
Sravana = first month of the rains; 4.25.15 Kartika = rains over, campaign begins;
Aranya 3.15 hemanta with the Sun 'firmly in the south' and long nights led by Pusya
(full moon in Pusya -> month Pausa). A lunar month named X has its mid-point at sidereal
Sun ~ S_X +- 15 deg (amanta/purnimanta and lunar-solar drift). Each pairing passes at an
epoch if that range overlaps the expected tropical-Sun window for the Indian climate.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import ephem  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"
# month: (sidereal Sun at mid-month, expected tropical window (start, end), description)
PAIRS = {
    "Caitra - groves in bloom (vasanta)": (0.0, (315.0, 45.0)),
    "Sravana - first month of the rains": (120.0, (80.0, 130.0)),
    "Kartika - rains over, campaign season": (210.0, (180.0, 240.0)),
    "Pausa - hemanta, Sun firmly in the south": (270.0, (225.0, 315.0)),
}
HALF = 15.0


def ayanamsa(year):
    jd = ephem.julian_calendar_to_jd(year, 7, 1)
    t = (jd - ephem.JD_J2000) / 36525.0
    general_precession = (5028.796195 * t + 1.1054348 * t ** 2 + 0.00007964 * t ** 3) / 3600.0
    return float(ephem.spica_lon_j2000(jd)) - 180.0 + general_precession


def in_window(lon, window):
    start, end = window
    return (lon - start) % 360 <= (end - start) % 360


def passes(mid_sidereal, window, aya):
    lons = (np.arange(mid_sidereal - HALF, mid_sidereal + HALF + 0.1, 1.0) + aya) % 360
    return bool(any(in_window(l, window) for l in lons))


def main():
    years = list(range(-13000, 2001, 50))
    rows = []
    for year in years:
        aya = ayanamsa(year)
        row = {"year": year, "ayanamsa_deg": round(aya, 2)}
        for name, (mid, window) in PAIRS.items():
            row[name] = passes(mid, window, aya)
        row["all_pass"] = all(row[n] for n in PAIRS)
        rows.append(row)
    ok = [r["year"] for r in rows if r["all_pass"]]
    span = (min(ok), max(ok)) if ok else None
    print(f"All four CE month-season pairings satisfied for years {span} (50-yr steps)")
    for name in PAIRS:
        good = [r["year"] for r in rows if r[name]]
        print(f"   {name:<45} satisfied {min(good)} .. {max(good)}" if good else f"   {name}: never")
    for y in (-6265, -4497, -5113, -12208, -1500, -500, 0, 500):
        r = min(rows, key=lambda r: abs(r["year"] - y))
        print(f"   year {y:>6}: " + ", ".join(f"{n.split(' -')[0]}={'ok' if r[n] else 'FAIL'}" for n in PAIRS))
    (DATA / "season_test.json").write_text(json.dumps({"all_pass_span": span, "rows": rows}, indent=1))


if __name__ == "__main__":
    main()
