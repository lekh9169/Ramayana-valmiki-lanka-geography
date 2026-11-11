"""Geography of every place at the Puranic end of Treta (~869 ka) and at Rama's birth window (~878 ka).

For each place: position on the plate then (NNR-MORVEL56), and for coastal places the nearest open sea at
the Treta sea level (Bintanja & van de Wal 2008) -- i.e. where the shore actually was. Also: whether Sri
Lanka was an island, the Treta-era southern cape, and the Treta-era mouth of the Tamraparni.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import coastal  # noqa: E402
import deep_sealevel  # noqa: E402
import gebco  # noqa: E402
import tectonics  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"
TRETA_END_BCE = 867_102
SOMALI_PLATE = {"mauritius", "reunion", "drowned_saya_de_malha", "drowned_nazareth_bank"}
BIRTH_BCE = TRETA_END_BCE + 11_000 + 40   # Rama reigned 11,000 years (Bala 1.1.97, vulgate) after the war at ~40


def years_ago(bce):
    return bce + 2026 - 1


def main():
    age, sl = deep_sealevel.bintanja()
    places = json.loads((DATA / "places.json").read_text(encoding="utf-8"))
    epochs = {"birth": BIRTH_BCE, "treta_end": TRETA_END_BCE}
    levels = {k: float(np.interp((v + 1950) / 1000.0, age, sl)) for k, v in epochs.items()}
    win = (age >= (TRETA_END_BCE + 1950) / 1000.0) & (age <= (BIRTH_BCE + 2000 + 1950) / 1000.0)
    out = {"epochs_bce": epochs, "sea_level_m": {k: round(v, 1) for k, v in levels.items()},
           "sea_level_range_birth_to_treta_end_m": [round(float(sl[win].min()), 1), round(float(sl[win].max()), 1)],
           "places": []}
    print("sea level:", out["sea_level_m"], "range", out["sea_level_range_birth_to_treta_end_m"])
    g = gebco.load_grid()
    for p in places:
        if p["lat"] is None:
            out["places"].append({"id": p["id"], "name": p["name"]})
            continue
        rec = {"id": p["id"], "name": p["name"], "today": [p["lat"], p["lon"]]}
        for k, bce in epochs.items():
            if p["id"] in SOMALI_PLATE:      # the India-plate pole does not apply to the Mascarenes
                rec[f"position_{k}"] = None
                continue
            la, lo = tectonics.position_at(p["lat"], p["lon"], years_ago(bce))
            rec[f"position_{k}"] = [round(la, 4), round(lo, 4)]
        z = gebco.sample(g, p["lat"], p["lon"])
        rec["elevation_above_treta_sea_m"] = None if z != z else round(z - levels["treta_end"])
        if p.get("coastal") or p["id"] in ("lanka_island", "mahendra"):
            d = coastal.distance_to_sea(p["lat"], p["lon"], levels["treta_end"], half=2.5)
            if d:
                rec["treta_shore"] = {"km_to_sea": d["km"], "nearest_sea": [d["nearest_sea_lat"], d["nearest_sea_lon"]]}
        out["places"].append(rec)
    (DATA / "treta_geo.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    for r in out["places"]:
        if "treta_shore" in r:
            print(f"   {r['name']:<45} shore then {r['treta_shore']['km_to_sea']:>6} km away at {r['treta_shore']['nearest_sea']}")


if __name__ == "__main__":
    main()
