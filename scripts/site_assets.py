"""Assets for the website: the hero relief (elevation packed into a PNG for in-browser flooding),
the sea-level -> date table it uses, and one GeoJSON with every map layer of both editions."""
import json
import sys
from pathlib import Path

import numpy as np
from matplotlib.colors import LightSource
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import deep_sealevel  # noqa: E402
import gebco  # noqa: E402
import rsl  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
DATA = ROOT / "data"
HERO_BOX = (5.7, 10.9, 77.0, 82.2)   # south, north, west, east: Kanyakumari, Palk Strait, all of Sri Lanka
HERO_STEP = 2                          # 30 arc-seconds


def hero_png():
    e, la, lo = gebco.window(gebco.load_grid(), *HERO_BOX)
    e = np.nan_to_num(e[::HERO_STEP, ::HERO_STEP], nan=-4000).astype(np.float64)
    la, lo = la[::HERO_STEP], lo[::HERO_STEP]
    shade = LightSource(azdeg=315, altdeg=35).hillshade(e, vert_exag=6, dx=900, dy=900)
    packed = np.clip(np.round(e), -6000, 6000).astype(np.int32) + 32768
    rgb = np.dstack([(packed >> 8).astype(np.uint8), (packed & 255).astype(np.uint8),
                     np.round(shade * 255).astype(np.uint8)])
    ASSETS.mkdir(exist_ok=True)
    Image.fromarray(rgb, "RGB").save(ASSETS / "palk_relief.png", optimize=True)
    meta = {"south": float(la[-1] - gebco.CELL * HERO_STEP / 2), "north": float(la[0] + gebco.CELL * HERO_STEP / 2),
            "west": float(lo[0] - gebco.CELL * HERO_STEP / 2), "east": float(lo[-1] + gebco.CELL * HERO_STEP / 2),
            "width": int(e.shape[1]), "height": int(e.shape[0])}
    print("hero relief", e.shape, meta)
    return meta


def sea_level_table():
    """For each sea level, when the sea last stood that low (regional Holocene curve) or, deeper than the
    Holocene record, the glacial; plus the Treta-epoch level for the Puranic end of Treta."""
    rows = []
    for level in np.arange(2.0, -130.5, -0.5):
        age = rsl.age_when_level_crossed(float(level))["central_ka"] if level < 0 else None
        rows.append({"level": float(level), "year": None if age is None else rsl.bp_to_year(age)})
    age, sl = deep_sealevel.bintanja()
    treta = float(np.interp((867_102 + 1950) / 1000.0, age, sl))
    return {"rows": rows, "treta_level": round(treta, 1), "treta_end_bce": 867_102}


def map_layers():
    places = json.loads((DATA / "places_computed.json").read_text(encoding="utf-8"))
    geo = json.loads((DATA / "treta_geo.json").read_text(encoding="utf-8"))
    g = {p["id"]: p for p in geo["places"]}
    feats = []
    for p in places:
        if p["lat"] is None:
            continue
        if p.get("treta") or p.get("drowned"):
            layer = "treta"
        elif p.get("rejected"):
            layer = "rejected"
        elif p.get("tradition"):
            layer = "tradition"
        else:
            layer = "valmiki"
        r = g.get(p["id"], {})
        feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [p["lon"], p["lat"]]},
                      "properties": {"id": p["id"], "name": p["name"], "layer": layer, "confidence": p["confidence"],
                                     "identification": p["identification"], "refs": p["valmiki_refs"], "clue": p["text_clue"],
                                     "sanskrit": p.get("sanskrit", ""), "route_order": p.get("route_order"),
                                     "paleo_note": p.get("paleo_note", ""),
                                     "plate_birth": r.get("position_birth"),
                                     "treta_shore": r.get("treta_shore")}})
        shore = r.get("treta_shore")
        if shore:
            la, lo = shore["nearest_sea"]
            feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [lo, la]},
                          "properties": {"name": f"Shore at the end of Treta, nearest {p['short']}", "layer": "treta_shore",
                                         "km": shore["km_to_sea"]}})
    # Treta coastline from the KML export (re-trace with the same routine)
    from export_treta import coast_lines
    level = geo["sea_level_m"]["treta_end"]
    for seg in coast_lines(level, [(5.0, 11.5, 76.0, 82.6), (-8.5, 8.0, 70.5, 74.2)]):
        feats.append({"type": "Feature", "geometry": {"type": "LineString", "coordinates": [[round(float(x), 4), round(float(y), 4)] for x, y in seg]},
                      "properties": {"layer": "treta_coast", "name": f"Coastline at {level:.0f} m (end of Treta)"}})
    route = sorted((p for p in places if p.get("route_order") and p["lat"] is not None), key=lambda p: p["route_order"])
    feats.append({"type": "Feature", "geometry": {"type": "LineString", "coordinates": [[p["lon"], p["lat"]] for p in route]},
                  "properties": {"layer": "route", "name": "Narrative route, Ayodhya to Lanka"}})
    (DATA / "map_layers.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False),
                                             encoding="utf-8")
    print("map layers:", len(feats), "features")


if __name__ == "__main__":
    meta = hero_png()
    meta["sea_levels"] = sea_level_table()
    (ASSETS / "hero_meta.json").write_text(json.dumps(meta), encoding="utf-8")
    map_layers()
