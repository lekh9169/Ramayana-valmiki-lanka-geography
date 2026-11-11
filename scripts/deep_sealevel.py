"""Global sea level over the last 3 Myr (Bintanja & van de Wal 2008, NOAA WDC Paleo #2011-119)
and the 0-798 ka stack of Spratt & Lisiecki (2016) as a cross-check."""
from pathlib import Path

import numpy as np

PALEO = Path(__file__).resolve().parents[1] / "data" / "paleo"


def bintanja():
    rows = []
    for line in (PALEO / "bintanja2008.txt").read_text(errors="ignore").splitlines():
        parts = line.split()
        if len(parts) == 9:
            try:
                rows.append([float(x) for x in parts])
            except ValueError:
                pass
    a = np.array(rows)
    order = np.argsort(a[:, 0])
    # column 9 is the sea-level DROP relative to present (positive = lower), so negate it
    return a[order, 0], -a[order, 8]  # age kyr BP, global sea level (m, present = 0)


def spratt():
    rows = []
    for line in (PALEO / "spratt2016.txt").read_text(errors="ignore").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split("\t")
        try:
            rows.append([float(parts[0]), float(parts[1])])
        except (ValueError, IndexError):
            pass
    a = np.array(rows)
    return a[:, 0], a[:, 1]  # age ka, sea level (m), long PC1 stack


if __name__ == "__main__":
    age, sl = bintanja()
    print(f"Bintanja & van de Wal 2008: {age.min():.1f}-{age.max():.1f} kyr, {len(age)} samples")
    last = age <= 1000
    print(f"  last 1 Myr: min {sl[last].min():.1f} m at {age[last][np.argmin(sl[last])]:.1f} ka, max {sl[last].max():.1f} m")
    for t in (867.0, 869.05, 871.0):
        print(f"  sea level at {t} ka: {np.interp(t, age, sl):.1f} m")
    w = (age >= 860) & (age <= 880)
    print(f"  860-880 ka range: {sl[w].min():.1f} .. {sl[w].max():.1f} m")
    for thr in (-3, -10, -40, -100):
        print(f"  fraction of last 1 Myr with sea level below {thr} m: {np.mean(sl[last] < thr):.0%}")
    sa, ss = spratt()
    ok = ~np.isnan(ss)
    print(f"Spratt & Lisiecki 2016: {sa.min():.0f}-{sa.max():.0f} ka; min {np.nanmin(ss):.1f} m; at 20 ka {np.interp(20, sa[ok], ss[ok]):.1f} m")
