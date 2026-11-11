"""The sky of the Treta Yuga (Puranic end of Treta = 867,102 BCE) for Rama's birth and the war.

1. REBOUND N-body (nbody.py) from J2000 back to 881,000 BCE, recording the ecliptic pole (Earth-Moon
   barycentre orbit normal) and Earth's eccentricity every 50 years.
2. Earth's spin axis precessed around that moving ecliptic pole (luni-solar torque; precession constant
   scaled for orbital eccentricity and for the faster spin and closer Moon of the past). Gives obliquity
   (checked against Berger & Loutre 1991) and the equinox, i.e. the seasons.
3. Forward through the window 881,000-867,000 BCE every 2 days: planets corrected for the N-body drift
   calibrated against DE441 (nbody_calib.py), stars moved by their 3-D space motion (Hipparcos), sidereal
   longitudes measured from Spica (Lahiri), zeta Piscium (Revati) or delta Cancri (Pushya).
4. Tests: the Bala Kanda 1.18 birth configuration (strict and 'Sun in Aries' readings), the month-season
   pairings of the Critical Edition, and the Yuddha 6.90 battle sky.
The Moon's position and the calendar day cannot be computed this far back (tidal acceleration and
Earth-rotation uncertainty amount to thousands of degrees), so candidate *seasons and years* are reported,
not dates; the navami / Punarvasu / lagna conditions are possible in roughly every other qualifying year.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import deep_sealevel  # noqa: E402
import nbody  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"
WIN_START_BCE, WIN_END_BCE = 881_000, 867_000           # birth window + room for the war (age <= 45)
TRETA_END_BCE = 867_102
SAMPLE_DAYS = 2.0          # integration step
RECORD_EVERY = 2           # keep every 2nd step -> one sample per 4 days
NB = 7                     # bodies kept: Sun, Mercury, Venus, EMB, Mars, Jupiter, Saturn
POLE_STEP_YR = 50.0
NAK = 360.0 / 27.0
EXALT = {"sun": 0, "venus": 11, "mars": 9, "jupiter": 3, "saturn": 6}
BODY_IDX = {"sun": 3, "mercury": 1, "venus": 2, "mars": 4, "jupiter": 5, "saturn": 6}   # sun handled via EMB
DRIFT_KEYS = {3: "emb", 2: "venus", 4: "mars", 5: "jupiter", 6: "saturn"}
# radial velocities not in the retrieved catalogues: literature values (sensitivity tested below)
RV_FALLBACK = {"Spica (Chitra, alf Vir)": 1.0, "Pushya (del Cnc)": 17.1, "Aldebaran (Rohini, alf Tau)": 54.3}
ANCHORS = {"Spica = 180° (Lahiri / Chitra-paksha)": ("Spica (Chitra, alf Vir)", 180.0),
           "zeta Psc = 359°50' (Revati-paksha)": ("Revati (zet Psc)", 359.0 + 50 / 60),
           "delta Cnc = 106° (Pushya-paksha)": ("Pushya (del Cnc)", 106.0)}
RITU = [("Shishira", 270), ("Vasanta", 330), ("Grishma", 30), ("Varsha", 90), ("Sharad", 150), ("Hemanta", 210)]


def bce_to_days(year_bce):
    return (-(year_bce - 1) - 2000.0) * 365.25


def days_to_bce(days):
    return int(round(1 - (2000.0 + days / 365.25)))


def load_stars():
    hip = {  # Hipparcos new reduction (van Leeuwen 2007, VizieR I/311), epoch J1991.25; RV from Pulkovo (III/252)
        "Spica (Chitra, alf Vir)": (201.29835228, -11.16124494, -42.35, -30.67, 13.06, None),
        "Revati (zet Psc)": (18.43250842, 7.57548938, 145.00, -55.69, 18.76, 15.0),
        "Pushya (del Cnc)": (131.17129191, 18.15486373, -17.67, -229.26, 24.98, None),
        "Pollux (Punarvasu, bet Gem)": (116.33068294, 28.02631022, -626.55, -45.80, 96.54, 3.2),
        "Castor (Punarvasu, alf Gem)": (113.65001968, 31.88863511, -191.45, -145.19, 64.12, 5.4),
        "Aldebaran (Rohini, alf Tau)": (68.98000194, 16.50976158, 63.45, -188.94, 48.94, None),
        "Regulus (Magha, alf Leo)": (152.09358042, 11.96719519, -248.73, 5.59, 41.13, 5.9)}
    return {k: (ra, de, pa, pd, plx, rv if rv is not None else RV_FALLBACK[k]) for k, (ra, de, pa, pd, plx, rv) in hip.items()}


def star_unit(star, days_from_j2000):
    ra, de, pa, pd, plx, rv = star
    return nbody.star_vector(ra, de, pa, pd, plx, rv, days_from_j2000 / 365.25 + 8.75)


def drift_rotate(xyz, vxyz, years, drift):
    """Remove the calibrated mean-longitude drift: rotate each heliocentric position about its orbit pole."""
    out = xyz.copy()
    for i, key in DRIFT_KEYS.items():
        r = xyz[:, i] - xyz[:, 0]
        h = np.cross(r, vxyz[:, i] - vxyz[:, 0])
        hn = h / np.linalg.norm(h, axis=1)[:, None]
        ang = -np.radians(drift[key]["deg_per_kyr"] * years / 1000.0)
        c, s = np.cos(ang)[:, None], np.sin(ang)[:, None]
        rot = r * c + np.cross(hn, r) * s + hn * np.sum(hn * r, axis=1)[:, None] * (1 - c)
        out[:, i] = xyz[:, 0] + rot
    return out


def phase_a(sim, t_stop_days):
    """Backward pass recording the ecliptic pole and eccentricity every POLE_STEP_YR."""
    ts, poles, eccs = [], [], []
    t = 0.0
    sim.dt = -SAMPLE_DAYS
    while t > t_stop_days - POLE_STEP_YR * 365.25:
        sim.integrate(t, exact_finish_time=0)
        xyz, vxyz = nbody.state(sim)
        r, v = xyz[3] - xyz[0], vxyz[3] - vxyz[0]
        h = np.cross(r, v)
        mu = nbody.GAUSS_K ** 2 * (1 + nbody.GM["emb"] / nbody.GM["sun"])
        e = np.linalg.norm(np.cross(v, h) / mu - r / np.linalg.norm(r))
        ts.append(sim.t)
        poles.append(h / np.linalg.norm(h))
        eccs.append(e)
        t -= POLE_STEP_YR * 365.25
    return np.array(ts), np.array(poles), np.array(eccs)


def precess_spin(ts, poles, eccs):
    """Spin axis s: ds/dt = alpha (s.k)(s x k), RK4 backward from the ICRF pole at J2000."""
    eps0 = np.radians(84381.406 / 3600.0)
    psi_dot = np.radians(5038.481507 / 3600.0 / 100.0)    # luni-solar precession, rad/yr (IAU 2006)
    alpha0 = psi_dot / np.cos(eps0)
    solar = 0.315                                           # solar share of the luni-solar torque
    g0 = solar * (1 - eccs[0] ** 2) ** -1.5 + (1 - solar)
    tidal_per_yr = 4.1e-4 / 869_000.0                       # faster spin (+2.3e-4) and closer Moon (+1.8e-4) at 869 ka

    def alpha(i_float):
        i0 = int(np.clip(np.floor(i_float), 0, len(ts) - 2))
        f = i_float - i0
        e = eccs[i0] * (1 - f) + eccs[i0 + 1] * f
        k = poles[i0] * (1 - f) + poles[i0 + 1] * f
        yrs = -(ts[i0] * (1 - f) + ts[i0 + 1] * f) / 365.25
        g = (solar * (1 - e ** 2) ** -1.5 + (1 - solar)) / g0
        return alpha0 * g * (1 + tidal_per_yr * yrs), k / np.linalg.norm(k)

    def deriv(s, i_float):
        a, k = alpha(i_float)
        return a * np.dot(s, k) * np.cross(s, k)

    spins = np.zeros_like(poles)
    s = np.array([0.0, 0.0, 1.0])
    spins[0] = s
    for i in range(len(ts) - 1):
        h = (ts[i + 1] - ts[i]) / 365.25                    # years (negative)
        k1 = deriv(s, i)
        k2 = deriv(s + 0.5 * h * k1, i + 0.5)
        k3 = deriv(s + 0.5 * h * k2, i + 0.5)
        k4 = deriv(s + h * k3, i + 1)
        s = s + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        s /= np.linalg.norm(s)
        spins[i + 1] = s
    return spins


def interp_vec(ts, vecs, t):
    out = np.stack([np.interp(t, ts[::-1], vecs[::-1, j]) for j in range(3)], axis=-1)
    return out / np.linalg.norm(out, axis=-1, keepdims=True)


def lon_from(vecs, pole, ref):
    """Longitude of each row of vecs in the plane with (per-row) normal `pole`, from direction `ref` (per row)."""
    ref = ref - np.sum(ref * pole, axis=1)[:, None] * pole
    ref /= np.linalg.norm(ref, axis=1)[:, None]
    y = np.cross(pole, ref)
    v = vecs - np.sum(vecs * pole, axis=1)[:, None] * pole
    return np.degrees(np.arctan2(np.sum(v * y, axis=1), np.sum(v * ref, axis=1))) % 360


def ritu(trop):
    for k, (name, start) in enumerate(RITU):
        end = RITU[(k + 1) % 6][1]
        if (trop - start) % 360 < (end - start) % 360:
            return name
    return "?"


def windows(mask, days):
    """Contiguous runs of True -> list of (start_day, end_day)."""
    if not mask.any():
        return []
    idx = np.where(mask)[0]
    breaks = np.where(np.diff(idx) > 1)[0]
    starts, ends = np.r_[idx[0], idx[breaks + 1]], np.r_[idx[breaks], idx[-1]]
    return [(float(days[a]), float(days[b])) for a, b in zip(starts, ends)]


def main():
    drift = json.loads((DATA / "nbody_drift_calibration.json").read_text())
    stars = load_stars()
    t0 = bce_to_days(WIN_START_BCE)
    sim = nbody.build_sim(SAMPLE_DAYS)
    print("Phase A: integrating back to", WIN_START_BCE, "BCE ...", flush=True)
    ts, poles, eccs = phase_a(sim, t0)
    spins = precess_spin(ts, poles, eccs)
    obliq = np.degrees(np.arccos(np.clip(np.sum(spins * poles, axis=1), -1, 1)))

    # obliquity check against Berger & Loutre (1991)
    bl = []
    for line in (DATA / "paleo" / "berger_loutre_1991_orbit91.txt").read_text().splitlines():
        p = line.split()
        if len(p) == 9:
            try:
                bl.append((float(p[0]), float(p[3])))
            except ValueError:
                pass
    bl = np.array(bl)
    kyr = ts / 365.25 / 1000.0
    check = []
    for k in (0, -10, -41, -100, -250, -500, -750, -869, -880):
        mine = float(np.interp(k, kyr[::-1], obliq[::-1]))
        ref = float(np.interp(k, bl[::-1, 0], bl[::-1, 1]))
        check.append({"kyr": k, "this_model_deg": round(mine, 3), "berger_loutre_deg": round(ref, 3)})
        print(f"   obliquity at {k:>5} kyr: model {mine:.3f}  Berger&Loutre {ref:.3f}")
    corr = float(np.corrcoef(np.interp(bl[bl[:, 0] >= kyr.min(), 0], kyr[::-1], obliq[::-1]),
                             bl[bl[:, 0] >= kyr.min(), 1])[0, 1])
    print(f"   correlation with Berger & Loutre over 0-{-kyr.min():.0f} kyr: {corr:.4f}")

    # Phase B: forward through the window
    print("Phase B: sampling the window ...", flush=True)
    sim.dt = SAMPLE_DAYS
    t_end = bce_to_days(WIN_END_BCE)
    n = int((t_end - sim.t) / (SAMPLE_DAYS * RECORD_EVERY))
    days = np.zeros(n)
    xyz_all = np.zeros((n, NB, 3), dtype=np.float32)    # float32: ~1e-7 AU, i.e. < 0.01 arcsec at planet distances
    vxyz_all = np.zeros((n, NB, 3), dtype=np.float32)
    xyz = np.zeros((10, 3))
    vxyz = np.zeros((10, 3))
    for i in range(n):
        sim.steps(RECORD_EVERY)
        sim.serialize_particle_data(xyz=xyz, vxvyvz=vxyz)
        days[i] = sim.t
        xyz_all[i] = xyz[:NB]
        vxyz_all[i] = vxyz[:NB]
    years = days / 365.25
    print(f"   {n:,} samples from {days_to_bce(days[0]):,} to {days_to_bce(days[-1]):,} BCE", flush=True)

    out = {"window_bce": [WIN_START_BCE, WIN_END_BCE], "treta_end_bce": TRETA_END_BCE,
           "obliquity_check": check, "obliquity_correlation_BL91": round(corr, 4),
           "drift_corrections_deg_at_869ka": {k: v["extrapolated_869ka_deg"] for k, v in drift.items()}, "anchors": {}}
    k_now = interp_vec(ts, poles, days)
    s_now = interp_vec(ts, spins, days)
    equinox = np.cross(s_now, k_now)
    equinox /= np.linalg.norm(equinox, axis=1)[:, None]
    chunk = 200_000
    geo = {b: np.zeros(n) for b in BODY_IDX}
    trop_sun = np.zeros(n)
    sid = {name: {b: np.zeros(n, dtype=np.float32) for b in BODY_IDX} for name in ANCHORS}
    star_lon_trop = {}
    for a in range(0, n, chunk):
        b = min(a + chunk, n)
        fixed = drift_rotate(xyz_all[a:b].astype(np.float64), vxyz_all[a:b].astype(np.float64), years[a:b], drift)
        emb = fixed[:, 3]
        vec = {"sun": fixed[:, 0] - emb}
        for body, i in BODY_IDX.items():
            if body != "sun":
                vec[body] = fixed[:, i] - emb
        trop = {body: lon_from(v, k_now[a:b], equinox[a:b]) for body, v in vec.items()}
        trop_sun[a:b] = trop["sun"]
        for name, (star, star_lon) in ANCHORS.items():
            sv = np.array([star_unit(stars[star], d) for d in days[a:b:500]])
            sv = np.stack([np.interp(np.arange(a, b), np.arange(a, b, 500)[:len(sv)], sv[:, j]) for j in range(3)], axis=1)
            sv /= np.linalg.norm(sv, axis=1)[:, None]
            star_trop = lon_from(sv, k_now[a:b], equinox[a:b])
            for body in BODY_IDX:
                sid[name][body][a:b] = (trop[body] - star_trop + star_lon) % 360
            star_lon_trop.setdefault(name, []).append(float(star_trop.mean()))
    del xyz_all, vxyz_all

    sea_age, sea_lvl = deep_sealevel.bintanja()
    for name in ANCHORS:
        L = sid[name]
        sign = {b: (L[b] // 30).astype(int) for b in L}
        slow = ((sign["jupiter"] == 3) & (sign["saturn"] == 6) & (sign["mars"] == 9) & (sign["venus"] == 11))
        strict = slow & (L["sun"] >= 342.0) & (L["sun"] < 357.33)
        aries = slow & (sign["sun"] == 0)
        # Yuddha 6.90: Mars on Vishakha; Mercury on Rohini is possible only if the Sun is within 28 deg of Rohini
        war_sky = ((L["mars"] // NAK).astype(int) == 15) & (L["sun"] >= 40 - 28) & (L["sun"] <= 53.33 + 28)
        res = {"strict_windows": [], "sun_in_aries_windows": []}
        for key, mask in (("strict_windows", strict), ("sun_in_aries_windows", aries)):
            for s, e in windows(mask, days):
                i = int(np.searchsorted(days, (s + e) / 2))
                yr = days_to_bce(s)
                age_ka = (yr + 1950) / 1000.0
                war = windows(war_sky & (days >= s + 30 * 365.25) & (days <= s + 45 * 365.25), days)
                res[key].append({"start_bce": yr, "end_bce": days_to_bce(e), "days": round(e - s + SAMPLE_DAYS),
                                 "sun_sid": round(float(L["sun"][i]), 1), "tropical_sun": round(float(trop_sun[i]), 1),
                                 "season": ritu(float(trop_sun[i])),
                                 "sea_level_m": round(float(np.interp(age_ka, sea_age, sea_lvl)), 1),
                                 "war_sky_episodes_age_30_45": len(war),
                                 "years_before_treta_end": yr - TRETA_END_BCE})
        # season of Chaitra and the CE month-season pairings across the window
        yrs = np.arange(WIN_START_BCE, WIN_END_BCE - 1, -500)
        seasons = []
        for y in yrs:
            i = int(np.clip(np.searchsorted(days, bce_to_days(y)), 0, n - 1))
            seg = slice(i, min(i + 92, n))                       # one year of 4-day samples
            def trop_at(sid_target):
                j = np.argmin(np.abs(((L["sun"][seg] - sid_target) + 180) % 360 - 180))
                return float(trop_sun[seg][j])
            c, sr, ka, pa = trop_at(0.0), trop_at(120.0), trop_at(210.0), trop_at(270.0)
            def within(x, lo, hi, half=15):
                return any(((x + d - lo) % 360) <= ((hi - lo) % 360) for d in np.arange(-half, half + 1))
            seasons.append({"year_bce": int(y), "chaitra_tropical_sun": round(c, 1), "chaitra_season": ritu(c),
                            "caitra_bloom_ok": within(c, 315, 45), "sravana_rains_ok": within(sr, 80, 130),
                            "kartika_ok": within(ka, 180, 240), "pausa_hemanta_ok": within(pa, 225, 315)})
        res["chaitra_seasons"] = seasons
        res["all_pairings_pass_years"] = [s["year_bce"] for s in seasons if s["caitra_bloom_ok"] and s["sravana_rains_ok"]
                                          and s["kartika_ok"] and s["pausa_hemanta_ok"]]
        out["anchors"][name] = res
        print(f"[{name}] strict birth windows: {len(res['strict_windows'])}; 'Sun in Aries': {len(res['sun_in_aries_windows'])}; "
              f"years passing all month-season pairings: {len(res['all_pairings_pass_years'])}/{len(seasons)}")
        for w in res["strict_windows"][:12]:
            print(f"     {w}")
    # how far the anchor stars and Punarvasu's stars have moved since then
    moved = {}
    for star in stars:
        v_then, v_now = star_unit(stars[star], bce_to_days(TRETA_END_BCE)), star_unit(stars[star], 0.0)
        moved[star] = round(float(np.degrees(np.arccos(np.clip(np.dot(v_then, v_now), -1, 1)))), 1)
    out["star_displacement_deg_since_treta_end"] = moved
    print("star displacement since the end of Treta (deg):", moved)
    (DATA / "treta_sky.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
