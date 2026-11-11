"""Search DE441 (-13000 .. -1) for the Bala Kanda 18.8-9 birth configuration of Rama.

Text (vulgate 1.18.8-9): Chaitra month, navami tithi, Aditi's nakshatra (Punarvasu),
five grahas in their exaltation signs, Karkata (Cancer) lagna, Jupiter together with
the Moon. Classical exaltation signs: Sun-Aries, Moon-Taurus, Mars-Capricorn,
Mercury-Virgo, Jupiter-Cancer, Venus-Pisces, Saturn-Libra.

Stage 1 (daily): slow-planet conditions + Sun near late Pisces.
Stage 2 (hourly, inside stage-1 windows): Moon conditions (tithi, nakshatra, sign).
Repeated for several zodiac origins (ayanamsa offsets) to show sensitivity.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import ephem  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "data"
START_JD = ephem.julian_calendar_to_jd(-13000, 1, 1)
END_JD = ephem.julian_calendar_to_jd(0, 1, 1)
NAKSHATRA = 360.0 / 27.0
PUNARVASU = (6 * NAKSHATRA, 7 * NAKSHATRA)  # 80.000 .. 93.333
EXALT = {"sun": 0, "moon": 1, "mars": 9, "mercury": 5, "jupiter": 3, "venus": 11, "saturn": 6}
OFFSETS = [-6.0, -4.0, -2.0, 0.0, 2.0, 4.0, 6.0]


def sign(lon):
    return (np.asarray(lon) // 30).astype(int) % 12


def stage1(offset):
    """Daily scan; returns list of [jd_start, jd_end] windows."""
    windows = []
    chunk = 365.25 * 250
    jd0 = START_JD
    max_merc_elong = 0.0
    while jd0 < END_JD:
        jd = np.arange(jd0, min(jd0 + chunk, END_JD), 1.0)
        lon = ephem.geocentric_lons(jd, ("sun", "mercury", "venus", "mars", "jupiter", "saturn"), offset)
        elong = np.abs((lon["mercury"] - lon["sun"] + 180) % 360 - 180)
        max_merc_elong = max(max_merc_elong, float(elong.max()))
        ok = ((sign(lon["jupiter"]) == 3) & (sign(lon["saturn"]) == 6) & (sign(lon["mars"]) == 9)
              & (sign(lon["venus"]) == 11) & (lon["sun"] >= 338.0))
        hits = jd[ok]
        if hits.size:
            breaks = np.where(np.diff(hits) > 1.5)[0]
            starts = np.r_[hits[0], hits[breaks + 1]]
            ends = np.r_[hits[breaks], hits[-1]]
            windows += [[float(s) - 1, float(e) + 1] for s, e in zip(starts, ends)]
        jd0 += chunk
    return windows, max_merc_elong


def stage2(windows, offset):
    found = []
    for s, e in windows:
        jd = np.arange(s, e, 1.0 / 24.0)
        lon = ephem.geocentric_lons(jd, offset_names := ("sun", "moon", "mercury", "venus", "mars",
                                                           "jupiter", "saturn"), offset)
        elong = (lon["moon"] - lon["sun"]) % 360
        tithi = (elong // 12).astype(int) + 1            # 1..30; shukla navami = 9
        nak = (lon["moon"] // NAKSHATRA).astype(int) + 1  # 1..27; Punarvasu = 7
        moon_ok = (tithi == 9) & (nak == 7)
        if not moon_ok.any():
            continue
        exalted = np.zeros(jd.size, dtype=int)
        for body in offset_names:
            exalted += (sign(lon[body]) == EXALT[body]).astype(int)
        moon_cancer = sign(lon["moon"]) == 3
        idx = np.where(moon_ok)[0]
        best = idx[np.argmax(exalted[idx] * 10 + moon_cancer[idx])]
        found.append({
            "jd_tdb": round(float(jd[best]), 4),
            "date": ephem.fmt_date(jd[best]),
            "hours_navami_and_punarvasu": int(moon_ok.sum()),
            "hours_also_moon_in_cancer": int((moon_ok & moon_cancer).sum()),
            "exalted_count": int(exalted[best]),
            "exalted": [b for b in offset_names if sign(lon[b][best]) == EXALT[b]],
            "lon": {b: round(float(lon[b][best]), 2) for b in offset_names},
        })
    return found


def main():
    summary = {"range": [ephem.fmt_date(START_JD), ephem.fmt_date(END_JD)], "runs": []}
    for offset in OFFSETS:
        windows, merc = stage1(offset)
        found = stage2(windows, offset)
        five = [f for f in found if f["exalted_count"] >= 5]
        print(f"ayanamsa offset {offset:+.0f} deg: {len(windows)} slow-planet windows, "
              f"{len(found)} with Chaitra shukla navami in Punarvasu, "
              f"{sum(f['hours_also_moon_in_cancer'] > 0 for f in found)} also Moon+Jupiter in Cancer, "
              f"{len(five)} with >=5 exalted; max Mercury elongation {merc:.1f} deg")
        for f in found:
            print(f"    {f['date']:<46} JD {f['jd_tdb']:.2f}  exalted={f['exalted_count']} "
                  f"{','.join(f['exalted'])}  moon-in-cancer-hours={f['hours_also_moon_in_cancer']}  "
                  f"Sun {f['lon']['sun']:.1f} Moon {f['lon']['moon']:.1f}")
        summary["runs"].append({"ayanamsa_offset_deg": offset, "stage1_windows": len(windows),
                                "max_mercury_elongation_deg": round(merc, 2), "matches": found})
    (OUT / "rama_birth_search.json").write_text(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
