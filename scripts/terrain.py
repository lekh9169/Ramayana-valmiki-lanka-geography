"""Terrain facts from GEBCO 2026 used to test the textual geography.

* Summit of Mahendragiri (Hanuman's launch point in Sundara 1) and other launch candidates.
* Distances from launch points to Sri Lanka's coast and to each 100-yojana hypothesis.
* Sri Lankan massifs: summits with >= 250 m local relief, how many comparable summits
  each has within 8 km ("tri-kuta" = three-peaked), distance from the Setu landfall.
* The Surya Siddhanta 'Lanka' (equator on Ujjain's meridian): depth, and nearest land at
  any Quaternary sea level (GEBCO cell above -130 m).
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).parent))
import gebco  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "data"
R = 6371.0088


def hav(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


def summit_near(g, lat, lon, radius_km=6.0):
    e, la, lo = gebco.window(g, lat - 0.08, lat + 0.08, lon - 0.08, lon + 0.08)
    lat2, lon2 = np.meshgrid(la, lo, indexing="ij")
    e = np.where(hav(lat, lon, lat2, lon2) <= radius_km, e, np.nan)
    r, c = np.unravel_index(np.nanargmax(e), e.shape)
    return float(la[r]), float(lo[c]), float(e[r, c])


def nearest_cells(g, lat, lon, condition, box):
    e, la, lo = gebco.window(g, *box)
    lat2, lon2 = np.meshgrid(la, lo, indexing="ij")
    mask = condition(e)
    d = np.where(mask, hav(lat, lon, lat2, lon2), np.inf)
    r, c = np.unravel_index(np.argmin(d), d.shape)
    return {"lat": round(float(la[r]), 4), "lon": round(float(lo[c]), 4), "elev_m": float(e[r, c]),
            "distance_km": round(float(d[r, c]), 1)}


def main():
    g = gebco.load_grid()
    res = {}
    mlat, mlon, melev = summit_near(g, 8.39, 77.52)
    res["mahendragiri_summit_gebco"] = {"lat": round(mlat, 4), "lon": round(mlon, 4), "elev_m": melev}
    print(f"Mahendragiri (TN) GEBCO summit: {mlat:.4f}N {mlon:.4f}E {melev:.0f} m")

    sl_box = (5.8, 10.0, 79.4, 82.0)

    def srilanka_land(e, level):
        """Land above `level` belonging to Sri Lanka or Mannar island (drops sand cays)."""
        labels, n = ndimage.label(e > level, structure=np.ones((3, 3)))
        sizes = ndimage.sum(np.ones_like(e), labels, index=np.arange(1, n + 1))
        keep = np.isin(labels, np.where(sizes >= 300)[0] + 1)
        return keep

    launch = {"Mahendragiri summit": (mlat, mlon), "Dhanushkodi / Arichal Munai": (9.18, 79.42),
              "Kanyakumari": (8.08, 77.55)}
    res["launch_to_srilanka"] = {}
    for name, (la, lo) in launch.items():
        row = {}
        for level in (0, -3, -10, -40, -120):
            row[f"coast_at_{level}m"] = nearest_cells(g, la, lo, lambda e, L=level: srilanka_land(e, L), sl_box)
        res["launch_to_srilanka"][name] = row
        print(f"{name:28s} -> nearest Sri Lankan coast now {row['coast_at_0m']['distance_km']} km "
              f"(at -10 m: {row['coast_at_-10m']['distance_km']} km)")

    # Surya Siddhanta Lanka: equator on Ujjain's meridian
    ujjain_lon = 75.7683
    depth = gebco.sample(g, 0.0, ujjain_lon)
    near_any = nearest_cells(g, 0.0, ujjain_lon, lambda e: e > -130, (-8.0, 8.0, 70.0, 80.0))
    near_now = nearest_cells(g, 0.0, ujjain_lon, lambda e: e > 0, (-8.0, 8.0, 70.0, 80.0))
    res["surya_siddhanta_lanka"] = {"lat": 0.0, "lon": ujjain_lon, "depth_m": depth,
                                    "nearest_cell_above_-130m": near_any, "nearest_land_now": near_now,
                                    "distance_from_mahendragiri_km": round(float(hav(mlat, mlon, 0, ujjain_lon)), 1)}
    print(f"Equator x Ujjain meridian: depth {depth:.0f} m; nearest seabed shallower than -130 m: "
          f"{near_any['distance_km']} km at {near_any['lat']}N {near_any['lon']}E ({near_any['elev_m']:.0f} m); "
          f"nearest land now {near_now['distance_km']} km")

    # Maldives: largest exposed area at LGM
    e, la, lo = gebco.window(g, -1.0, 7.5, 72.0, 74.2)
    cell = (np.radians(gebco.CELL) * R) ** 2 * np.cos(np.radians(la))[:, None]
    res["maldives_exposed_km2"] = {str(L): round(float((cell * (e > L)).sum())) for L in (0, -40, -80, -120)}
    print("Maldives exposed area km2 by sea level:", res["maldives_exposed_km2"])

    # Sri Lankan summits
    e, la, lo = gebco.window(g, 5.8, 9.9, 79.5, 82.0)
    peaks = (e == ndimage.maximum_filter(np.nan_to_num(e, nan=-9999), size=13)) & (e > 200)
    low = ndimage.minimum_filter(np.nan_to_num(e, nan=9999), size=23)  # ~10 km box
    relief = e - low
    pk = np.argwhere(peaks & (relief >= 250))
    rows = []
    for r, c in pk:
        rows.append({"lat": float(la[r]), "lon": float(lo[c]), "elev_m": float(e[r, c]), "relief_m": float(relief[r, c])})
    for p in rows:
        close = [q for q in rows if q is not p and hav(p["lat"], p["lon"], q["lat"], q["lon"]) <= 8.0
                 and q["elev_m"] >= 0.75 * p["elev_m"]]
        p["comparable_summits_within_8km"] = len(close)
        p["km_from_talaimannar"] = round(float(hav(p["lat"], p["lon"], 9.09, 79.72)), 1)
    rows.sort(key=lambda p: -p["elev_m"])
    res["srilanka_summits"] = rows
    print(f"Sri Lanka: {len(rows)} summits with >=250 m relief; top 15:")
    for p in rows[:15]:
        print(f"   {p['lat']:.3f}N {p['lon']:.3f}E {p['elev_m']:6.0f} m relief {p['relief_m']:5.0f} "
              f"neighbours {p['comparable_summits_within_8km']}  {p['km_from_talaimannar']:6.1f} km from Talaimannar")
    first_high = min((p for p in rows if p["elev_m"] >= 300), key=lambda p: p["km_from_talaimannar"])
    print(f"Nearest >=300 m summit to the Setu landfall: {first_high}")
    res["nearest_300m_summit_to_landfall"] = first_high
    # India - Maldives sill (30" sampling is enough for a km-deep saddle)
    import sill  # noqa: E402
    e, la, lo = gebco.window(g, -1.0, 9.5, 71.0, 79.0)
    e, la, lo = e[::2, ::2], la[::2], lo[::2]
    res["india_maldives_sill_m"] = round(sill.sill_level(e, sill.idx(la, lo, 8.5, 77.5),
                                                         sill.idx(la, lo, 4.175, 73.509),
                                                         lo=-4000, hi=10, tol=1), 0)
    print(f"India - Maldives sill: {res['india_maldives_sill_m']:.0f} m")
    (OUT / "terrain.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
