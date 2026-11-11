"""Treta-edition figures: route and the south at the Treta sea level, and the Treta timeline chart."""
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
import deep_sealevel  # noqa: E402
import plotlib  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"


def route_and_south(geo, places):
    level = geo["sea_level_m"]["treta_end"]
    pid = {p["id"]: p for p in places}
    fig, ax = plt.subplots(figsize=(9, 11.5))
    elev, lats, lons = plotlib.relief(ax, 5.0, 29.5, 70.5, 86.5, sea_level=level, step=6, land_max=3500)
    plotlib.coastline(ax, elev, lats, lons, 0.0, colors="black", linewidths=0.4, linestyles=":")
    route = sorted((p for p in places if p.get("route_order") and p["lat"] is not None), key=lambda p: p["route_order"])
    ax.plot([p["lon"] for p in route], [p["lat"] for p in route], color="#d62828", lw=1.3, alpha=0.8, zorder=4)
    for p in places:
        if p.get("on_overview") and p["lat"] is not None:
            plotlib.place_marker(ax, p["lon"], p["lat"], p["short"], size=22, fontsize=6.5,
                                 dx=p.get("label_dx", 0.25), dy=p.get("label_dy", 0.1))
    ax.set_title(f"Treta edition: the route on land as it stood at the Puranic end of Treta (~869 ka, sea level {level:.0f} m)\n"
                 "GEBCO 2026 relief; dotted = today's coast. India and Sri Lanka are one landmass.", fontsize=9.5)
    print(plotlib.save(fig, "T1_route_treta.png"))

    fig, ax = plt.subplots(figsize=(10, 8.5))
    elev, lats, lons = plotlib.relief(ax, 6.0, 10.6, 76.2, 82.2, sea_level=level, step=1, land_max=2400, sea_min=-4000)
    plotlib.coastline(ax, elev, lats, lons, 0.0, colors="black", linewidths=0.5, linestyles=":")
    rows = {r["id"]: r for r in geo["places"]}
    for pid_, label in (("tamraparni", "Tamraparni mouth"), ("ocean_shore", "Southern shore (beyond Kanyakumari)"),
                        ("setu_start", "Sea nearest Dhanushkodi"), ("mahendra", "Sea nearest Mahendragiri")):
        r = rows.get(pid_)
        if r and "treta_shore" in r:
            la, lo = r["treta_shore"]["nearest_sea"]
            plotlib.place_marker(ax, lo, la, f"{label} then\n{la:.3f}°N {lo:.3f}°E", color="#ffbe0b", marker="*",
                                 size=90, fontsize=6.5, dx=0.08, dy=-0.25)
            p = pid[pid_]
            ax.plot([p["lon"], lo], [p["lat"], la], color="#ffbe0b", lw=0.8, ls="--")
            plotlib.place_marker(ax, p["lon"], p["lat"], p["short"], size=16, fontsize=6.5, dx=0.06, dy=0.06)
    ax.set_title(f"The south at the Treta sea level ({level:.0f} m): Palk Bay is dry land, the Gulf of Mannar is open sea.\n"
                 "Stars = where the shore lay then; dotted = today's coast", fontsize=9.5)
    print(plotlib.save(fig, "T2_south_treta.png"))


def timeline(sky, geo):
    age, sl = deep_sealevel.bintanja()
    w = (age >= 860) & (age <= 890)
    lahiri = sky["anchors"]["Spica = 180° (Lahiri / Chitra-paksha)"]
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(12, 7.5), sharex=True, gridspec_kw={"height_ratios": [1.3, 1]})
    ax.plot(age[w], sl[w], color="#1d4e89", lw=2, label="Global sea level (Bintanja & van de Wal 2008)")
    ax.axhline(-3, color="#e63946", ls="--", lw=1, label="Adam's Bridge sand-crest sill (−3 m)")
    ax.axhline(-10, color="#f4a261", ls=":", lw=1, label="Adam's Bridge rock sill (−10 m)")
    treta_ka = (sky["treta_end_bce"] + 1950) / 1000
    for a in (ax, ax2):
        a.axvline(treta_ka, color="black", lw=1.2)
        a.axvspan((sky["treta_end_bce"] + 11_040 + 1950) / 1000 - 0.3, (sky["treta_end_bce"] + 11_040 + 1950) / 1000 + 0.3,
                  color="#e85d04", alpha=0.15)
        for wnd in lahiri["strict_windows"]:
            a.axvline((wnd["start_bce"] + 1950) / 1000, color="#d62828", lw=1.4, alpha=0.9)
        for wnd in lahiri["sun_in_aries_windows"]:
            a.axvline((wnd["start_bce"] + 1950) / 1000, color="#f77f00", lw=1.0, ls="--", alpha=0.9)
    ax.text(treta_ka, -2, " end of Treta\n (867,102 BCE)", fontsize=7, va="top")
    ax.set_ylabel("Sea level (m)")
    ax.set_ylim(-115, 5)
    ax.legend(fontsize=7, loc="lower left")
    ax.set_title("Treta window: sea level, Rama's-birth sky windows (red = strict reading, orange dashed = 'Sun in Aries' reading; "
                 "Spica zodiac) and the season of Chaitra", fontsize=9)
    ys = [(s["year_bce"] + 1950) / 1000 for s in lahiri["chaitra_seasons"]]
    trop = [s["chaitra_tropical_sun"] for s in lahiri["chaitra_seasons"]]
    ax2.plot(ys, trop, "o-", color="#2a9d8f", ms=3, label="Tropical longitude of the Sun in mid-Chaitra")
    for lo, hi, name in ((330, 360, "Vasanta"), (0, 30, "Vasanta"), (270, 330, "Shishira"), (210, 270, "Hemanta"),
                         (150, 210, "Sharad"), (90, 150, "Varsha"), (30, 90, "Grishma")):
        ax2.axhspan(lo, hi, color="#2a9d8f" if name == "Vasanta" else "#cccccc", alpha=0.12)
        ax2.text(ys[-1], (lo + hi) / 2, f" {name}", fontsize=6.5, va="center")
    ax2.set_ylim(0, 360)
    ax2.set_ylabel("Tropical Sun (°)")
    ax2.set_xlabel("Age (thousand years before 1950)")
    ax2.set_xlim(888, 862)
    ax2.legend(fontsize=7, loc="upper right")
    fig.tight_layout()
    print(plotlib.save(fig, "T3_treta_timeline.png"))


if __name__ == "__main__":
    g = json.loads((DATA / "treta_geo.json").read_text(encoding="utf-8"))
    pl = json.loads((DATA / "places.json").read_text(encoding="utf-8"))
    route_and_south(g, pl)
    timeline(json.loads((DATA / "treta_sky.json").read_text()), g)
