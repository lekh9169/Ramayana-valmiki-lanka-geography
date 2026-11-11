"""Measure the N-body (Newtonian) heliocentric mean-longitude drift against DE441 (via Horizons)
and fit a linear rate per body; the drift is the missing general-relativistic mean-motion offset."""
import json
from pathlib import Path

import numpy as np

import nbody

DATA = Path(__file__).resolve().parents[1] / "data"
ECL = np.radians(84381.406 / 3600.0)
IDX = {"emb": 3, "mercury": 1, "venus": 2, "mars": 4, "jupiter": 5, "saturn": 6}


def to_ecl(v):
    x, y, z = v
    return np.array([x, y * np.cos(ECL) + z * np.sin(ECL), -y * np.sin(ECL) + z * np.cos(ECL)])


def lon(v):
    return np.degrees(np.arctan2(v[1], v[0])) % 360


def main():
    ref = json.loads((DATA / "horizons_de441_helio.json").read_text())
    jds = [r[0] for r in ref["emb"]]
    sim = nbody.build_sim(2.0)
    sim.dt = -2.0
    diffs = {b: [] for b in IDX}
    years = []
    for k, jd in sorted(enumerate(jds), key=lambda x: -x[1]):
        sim.integrate(jd - nbody.JD_J2000)
        xyz, vxyz = nbody.state(sim)
        xyz = nbody.mercury_gr_correction(xyz, vxyz, sim.t)
        years.append((jd - nbody.JD_J2000) / 365.25)
        for b, i in IDX.items():
            mine = lon(to_ecl(xyz[i] - xyz[0]))
            de = lon(np.array(ref[b][k][1:4]))
            diffs[b].append(((mine - de) + 180) % 360 - 180)
    years = np.array(years)
    out = {}
    for b in IDX:
        d = np.array(diffs[b])
        lin = np.polyfit(years, d, 1)
        quad = np.polyfit(years, d, 2)
        res = d - np.polyval(lin, years)
        out[b] = {"deg_per_kyr": round(float(lin[0] * 1000), 6), "offset_deg": round(float(lin[1]), 5),
                  "quadratic_deg_per_kyr2": float(quad[0] * 1e6), "rms_residual_deg": round(float(res.std()), 5),
                  "extrapolated_869ka_deg": round(float(lin[0] * -869_128), 2)}
        print(f"{b:8s} drift {lin[0]*1000:+.5f} deg/kyr  quad {quad[0]*1e6:+.2e} deg/kyr^2  rms {res.std():.4f} deg  "
              f"-> at 869 ka {lin[0] * -869128:+.2f} deg")
    (DATA / "nbody_drift_calibration.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
