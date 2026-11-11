"""Route overview (Ayodhya -> Lanka) and Sri Lanka detail maps from places.json."""
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
import plotlib  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"


def load_places():
    return [p for p in json.loads((DATA / "places.json").read_text(encoding="utf-8")) if p["lat"] is not None]


def route_map(places):
    fig, ax = plt.subplots(figsize=(9, 11.5))
    plotlib.relief(ax, 5.5, 29.5, 70.5, 86.5, step=6, land_max=3500)
    route = [p for p in places if p.get("route_order")]
    route.sort(key=lambda p: p["route_order"])
    ax.plot([p["lon"] for p in route], [p["lat"] for p in route], color="#d62828", lw=1.3, alpha=0.8, zorder=4)
    for p in places:
        if p.get("on_overview"):
            plotlib.place_marker(ax, p["lon"], p["lat"], p["short"], size=22, fontsize=6.5,
                                 dx=p.get("label_dx", 0.25), dy=p.get("label_dy", 0.1),
                                 color={"high": "#d62828", "medium": "#f77f00", "low": "#7b2cbf"}[p["confidence"]])
    ax.set_title("Places of the Valmiki Ramayana — best-supported identifications on GEBCO 2026 relief\n"
                 "(red = high, orange = medium, purple = low confidence; line = narrative order)", fontsize=10)
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    print(plotlib.save(fig, "01_route_overview.png"))


def lanka_map(places):
    terrain = json.loads((DATA / "terrain.json").read_text())
    fig, ax = plt.subplots(figsize=(9, 10.5))
    plotlib.relief(ax, 5.8, 10.0, 78.8, 82.0, step=1, land_max=2400)
    for p in places:
        if p.get("on_lanka_map"):
            plotlib.place_marker(ax, p["lon"], p["lat"], p["short"], size=24, fontsize=6.5,
                                 dx=p.get("lk_dx", 0.06), dy=p.get("lk_dy", 0.03),
                                 color={"high": "#d62828", "medium": "#f77f00", "low": "#7b2cbf"}[p["confidence"]])
    top = [s for s in terrain["srilanka_summits"] if s["relief_m"] >= 600][:40]
    ax.scatter([s["lon"] for s in top], [s["lat"] for s in top], marker="^", s=14, c="black", zorder=4,
               label="GEBCO summits with ≥600 m local relief")
    ax.legend(loc="lower left", fontsize=7)
    ax.set_title("Lanka: Sri Lankan sites of the Ramayana tradition and major summits (GEBCO 2026)", fontsize=10)
    print(plotlib.save(fig, "06_lanka_detail.png"))


if __name__ == "__main__":
    places = load_places()
    route_map(places)
    lanka_map(places)
