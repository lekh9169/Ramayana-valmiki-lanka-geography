"""Which Sri Lankan terrain can be seen from the Setu landfall and from Rameswaram?

Geometric horizon with standard refraction (k = 0.13): a target of height H at distance d
is above the horizon of an observer at height h when d <= 3.86 (sqrt(h) + sqrt(H)) km.
Intermediate terrain is ignored (the northern Sri Lankan plain is < 100 m), so this is an
upper bound on visibility.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import gebco  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"
R = 6371.0088


def visible_targets(lat, lon, observer_h):
    g = gebco.load_grid()
    e, la, lo = gebco.window(g, 5.8, 10.0, 79.5, 82.0)
    lat2, lon2 = np.meshgrid(la, lo, indexing="ij")
    p1, p2 = np.radians(lat), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon) / 2) ** 2
    d = 2 * R * np.arcsin(np.sqrt(a))
    height = np.clip(np.nan_to_num(e), 0, None)
    vis = (height > 0) & (d <= 3.86 * (np.sqrt(observer_h) + np.sqrt(height)))
    far = vis & (height >= 100)
    best = None
    if far.any():
        r, c = np.unravel_index(np.argmax(np.where(far, height, -1)), height.shape)
        best = {"lat": round(float(la[r]), 4), "lon": round(float(lo[c]), 4), "elev_m": float(height[r, c]),
                "km": round(float(d[r, c]), 1)}
    return {"observer": [lat, lon, observer_h], "highest_visible_ge_100m": best,
            "max_visible_elev_m": float(height[vis].max()) if vis.any() else None}


if __name__ == "__main__":
    out = {}
    for name, lat, lon, h in (("Talaimannar (Setu landfall), eye 10 m", 9.09, 79.72, 10),
                              ("Talaimannar, from a 30 m dune/tree", 9.09, 79.72, 30),
                              ("Rameswaram Gandhamadana hill, 15 m", 9.30, 79.31, 15),
                              ("Mahendragiri summit 1555 m", 8.3854, 77.4896, 1555)):
        out[name] = visible_targets(lat, lon, h)
        print(name, out[name])
    (DATA / "visibility.json").write_text(json.dumps(out, indent=1))
