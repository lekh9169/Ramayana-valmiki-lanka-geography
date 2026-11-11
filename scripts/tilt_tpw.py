"""Axial tilt and true polar wander (TPW) at the Puranic end of Treta (~869 ka).

* Obliquity (tilt of the spin axis to the orbit, Berger & Loutre 1991) sets the tropics, not the
  equator: the equator is the great circle 90 deg from the spin axis *on the crust*, so tilt does
  not move it or Ujjain's meridian.
* What can move the equator across the crust is TPW: the whole solid Earth rotating relative to the
  spin axis as mass is redistributed. This script moves the pole by delta degrees toward every
  azimuth, rebuilds the equator and Ujjain's meridian, finds where they cross (south of Ujjain), carries
  that point to today's coordinates with the plate motion, and asks GEBCO whether it was ever land.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import gebco  # noqa: E402
import tectonics  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"
YEARS = 869_052 + 76
UJJAIN = (23.1713, 75.7665)
LAND_LEVEL = -149.0  # deepest glacial sea level (-128 m) plus ~21 m ridge subsidence: most favourable case


def unit(lat, lon):
    p, l = np.radians(lat), np.radians(lon)
    return np.array([np.cos(p) * np.cos(l), np.cos(p) * np.sin(l), np.sin(p)])


def latlon(v):
    v = v / np.linalg.norm(v)
    return float(np.degrees(np.arcsin(v[2]))), float(np.degrees(np.arctan2(v[1], v[0])))


def obliquity():
    rows = []
    for line in (DATA / "paleo" / "berger_loutre_1991_orbit91.txt").read_text().splitlines():
        parts = line.split()
        if len(parts) == 9:
            try:
                rows.append((float(parts[0]), float(parts[3])))
            except ValueError:
                pass
    a = np.array(rows)
    last = a[a[:, 0] >= -1000]
    return {"at_869ka_deg": float(np.interp(-869.05, a[::-1, 0], a[::-1, 1])), "today_deg": float(a[a[:, 0] == 0][0, 1]),
            "last_1myr_range_deg": [float(last[:, 1].min()), float(last[:, 1].max())]}


def crossing(delta_deg, pole_toward_lon):
    """Equator x Ujjain-meridian point (in today's coordinates) if the pole had sat delta_deg away."""
    uj_then = unit(*tectonics.position_at(*UJJAIN, YEARS))
    d, lam = np.radians(delta_deg), np.radians(pole_toward_lon)
    pole = np.array([np.sin(d) * np.cos(lam), np.sin(d) * np.sin(lam), np.cos(d)])
    foot = uj_then - (uj_then @ pole) * pole  # Ujjain's meridian meets the equator 90 deg from the pole
    lat_then, lon_then = latlon(foot)
    return tectonics.position_at(lat_then, lon_then, -YEARS)


def main():
    grid = gebco.load_grid()
    out = {"obliquity": obliquity(), "tpw": []}
    o = out["obliquity"]
    print(f"Obliquity: {o['at_869ka_deg']:.3f} deg at 869 ka vs {o['today_deg']:.3f} today "
          f"(last 1 Myr {o['last_1myr_range_deg'][0]:.2f}-{o['last_1myr_range_deg'][1]:.2f})")
    base = crossing(0.0, 0.0)
    out["no_tpw_point"] = [round(base[0], 4), round(base[1], 4)]
    for delta in (0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0):
        best = None
        for lam in np.arange(0, 360, 2.0):
            lat, lon = crossing(delta, lam)
            z = gebco.sample(grid, lat, lon)
            if best is None or z > best["depth_m"]:
                best = {"pole_toward_lon": float(lam), "lat": round(lat, 3), "lon": round(lon, 3), "depth_m": z}
        best["delta_deg"] = delta
        best["was_land"] = best["depth_m"] > LAND_LEVEL
        out["tpw"].append(best)
        print(f"TPW {delta:4.2f} deg: shallowest possible crossing {best['lat']:.3f}N {best['lon']:.3f}E depth "
              f"{best['depth_m']:.0f} m (pole moved toward {best['pole_toward_lon']:.0f}E) -> land: {best['was_land']}")
    # smallest TPW that puts the crossing on seabed shallower than LAND_LEVEL
    need = None
    for delta in np.arange(0.1, 6.01, 0.05):
        for lam in np.arange(0, 360, 2.0):
            lat, lon = crossing(delta, lam)
            if gebco.sample(grid, lat, lon) > LAND_LEVEL:
                need = {"delta_deg": round(float(delta), 2), "pole_toward_lon": float(lam), "lat": round(lat, 3), "lon": round(lon, 3)}
                break
        if need:
            break
    out["minimum_tpw_for_land"] = need
    print(f"Minimum TPW needed for the crossing to have been land: {need}")
    (DATA / "tilt_tpw.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
