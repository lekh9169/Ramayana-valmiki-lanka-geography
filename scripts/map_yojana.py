"""Map: where '100 yojanas' south of the Mahendra launch point falls, for each yojana value,
over present and Last-Glacial-Maximum coastlines (GEBCO 2026)."""
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
import plotlib  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"
R = 6371.0088
# km per yojana: setu-calibrated from GEBCO (gap 32-46 km / 100); textual-astronomical definitions
YOJANA = [
    ("Setu-calibrated (GEBCO gap / 100)", 0.46, "#ffbe0b"),
    ("Surya Siddhanta (Earth dia. 1600 y.)", 12742 / 1600, "#fb5607"),
    ("Aryabhatiya (Earth dia. 1050 y.)", 12742 / 1050, "#ff006e"),
    ("Arthashastra-type long yojana (~14.6 km)", 14.6, "#8338ec"),
]


def circle(lat, lon, radius_km, n=720):
    brg = np.linspace(0, 2 * np.pi, n)
    d = radius_km / R
    p1, l1 = np.radians(lat), np.radians(lon)
    p2 = np.arcsin(np.sin(p1) * np.cos(d) + np.cos(p1) * np.sin(d) * np.cos(brg))
    l2 = l1 + np.arctan2(np.sin(brg) * np.sin(d) * np.cos(p1), np.cos(d) - np.sin(p1) * np.sin(p2))
    return np.degrees(p2), np.degrees(l2)


def main():
    terrain = json.loads((DATA / "terrain.json").read_text())
    m = terrain["mahendragiri_summit_gebco"]
    fig, ax = plt.subplots(figsize=(9, 10))
    elev, lats, lons = plotlib.relief(ax, -12, 16, 64, 92, sea_level=0, step=8)
    plotlib.coastline(ax, elev, lats, lons, -120, colors="#e63946", linewidths=0.7, linestyles="--")
    for label, km, color in YOJANA:
        la, lo = circle(m["lat"], m["lon"], 100 * km)
        ax.plot(lo, la, color=color, lw=1.6, label=f"100 yojanas = {100 * km:,.0f} km — {label}")
    plotlib.place_marker(ax, m["lon"], m["lat"], "Mahendragiri", dx=-4.2, dy=0.4)
    ss = terrain["surya_siddhanta_lanka"]
    plotlib.place_marker(ax, ss["lon"], ss["lat"], "Surya Siddhanta 'Lanka'\n(0°, Ujjain meridian)\n"
                         f"depth {ss['depth_m']:.0f} m", color="#ffbe0b", marker="*", size=120, dx=0.5, dy=-2.2)
    ax.axhline(0, color="white", lw=0.5, alpha=0.6)
    ax.plot([], [], color="#e63946", lw=0.7, ls="--", label="LGM coastline (-120 m, ~20 ka)")
    ax.legend(loc="lower left", fontsize=7, framealpha=0.9)
    ax.set_title("Where does '100 yojanas' from Mahendra land? (GEBCO 2026)", fontsize=11)
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    print(plotlib.save(fig, "04_hundred_yojana_arcs.png"))


if __name__ == "__main__":
    main()
