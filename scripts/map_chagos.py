"""Figures for the Chagos-Laccadive scan: ridge crest profile and the drowned islands of Chagos."""
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
import plotlib  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"


def ridge_profile(scan):
    prof = scan["ridge_profile"]
    lat = np.array([p["lat"] for p in prof])
    z = np.clip(np.array([p["crest_m"] for p in prof]), -5000, 3)  # GEBCO atoll 'land' heights are artefacts
    fig, ax = plt.subplots(figsize=(12, 4.6))
    ax.fill_between(lat, -5000, z, color="#d9c88c")
    ax.plot(lat, z, color="#8c6e54", lw=0.8)
    for level, color, label in ((0, "#1d4e89", "present sea level"), (-90, "#e85d04", "sea level at the Puranic end of Treta (-90 m)"),
                                (-128, "#7b2cbf", "deepest glacial sea level of the last 1 Myr (-128 m)")):
        ax.axhline(level, color=color, lw=1.2, ls="--" if level else "-", label=label)
    for name, la in (("Lakshadweep", 10.6), ("Male", 4.2), ("Huvadhu", 0.5), ("Addu", -0.6), ("Peros Banhos", -5.3),
                     ("Great Chagos Bank", -6.2), ("Diego Garcia", -7.3)):
        ax.annotate(name, (la, 20), rotation=90, fontsize=7, ha="center", va="bottom")
    ax.axvline(0, color="grey", lw=0.6)
    ax.set_xlim(12.6, -12)
    ax.set_ylim(-4500, 900)
    ax.set_xlabel("Latitude (°N) — north on the left")
    ax.set_ylabel("Shallowest depth in each 0.05° band (m)")
    ax.set_title("Chagos–Laccadive ridge crest, Lakshadweep to Chagos (GEBCO 2026, 71–74°E). Segments above the dashed "
                 "lines were land in glacial times; the deep gaps between them never were", fontsize=9.5)
    ax.legend(fontsize=7, loc="lower left")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    print(plotlib.save(fig, "08_ridge_crest_profile.png"))


def chagos_map(scan):
    fig, axes = plt.subplots(1, 2, figsize=(14, 7.6))
    for ax, level, title in ((axes[0], -90.0, "At the Puranic end of Treta (~869 ka): sea level −90 m"),
                             (axes[1], 0.0, "Today")):
        elev, lats, lons = plotlib.relief(ax, -8.8, -3.8, 70.0, 73.6, sea_level=level, step=1, land_max=400, sea_min=-5000)
        plotlib.coastline(ax, elev, lats, lons, -90.0, colors="#e85d04", linewidths=0.5)
        ax.set_title(title, fontsize=10)
        offsets = {"Great Chagos Bank / Egmont Islands": (0.15, 0.05), "Pitt Bank": (0.12, 0.05), "Speakers Bank": (0.15, 0.1),
                   "Peros Banhos": (-0.95, 0.25), "Salomon Islands / Blenheim Reef": (0.2, -0.05), "Diego Garcia": (0.1, 0.05)}
        labelled = set()
        for b in scan["banks"]:  # sorted largest first, so each name labels its main bank only
            if b["name"] not in offsets or b["name"] in labelled:
                continue
            labelled.add(b["name"])
            dx, dy = offsets[b["name"]]
            short = b["name"].split(" / ")[0]
            if level == 0:
                txt = f"{short}: {b['emergent_area_km2']['lost_since_treta']:,.0f} km² now under water"
                if b["drowning_age_ka_holocene"]:
                    txt += f" (drowned ~{b['drowning_age_ka_holocene']:.1f} ka)"
            else:
                txt = f"{short}: {b['emergent_area_km2']['treta_-90m']:,.0f} km²"
            plotlib.place_marker(ax, b["centroid"][1], b["centroid"][0], txt, size=12, fontsize=6.5, dx=dx, dy=dy,
                                 color="#7b2cbf")
        for c in scan["depression_shape_summary"]["near_circular_deep_basins"]:
            if -8.8 <= c["centroid"][0] <= -3.8 and 70 <= c["centroid"][1] <= 73.6:
                ax.scatter([c["centroid"][1]], [c["centroid"][0]], marker="o", s=60, facecolors="none", edgecolors="yellow",
                           label="near-circular closed basin (rim {:+d} m vs surroundings)".format(c["rim_minus_surroundings_m"]))
        ax.legend(loc="lower right", fontsize=6.5)
    fig.suptitle("Chagos Archipelago: GEBCO 2026 bathymetry flooded to −90 m and to today's sea level "
                 "(orange line = the −90 m coastline)", fontsize=10)
    fig.tight_layout()
    print(plotlib.save(fig, "09_chagos_drowned_islands.png"))


if __name__ == "__main__":
    data = json.loads((DATA / "chagos_scan.json").read_text())
    ridge_profile(data)
    chagos_map(data)
