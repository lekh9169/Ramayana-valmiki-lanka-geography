"""Export places.json (+ computed paleo fields) to GeoJSON, KML (Google Earth) and CSV."""
import csv
import json
from pathlib import Path
from xml.sax.saxutils import escape

DATA = Path(__file__).resolve().parents[1] / "data"
COLORS = {"high": "ff2828d6", "medium": "ff007ff7", "low": "ffbf2c7b"}  # KML aabbggrr


def main():
    places = json.loads((DATA / "places_computed.json").read_text(encoding="utf-8"))
    features = []
    for p in places:
        if p["lat"] is None:
            continue
        props = {k: v for k, v in p.items() if k not in ("lat", "lon")}
        features.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [p["lon"], p["lat"]]},
                         "properties": props})
        for alt in p.get("alternatives", []):
            features.append({"type": "Feature",
                             "geometry": {"type": "Point", "coordinates": [alt["lon"], alt["lat"]]},
                             "properties": {"id": p["id"] + "_alt", "name": f"{p['name']} — alternative: {alt['name']}",
                                            "note": alt.get("note", ""), "confidence": "low", "alternative": True}})
    (DATA / "valmiki_places.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": features},
                                                            indent=1, ensure_ascii=False), encoding="utf-8")

    styles = "".join(f'<Style id="{k}"><IconStyle><color>{v}</color><scale>1.0</scale>'
                     f'<Icon><href>http://maps.google.com/mapfiles/kml/paddle/wht-circle.png</href></Icon>'
                     f'</IconStyle></Style>' for k, v in COLORS.items())
    marks = []
    for f in features:
        pr = f["properties"]
        lon, lat = f["geometry"]["coordinates"]
        desc = "<br/>".join(f"<b>{escape(str(k))}</b>: {escape(str(v))}" for k, v in pr.items()
                            if k not in ("id",) and v not in (None, "", []))
        marks.append(f"<Placemark><name>{escape(pr['name'])}</name><styleUrl>#{pr.get('confidence', 'low')}</styleUrl>"
                     f"<description><![CDATA[{desc}]]></description>"
                     f"<Point><coordinates>{lon:.5f},{lat:.5f},0</coordinates></Point></Placemark>")
    route = sorted((p for p in places if p.get("route_order")), key=lambda p: p["route_order"])
    line = " ".join(f"{p['lon']:.5f},{p['lat']:.5f},0" for p in route)
    kml = ('<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document>'
           "<name>Valmiki Ramayana places (data-driven identification)</name>" + styles +
           "".join(marks) +
           '<Placemark><name>Narrative route (Ayodhya to Lanka)</name><Style><LineStyle><color>ff2828d6</color>'
           f'<width>2</width></LineStyle></Style><LineString><tessellate>1</tessellate><coordinates>{line}'
           "</coordinates></LineString></Placemark></Document></kml>")
    (DATA / "valmiki_places.kml").write_text(kml, encoding="utf-8")

    cols = ["id", "name", "sanskrit", "identification", "lat", "lon", "confidence", "valmiki_refs",
            "text_clue", "gebco_elev_m", "plate_velocity_mm_yr", "tectonic_shift_m_since_epoch", "epoch_lat", "epoch_lon", "paleo_note", "coord_source"]
    with open(DATA / "valmiki_places.csv", "w", newline="", encoding="utf-8-sig") as handle:
        w = csv.DictWriter(handle, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for p in places:
            w.writerow({k: p.get(k, "") for k in cols})
    print(f"exported {len(features)} features")


if __name__ == "__main__":
    main()
