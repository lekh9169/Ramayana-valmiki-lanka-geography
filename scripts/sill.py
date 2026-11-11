"""Land-bridge sill between peninsular India and Sri Lanka from GEBCO 2026.

The sill is the highest sea level at which a continuous strip of land still links the
two landmasses: the max over all paths of the min elevation along the path. Found by
bisection on the flood level with connected-component labelling (4-connectivity, i.e.
no diagonal leaks), then the crest path is traced with a max-min Dijkstra.
"""
import heapq
import json
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).parent))
import gebco  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "data"
FOUR = ndimage.generate_binary_structure(2, 1)


def connected(elev, level, a, b):
    labels, _ = ndimage.label(elev > level, structure=FOUR)
    return labels[a] != 0 and labels[a] == labels[b]


def sill_level(elev, a, b, lo=-200.0, hi=50.0, tol=0.05):
    if not connected(elev, lo, a, b):
        return None
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if connected(elev, mid, a, b):
            lo = mid
        else:
            hi = mid
    return lo


def crest_path(elev, start, goal):
    """Path maximising the minimum elevation (ties broken by length)."""
    rows, cols = elev.shape
    best = np.full(elev.shape, -np.inf)
    prev = -np.ones(elev.shape + (2,), dtype=np.int32)
    best[start] = elev[start]
    heap = [(-best[start], 0, start)]
    while heap:
        neg, steps, (r, c) = heapq.heappop(heap)
        if (r, c) == goal:
            break
        if -neg < best[r, c]:
            continue
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not np.isnan(elev[nr, nc]):
                value = min(-neg, elev[nr, nc])
                if value > best[nr, nc]:
                    best[nr, nc] = value
                    prev[nr, nc] = (r, c)
                    heapq.heappush(heap, (-value, steps + 1, (nr, nc)))
    path = [goal]
    while path[-1] != start:
        r, c = path[-1]
        path.append(tuple(prev[r, c]))
    return path[::-1]


def idx(lats, lons, lat, lon):
    return int(np.argmin(np.abs(lats - lat))), int(np.argmin(np.abs(lons - lon)))


def haversine_km(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi, dl = p2 - p1, np.radians(lon2 - lon1)
    h = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * 6371.0088 * np.arcsin(np.sqrt(h))


def main():
    grid = gebco.load_grid()
    elev, lats, lons = gebco.window(grid, 5.5, 11.6, 76.5, 82.5)
    india = idx(lats, lons, 9.93, 78.12)      # Madurai
    lanka = idx(lats, lons, 6.81, 80.50)      # Adam's Peak (Sri Pada)
    level = sill_level(elev, india, lanka)
    print(f"India-Sri Lanka land-bridge sill (GEBCO 2026, 4-connected): {level:.2f} m")

    # Which corridor carries the sill? Test the Adam's Bridge corridor and the northern
    # Palk Strait corridor (Point Calimere - Jaffna) separately by masking the other.
    results = {"sill_all_m": round(level, 2)}
    lat_grid = lats[:, None] * np.ones_like(lons)[None, :]
    lon_grid = np.ones_like(lats)[:, None] * lons[None, :]
    adams_only = elev.copy()
    adams_only[(lat_grid > 9.45) & (lon_grid > 79.2) & (lon_grid < 80.4)] = -999  # block Palk Strait north
    palk_only = elev.copy()
    palk_only[(lat_grid < 9.45) & (lat_grid > 8.6) & (lon_grid > 79.1) & (lon_grid < 79.95)] = -999  # block Adam's Bridge
    for name, arr in (("adams_bridge_corridor", adams_only), ("palk_strait_north_corridor", palk_only)):
        value = sill_level(arr, india, lanka)
        results[f"sill_{name}_m"] = None if value is None else round(value, 2)
        print(f"  {name:28s} sill = {value:.2f} m")

    # Crest path across Adam's Bridge, Rameswaram island to Mannar island
    sub, slats, slons = gebco.window(grid, 8.8, 9.45, 79.15, 80.0)
    start = idx(slats, slons, 9.288, 79.313)   # Rameswaram town
    goal = idx(slats, slons, 8.98, 79.91)      # Mannar town
    path = crest_path(sub, start, goal)
    profile = []
    dist = 0.0
    for k, (r, c) in enumerate(path):
        if k:
            pr, pc = path[k - 1]
            dist += haversine_km(slats[pr], slons[pc], slats[r], slons[c])
        profile.append({"km": round(dist, 3), "lat": round(float(slats[r]), 5),
                        "lon": round(float(slons[c]), 5), "elev_m": float(sub[r, c])})
    lowest = min(profile, key=lambda p: p["elev_m"])
    print(f"Adam's Bridge crest path: {len(path)} cells, {dist:.1f} km Rameswaram->Mannar; "
          f"lowest point {lowest['elev_m']:.0f} m at {lowest['lat']:.4f}N {lowest['lon']:.4f}E (km {lowest['km']:.1f})")
    # Submerged stretch between the two islands only (drop the on-island ends)
    wet = [p for p in profile if p["elev_m"] <= 0]
    if wet:
        print(f"  submerged crest from km {wet[0]['km']:.1f} to {wet[-1]['km']:.1f} "
              f"({wet[-1]['km'] - wet[0]['km']:.1f} km), mean depth {np.mean([p['elev_m'] for p in wet]):.1f} m")
    results["adams_bridge_crest"] = {"length_km": round(dist, 2), "lowest": lowest,
                                     "submerged_from_km": wet[0]["km"] if wet else None,
                                     "submerged_to_km": wet[-1]["km"] if wet else None}
    (OUT / "adams_bridge_profile.json").write_text(json.dumps(profile, indent=1))
    (OUT / "sill_results.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
