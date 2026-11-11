"""Scan the Chagos-Laccadive ridge for islands that existed in the Treta epoch (~869 ka) and are gone now.

1. Plate positions of every key point at 869 ka (India plate, NNR-MORVEL56), and the size of the
   India-Capricorn diffuse-boundary motion that affects Chagos.
2. India's southern coast at the Treta and glacial sea levels, and the sea gap from it to each ridge landmass.
3. Ridge crest profile from Lakshadweep to Chagos (shallowest depth per latitude band).
4. Bank inventory around Chagos and the equatorial Maldives: area emergent today, at the Treta sea level
   (-90 m), at the deepest glacial level (-128 m) and with ridge subsidence (-149 m); when each drowned.
5. Seamounts whose summits never reached the surface in the last 1 Myr.
6. Closed depressions (crater-like basins) found by priority-flood depression filling.
"""
import heapq
import json
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).parent))
import gebco  # noqa: E402
import rsl  # noqa: E402
import tectonics  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"
R = 6371.0088
EIGHT = np.ones((3, 3), dtype=bool)
YEARS = 869_052 + 76
LEVELS = {"today": 0.0, "treta_-90m": -90.0, "glacial_-128m": -128.0, "glacial+subsidence_-149m": -149.0}
NAMED = {  # well-charted features only; anything else is reported by its coordinates
    "Great Chagos Bank": (-6.20, 71.90), "Peros Banhos": (-5.29, 71.85), "Salomon Islands": (-5.33, 72.25),
    "Diego Garcia": (-7.32, 72.42), "Egmont Islands": (-6.67, 71.36), "Speakers Bank": (-4.88, 72.33),
    "Blenheim Reef": (-5.20, 72.47), "Pitt Bank": (-7.05, 71.33), "Huvadhu atoll": (0.52, 73.28),
    "Fuvahmulah": (-0.30, 73.43), "Addu atoll": (-0.63, 73.16), "Laamu / Thaa atolls": (2.0, 73.4)}
# Real present-day land (Wikipedia: Great Chagos Bank, Pitt Bank, Speakers Bank, Chagos Archipelago). GEBCO's 15"
# cells show 'land' up to ~200 m on these reefs (Pitt Bank has none), so GEBCO heights > ATOLL_CAP_M are artefacts.
KNOWN_LAND_KM2 = {"Great Chagos Bank": 5.6, "Pitt Bank": 0.0, "Speakers Bank": 0.001, "Diego Garcia": 32.5}
ATOLL_CAP_M = 3.0
POINTS = {"Mahendragiri": (8.3883, 77.5214), "Kanyakumari": (8.0780, 77.5505), "Ujjain": (23.1713, 75.7665),
          "Huvadhu atoll": (0.519, 73.283), "Addu atoll": (-0.636, 73.161), "Diego Garcia": (-7.32, 72.42),
          "Great Chagos Bank": (-6.20, 71.90), "Sri Lanka (centre)": (7.8731, 80.7718)}


