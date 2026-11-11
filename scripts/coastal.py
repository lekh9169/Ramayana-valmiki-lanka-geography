"""Distance from a site to the open sea at a given relative sea level (GEBCO 2026).

Sea at level L = cells with elevation <= L connected to the edge of a 1.2-degree window
(so inland depressions and lagoons cut off from the ocean are not counted as sea).
"""
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).parent))
import gebco  # noqa: E402

R = 6371.0088
_G = None


def _grid():
    global _G
    if _G is None:
        _G = gebco.load_grid()
    return _G


def distance_to_sea(lat, lon, level, half=0.6):
    e, la, lo = gebco.window(_grid(), lat - half, lat + half, lon - half, lon + half)
    water = np.nan_to_num(e, nan=-9999) <= level
    labels, _ = ndimage.label(water)
    edge = np.unique(np.r_[labels[0], labels[-1], labels[:, 0], labels[:, -1]])
    edge = edge[edge != 0]
    sea = np.isin(labels, edge)
    if not sea.any():
        return None
    lat2, lon2 = np.meshgrid(la, lo, indexing="ij")
    p1, p2 = np.radians(lat), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon) / 2) ** 2
    d = np.where(sea, 2 * R * np.arcsin(np.sqrt(a)), np.inf)
    r, c = np.unravel_index(np.argmin(d), d.shape)
    here = gebco.sample(_grid(), lat, lon)
    return {"km": round(float(d[r, c]), 2), "nearest_sea_lat": round(float(la[r]), 4),
            "nearest_sea_lon": round(float(lo[c]), 4), "site_elev_m": here, "submerged": here <= level}


if __name__ == "__main__":
    for name, lat, lon in (("Korkai", 8.633, 78.083), ("Rameswaram temple", 9.288, 79.317),
                           ("Talaimannar", 9.09, 79.72), ("Kanyakumari", 8.078, 77.541)):
        for level in (-10, -3, 0, 1.5):
            print(name, level, distance_to_sea(lat, lon, level))
