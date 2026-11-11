"""Re-run the whole analysis in order. Usage:  python run_all.py
Requires: numpy, scipy, matplotlib, jplephem (pip install --user ...), the GEBCO 2026
GeoTIFF (path in gebco.py) and JPL DE441 part 1 (path in ephem.py, ~1.65 GB from
https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de441_part-1.bsp).
"""
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
STEPS = [
    "make_places.py",     # places list (verified coordinates + Valmiki references)
    "make_geo_notes.py",  # literature notes (text clues, rivers, sources)
    "sill.py",            # India-Sri Lanka land-bridge sill
    "setu_shape.py",      # Adam's Bridge length / width / crest profile
    "setu_states.py",     # crest state per sea level
    "terrain.py",         # summits, launch distances, equatorial-Lanka test
    "visibility.py",      # horizon test from Setu landfall / Mahendragiri
    "astro_search.py",    # DE441 search for the Bala Kanda 18 configuration
    "astro_checks.py",    # published-date check, alt. reading, seasons
    "season_test.py",     # month-season precession test (CE layer)
    "war_check.py",       # Mercury-Rohini / Mars-Vishakha at the last battle
    "text_distances.py",  # stated distances vs measured; implied yojana
    "deep_time.py",       # Treta-Yuga (~869 ka) equatorial Chagos-Laccadive test
    "chagos_scan.py",     # 869-ka positions, southern coast, drowned banks, seamounts, basins
    "tilt_tpw.py",        # obliquity and true polar wander vs the equator x Ujjain point
    "lemuria_mauritius.py",  # Kumari Kandam, Lemuria and Mauritius tests (GEBCO + NOAA ETOPO 2022)
    "compute_places.py",  # per-place GEBCO / tectonic / shoreline fields
    "export_places.py",   # GeoJSON, KML, CSV
    "map_route.py", "map_palk.py", "map_yojana.py", "map_deep.py", "map_chagos.py", "map_lemuria.py", "charts.py",
    "build_report.py",
    # --- Treta-Yuga edition ---
    "nbody_calib.py",       # N-body drift vs DE441 (uses data/horizons_de441_helio.json)
    "nbody_validate.py",    # check against saved DE441 dates, raw and drift-corrected
    "treta_sky.py",         # N-body sky, precession, star motions over the Treta window (~7 min)
    "treta_geo.py",         # positions and shorelines at the Treta sea level
    "map_treta.py",
    "export_treta.py",      # Treta KML (with -90 m coastline) and CSV
    "build_treta_report.py",
    # --- website ---
    "site_assets.py",       # hero relief PNG, sea-level table, combined map layers
    "build_site.py",        # index (home), map, data, about pages
]

NEEDS_DE441 = {"astro_search.py", "astro_checks.py", "season_test.py", "war_check.py"}
NEEDS_DE440S = {"nbody_calib.py", "nbody_validate.py", "treta_sky.py"}

if __name__ == "__main__":
    import ephem
    have_de441 = Path(ephem.BSP).exists()
    import nbody
    have_de440s = Path(nbody.DE440S).exists()
    if not have_de441:
        print(f"DE441 not found at {ephem.BSP}: skipping the astronomy steps and reusing their saved results in data/")
    if not have_de440s:
        print(f"DE440s not found at {nbody.DE440S}: skipping the N-body steps and reusing their saved results in data/")
    for step in STEPS:
        if step in NEEDS_DE440S and not have_de440s:
            print(f"\n=== {step} === skipped (needs DE440s)")
            continue
        if step in NEEDS_DE441 and not have_de441:
            print(f"\n=== {step} === skipped (needs DE441)")
            continue
        print(f"\n=== {step} ===")
        runpy.run_path(str(HERE / step), run_name="__main__")
