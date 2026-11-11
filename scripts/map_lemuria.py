"""Figures for Lemuria / Kumari Kandam (GEBCO 2026) and Mauritius / the Mascarene banks (NOAA ETOPO 2022)."""
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource

sys.path.insert(0, str(Path(__file__).parent))
import plotlib  # noqa: E402
from lemuria_mauritius import load_etopo  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"


def kumari_kandam_map(res):
    fig, ax = plt.subplots(figsize=(10, 9))
    elev, lats, lons = plotlib.relief(ax, 3.0, 11.0, 74.5, 82.5, sea_level=-128.0, step=2, land_max=2400, sea_min=-5000)
    drowned = np.where((elev > -128) & (elev <= 0), 1.0, np.nan)
    ax.contourf(lons, lats, drowned, levels=[0.5, 1.5], colors=["#E3C98F"], alpha=0.55)
    plotlib.coastline(ax, elev, lats, lons, 0.0, colors="black", linewidths=0.5)
    for key, depth in res["ocean_depth_south_of_kanyakumari_m"].items():
        lat = float(key.split("N")[0])
        if lat >= 3:
            plotlib.place_marker(ax, 77.5, lat, f"{abs(depth):,.0f} m deep", color="#9ED6CC", size=14, fontsize=7, dx=0.12, dy=-0.05)
    plotlib.place_marker(ax, 77.5505, 8.078, "Kanyakumari", size=18, fontsize=7, dx=0.12, dy=0.12)
    g = res["glacial_-128m"]
    ax.set_title(f"Kumari Kandam tested: land that is sea today but was dry at the ice-age low (−128 m), in sand.\n"
                 f"{g['land_now_under_sea_km2']:,} km² in all; south of Kanyakumari it reached only to {g['southernmost_land_below_india_lat']:.2f}°N "
                 "before the sea floor drops away (GEBCO 2026)", fontsize=9.5)
    print(plotlib.save(fig, "11_kumari_kandam.png"))


def mascarene_map(rows):
    z, la, lo, _ = load_etopo()
    zz = np.nan_to_num(z, nan=-5000)
    shade = LightSource(azdeg=315, altdeg=40).hillshade(zz, vert_exag=4, dx=1800, dy=1800)
    fig, axes = plt.subplots(1, 2, figsize=(13, 9.5))
    for ax, level, title in ((axes[0], -90.0, "At the Puranic end of Treta (~869 ka): sea level −90 m"), (axes[1], 0.0, "Today")):
        rel = zz - level
        land = plotlib.LAND(np.clip(rel / 2500, 0, 1))[..., :3]
        sea = plotlib.SEA(np.clip(1 - rel / -5000, 0, 1))[..., :3]
        rgb = np.where((rel > 0)[..., None], land, sea) * (0.55 + 0.45 * shade[..., None])
        ax.imshow(np.clip(rgb, 0, 1), extent=[lo[0], lo[-1], la[-1], la[0]], origin="upper")
        ax.contour(lo, la, zz, levels=[0.0], colors="black", linewidths=0.4)
        ax.set_aspect(1 / np.cos(np.radians(-14)))
        ax.set_title(title, fontsize=10)
        for r in rows:
            if not r.get("centroid"):
                continue
            a = r[f"land_{'treta_-90m' if level < 0 else 'today'}_km2"]
            label = f"{r['name']}\n{a:,.0f} km²" if level < 0 else r["name"]
            plotlib.place_marker(ax, r["centroid"][1], r["centroid"][0], label, size=14, fontsize=7, dx=0.15, dy=0.1, color="#B7791F")
    fig.suptitle("Mauritius and the Mascarene banks (NOAA ETOPO 2022, 1′): the banks were large islands in glacial times; "
                 "Mauritius and Réunion barely change", fontsize=10)
    fig.tight_layout()
    print(plotlib.save(fig, "10_mascarenes_mauritius.png"))


if __name__ == "__main__":
    res = json.loads((DATA / "lemuria_mauritius.json").read_text())
    kumari_kandam_map(res["kumari_kandam"])
    mascarene_map(res["mascarenes"])