def hav(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def window(south, north, west, east, step):
    e, la, lo = gebco.window(gebco.load_grid(), south, north, west, east)
    return np.nan_to_num(e[::step, ::step], nan=-9999.0), la[::step], lo[::step]


def cell_area(lats, step, shape):
    return ((np.radians(gebco.CELL * step) * R) ** 2 * np.cos(np.radians(lats)))[:, None] * np.ones(shape)


def plate_positions():
    rows, then = [], {}
    for name, (la, lo) in POINTS.items():
        t = tectonics.position_at(la, lo, YEARS)
        then[name] = t
        shift = hav(la, lo, *t)
        rows.append({"name": name, "today": [la, lo], "at_869ka": [round(t[0], 4), round(t[1], 4)],
                     "shift_km": round(float(shift), 1)})
    pairs = []
    for a, b in (("Mahendragiri", "Huvadhu atoll"), ("Mahendragiri", "Addu atoll"), ("Kanyakumari", "Diego Garcia"),
                 ("Mahendragiri", "Sri Lanka (centre)")):
        d0 = hav(*POINTS[a], *POINTS[b])
        d1 = hav(*then[a], *then[b])
        pairs.append({"pair": f"{a} - {b}", "km_today": round(float(d0), 1), "km_at_869ka": round(float(d1), 1)})
    # India-Capricorn rotation (DeMets, Gordon & Royer 2005): pole near 4 S, 75 E, ~0.28 deg/Myr
    ang = np.radians(0.28 * YEARS / 1e6)
    cap = float(ang * hav(-4.0, 75.0, *POINTS["Diego Garcia"]))
    return {"points": rows, "distances": pairs, "india_capricorn_shift_at_chagos_km": round(cap, 1)}


def southern_coast():
    e, la, lo = window(-9.0, 15.0, 66.0, 82.5, 2)
    india = (int(np.argmin(np.abs(la - 9.93))), int(np.argmin(np.abs(lo - 78.12))))
    out = {}
    dy = np.radians(gebco.CELL * 2) * R
    for name, level in LEVELS.items():
        labels, _ = ndimage.label(e > level, structure=EIGHT)
        mask = labels == labels[india]
        rows = np.where(mask.any(axis=1))[0]
        south_row = rows.max()
        south_col = int(np.mean(np.where(mask[south_row])[0]))
        tip = (float(la[south_row]), float(lo[south_col]))
        west = mask & (lo[None, :] < 78.6)
        wrows = np.where(west.any(axis=1))[0]
        cape = (float(la[wrows.max()]), float(lo[int(np.mean(np.where(west[wrows.max()])[0]))]))
        dist = ndimage.distance_transform_edt(~mask, sampling=(dy, dy * np.cos(np.radians(5.0))))
        gaps = {}
        for target, (tla, tlo) in (("Lakshadweep (Kavaratti)", (10.565, 72.642)), ("Male", (4.175, 73.509)),
                                   ("Huvadhu atoll", (0.519, 73.283)), ("Great Chagos Bank", (-6.20, 71.90))):
            r, c = int(np.argmin(np.abs(la - tla))), int(np.argmin(np.abs(lo - tlo)))
            lab = labels[r, c]
            if lab == 0:
                gaps[target] = None
                continue
            gaps[target] = round(float(dist[labels == lab].min()))
        out[name] = {"sea_level_m": level, "southern_tip": [round(tip[0], 3), round(tip[1], 3)],
                     "tip_km_south_of_kanyakumari": round(float(hav(8.078, 77.5505, *tip))),
                     "cape_south_of_kanyakumari": [round(cape[0], 3), round(cape[1], 3)],
                     "cape_shift_km": round(float(hav(8.078, 77.5505, *cape))),
                     "sea_gap_km_from_indian_coast": gaps}
    return out


def ridge_profile():
    # 71.0-74.0 E keeps the Indian continental shelf out; north of 12.6 N the ridge merges with it
    e, la, lo = window(-12.0, 12.6, 71.0, 74.0, 2)
    band = 0.05
    rows = []
    for top in np.arange(12.6, -12.0, -band):
        sel = (la <= top) & (la > top - band)
        if not sel.any():
            continue
        crest = float(e[sel].max())
        c = np.unravel_index(np.argmax(e[sel]), e[sel].shape)[1]
        rows.append({"lat": round(float(top - band / 2), 3), "crest_m": crest, "lon": round(float(lo[c]), 3)})
    return rows


def bank_inventory():
    e, la, lo = window(-10.0, 3.0, 69.0, 75.5, 1)
    area = cell_area(la, 1, e.shape)
    labels, n = ndimage.label(e > -200.0, structure=EIGHT)
    sizes = ndimage.sum(area, labels, index=np.arange(1, n + 1))
    lat2, lon2 = np.meshgrid(la, lo, indexing="ij")
    rows = []
    for k in range(1, n + 1):
        if sizes[k - 1] < 5:
            continue
        m = labels == k
        clat, clon = float(lat2[m].mean()), float(lon2[m].mean())
        if clat > 2.6:
            continue
        summit = min(float(e[m].max()), ATOLL_CAP_M)
        name = None
        for nm, (pla, plo) in NAMED.items():
            if float(hav(pla, plo, lat2[m], lon2[m]).min()) < 15:
                name = nm if name is None else f"{name} / {nm}"
        areas = {k2: round(float(area[m & (e > lv)].sum()), 1) for k2, lv in LEVELS.items()}
        for lv in (-40.0, -20.0, -10.0):
            areas[f"at_{int(lv)}m"] = round(float(area[m & (e > lv)].sum()), 1)
        # sea level at which the emergent area falls below 5 % of its glacial size -> drowning age (Holocene curve)
        drown_level = None
        if areas["glacial_-128m"] > 0:
            for lv in np.arange(-128, 1, 1.0):
                if area[m & (e > lv)].sum() < 0.05 * areas["glacial_-128m"]:
                    drown_level = float(lv)
                    break
        drown_age = None
        if drown_level is not None and drown_level < -1:
            drown_age = rsl.age_when_level_crossed(drown_level)["central_ka"]
        known = next((v for nm, v in KNOWN_LAND_KM2.items() if name and nm in name), None)
        today = known if known is not None else areas["today"]
        areas["today_real_or_gebco"] = today
        lost = areas["treta_-90m"] - today
        areas["lost_since_treta"] = round(max(lost, 0.0), 1)
        if areas["glacial_-128m"] > 0 and today < 0.05 * areas["glacial_-128m"]:
            status = "drowned: 95% or more of its glacial-era land is now under water"
        elif today > 0:
            status = "partly drowned: reef islets remain on a once larger plateau"
        elif areas["glacial_-128m"] > 0:
            status = "DROWNED: an island in glacial times, under water today"
        elif areas["glacial+subsidence_-149m"] > 0:
            status = "drowned only if the ridge subsided >21 m (marginal)"
        else:
            status = "never an island in the last 1 Myr"
        rows.append({"name": name or f"unnamed bank {clat:.2f}, {clon:.2f}", "centroid": [round(clat, 3), round(clon, 3)],
                     "bank_area_above_-200m_km2": round(float(sizes[k - 1])), "summit_m": summit,
                     "emergent_area_km2": areas, "drowned_at_sea_level_m": drown_level,
                     "drowning_age_ka_holocene": None if drown_age is None else round(drown_age, 1),
                     "today_source": "published" if known is not None else "GEBCO (overstates atoll land)", "status": status})
    rows.sort(key=lambda r: -r["emergent_area_km2"]["treta_-90m"])
    return rows


def seamounts():
    e, la, lo = window(-12.0, 3.0, 66.0, 77.0, 2)
    peaks = (e == ndimage.maximum_filter(e, size=21)) & (e < -150) & (e > -3000)
    relief = e - ndimage.minimum_filter(e, size=51)
    rows = []
    for r, c in np.argwhere(peaks & (relief >= 500)):
        need = (-float(e[r, c]) - 128.0) / (YEARS / 1e6)  # m/Myr of subsidence needed to have been an island
        rows.append({"lat": round(float(la[r]), 3), "lon": round(float(lo[c]), 3), "summit_m": float(e[r, c]),
                     "relief_m": round(float(relief[r, c])), "subsidence_needed_m_per_myr": round(need)})
    rows.sort(key=lambda r: -r["summit_m"])
    return rows


def closed_depressions():
    """Priority-flood fill from the window edge; filled - original = depth of closed basins."""
    e, la, lo = window(-10.0, 3.0, 69.0, 75.5, 4)
    rows_n, cols_n = e.shape
    filled = np.full(e.shape, np.inf)
    seen = np.zeros(e.shape, dtype=bool)
    heap = []
    for r in range(rows_n):
        for c in (0, cols_n - 1):
            heapq.heappush(heap, (e[r, c], r, c)); seen[r, c] = True
    for c in range(cols_n):
        for r in (0, rows_n - 1):
            if not seen[r, c]:
                heapq.heappush(heap, (e[r, c], r, c)); seen[r, c] = True
    while heap:
        z, r, c = heapq.heappop(heap)
        filled[r, c] = z
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows_n and 0 <= nc < cols_n and not seen[nr, nc]:
                    seen[nr, nc] = True
                    heapq.heappush(heap, (max(z, e[nr, nc]), nr, nc))
    depth = filled - e
    area = cell_area(la, 4, e.shape)
    labels, n = ndimage.label(depth > 20.0, structure=EIGHT)
    lat2, lon2 = np.meshgrid(la, lo, indexing="ij")
    rows = []
    for k in range(1, n + 1):
        m = labels == k
        a = float(area[m].sum())
        if a < 20:
            continue
        rim = float(filled[m].max())
        yy = (lat2[m] - lat2[m].mean()) * 111.2
        xx = (lon2[m] - lon2[m].mean()) * 111.2 * np.cos(np.radians(lat2[m].mean()))
        if m.sum() >= 3:
            w, v = np.linalg.eigh(np.cov(np.vstack([xx, yy])))
            elong = float(np.sqrt(max(w[1], 1e-9) / max(w[0], 1e-9)))
            strike = float(np.degrees(np.arctan2(v[0, 1], v[1, 1])) % 180)
        else:
            elong, strike = 1.0, 0.0
        kind = "atoll lagoon (reef-rimmed basin on a bank top)" if rim > -200 else "deep-sea basin between ridges / fracture-zone trough"
        rows.append({"centroid": [round(float(lat2[m].mean()), 3), round(float(lon2[m].mean()), 3)], "area_km2": round(a),
                     "max_depth_below_rim_m": round(float(depth[m].max())), "rim_m": round(rim), "kind": kind,
                     "elongation": round(elong, 1), "strike_deg": round(strike)})
    rows.sort(key=lambda r: -r["area_km2"])
    return rows


def main():
    out = {"plate": plate_positions()}
    for p in out["plate"]["points"]:
        print(f"{p['name']:<20} today {p['today']} -> 869 ka {p['at_869ka']} (moved {p['shift_km']} km)")
    for d in out["plate"]["distances"]:
        print(f"   {d['pair']:<36} {d['km_today']} km today, {d['km_at_869ka']} km at 869 ka")
    print(f"   India-Capricorn boundary motion at Chagos over 869 kyr: <= {out['plate']['india_capricorn_shift_at_chagos_km']} km")
    out["southern_coast"] = southern_coast()
    for k, v in out["southern_coast"].items():
        print(f"[{k}] India's southern tip {v['southern_tip']} ({v['tip_km_south_of_kanyakumari']} km from Kanyakumari); "
              f"sea gaps: {v['sea_gap_km_from_indian_coast']}")
    out["ridge_profile"] = ridge_profile()
    out["banks"] = bank_inventory()
    print("Banks (sorted by area emergent at -90 m):")
    for b in out["banks"][:14]:
        print(f"   {b['name']:<45} summit {b['summit_m']:>6.0f} m  today {b['emergent_area_km2']['today']:>7} km2  "
              f"-90m {b['emergent_area_km2']['treta_-90m']:>8} km2  lost {b['emergent_area_km2']['lost_since_treta']:>8}  -128m {b['emergent_area_km2']['glacial_-128m']:>8} km2  "
              f"drowned ~{b['drowning_age_ka_holocene']} ka  [{b['status']}]")
    out["seamounts"] = seamounts()
    print(f"Seamounts (relief >= 500 m, summit -150..-3000 m): {len(out['seamounts'])}; shallowest:")
    for s in out["seamounts"][:6]:
        print(f"   {s}")
    out["closed_depressions"] = closed_depressions()
    kinds = {}
    for d in out["closed_depressions"]:
        kinds[d["kind"]] = kinds.get(d["kind"], 0) + 1
    print(f"Closed depressions > 20 km2 and > 20 m deep: {len(out['closed_depressions'])} {kinds}")
    deep = [d for d in out["closed_depressions"] if d["kind"].startswith("deep") and d["area_km2"] >= 200]
    ns = [d for d in deep if d["elongation"] >= 2 and (d["strike_deg"] <= 30 or d["strike_deg"] >= 150)]
    circ = [d for d in out["closed_depressions"] if d["elongation"] < 1.3 and d["area_km2"] >= 200 and d["kind"].startswith("deep")]
    e4, la4, lo4 = window(-10.0, 3.0, 69.0, 75.5, 4)
    for d in circ:
        r0 = np.sqrt(d["area_km2"] / np.pi)
        lat2, lon2 = np.meshgrid(la4, lo4, indexing="ij")
        dist = hav(d["centroid"][0], d["centroid"][1], lat2, lon2)
        inner = e4[(dist >= r0) & (dist < 1.5 * r0)].mean()
        outer = e4[(dist >= 2.0 * r0) & (dist < 3.0 * r0)].mean()
        d["radius_km"] = round(float(r0), 1)
        d["rim_minus_surroundings_m"] = round(float(inner - outer))
    out["depression_shape_summary"] = {"deep_basins_ge_200km2": len(deep), "elongated_north_south": len(ns),
                                       "near_circular_deep_basins": circ}
    print(f"   deep basins >= 200 km2: {len(deep)}; elongated N-S (aspect >= 2, strike within 30 deg of N): {len(ns)}; "
          f"near-circular: {len(circ)}")
    for d in out["closed_depressions"][:8]:
        print(f"   {d}")
    (DATA / "chagos_scan.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
