"""Geometry of the Adam's Bridge (Rama Setu) shoal from GEBCO 2026.

For each depth cut-off D the shoal is the set of cells with elevation >= -D that are
connected to the crest between Rameswaram and Mannar islands. Reports the gap length
(shortest geodesic path between the two islands through the shoal), the shoal area,
and mean width = area / length. Valmiki (Yuddha 22) gives 100 yojanas x 10 yojanas,
so the interesting number is the length/width ratio, which does not depend on the
unknown length of a yojana.
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
EIGHT = ndimage.generate_binary_structure(2, 2)
R_KM = 6371.0088


def cell_km(lat):
    dy = np.radians(gebco.CELL) * R_KM
    dx = dy * np.cos(np.radians(lat))
    return dy, dx


def geodesic_shortest(mask, lats, sources, targets):
    """Dijkstra over 8-neighbours inside mask; returns (km, path)."""
    rows, cols = mask.shape
    dist = np.full(mask.shape, np.inf)
    prev = {}
    heap = []
    for s in sources:
        dist[s] = 0.0
        heapq.heappush(heap, (0.0, s))
    target_set = set(map(tuple, targets))
    while heap:
        d, (r, c) = heapq.heappop(heap)
        if d > dist[r, c]:
            continue
        if (r, c) in target_set:
            path = [(r, c)]
            while path[-1] in prev:
                path.append(prev[path[-1]])
            return d, path[::-1]
        dy, dx = cell_km(lats[r])
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and mask[nr, nc]:
                    step = np.hypot(dr * dy, dc * dx)
                    if d + step < dist[nr, nc]:
                        dist[nr, nc] = d + step
                        prev[(nr, nc)] = (r, c)
                        heapq.heappush(heap, (d + step, (nr, nc)))
    return None, []


def main():
    grid = gebco.load_grid()
    elev, lats, lons = gebco.window(grid, 8.85, 9.40, 79.15, 80.05)
    land_labels, _ = ndimage.label(elev > 0, structure=EIGHT)

    def label_at(lat, lon):
        return land_labels[int(np.argmin(np.abs(lats - lat))), int(np.argmin(np.abs(lons - lon)))]

    rameswaram = land_labels == label_at(9.288, 79.313)
    mannar = land_labels == label_at(9.05, 79.80)
    if not rameswaram.any() or not mannar.any():
        raise SystemExit("island seeds did not land on GEBCO land cells")
    # Island edge cells adjacent to water are the start/end set
    rame_cells = np.argwhere(rameswaram)
    mann_cells = np.argwhere(mannar)
    print(f"Rameswaram island cells: {len(rame_cells)}, Mannar island cells: {len(mann_cells)}")
    print(f"Rameswaram island easternmost GEBCO land: lon {lons[rame_cells[:,1].max()]:.4f}")
    print(f"Mannar island westernmost GEBCO land:     lon {lons[mann_cells[:,1].min()]:.4f}")

    cell_area = np.array([cell_km(lat)[0] * cell_km(lat)[1] for lat in lats])[:, None] * np.ones(elev.shape)
    rows = []
    for depth in (3, 4, 5, 6, 8, 10, 15):
        shallow = (elev >= -depth) & ~rameswaram & ~mannar
        mask = shallow | rameswaram | mannar
        # shortest path from the Rameswaram coast to the Mannar coast through shallow cells
        sources = [tuple(c) for c in rame_cells]
        targets = [tuple(c) for c in mann_cells]
        length, path = geodesic_shortest(mask, lats, sources, targets)
        if length is None:
            print(f"depth {depth:>3} m: islands not linked")
            continue
        path_cells = set(path)
        # Shoal body = shallow cells connected to the crest path
        shoal_labels, _ = ndimage.label(shallow, structure=EIGHT)
        crest_labels = {shoal_labels[r, c] for (r, c) in path if shoal_labels[r, c]}
        shoal = np.isin(shoal_labels, list(crest_labels))
        # Keep only the corridor between the islands (lon window of the gap)
        gap_lon_min = lons[rame_cells[:, 1].max()]
        gap_lon_max = lons[mann_cells[:, 1].min()]
        corridor = (lons[None, :] >= gap_lon_min) & (lons[None, :] <= gap_lon_max)
        shoal_gap = shoal & corridor
        area = float((cell_area * shoal_gap).sum())
        width = area / length
        if depth == 3:  # the sill level: every cell on this path is >= -3 m, i.e. the crest
            prof, run = [], 0.0
            for k, (r, c) in enumerate(path):
                if k:
                    pr, pc = path[k - 1]
                    dy, dx = cell_km(lats[r])
                    run += np.hypot((r - pr) * dy, (c - pc) * dx)
                prof.append({"km": round(run, 3), "lat": round(float(lats[r]), 5),
                             "lon": round(float(lons[c]), 5), "elev_m": float(elev[r, c])})
            (OUT / "setu_crest_profile.json").write_text(json.dumps(prof, indent=1))
        rows.append({"depth_cutoff_m": depth, "gap_length_km": round(length, 2),
                     "shoal_area_km2": round(area, 1), "mean_width_km": round(width, 2),
                     "length_to_width": round(length / width, 1)})
        print(f"depth {depth:>3} m: gap {length:6.2f} km, shoal area {area:7.1f} km2, "
              f"mean width {width:5.2f} km, L/W = {length / width:5.1f}")
    (OUT / "setu_shape.json").write_text(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
