"""Sea-level timeline and Adam's Bridge crest profile charts."""
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
import plotlib  # noqa: E402
import rsl  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"


def sea_level_chart():
    age, level, sigma, _ = rsl.load()
    sill = json.loads((DATA / "sill_results.json").read_text())
    epochs = json.loads((DATA / "epochs.json").read_text())
    fig, (ax, axz) = plt.subplots(1, 2, figsize=(13, 5), gridspec_kw={"width_ratios": [1.3, 1]})
    for a, xmax, ymin in ((ax, 21, -135), (axz, 10, -30)):
        a.fill_between(age, level - sigma, level + sigma, color="#4f86c6", alpha=0.25, label="±1σ")
        a.plot(age, level, color="#1d4e89", lw=2, label="Relative sea level, Gulf of Mannar (model)")
        a.axhline(sill["sill_all_m"], color="#e63946", lw=1.2, ls="--",
                  label=f"India–Sri Lanka sill (Adam's Bridge) {sill['sill_all_m']:.1f} m")
        a.axhline(sill["sill_palk_strait_north_corridor_m"], color="#f4a261", lw=1, ls=":",
                  label=f"Northern Palk Strait sill {sill['sill_palk_strait_north_corridor_m']:.1f} m")
        for e in epochs:
            if e.get("chart"):
                a.axvline(e["age_ka"], color=e.get("color", "grey"), lw=1, alpha=0.8)
                if e["age_ka"] <= xmax:
                    a.text(e["age_ka"], ymin + 2, e["short"], rotation=90, fontsize=7, va="bottom", ha="right",
                           color=e.get("color", "grey"))
        a.set_xlim(xmax, 0)
        a.set_ylim(ymin, 6)
        a.set_xlabel("Age (thousand years before 1950)")
        a.set_ylabel("m relative to present sea level")
        a.grid(alpha=0.3)
    ax.legend(fontsize=7, loc="upper left")
    ax.set_title("Sea level since the Last Glacial Maximum", fontsize=10)
    axz.set_title("Zoom: the last 10,000 years", fontsize=10)
    fig.tight_layout()
    print(plotlib.save(fig, "05_sea_level_timeline.png"))


def bridge_profile_chart():
    shape = json.loads((DATA / "setu_shape.json").read_text())
    prof = json.loads((DATA / "setu_crest_profile.json").read_text())
    epochs = json.loads((DATA / "epochs.json").read_text())
    km = np.array([p["km"] for p in prof])
    z = np.array([p["elev_m"] for p in prof])
    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.fill_between(km, -20, z, color="#d9c88c", step="mid")
    ax.plot(km, z, color="#8c6e54", lw=1.2, drawstyle="steps-mid", label="GEBCO crest of the shoal")
    for e in epochs:
        if e.get("profile"):
            level, _ = rsl.rsl_at(e["age_ka"])
            ax.axhline(level, color=e.get("color", "#1d4e89"), lw=1.1, ls="--",
                       label=f"sea level {e['short']}: {level:+.1f} m")
    ax.axhline(0, color="#1d4e89", lw=1.5, label="present sea level")
    ax.set_ylim(-14, 6)
    ax.set_xlim(km.min(), km.max())
    ax.set_xlabel("Distance along the crest from the Rameswaram island shore (km)")
    ax.set_ylabel("Elevation (m)")
    w4 = next(s for s in shape if s["depth_cutoff_m"] == 4)
    ax.set_title(f"Adam's Bridge (Rama Setu) crest profile — gap {w4['gap_length_km']:.0f} km; "
                 f"shoal width at the −4 m isobath {w4['mean_width_km']:.1f} km (L/W ≈ {w4['length_to_width']:.0f}, "
                 "cf. Valmiki's 100 × 10 yojanas)", fontsize=9)
    ax.legend(fontsize=7, loc="lower right", ncol=2)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    print(plotlib.save(fig, "03_adams_bridge_profile.png"))


if __name__ == "__main__":
    sea_level_chart()
    bridge_profile_chart()
