"""Relative sea level (RSL) model for the Gulf of Mannar / Palk Strait.

Reads data/rsl_curve.csv (age_ka, rsl_m, sigma_m, source) and interpolates linearly.
RSL is relative to present mean sea level at the site, so 'land at epoch t' is any GEBCO
cell with elevation > RSL(t) (minus a sediment correction where noted).
"""
import csv
from pathlib import Path

import numpy as np

CURVE = Path(__file__).resolve().parents[1] / "data" / "rsl_curve.csv"


def load():
    with open(CURVE, newline="", encoding="utf-8") as handle:
        rows = [r for r in csv.DictReader(handle) if not r["age_ka"].startswith("#")]
    age = np.array([float(r["age_ka"]) for r in rows])
    level = np.array([float(r["rsl_m"]) for r in rows])
    sigma = np.array([float(r["sigma_m"]) for r in rows])
    order = np.argsort(age)
    return age[order], level[order], sigma[order], rows


def rsl_at(age_ka):
    age, level, sigma, _ = load()
    return float(np.interp(age_ka, age, level)), float(np.interp(age_ka, age, sigma))


def age_when_level_crossed(threshold_m):
    """Youngest age (ka) at which the curve rises through threshold, with +-1 sigma bounds."""
    age, level, sigma, _ = load()
    fine = np.linspace(age.min(), age.max(), 20001)
    out = []
    for curve in (np.interp(fine, age, level - sigma), np.interp(fine, age, level),
                  np.interp(fine, age, level + sigma)):
        below = np.where(curve < threshold_m)[0]
        out.append(float(fine[below.min()]) if below.size else None)
    # curve-sigma is lower -> crosses later (younger); return (central, young, old)
    return {"central_ka": out[1], "young_bound_ka": out[0], "old_bound_ka": out[2]}


def bp_to_year(age_ka):
    """ka before 1950 -> astronomical year."""
    return int(round(1950 - age_ka * 1000))


def year_to_bp(year):
    return (1950 - year) / 1000.0
