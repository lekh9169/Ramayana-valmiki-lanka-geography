"""Treta-edition exports: KML (places, shore points of the time, -90 m coastline) and CSV."""
import csv
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
import gebco  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"
STYLE = {"high": "ff2828d6", "medium": "ff007ff7", "low": "ffbf2c7b", "shore": "ff0bbeff"}


def coast_lines(level, boxes, min_pts=25, every=3):
    lines = []
    g = gebco.load_grid()
    for box in boxes:
        e, la, lo = gebco.window(g, *box)
        e, la, lo = e[::2, ::2], la[::2], lo[::2]
        cs = plt.contour(lo, la, np.nan_to_num(e, nan=-9999), levels=[level])
        for seg in cs.allsegs[0]:
            if len(seg) >= min_pts:
                lines.append(seg[::every])
        plt.close("all")
    return lines


def main():
    geo = json.loads((DATA / "treta_geo.json").read_text(encoding="utf-8"))
    places = {p["id"]: p for p in json.loads((DATA / "places_computed.json").read_text(encoding="utf-8"))}
    level = geo["sea_level_m"]["treta_end"]
    styles = "".join(f'<Style id="{k}"><IconStyle><color>{v}</color><Icon><href>http://maps.google.com/mapfiles/kml/paddle/wht-circle.png'
                     f'</href></Icon></IconStyle><LineStyle><color>{v}</color><width>1.5</width></LineStyle></Style>' for k, v in STYLE.items())
    marks, rows = [], []
    for r in geo["places"]:
        p = places.get(r["id"])
        if not p or p["lat"] is None:
            continue
        shore = r.get("treta_shore")
        desc = {"Identification": p["identification"], "Valmiki reference": p["valmiki_refs"],
                "Today": f"{p['lat']:.4f}, {p['lon']:.4f}",
                "On the plate at Rama's birth (~878,142 BCE)": (", ".join(f"{v:.4f}" for v in r["position_birth"])
                                                                if r["position_birth"] else "Somali plate (India pole not applicable)"),
                "On the plate at the end of Treta (867,102 BCE)": (", ".join(f"{v:.4f}" for v in r["position_treta_end"])
                                                                   if r["position_treta_end"] else ""),
                "Height above the Treta sea (m)": r.get("elevation_above_treta_sea_m"),
                "Shore at the Treta sea level": (f"{shore['km_to_sea']} km away at {shore['nearest_sea'][0]:.4f}, "
                                                 f"{shore['nearest_sea'][1]:.4f}") if shore else "",
                "Confidence": p["confidence"]}
        html = "<br/>".join(f"<b>{escape(k)}</b>: {escape(str(v))}" for k, v in desc.items() if v not in ("", None))
        marks.append(f"<Placemark><name>{escape(p['name'])}</name><styleUrl>#{p['confidence']}</styleUrl>"
                     f"<description><![CDATA[{html}]]></description><Point><coordinates>{p['lon']:.5f},{p['lat']:.5f},0"
                     f"</coordinates></Point></Placemark>")
        if shore:
            la, lo = shore["nearest_sea"]
            marks.append(f"<Placemark><name>Treta shore nearest {escape(p['short'])}</name><styleUrl>#shore</styleUrl>"
                         f"<description>Sea level {level:.0f} m (~869 ka)</description><Point><coordinates>{lo:.5f},{la:.5f},0"
                         f"</coordinates></Point></Placemark>")
        rows.append({"id": p["id"], "name": p["name"], "lat_today": p["lat"], "lon_today": p["lon"],
                     "lat_birth_plate": (r["position_birth"] or ["", ""])[0], "lon_birth_plate": (r["position_birth"] or ["", ""])[1],
                     "lat_treta_end_plate": (r["position_treta_end"] or ["", ""])[0],
                     "lon_treta_end_plate": (r["position_treta_end"] or ["", ""])[1],
                     "height_above_treta_sea_m": r.get("elevation_above_treta_sea_m"),
                     "treta_shore_km": shore["km_to_sea"] if shore else "",
                     "treta_shore_lat": shore["nearest_sea"][0] if shore else "", "treta_shore_lon": shore["nearest_sea"][1] if shore else "",
                     "confidence": p["confidence"], "valmiki_refs": p["valmiki_refs"]})
    lines = coast_lines(level, [(5.0, 11.5, 76.0, 82.6), (-8.5, 8.0, 70.5, 74.2)])
    coast = "".join(f"<Placemark><name>Coastline at {level:.0f} m (Treta)</name><styleUrl>#shore</styleUrl><LineString><tessellate>1</tessellate>"
                    f"<coordinates>{' '.join(f'{x:.4f},{y:.4f},0' for x, y in seg)}</coordinates></LineString></Placemark>"
                    for seg in lines)
    kml = ('<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document>'
           "<name>Valmiki Ramayana places: Treta-Yuga edition (~869,000 years ago)</name>" + styles +
           "<Folder><name>Places (today's ground, with Treta-epoch details)</name>" + "".join(marks) + "</Folder>"
           f"<Folder><name>Coastline at the Treta sea level ({level:.0f} m)</name>{coast}</Folder></Document></kml>")
    (DATA / "valmiki_places_treta.kml").write_text(kml, encoding="utf-8")
    with open(DATA / "valmiki_places_treta.csv", "w", newline="", encoding="utf-8-sig") as handle:
        w = csv.DictWriter(handle, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"KML: {len(marks)} placemarks, {len(lines)} coastline segments; CSV: {len(rows)} rows")


if __name__ == "__main__":
    main()
