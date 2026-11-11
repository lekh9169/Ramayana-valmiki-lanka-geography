"""Compare Valmiki's stated distances with GEBCO/real geometry; derive the implied yojana."""
import json
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parents[1] / "data"
R = 6371.0088


def hav(a, b):
    (la1, lo1), (la2, lo2) = a, b
    p1, p2 = np.radians(la1), np.radians(la2)
    h = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lo2 - lo1) / 2) ** 2
    return float(2 * R * np.arcsin(np.sqrt(h)))


def bearing(a, b):
    (la1, lo1), (la2, lo2) = map(lambda x: (np.radians(x[0]), np.radians(x[1])), (a, b))
    y = np.sin(lo2 - lo1) * np.cos(la2)
    x = np.cos(la1) * np.sin(la2) - np.sin(la1) * np.cos(la2) * np.cos(lo2 - lo1)
    return float(np.degrees(np.arctan2(y, x)) % 360)


def main():
    places = {p["id"]: p for p in json.loads((DATA / "places.json").read_text(encoding="utf-8"))}
    terrain = json.loads((DATA / "terrain.json").read_text())
    shape = json.loads((DATA / "setu_shape.json").read_text())
    pt = lambda k: (places[k]["lat"], places[k]["lon"])  # noqa: E731
    rows = []

    def row(clue, ref, stated, unit_count, unit, km):
        rows.append({"clue": clue, "ref": ref, "stated": stated, "measured_km": round(km, 1),
                     "implied_km_per_unit": round(km / unit_count, 2), "unit": unit})

    row("Prayaga to Chitrakuta", "2.54.28 (CE 2.48.25)", "10 krosha", 10, "krosha", hav(pt("prayaga"), pt("chitrakuta")))
    row("Agastya's ashram (Akole) to Panchavati", "3.13.13 (CE 3.12.13)", "2 yojanas", 2, "yojana",
        hav(pt("agastya_ashram"), pt("panchavati")))
    row("Mahendragiri to the Sri Lankan coast (Hanuman's leap)", "4.58.20; 5.1.200 (CE 4.57.20; 5.1.182)",
        "100 yojanas", 100, "yojana", terrain["launch_to_srilanka"]["Mahendragiri summit"]["coast_at_0m"]["distance_km"])
    row("Setu: Dhanushkodi tip to Mannar island", "6.22.74 (CE 6.15.20)", "100 yojanas long", 100, "yojana",
        terrain["launch_to_srilanka"]["Dhanushkodi / Arichal Munai"]["coast_at_0m"]["distance_km"])
    w4 = next(s for s in shape if s["depth_cutoff_m"] == 4)
    row("Setu width (shoal at the -4 m isobath)", "6.22.74 (CE 6.15.20)", "10 yojanas wide", 10, "yojana",
        w4["mean_width_km"])
    row("Length of the island of Lanka (Sri Lanka, Point Pedro to Dondra Head)", "4.41.24 (CE 4.40.24)",
        "100 yojanas long", 100, "yojana", hav((9.8350, 80.2125), (5.9230, 80.5890)))
    bear = bearing(pt("pampa"), pt("rishyamuka"))
    out = {"distances": rows,
           "rishyamuka_bearing_from_pampa_deg": round(bear, 0),
           "rishyamuka_note": "Text: Rishyamuka is 'purastat' (in front of / east of) Pampa (3.73.31, CE 3.69.24)"}
    for r in rows:
        print(f"{r['clue']:<70} stated {r['stated']:<17} measured {r['measured_km']:7.1f} km -> "
              f"{r['implied_km_per_unit']:6.2f} km per {r['unit']}")
    print(f"Rishyamuka bearing from Pampa Sarovar: {bear:.0f} deg")
    (DATA / "text_distances.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
