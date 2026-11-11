"""Horizontal plate-motion correction: where a site sat in a no-net-rotation frame at epoch t.

Uses an Euler-pole rotation for the India plate. All Ramayana sites in India and Sri Lanka
ride the same plate, so their relative geometry is unchanged; the correction only matters
for comparing ancient positions against fixed (mantle / astronomical) references such as
'the equator' or an observer's latitude. Default pole: NNR-MORVEL56 (Argus, Gordon & DeMets
2011), India plate, set via INDIA_POLE below.
"""
import numpy as np

# (pole latitude deg N, pole longitude deg E, rate deg per Myr) — NNR-MORVEL56 India plate
INDIA_POLE = (50.37, -3.29, 0.544)
R_KM = 6371.0088


def _unit(lat, lon):
    p, l = np.radians(lat), np.radians(lon)
    return np.array([np.cos(p) * np.cos(l), np.cos(p) * np.sin(l), np.sin(p)])


def velocity_mm_yr(lat, lon, pole=INDIA_POLE):
    """Return (east, north, speed, azimuth_deg) of present plate velocity at the site."""
    plat, plon, rate = pole
    omega = _unit(plat, plon) * np.radians(rate) / 1e6  # rad/yr
    r = _unit(lat, lon) * R_KM * 1e6  # mm
    v = np.cross(omega, r)
    p, l = np.radians(lat), np.radians(lon)
    east = np.array([-np.sin(l), np.cos(l), 0.0])
    north = np.array([-np.sin(p) * np.cos(l), -np.sin(p) * np.sin(l), np.cos(p)])
    ve, vn = float(v @ east), float(v @ north)
    return ve, vn, float(np.hypot(ve, vn)), float(np.degrees(np.arctan2(ve, vn)) % 360)


def position_at(lat, lon, years_before_present, pole=INDIA_POLE):
    """Rotate the site backwards along the plate's Euler rotation."""
    plat, plon, rate = pole
    axis = _unit(plat, plon)
    angle = -np.radians(rate) * years_before_present / 1e6
    x = _unit(lat, lon)
    rotated = (x * np.cos(angle) + np.cross(axis, x) * np.sin(angle)
               + axis * (axis @ x) * (1 - np.cos(angle)))
    return float(np.degrees(np.arcsin(rotated[2]))), float(np.degrees(np.arctan2(rotated[1], rotated[0])))


if __name__ == "__main__":
    for name, lat, lon in (("Talaimannar", 9.09, 79.72), ("Ayodhya", 26.80, 82.20)):
        ve, vn, s, az = velocity_mm_yr(lat, lon)
        print(f"{name}: v = {s:.1f} mm/yr toward {az:.0f} deg (E {ve:.1f}, N {vn:.1f})")
        for t in (7000, 8300, 14200):
            la, lo = position_at(lat, lon, t)
            dkm = np.hypot((la - lat) * 111.2, (lo - lon) * 111.2 * np.cos(np.radians(lat)))
            print(f"   {t:>6} yr ago: {la:.5f}N {lo:.5f}E  (shift {dkm * 1000:.0f} m)")
