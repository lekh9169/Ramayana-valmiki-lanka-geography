"""Cross-checks for the astronomical dating:
1. A widely cited published date (P. Bhatnagar, 2004: 10 Jan 5114 BCE) re-evaluated on DE441.
2. The 'Sun in Aries' reading (Sun, Mars, Jupiter, Venus, Saturn exalted; Moon in
   Punarvasu) searched without the tithi condition, then the tithi reported.
3. Season (ritu) of Chaitra at each candidate epoch: tropical Sun from the IAU 2006
   general precession in longitude (adequate at month level over this range).
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import ephem  # noqa: E402
from astro_search import EXALT, NAKSHATRA, sign  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "data"
NAK_NAMES = ("Ashvini Bharani Krittika Rohini Mrigashira Ardra Punarvasu Pushya Ashlesha Magha "
             "PurvaPhalguni UttaraPhalguni Hasta Chitra Svati Vishakha Anuradha Jyeshtha Mula "
             "PurvaAshadha UttaraAshadha Shravana Dhanishtha Shatabhisha PurvaBhadrapada "
             "UttaraBhadrapada Revati").split()
SIGNS = "Aries Taurus Gemini Cancer Leo Virgo Libra Scorpio Sagittarius Capricorn Aquarius Pisces".split()
RITU = [("Shishira", 270), ("Vasanta", 330), ("Grishma", 30), ("Varsha", 90), ("Sharad", 150), ("Hemanta", 210)]
NAMES = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn")


def delta_t_days(year):
    """Morrison & Stephenson (2004) long-term parabola, seconds -> days."""
    u = (year - 1820) / 100.0
    return (-20 + 32 * u * u) / 86400.0


def general_precession_deg(jd):
    t = (jd - ephem.JD_J2000) / 36525.0
    return (5028.796195 * t + 1.1054348 * t ** 2 + 0.00007964 * t ** 3) / 3600.0


def tropical_sun(jd):
    lon = ephem.geocentric_lons(jd, ("sun",))["sun"][0]
    ayanamsa = float(ephem.spica_lon_j2000(jd)) - 180.0 + general_precession_deg(jd)
    return (lon + ayanamsa) % 360.0


def ritu(trop):
    for k, (name, start) in enumerate(RITU):
        end = RITU[(k + 1) % 6][1]
        if (trop - start) % 360 < (end - start) % 360:
            return name
    return "?"


def describe(jd):
    lon = {k: float(v[0]) for k, v in ephem.geocentric_lons(jd, NAMES).items()}
    elong = (lon["moon"] - lon["sun"]) % 360
    tithi = int(elong // 12) + 1
    paksha = "Shukla" if tithi <= 15 else "Krishna"
    trop = tropical_sun(jd)
    return {
        "date": ephem.fmt_date(jd), "jd_tdb": round(jd, 3),
        "tithi": f"{paksha} {tithi if tithi <= 15 else tithi - 15}",
        "moon_nakshatra": NAK_NAMES[int(lon['moon'] // NAKSHATRA)],
        "signs": {b: SIGNS[int(lon[b] // 30)] for b in NAMES},
        "exalted": [b for b in NAMES if int(lon[b] // 30) == EXALT[b]],
        "sidereal_lon": {b: round(v, 2) for b, v in lon.items()},
        "tropical_sun": round(trop, 1), "ritu_of_sun": ritu(trop),
    }


def sun_in_aries_search(offset=0.0):
    hits = []
    start = ephem.julian_calendar_to_jd(-13000, 1, 1)
    end = ephem.julian_calendar_to_jd(0, 1, 1)
    chunk = 365.25 * 250
    jd0 = start
    while jd0 < end:
        jd = np.arange(jd0, min(jd0 + chunk, end), 1.0)
        lon = ephem.geocentric_lons(jd, ("sun", "venus", "mars", "jupiter", "saturn"), offset)
        ok = ((sign(lon["sun"]) == 0) & (sign(lon["jupiter"]) == 3) & (sign(lon["saturn"]) == 6)
              & (sign(lon["mars"]) == 9) & (sign(lon["venus"]) == 11))
        for day in jd[ok]:
            hourly = np.arange(day, day + 1, 1 / 24)
            moon = ephem.geocentric_lons(hourly, ("moon",), offset)["moon"]
            in_punarvasu = (moon // NAKSHATRA).astype(int) == 6
            if in_punarvasu.any():
                hits.append(float(hourly[np.argmax(in_punarvasu)]))
        jd0 += chunk
    # one representative per month-long episode
    reps = []
    for h in hits:
        if not reps or h - reps[-1] > 20:
            reps.append(h)
    return reps


def main():
    report = {}
    # 1. Bhatnagar (2004): 10 Jan 5114 BCE, ~12:30 local at Ayodhya (UT+5:29)
    jd_civil = ephem.julian_calendar_to_jd(-5113, 1, 10) + (12.5 - 5.49) / 24
    dt = delta_t_days(-5113)
    report["bhatnagar_5114BCE"] = {
        "assumption": "10 Jan 5114 BCE Julian, 12:30 local mean time at Ayodhya",
        "delta_t_days": round(dt, 2),
        "without_delta_t": describe(jd_civil),
        "with_delta_t": describe(jd_civil + dt),
    }
    for key in ("without_delta_t", "with_delta_t"):
        d = report["bhatnagar_5114BCE"][key]
        print(f"Bhatnagar date ({key}): {d['date']} tithi {d['tithi']}, Moon in {d['moon_nakshatra']}, "
              f"signs {d['signs']}, exalted {d['exalted']}")

    # 2. Sun-in-Aries reading
    reps = sun_in_aries_search()
    report["sun_in_aries_reading"] = [describe(j) for j in reps]
    print(f"\n'Sun in Aries' reading (Sun,Mars,Jup,Ven,Sat exalted + Moon in Punarvasu): {len(reps)} episodes")
    for d in report["sun_in_aries_reading"]:
        print(f"   {d['date']:<46} tithi {d['tithi']:<11} Moon {d['moon_nakshatra']:<9} "
              f"exalted {len(d['exalted'])}: {','.join(d['exalted'])}  season {d['ritu_of_sun']}")

    # 3. Season of the strict-reading candidates (from astro_search.py output)
    search = json.loads((OUT / "rama_birth_search.json").read_text())
    lahiri = next(r for r in search["runs"] if r["ayanamsa_offset_deg"] == 0.0)
    report["strict_reading_candidates"] = [describe(m["jd_tdb"]) for m in lahiri["matches"]]
    print("\nStrict reading (navami + Punarvasu + Jupiter & Moon in Cancer), Lahiri zodiac:")
    for d in report["strict_reading_candidates"]:
        print(f"   {d['date']:<46} tithi {d['tithi']:<10} Moon {d['moon_nakshatra']:<9} exalted "
              f"{','.join(d['exalted'])}; tropical Sun {d['tropical_sun']} -> season {d['ritu_of_sun']}")

    # Season of Chaitra through time: tropical Sun when sidereal Sun = 350 (mid-Chaitra navami)
    report["chaitra_season_by_epoch"] = []
    print("\nSeason in which Chaitra (sidereal Sun ~350 deg) falls, by epoch:")
    for year in (-12000, -10000, -8000, -6265, -5113, -4497, -3000, -1500, -500, 0, 500, 1950):
        jd = ephem.julian_calendar_to_jd(year, 1, 1)
        days = np.arange(jd, jd + 366, 1.0)
        sun = ephem.geocentric_lons(days, ("sun",))["sun"]
        j = float(days[np.argmin(np.abs(((sun - 350) + 180) % 360 - 180))])
        trop = tropical_sun(j)
        report["chaitra_season_by_epoch"].append({"year": year, "tropical_sun": round(trop, 1), "ritu": ritu(trop)})
        print(f"   year {year:>6}: tropical Sun {trop:6.1f} -> {ritu(trop)}")
    (OUT / "astro_checks.json").write_text(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
