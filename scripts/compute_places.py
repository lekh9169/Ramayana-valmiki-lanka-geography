"""Attach computed fields to every place in places.json:

* GEBCO 2026 elevation at the point
* plate-motion shift since the reference epoch (India plate, NNR frame) and the epoch position
* for coastal places: distance to the open sea at present and at each reference epoch's sea level
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import coastal  # noqa: E402
import gebco  # noqa: E402
import rsl  # noqa: E402
import tectonics  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"


def main():
    places = json.loads((DATA / "places.json").read_text(encoding="utf-8"))
    ref_epochs = [e for e in json.loads((DATA / "epochs.json").read_text())
                  if e["kind"] in ("astro_strict", "philology")]
    g = gebco.load_grid()
    for p in places:
        if p["lat"] is None:
            continue
        z = gebco.sample(g, p["lat"], p["lon"])
        p["gebco_elev_m"] = None if z != z else z          # NaN: outside the GEBCO subset (Mascarenes: see ETOPO)
        years = (2026 - 1950) + max(e["age_ka"] for e in ref_epochs) * 1000
        lat0, lon0 = tectonics.position_at(p["lat"], p["lon"], years)
        ve, vn, speed, az = tectonics.velocity_mm_yr(p["lat"], p["lon"])
        p["plate_velocity_mm_yr"] = round(speed, 1)
        p["plate_velocity_azimuth_deg"] = round(az)
        p["tectonic_shift_m_since_epoch"] = round(speed * years / 1000)
        p["position_at_oldest_reference_epoch_nnr"] = [round(lat0, 5), round(lon0, 5)]
        if p.get("coastal"):
            p["sea_distance_km"] = {}
            for e in ref_epochs + [{"short": "present", "age_ka": -0.076}]:
                level, sigma = rsl.rsl_at(e["age_ka"])
                d = coastal.distance_to_sea(p["lat"], p["lon"], level)
                p["sea_distance_km"][e["short"]] = None if d is None else {
                    "rsl_m": round(level, 1), "km": d["km"], "submerged": bool(d["submerged"])}
    (DATA / "places_computed.json").write_text(json.dumps(places, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"computed {len(places)} places")


if __name__ == "__main__":
    main()
