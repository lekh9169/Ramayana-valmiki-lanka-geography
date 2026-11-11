"""Paleo-coastline panels for the Palk Strait / Gulf of Mannar at key epochs.

Land at epoch t = GEBCO elevation > RSL(t). Epochs combine the sea-level history with the
astronomical candidates from astro_search.py / astro_checks.py.
"""
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
import plotlib  # noqa: E402
import rsl  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"
BOX = (7.6, 10.6, 77.6, 81.2)


def epochs():
    eps = json.loads((DATA / "epochs.json").read_text())
    return [(e["label"], e["age_ka"]) for e in eps if e.get("panel")]


def main():
    panels = epochs()
    cols = 4
    rows = int(np.ceil(len(panels) / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(4.2 * cols, 4.3 * rows))
    sill = json.loads((DATA / "sill_results.json").read_text())["sill_all_m"]
    for ax, (label, age) in zip(axes.flat, panels):
        level, sigma = rsl.rsl_at(age)
        elev, lats, lons = plotlib.relief(ax, *BOX, sea_level=level, step=2, land_max=1500, sea_min=-1500)
        plotlib.coastline(ax, elev, lats, lons, 0.0, colors="black", linewidths=0.5, linestyles=":")
        state = "LAND BRIDGE" if level < sill else "island (strait open)"
        when = "today" if age <= 0 else f"{age:.1f} ka BP"
        ax.set_title(f"{label}\n{when} · RSL {level:+.1f} ± {sigma:.1f} m · {state}", fontsize=8)
        ax.tick_params(labelsize=6)
        for name, lat, lon in (("Rameswaram", 9.288, 79.313), ("Talaimannar", 9.09, 79.72),
                               ("Jaffna", 9.66, 80.01), ("Korkai", 8.633, 78.083)):
            ax.scatter([lon], [lat], s=6, c="#d62828", zorder=5)
    for ax in list(axes.flat)[len(panels):]:
        ax.axis("off")
    fig.suptitle("India – Sri Lanka coastline through time (GEBCO 2026 bathymetry flooded to the relative "
                 f"sea level of each epoch; dotted = present coast; land-bridge sill {sill:.1f} m)", fontsize=10)
    fig.tight_layout()
    print(plotlib.save(fig, "02_palk_strait_paleocoast.png"))


if __name__ == "__main__":
    main()
