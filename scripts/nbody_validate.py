"""Validate the N-body sky against JPL DE441 results saved earlier (6266 BCE, 4498 BCE, 7120 BCE, 5352 BCE)."""
import json
from pathlib import Path

import numpy as np

import nbody

DATA = Path(__file__).resolve().parents[1] / "data"
ECL = np.radians(84381.406 / 3600.0)
SPICA = (201.29824736, -11.16131949, -42.35, -30.67)
IDX = {"sun": 0, "mercury": 1, "venus": 2, "mars": 4, "jupiter": 5, "saturn": 6}


def j2000_ecl_lon(vec):
    x, y, z = vec[..., 0], vec[..., 1], vec[..., 2]
    ye = y * np.cos(ECL) + z * np.sin(ECL)
    return np.degrees(np.arctan2(ye, x)) % 360


def spica_lon_linear(jd):
    yrs = (jd - nbody.JD_J2000) / 365.25
    dec = SPICA[1] + SPICA[3] * yrs / 3.6e6
    ra = SPICA[0] + SPICA[2] * yrs / 3.6e6 / np.cos(np.radians(dec))
    r, d = np.radians(ra), np.radians(dec)
    return j2000_ecl_lon(np.array([np.cos(d) * np.cos(r), np.cos(d) * np.sin(r), np.sin(d)]))


def main(correct):
    """correct=False: raw Newtonian integration; True: after removing the drift fitted in nbody_calib.py."""
    from treta_sky import drift_rotate
    drift = json.loads((DATA / "nbody_drift_calibration.json").read_text())
    search = json.loads((DATA / "rama_birth_search.json").read_text())
    checks = json.loads((DATA / "astro_checks.json").read_text())
    targets = [(m["date"], m["jd_tdb"], m["lon"]) for m in next(r for r in search["runs"] if r["ayanamsa_offset_deg"] == 0)["matches"]]
    targets += [(d["date"], d["jd_tdb"], d["sidereal_lon"]) for d in checks["sun_in_aries_reading"]]
    targets.sort(key=lambda t: -t[1])
    sim = nbody.build_sim(2.0)
    sim.dt = -2.0
    rows = []
    for date, jd, ref in targets:
        sim.integrate(jd - nbody.JD_J2000)
        xyz, vxyz = nbody.state(sim)
        xyz = nbody.mercury_gr_correction(xyz, vxyz, sim.t)
        if correct:
            xyz = drift_rotate(xyz[None], vxyz[None], np.array([sim.t / 365.25]), drift)[0]
        zero = spica_lon_linear(jd) - 180.0
        row = {"date": date}
        for body, i in IDX.items():
            lon = (j2000_ecl_lon(xyz[i] - xyz[3]) - zero) % 360
            row[body] = round(float(((lon - ref[body]) + 180) % 360 - 180), 3)
        rows.append(row)
        print(f"{date:<46} N-body minus DE441 (deg): " + "  ".join(f"{b} {row[b]:+.3f}" for b in IDX))
    worst = {b: max(abs(r[b]) for r in rows) for b in IDX}
    print("max |difference| per body:", worst)
    name = "nbody_validation_corrected.json" if correct else "nbody_validation.json"
    (DATA / name).write_text(json.dumps({"rows": rows, "max_abs_diff_deg": worst}, indent=1))


if __name__ == "__main__":
    for flag in (False, True):
        print("drift-corrected" if flag else "raw Newtonian")
        main(flag)
