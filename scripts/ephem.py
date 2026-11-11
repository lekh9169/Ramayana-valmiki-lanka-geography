"""Geocentric sidereal longitudes from JPL DE441 (part 1: -13200 .. 1969).

Sidereal longitude is measured from a zodiac anchored on Spica (Chitra) = 180 deg
(the Lahiri / Chitrapaksha convention), computed as the difference of ecliptic
longitudes in the fixed J2000 ecliptic frame. Precession cancels in that difference;
the residual from the motion of the ecliptic plane is < 0.1 deg over 15 kyr, far
below the 13.3 deg nakshatra and 30 deg rashi widths tested here.
"""
import os
from pathlib import Path

import numpy as np
from jplephem.spk import SPK

# JPL DE441 part 1 (1.65 GB, https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de441_part-1.bsp):
# set the DE441_BSP environment variable, or put the file in <project>/ephemeris/.
BSP = Path(os.environ.get("DE441_BSP", Path(__file__).resolve().parents[1] / "ephemeris" / "de441_part-1.bsp"))
OBLIQUITY_J2000 = np.radians(84381.406 / 3600.0)  # IAU 2006
JD_J2000 = 2451545.0

# Spica (alpha Vir), Hipparcos (van Leeuwen 2007): ICRS J2000 + proper motion (mas/yr)
SPICA_RA, SPICA_DEC = 201.29824736, -11.16131949
SPICA_PM_RA_COSDEC, SPICA_PM_DEC = -42.35, -30.67

_kernel = None


def kernel():
    global _kernel
    if _kernel is None:
        _kernel = SPK.open(str(BSP))
    return _kernel


def _seg(center, target):
    return kernel()[center, target]


def _ecliptic_lon_lat(xyz):
    x, y, z = xyz
    ce, se = np.cos(OBLIQUITY_J2000), np.sin(OBLIQUITY_J2000)
    ye = y * ce + z * se
    ze = -y * se + z * ce
    lon = np.degrees(np.arctan2(ye, x)) % 360.0
    lat = np.degrees(np.arctan2(ze, np.hypot(x, ye)))
    return lon, lat


def spica_lon_j2000(jd):
    years = (np.asarray(jd) - JD_J2000) / 365.25
    dec = SPICA_DEC + SPICA_PM_DEC * years / 3.6e6
    ra = SPICA_RA + SPICA_PM_RA_COSDEC * years / 3.6e6 / np.cos(np.radians(dec))
    r, d = np.radians(ra), np.radians(dec)
    xyz = np.array([np.cos(d) * np.cos(r), np.cos(d) * np.sin(r), np.sin(d)])
    return _ecliptic_lon_lat(xyz)[0]


def earth_ssb(jd):
    return _seg(0, 3).compute(jd) + _seg(3, 399).compute(jd)


BODIES = {"sun": (0, 10), "mercury": (0, 1), "venus": (0, 2), "mars": (0, 4),
          "jupiter": (0, 5), "saturn": (0, 6)}


def geocentric_lons(jd, names=("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"),
                    ayanamsa_offset=0.0):
    """Sidereal geocentric longitudes (deg) for the requested bodies at TDB Julian dates.

    ayanamsa_offset shifts the zodiac origin (deg): positive = zodiac starts later.
    """
    jd = np.atleast_1d(np.asarray(jd, dtype=float))
    zero = spica_lon_j2000(jd) - 180.0 + ayanamsa_offset
    out = {}
    earth = None
    for name in names:
        if name == "moon":
            vec = _seg(3, 301).compute(jd) - _seg(3, 399).compute(jd)
        else:
            if earth is None:
                earth = earth_ssb(jd)
            vec = _seg(*BODIES[name]).compute(jd) - earth
        out[name] = (_ecliptic_lon_lat(vec)[0] - zero) % 360.0
    return out


def jd_to_julian_calendar(jd):
    """Proleptic Julian calendar (astronomical year numbering: year 0 = 1 BCE)."""
    jd = float(jd) + 0.5
    shift_cycles = 0
    if jd < 0:  # move into positive range by whole 4-year Julian cycles
        shift_cycles = int(np.ceil(-jd / 1461.0)) + 1
        jd += shift_cycles * 1461
    z = int(jd)
    f = jd - z
    b = z + 1524
    c = int((b - 122.1) / 365.25)
    d = int(365.25 * c)
    e = int((b - d) / 30.6001)
    day = b - d - int(30.6001 * e) + f
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715
    year -= 4 * shift_cycles
    return year, month, day


def julian_calendar_to_jd(year, month, day):
    """Inverse of jd_to_julian_calendar (astronomical year numbering)."""
    shift_cycles = 0
    if year < -4712:
        shift_cycles = (-4712 - year) // 4 + 1
        year += 4 * shift_cycles
    if month <= 2:
        year -= 1
        month += 12
    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day - 1524.5
    return jd - shift_cycles * 1461


def gregorian_to_jd(year, month, day):
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    jdn = day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    return jdn - 0.5


def fmt_date(jd):
    y, m, d = jd_to_julian_calendar(jd)
    era = f"{1 - y} BCE" if y <= 0 else f"{y} CE"
    months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    return f"{int(d):02d} {months[m - 1]} {era} (Julian cal., astronomical year {y})"


if __name__ == "__main__":
    # Self-checks: calendar round trip, and Lahiri ayanamsa at J2000 ~ 23.85 deg
    for y, m, d in [(2000, 1, 1), (-5113, 1, 10), (-12208, 3, 1), (-4712, 1, 1)]:
        jd = julian_calendar_to_jd(y, m, d)
        assert jd_to_julian_calendar(jd)[:2] == (y, m), (y, m, d, jd, jd_to_julian_calendar(jd))
    print("Lahiri-style ayanamsa at J2000 (Spica J2000 ecl. lon - 180):",
          round(float(spica_lon_j2000(JD_J2000)) - 180.0, 4))
    # Mesha sankranti 1950 (Lahiri) fell on 13 April 1950; DE441 part 1 ends in 1969
    for day in (12, 13, 14):
        jd = gregorian_to_jd(1950, 4, day)
        print(f"Sidereal Sun {day} Apr 1950 0h TT:", np.round(geocentric_lons(jd, ("sun",))["sun"], 3))
