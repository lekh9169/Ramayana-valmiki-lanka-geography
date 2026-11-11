"""Map: the equatorial Chagos-Laccadive ridge at the sea level of the Puranic end of Treta (~869 ka)."""
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
import plotlib  # noqa: E402
from map_yojana import circle  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"


def main():
    d = json.loads((DATA / "deep_time.json").read_text())
    level = d["sea_level"]["at_treta_end_m"]
    fig, ax = plt.subplots(figsize=(9.5, 11))
    elev, lats, lons = plotlib.relief(ax, -2.5, 12.5, 69.5, 82.5, sea_level=level, step=4, land_max=2500)
    plotlib.coastline(ax, elev, lats, lons, 0.0, colors="black", linewidths=0.4, linestyles=":")
    # equator today and at the Treta epoch (in present-day plate coordinates)
    ax.axhline(0, color="white", lw=0.8, ls="--")
    eq = np.array(d["plate"]["equator_then_in_present_coords"])
    ax.plot(eq[:, 1], eq[:, 0], color="#ffbe0b", lw=1.2, label="Equator ~869 ka (in today's coordinates)")
    ax.axvline(75.7665, color="#ffbe0b", lw=0.8, ls=":", label="Ujjain meridian (75.77°E)")
    p = d["plate"]["equator_x_ujjain_meridian_then_in_present_coords"]
    plotlib.place_marker(ax, p[1], p[0], f"Equator x Ujjain meridian\nat ~869 ka: {d['plate']['depth_there_m']:.0f} m deep",
                         color="#ffbe0b", marker="*", size=140, dx=0.3, dy=-1.1)
    for km, color in ((8.0, "#fb5607"), (9.5, "#ff006e"), (11.0, "#8338ec")):
        la, lo = circle(8.3883, 77.5214, 100 * km)
        ax.plot(lo, la, color=color, lw=1.1, label=f"100 yojanas from Mahendragiri at {km:g} km/yojana")
    sills = d["sills_to_india_m"]
    labels = {"Huvadhu atoll (equator, N)": (0.519, 73.283, -2.9, 0.25), "Fuvahmulah (equator)": (-0.307, 73.433, 0.25, -0.35),
              "Addu atoll (equator, S)": (-0.636, 73.161, -2.6, -0.45), "Male": (4.175, 73.509, 0.3, 0.1),
              "Lakshadweep (Kavaratti)": (10.565, 72.642, 0.3, 0.1)}
    for name, (la, lo, dx, dy) in labels.items():
        plotlib.place_marker(ax, lo, la, f"{name.split(' (')[0]}\nsill to India {sills[name]:,} m",
                             color="#7b2cbf", size=26, fontsize=6.5, dx=dx, dy=dy)
    plotlib.place_marker(ax, 77.5214, 8.3883, "Mahendragiri", size=26, fontsize=6.5, dx=0.25, dy=0.15)
    plotlib.place_marker(ax, 80.77, 7.87, "Sri Lanka (joined to India\nat this sea level)", size=26, fontsize=6.5,
                         dx=0.3, dy=0.1)
    ax.legend(loc="upper right", fontsize=6.5, framealpha=0.9)
    ax.set_title(f"Treta Yuga test (Puranic end of Treta, ~869 ka): land at sea level {level:.0f} m "
                 "(Bintanja & van de Wal 2008)\nGEBCO 2026 relief; dotted = present coastline", fontsize=9.5)
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    print(plotlib.save(fig, "07_treta_equatorial_test.png"))


if __name__ == "__main__":
    main()
