"""Deep-time test: an equatorial Lanka on the Chagos-Laccadive ridge in the Treta Yuga.

Chronologies (end of Treta, where tradition places Rama):
  * Puranic / Surya Siddhanta yuga lengths (Krita 1,728,000; Treta 1,296,000; Dvapara 864,000;
    Kali 432,000 yr) with Kali beginning 3102 BCE  ->  Treta ended 867,102 BCE (~869 ka BP).
  * The tradition that Rama lived in the Treta of the 24th maha-yuga (current = 28th) -> ~18.1 Ma.
  * Manusmriti 1.69-71 / Mahabharata 3.186 literal 12,000-year cycle (Treta 3,600 yr)
    -> Treta 9102-5502 BCE (already covered by the Holocene analysis in report sections 3-4).

For the ~869 ka case this script uses:
  * global sea level from Bintanja & van de Wal (2008);
  * thermal subsidence of the ~55 Myr-old ridge (depth ~ 365 sqrt(t) m, Parsons-Sclater/Stein-Stein form):
    ~21 m in 869 kyr, so the ridge stood ~21 m higher than today relative to the seabed;
  * India-plate rotation (NNR-MORVEL56) to place the equator and Ujjain's meridian as they were then.
Then GEBCO 2026 decides which landmasses existed, how deep the gaps were, and where '100 yojanas' falls.
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).parent))
import deep_sealevel  # noqa: E402
import gebco  # noqa: E402
import tectonics  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"
R = 6371.0088
EIGHT = np.ones((3, 3), dtype=bool)
BOX = (-9.0, 15.0, 66.0, 82.5)          # south, north, west, east
STEP = 2                                 # 30 arc-seconds is ample for km-scale gaps
UJJAIN = (23.1713, 75.7665)              # Jantar Mantar (Vedh Shala), Ujjain
MAHENDRAGIRI = (8.3883, 77.5214)
KANYAKUMARI = (8.0780, 77.5505)
KALI_START_BCE = 3102
TRETA_END_BCE = KALI_START_BCE + 864_000                        # Puranic
# back from 3102 BCE: 28th maha-yuga's Dvapara+Treta+Krita, three whole maha-yugas (27th-25th),
# then the 24th's Kali and Dvapara, reaching the end of its Treta
TRETA_END_24TH_BCE = KALI_START_BCE + (864_000 + 1_296_000 + 1_728_000) + 3 * 4_320_000 + (432_000 + 864_000)
RIDGE_AGE_MYR = 55.0


def hav(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def subsidence_m(years, age_myr=RIDGE_AGE_MYR):
    t1, t0 = age_myr, age_myr - years / 1e6
    return 365.0 * (np.sqrt(t1) - np.sqrt(t0))


def load():
    elev, lats, lons = gebco.window(gebco.load_grid(), *BOX)
    return elev[::STEP, ::STEP], lats[::STEP], lons[::STEP]


def components(elev, level, min_cells=4):
    labels, n = ndimage.label(np.nan_to_num(elev, nan=-9999) > level, structure=EIGHT)
    sizes = ndimage.sum(np.ones_like(elev), labels, index=np.arange(1, n + 1))
    return labels, [k + 1 for k in range(n) if sizes[k] >= min_cells]


def sill_between(elev, a, b, lo=-4500.0, hi=50.0, tol=2.0):
    def joined(level):
        labels, _ = ndimage.label(np.nan_to_num(elev, nan=-9999) > level, structure=EIGHT)
        return labels[a] != 0 and labels[a] == labels[b]
    if not joined(lo):
        return None
    while hi - lo > tol:
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if joined(mid) else (lo, mid)
    return lo


def main():
    age, sl = deep_sealevel.bintanja()
    t_ka = (TRETA_END_BCE + 1950) / 1000.0
    sl_treta = float(np.interp(t_ka, age, sl))
    win = (age >= t_ka - 10) & (age <= t_ka + 10)
    sub = float(subsidence_m(t_ka * 1000))
    last_myr = age <= 1000
    out = {"chronology": {
        "puranic_treta_end_bce": TRETA_END_BCE, "puranic_treta_end_ka_bp": round(t_ka, 2),
        "puranic_treta_start_bce": TRETA_END_BCE + 1_296_000,
        "rama_24th_mahayuga_treta_end_bce": TRETA_END_24TH_BCE,
        "manusmriti_literal_treta_bce": [9102, 5502]},
        "sea_level": {"at_treta_end_m": round(sl_treta, 1),
                      "within_10kyr_m": [round(float(sl[win].min()), 1), round(float(sl[win].max()), 1)],
                      "last_1myr_min_m": round(float(sl[last_myr].min()), 1),
                      "fraction_last_1myr_below_minus10m": round(float(np.mean(sl[last_myr] < -10)), 3),
                      "source": "Bintanja & van de Wal 2008 (Nature 454:869), NOAA WDC Paleo #2011-119"},
        "ridge_subsidence_since_m": round(sub, 1)}
    print(f"Puranic end of Treta: {TRETA_END_BCE:,} BCE = {t_ka:.1f} ka; sea level {sl_treta:.0f} m "
          f"(±10 kyr: {sl[win].min():.0f} to {sl[win].max():.0f} m); ridge subsidence since then ~{sub:.0f} m")

    elev, lats, lons = load()
    lat2, lon2 = np.meshgrid(lats, lons, indexing="ij")
    idx = lambda la, lo: (int(np.argmin(np.abs(lats - la))), int(np.argmin(np.abs(lons - lo))))  # noqa: E731
    india = idx(9.93, 78.12)

    # --- plate motion: where were the equator and Ujjain's meridian 869 kyr ago? -----------------
    years = t_ka * 1000 + 76
    uj_then = tectonics.position_at(*UJJAIN, years)
    # point on the equator at Ujjain's then-longitude, carried forward to today's plate coordinates
    eq_then_lat, eq_then_lon = 0.0, uj_then[1]
    p_now = tectonics.position_at(eq_then_lat, eq_then_lon, -years)
    # the then-equator traced in present-day coordinates (for the map)
    eq_line = [tectonics.position_at(0.0, lo, -years) for lo in np.arange(66, 83, 0.5)]
    out["plate"] = {"ujjain_then": [round(uj_then[0], 4), round(uj_then[1], 4)],
                    "equator_x_ujjain_meridian_then_in_present_coords": [round(p_now[0], 4), round(p_now[1], 4)],
                    "depth_there_m": gebco.sample(gebco.load_grid(), *p_now),
                    "equator_then_in_present_coords": [[round(a, 4), round(b, 4)] for a, b in eq_line]}
    print(f"Ujjain then {uj_then[0]:.4f}N {uj_then[1]:.4f}E; equator x Ujjain meridian then = today's "
          f"{p_now[0]:.4f}N {p_now[1]:.4f}E, depth {out['plate']['depth_there_m']:.0f} m")

    # --- landmasses at the Treta sea level (with and without the subsidence correction) ------------
    cases = {"treta_sea_level": sl_treta, "treta_plus_subsidence": sl_treta - sub,
             "deepest_glacial": float(sl[last_myr].min()), "deepest_plus_subsidence": float(sl[last_myr].min()) - sub}
    out["cases"] = {}
    cell_km2 = (np.radians(gebco.CELL * STEP) * R) ** 2 * np.cos(np.radians(lat2))
    for name, level in cases.items():
        labels, comps = components(elev, level)
        india_label = labels[india]
        rows = []
        for k in comps:
            mask = labels == k
            area = float(cell_km2[mask].sum())
            r, c = np.unravel_index(np.argmax(np.where(mask, elev, -1e9)), elev.shape)
            clat, clon = float(lat2[mask].mean()), float(lon2[mask].mean())
            if k != india_label and not (70.0 <= clon <= 75.8 and -8.5 <= clat <= 14.5):
                continue  # keep the ridge (Lakshadweep-Maldives-Chagos) and the Indian mainland
            dist_m = float(hav(MAHENDRAGIRI[0], MAHENDRAGIRI[1], lat2[mask], lon2[mask]).min())
            rows.append({"label": int(k), "is_india": bool(k == india_label),
                         "centroid": [round(clat, 3), round(clon, 3)], "area_km2": round(area),
                         "summit": [round(float(lats[r]), 3), round(float(lons[c]), 3)],
                         # GEBCO 'land' heights on atolls are artefacts (Pitt Bank shows 156 m; it has no land):
                         # cap ridge tops at +3 m, the height of real reef islets
                         "relief_above_sea_m": round((float(elev[r, c]) if k == india_label else min(float(elev[r, c]), 3.0)) - level),
                         "km_from_mahendragiri": round(dist_m), "km_per_yojana_if_100": round(dist_m / 100, 2),
                         "km_from_equator": round(abs(clat) * 111.2),
                         "km_from_ujjain_meridian_then": round(abs(clon - uj_then[1]) * 111.2 * np.cos(np.radians(clat)))})
        sri_lanka_joined = bool(labels[idx(7.5, 80.7)] == india_label)
        rows.sort(key=lambda r: -r["area_km2"])
        out["cases"][name] = {"sea_level_m": round(level, 1), "sri_lanka_joined_to_india": sri_lanka_joined,
                              "landmasses": rows}
        ridge = [r for r in rows if not r["is_india"]]
        eq = [r for r in ridge if r["km_from_equator"] <= 300]
        print(f"[{name}] level {level:.0f} m: Sri Lanka joined to India: {sri_lanka_joined}; ridge landmasses "
              f"{len(ridge)} ({sum(r['area_km2'] for r in ridge):,} km2); within 300 km of the equator: {len(eq)}")
        for r in eq:
            print(f"     {r['centroid']}  {r['area_km2']:>6,} km2  relief {r['relief_above_sea_m']:>4} m  "
                  f"{r['km_from_mahendragiri']:>5} km from Mahendragiri -> {r['km_per_yojana_if_100']} km/yojana")

    # --- sills (deepest point a causeway or walk would have to cross) -------------------------------
    targets = {"Lakshadweep (Kavaratti)": (10.565, 72.642), "Maldives north (Ihavandhippolhu)": (6.95, 72.93),
               "Male": (4.175, 73.509), "Huvadhu atoll (equator, N)": (0.50, 73.25),
               "Fuvahmulah (equator)": (-0.298, 73.424), "Addu atoll (equator, S)": (-0.63, 73.16),
               "Great Chagos Bank": (-6.30, 71.80), "Sri Lanka": (7.5, 80.7)}
    out["sills_to_india_m"] = {}
    for name, (la, lo) in targets.items():
        s = sill_between(elev, india, idx(la, lo))
        out["sills_to_india_m"][name] = None if s is None else round(s)
        print(f"   sill India -> {name:<34} {s:8.0f} m")
    # equatorial Maldives internal channels (are the three atolls one 'Trikuta'?)
    out["sills_between_equatorial_atolls_m"] = {
        "Huvadhu-Fuvahmulah": round(sill_between(elev, idx(0.50, 73.25), idx(-0.298, 73.424))),
        "Fuvahmulah-Addu": round(sill_between(elev, idx(-0.298, 73.424), idx(-0.63, 73.16))),
        "Male-Huvadhu": round(sill_between(elev, idx(4.175, 73.509), idx(0.50, 73.25)))}
    print("   equatorial atoll channels:", out["sills_between_equatorial_atolls_m"])

    # --- the Miocene (24th maha-yuga) reading: where was Sri Lanka relative to the equator? ---------
    yrs24 = TRETA_END_24TH_BCE + 2026
    sl_then = tectonics.position_at(7.87, 80.77, yrs24)
    out["miocene_24th_mahayuga"] = {"years_ago": yrs24, "sri_lanka_centre_then_nnr_extrapolated": [round(v, 2) for v in sl_then],
                                    "caveat": "NNR-MORVEL56 is a present-day model; over 18 Myr use a paleomagnetic frame (error several degrees)"}
    print(f"24th maha-yuga Treta end ~{yrs24 / 1e6:.1f} Ma: Sri Lanka centre then ~{sl_then[0]:.1f}N {sl_then[1]:.1f}E (rough)")
    (DATA / "deep_time.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
