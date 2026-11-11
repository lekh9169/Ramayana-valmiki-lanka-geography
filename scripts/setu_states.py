"""State of the Adam's Bridge crest at each sea level: wet length, number of channels, max depth."""
import json
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parents[1] / "data"


def states(levels=np.arange(-4.0, 2.51, 0.5)):
    prof = json.loads((DATA / "setu_crest_profile.json").read_text())
    km = np.array([p["km"] for p in prof])
    z = np.array([p["elev_m"] for p in prof])
    seg = np.diff(km, prepend=km[0])
    out = []
    for level in levels:
        wet = z < level
        channels = int(np.sum(np.diff(np.r_[0, wet.astype(int)]) == 1))
        out.append({"sea_level_m": float(level), "wet_km": round(float(seg[wet].sum()), 1),
                    "dry_km": round(float(seg[~wet].sum()), 1), "channels": channels,
                    "max_water_depth_m": round(float(max(0.0, level - z.min())), 1)})
    return out


if __name__ == "__main__":
    rows = states()
    for r in rows:
        print(r)
    (DATA / "setu_states.json").write_text(json.dumps(rows, indent=1))
