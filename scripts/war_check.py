"""Yuddha CE 6.90.27-30 (present in the Critical Edition): at Ravana's last battle Mercury
'stood assailing' Rohini and Mars Vishakha. Test each candidate birth epoch: does that
sky occur when Rama would be ~30-45 years old? Also report how common it is in general.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import ephem  # noqa: E402
from astro_search import NAKSHATRA  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"
ROHINI, VISHAKHA = 3, 15  # zero-based nakshatra indices


def days_matching(y0, y1, step=1.0):
    jd = np.arange(ephem.julian_calendar_to_jd(y0, 1, 1), ephem.julian_calendar_to_jd(y1, 1, 1), step)
    lon = ephem.geocentric_lons(jd, ("mercury", "mars"))
    ok = ((lon["mercury"] // NAKSHATRA).astype(int) == ROHINI) & ((lon["mars"] // NAKSHATRA).astype(int) == VISHAKHA)
    return jd[ok]


def main():
    out = {"candidates": []}
    candidates = [("6266 BCE (strict A)", -6265), ("4498 BCE (strict B)", -4497),
                  ("7120 BCE (Sun-in-Aries)", -7119), ("5352 BCE (Sun-in-Aries)", -5351)]
    for label, year in candidates:
        hits = days_matching(year + 30, year + 46)
        episodes = []
        for h in hits:
            if not episodes or h - episodes[-1][-1] > 5:
                episodes.append([h])
            else:
                episodes[-1].append(h)
        summary = [{"start": ephem.fmt_date(e[0]), "days": len(e),
                    "rama_age_years": round((e[0] - ephem.julian_calendar_to_jd(year, 1, 1)) / 365.25, 1)}
                   for e in episodes]
        out["candidates"].append({"birth": label, "episodes_age_30_45": summary})
        print(f"{label}: {len(summary)} episode(s) at age 30-45: " +
              "; ".join(f"{s['start']} (age {s['rama_age_years']}, {s['days']} d)" for s in summary))
    # base rate: fraction of 16-year windows containing at least one such day, 6000 BCE - 0
    hits = days_matching(-6000, 0, 2.0)
    years = np.array([ephem.jd_to_julian_calendar(h)[0] for h in hits])
    windows = np.arange(-6000, -16, 16)
    frac = float(np.mean([np.any((years >= w) & (years < w + 16)) for w in windows]))
    out["base_rate_16yr_windows"] = round(frac, 3)
    print(f"Base rate: {frac:.0%} of 16-year windows (6000 BCE-0) contain such a sky")
    (DATA / "war_check.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
