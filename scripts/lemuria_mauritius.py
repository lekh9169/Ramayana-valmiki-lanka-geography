"""Lemuria, Kumari Kandam and Mauritius, tested on the bathymetry.

* Kumari Kandam (GEBCO 2026): how far land really reached south of Kanyakumari at glacial sea levels, how much of
  South India and Sri Lanka has been drowned since, and how deep the ocean is beyond.
* Lemuria (GEBCO 2026): all land the Indian Ocean held at the lowest sea level of the last million years, against the
  depths a sunken continent would have to cross.
* Mauritius and the Mascarene banks (NOAA ETOPO 2022, 1', because they lie west of the GEBCO subset's 62.76 E edge):
  island and bank areas today, at the Treta sea level (-90 m) and at -128 m; distances and the yojana they imply; and
  the deepest point between the Mascarenes and Chagos.
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).parent))
import gebco  # noqa: E402
import rsl  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ETOPO = DATA / "etopo" / "etopo2022_mascarene_1min.asc"
R = 6371.0088
EIGHT = np.ones((3, 3), dtype=bool)
LEVELS = {"today": 0.0, "treta_-90m": -90.0, "glacial_-128m": -128.0}
MAHENDRAGIRI = (8.3883, 77.5214)
UJJAIN_LON = 75.7665
MASCARENE_NAMES = {"Mauritius": (-20.20, 57.55), "Reunion": (-21.12, 55.53), "Rodrigues": (-19.70, 63.42),
                   "Saya de Malha Bank": (-10.5, 61.3), "Nazareth Bank": (-14.5, 60.6),
                   "Cargados Carajos (St Brandon)": (-16.5, 59.6)}


def hav(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def load_etopo():
    lines = ETOPO.read_text().splitlines()
    head = {l.split()[0]: float(l.split()[1]) for l in lines[:6]}
    z = np.array([[float(v) for v in l.split()] for l in lines[6:]])
    cell = head["cellsize"]
    lats = head["yllcenter"] + cell * (head["nrows"] - 1 - np.arange(int(head["nrows"])))
    lons = head["xllcenter"] + cell * np.arange(int(head["ncols"]))
    z[z == head["nodata_value"]] = np.nan
    return z, lats, lons, cell


def area_grid(lats, lons, cell):
    return (np.radians(cell) * R) ** 2 * np.cos(np.radians(lats))[:, None] * np.ones((len(lats), len(lons)))


def kumari_kandam():
    g = gebco.load_grid()
    e, la, lo = gebco.window(g, 3.0, 12.5, 74.5, 82.6)
    e = np.nan_to_num(e[::2, ::2], nan=-9999)
    la, lo = la[::2], lo[::2]
    area = area_grid(la, lo, gebco.CELL * 2)
    india = (int(np.argmin(np.abs(la - 9.93))), int(np.argmin(np.abs(lo - 78.12))))
    out = {}
    lat2 = la[:, None] * np.ones_like(lo)[None, :]
    lon2 = np.ones_like(la)[:, None] * lo[None, :]
    for name, level in LEVELS.items():
        labels, _ = ndimage.label(e > level, structure=EIGHT)
        main = labels == labels[india]
        drowned = main & (e <= 0)
        south_of_cape = main & (lon2 < 78.6)
        out[name] = {"sea_level_m": level,
                     "land_now_under_sea_km2": round(float(area[drowned].sum())),
                     "of_which_palk_bay_strait_km2": round(float(area[drowned & (lat2 >= 9.0) & (lon2 >= 78.8) & (lon2 <= 80.4)].sum())),
                     "of_which_south_of_kanyakumari_km2": round(float(area[drowned & (lat2 < 8.1) & (lon2 < 78.6)].sum())),
                     "southernmost_land_below_india_lat": round(float(lat2[south_of_cape].min()), 3)}
    depths = {f"{lat}N 77.5E": gebco.sample(g, lat, 77.5) for lat in (7.0, 6.0, 5.0, 3.0, 0.0)}
    out["ocean_depth_south_of_kanyakumari_m"] = depths
    print("Kumari Kandam:", json.dumps(out, indent=0)[:900])
    return out


def mascarenes():
    z, la, lo, cell = load_etopo()
    area = area_grid(la, lo, cell)
    labels, n = ndimage.label(np.nan_to_num(z, nan=-9999) > -200, structure=EIGHT)
    lat2, lon2 = np.meshgrid(la, lo, indexing="ij")
    rows = []
    for name, (pla, plo) in MASCARENE_NAMES.items():
        r, c = int(np.argmin(np.abs(la - pla))), int(np.argmin(np.abs(lo - plo)))
        k = labels[r, c]
        if k == 0:  # nearest bank cell within 60 km
            d = np.where(labels > 0, hav(pla, plo, lat2, lon2), np.inf)
            if d.min() > 60:
                rows.append({"name": name, "found": False})
                continue
            rr, cc = np.unravel_index(np.argmin(d), d.shape)
            k = labels[rr, cc]
        m = labels == k
        summit = float(np.nanmax(z[m]))
        rec = {"name": name, "centroid": [round(float(lat2[m].mean()), 3), round(float(lon2[m].mean()), 3)],
               "summit_m": summit, "bank_area_above_-200m_km2": round(float(area[m].sum()))}
        for key, level in LEVELS.items():
            rec[f"land_{key}_km2"] = round(float(area[m & (z > level)].sum()), 1)
        dist = float(hav(MAHENDRAGIRI[0], MAHENDRAGIRI[1], lat2[m], lon2[m]).min())
        rec.update({"km_from_mahendragiri": round(dist), "km_per_yojana_if_100": round(dist / 100, 1),
                    "km_from_equator": round(abs(rec["centroid"][0]) * 111.2),
                    "km_from_ujjain_meridian": round(abs(rec["centroid"][1] - UJJAIN_LON) * 111.2 *
                                                    np.cos(np.radians(rec["centroid"][0])))})
        if rec["land_today_km2"] < 0.05 * max(rec["land_glacial_-128m_km2"], 1e-9):
            for lv in np.arange(-128, 1, 1.0):
                if area[m & (z > lv)].sum() < 0.05 * rec["land_glacial_-128m_km2"]:
                    rec["drowned_at_m"] = float(lv)
                    rec["drowned_ka"] = round(rsl.age_when_level_crossed(float(lv))["central_ka"], 1) if lv < -1 else None
                    break
        rows.append(rec)
        print(f"   {name:<30} summit {summit:7.0f} m  today {rec['land_today_km2']:>8} km2  -90m {rec['land_treta_-90m_km2']:>8}  "
              f"-128m {rec['land_glacial_-128m_km2']:>8}  {dist:,.0f} km from Mahendragiri")
    return rows


def mascarene_chagos_sill():
    """Highest sea level at which land would run from the GEBCO subset's west edge (62.8 E) to Chagos."""
    g = gebco.load_grid()
    e, la, lo = gebco.window(g, -22.0, -2.0, 62.77, 73.0)
    e = np.nan_to_num(e[::2, ::2], nan=-9999)
    la, lo = la[::2], lo[::2]
    chagos = (int(np.argmin(np.abs(la - -6.2))), int(np.argmin(np.abs(lo - 71.9))))

    def joined(level):
        labels, _ = ndimage.label(e > level, structure=EIGHT)
        k = labels[chagos]
        return k != 0 and np.any(labels[:, 0] == k)

    lo_lv, hi_lv = -6000.0, 10.0
    if not joined(lo_lv):
        return None
    while hi_lv - lo_lv > 5:
        mid = (lo_lv + hi_lv) / 2
        lo_lv, hi_lv = (mid, hi_lv) if joined(mid) else (lo_lv, mid)
    print(f"   Mascarene side (62.8 E) to Chagos: never shallower than {lo_lv:.0f} m")
    return round(lo_lv)


def lemuria_scale():
    dt = json.loads((DATA / "deep_time.json").read_text())
    ridge = [r for r in dt["cases"]["deepest_glacial"]["landmasses"] if not r["is_india"]]
    g = gebco.load_grid()
    e, la, lo = gebco.window(g, -12.0, 5.0, 64.0, 80.0)
    ocean = e[e < -1000]
    return {"chagos_laccadive_land_at_-128m_km2": sum(r["area_km2"] for r in ridge),
            "chagos_laccadive_landmasses": len(ridge),
            "median_depth_of_open_ocean_12S_5N_64_80E_m": round(float(np.median(ocean))),
            "sri_lanka_area_km2_for_scale": 65610}


def main():
    out = {"kumari_kandam": kumari_kandam()}
    print("Mascarene banks and islands (ETOPO 2022):")
    out["mascarenes"] = mascarenes()
    out["mascarene_to_chagos_sill_m"] = mascarene_chagos_sill()
    out["lemuria"] = lemuria_scale()
    print("Lemuria scale:", out["lemuria"])
    (DATA / "lemuria_mauritius.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
