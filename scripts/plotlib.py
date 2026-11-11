"""Shared plotting helpers: shaded relief from GEBCO, coastlines at a chosen sea level."""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, LightSource

sys.path.insert(0, str(Path(__file__).parent))
import gebco  # noqa: E402

MAPS = Path(__file__).resolve().parents[1] / "maps"
_GRID = None


def grid():
    global _GRID
    if _GRID is None:
        _GRID = gebco.load_grid()
    return _GRID


SEA = LinearSegmentedColormap.from_list("sea", ["#0b2545", "#13315c", "#1d4e89", "#4f86c6", "#a7c5eb", "#dcebf7"])
LAND = LinearSegmentedColormap.from_list("land", ["#5b8c5a", "#a3b86c", "#d9c88c", "#b08d57", "#8c6e54", "#f2f2f2"])


def relief(ax, south, north, west, east, sea_level=0.0, step=1, land_max=2500, sea_min=-4500):
    """Draw hillshaded relief where land/sea is decided against `sea_level` (m, present datum)."""
    elev, lats, lons = gebco.window(grid(), south, north, west, east)
    elev = elev[::step, ::step]
    lats, lons = lats[::step], lons[::step]
    rel = elev - sea_level
    ls = LightSource(azdeg=315, altdeg=40)
    dx = np.radians(gebco.CELL * step) * 6371000 * np.cos(np.radians(np.mean(lats)))
    dy = np.radians(gebco.CELL * step) * 6371000
    shade = ls.hillshade(np.nan_to_num(elev), vert_exag=4, dx=dx, dy=dy)
    land_rgb = LAND(np.clip(rel / land_max, 0, 1))[..., :3]
    sea_rgb = SEA(np.clip(1 - rel / sea_min, 0, 1))[..., :3]
    rgb = np.where((rel > 0)[..., None], land_rgb, sea_rgb)
    rgb = rgb * (0.55 + 0.45 * shade[..., None])
    extent = [lons[0] - gebco.CELL * step / 2, lons[-1] + gebco.CELL * step / 2,
              lats[-1] - gebco.CELL * step / 2, lats[0] + gebco.CELL * step / 2]
    ax.imshow(np.clip(rgb, 0, 1), extent=extent, origin="upper", interpolation="bilinear")
    ax.set_xlim(west, east)
    ax.set_ylim(south, north)
    ax.set_aspect(1 / np.cos(np.radians((south + north) / 2)))
    return elev, lats, lons


def coastline(ax, elev, lats, lons, level, **kw):
    ax.contour(lons, lats, elev, levels=[level], **kw)


def place_marker(ax, lon, lat, label, color="#d62828", size=28, fontsize=7, dx=0.05, dy=0.05, marker="o"):
    ax.scatter([lon], [lat], s=size, c=color, edgecolors="white", linewidths=0.6, zorder=5, marker=marker)
    if label:
        ax.annotate(label, (lon, lat), xytext=(lon + dx, lat + dy), fontsize=fontsize, color="black",
                    zorder=6, bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.75))


def save(fig, name):
    MAPS.mkdir(exist_ok=True)
    path = MAPS / name
    fig.savefig(path, dpi=170, bbox_inches="tight")
    plt.close(fig)
    return path
