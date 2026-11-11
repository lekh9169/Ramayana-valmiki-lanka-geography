"""Build report_treta_yuga.html: the full analysis redone on the Puranic Treta-Yuga timeline (~869 ka).
Every number is read from data/*.json produced by the Treta scripts."""
import json
from pathlib import Path

from build_report import ROOT, build, esc, fig, j, table

ANCHOR_SHORT = {"Spica = 180° (Lahiri / Chitra-paksha)": "Spica (Lahiri)",
                "zeta Psc = 359°50' (Revati-paksha)": "ζ Psc (Revati)",
                "delta Cnc = 106° (Pushya-paksha)": "δ Cnc (Pushya)"}


def ll(v):
    if not v:
        return "—"
    lat, lon = v
    return f"{abs(lat):.4f}°{'N' if lat >= 0 else 'S'}, {lon:.4f}°E"


def sections():
    sky, geo, dt, cs, tt = j("treta_sky.json"), j("treta_geo.json"), j("deep_time.json"), j("chagos_scan.json"), j("tilt_tpw.json")
    calib, val = j("nbody_drift_calibration.json"), j("nbody_validation_corrected.json")
    places = {p["id"]: p for p in j("places_computed.json")}
    g = {p["id"]: p for p in geo["places"]}
    sl = geo["sea_level_m"]
    out = []
    out.append(f"""
<h1>Treta-Yuga edition: the places of the Valmiki Ramayana on a ~870,000-year timeline</h1>
<p class="small">Companion to the <a href="report.html">historical edition</a> (see the <a href="index.html">comparison page</a>).
Same GEBCO 2026 grid and the same Sanskrit evidence. This edition assumes the Puranic chronology and recomputes the sky,
the sea, the coasts and the coordinates for it.</p>
<div class="note"><b>Assumptions.</b> Kali Yuga began in 3102 BCE; Dvapara lasted 864,000 years. Treta therefore ended in
<b>{sky['treta_end_bce']:,} BCE</b>. Rama lived at the end of Treta and reigned 11,000 years after the war (Bala 1.1.97,
vulgate), which puts his birth near <b>{geo['epochs_bce']['birth']:,} BCE</b>. The birth sky is searched across
{sky['window_bce'][0]:,}–{sky['window_bce'][1]:,} BCE. What cannot be computed this far back: the Moon's position (the
tidal-acceleration uncertainty alone is thousands of degrees), the calendar day, the time of day and therefore the lagna,
and Mercury's position (to within tens of degrees). Results are given as candidate years and seasons, not dates.</div>
""")
    # ---------- 1. answer table
    rows = []
    for pid, role in (("ayodhya", "Ayodhya"), ("prayaga", "Prayaga"), ("chitrakuta", "Chitrakuta"), ("panchavati", "Panchavati"),
                      ("kishkindha", "Kishkindha"), ("malaya", "Malaya"), ("mahendra", "Mahendra"), ("tamraparni", "Tamraparni mouth"),
                      ("ocean_shore", "Southern ocean shore"), ("setu_start", "Setu, Indian end"), ("setu_end", "Setu, Lanka end"),
                      ("lanka_island", "Lanka = Sri Lanka?")):
        p, r = places[pid], g.get(pid, {})
        shore = r.get("treta_shore")
        env = (f"shore {shore['km_to_sea']:.0f} km away, at {ll(shore['nearest_sea'])}" if shore else
               (f"{r['elevation_above_treta_sea_m']:,} m above the sea of that time" if r.get("elevation_above_treta_sea_m") is not None
                else "outside the GEBCO subset (see Section 4.2)"))
        rows.append([esc(role), ll([p["lat"], p["lon"]]), ll(r.get("position_birth")), env])
    for pid in ("treta_huvadhu", "treta_fuvahmulah", "treta_addu", "treta_equator_point", "drowned_great_chagos"):
        p = places[pid]
        rows.append([esc(p["name"]), ll([p["lat"], p["lon"]]), "≈ 52 km SW of today's position", esc(p["identification"])])
    out.append(f"""
<h2>1. Coordinates on the Treta timeline</h2>
<p>"Today" is where to find each spot on a modern map. "On the plate at Rama's birth" is where that same ground stood
{geo['epochs_bce']['birth'] + 2025:,} years ago (India-plate rotation, NNR-MORVEL56). Every site moved together, so the distances
between them are unchanged. The last column describes the place in the world of {sl['treta_end']:.0f} m sea level.</p>
{table(["Place", "Today", "On the plate at Rama's birth", "Setting at the Treta sea level"], rows)}
<div class="key"><b>What the Treta timeline does to Lanka.</b> Throughout the window the sea stood
{geo['sea_level_range_birth_to_treta_end_m'][0]:.0f} to {geo['sea_level_range_birth_to_treta_end_m'][1]:.0f} m below
today, so Sri Lanka was part of the Indian mainland and the Palk Bay was dry land. A Lanka "across the ocean" must then
lie elsewhere. The only land near the equator was the Maldives plateaus (Huvadhu, Fuvahmulah, Addu), 837 km of open sea
from the Treta coast, across a channel at least 2,286 m deep. The Setu fails either way: it is not needed for Sri Lanka
and impossible for the Maldives.</div>
{fig("T1_route_treta.png", "Figure T1. The route on the land of the Treta epoch (sea level −90 m).")}
""")
    # ---------- 2. chronology
    ch = dt["chronology"]
    out.append(f"""
<h2>2. Chronologies</h2>
{table(["Chronology", "End of Treta", "Rama's birth (end of Treta + 11,000-year reign + ~40 yr)"], [
        ["Puranic / Surya Siddhanta: maha-yuga 4,320,000 yr, Treta 1,296,000 yr (this edition)", f"{ch['puranic_treta_end_bce']:,} BCE", f"~{geo['epochs_bce']['birth']:,} BCE"],
        ["Tradition placing Rama in the 24th maha-yuga", f"{ch['rama_24th_mahayuga_treta_end_bce']:,} BCE", "Miocene; before any hominin, not modelled"],
        ["Manusmriti 1.69–71 / Mahabharata 3.186 literal 12,000-yr cycle", "5502 BCE", "covered by the historical edition"]])}
""")
    # ---------- 3. astronomy
    vmax = val["max_abs_diff_deg"]
    oc = sky["obliquity_check"]
    anchor_rows = []
    for name, res in sky["anchors"].items():
        for w in res["strict_windows"]:
            anchor_rows.append([esc(ANCHOR_SHORT[name]), f"{w['start_bce']:,} BCE", f"{w['days']}", f"{min(w['days'] / 29.53, 1):.0%}", f"{w['sun_sid']:.1f}°",
                                f"{w['tropical_sun']:.1f}° ({esc(w['season'])})", f"{w['sea_level_m']:.0f} m",
                                f"{w['war_sky_episodes_age_30_45']}", f"{w['years_before_treta_end']:,}"])
    aries_rows = []
    for name, res in sky["anchors"].items():
        for w in res["sun_in_aries_windows"]:
            aries_rows.append([esc(ANCHOR_SHORT[name]), f"{w['start_bce']:,} BCE", f"{w['days']}", f"{w['tropical_sun']:.1f}° ({esc(w['season'])})"])
    season_rows = [[esc(ANCHOR_SHORT[n]), f"{len(r['all_pairings_pass_years'])} of {len(r['chaitra_seasons'])}",
                    ", ".join(f"{y:,}" for y in r["all_pairings_pass_years"][:6]) + (" …" if len(r["all_pairings_pass_years"]) > 6 else "")]
                   for n, r in sky["anchors"].items()]
    star_rows = [[esc(k), f"{v:.1f}°"] for k, v in sky["star_displacement_deg_since_treta_end"].items()]
    cal_rows = [[esc(k), f"{v['deg_per_kyr']:+.5f}", f"{v['rms_residual_deg']:.4f}", f"{v['extrapolated_869ka_deg']:+.1f}°"]
                for k, v in calib.items()]
    out.append(f"""
<h2>3. The sky of the Treta Yuga</h2>
<h3>3.1 How it was computed, and how well</h3>
<ul>
<li><b>Planets:</b> a REBOUND symplectic N-body integration (Sun plus nine planetary systems; initial state from JPL DE440s at
J2000; 2-day steps) run back to {sky['window_bce'][0]:,} BCE. A Newtonian integration slowly drifts in longitude because it
lacks general relativity. The drift was measured against DE441 at 15 epochs from 9,900 BCE to 2000 CE (JPL Horizons) and
is a straight line, so it is removed:
{table(["Body", "Drift (deg/kyr)", "Scatter about the line (deg)", "Correction at 869 ka"], cal_rows)}
Independent check against four earlier DE441 dates (4498–7120 BCE) after correction: Sun {vmax['sun']:.3f}°, Venus
{vmax['venus']:.3f}°, Mars {vmax['mars']:.3f}°, Jupiter {vmax['jupiter']:.3f}°, Saturn {vmax['saturn']:.3f}°. Estimated
uncertainty at 869 ka: Sun and Venus ±1°, Mars ±1–2°, Jupiter and Saturn ±0.1°, against 30° signs and 13.3°
nakshatras. Mercury is unreliable (no relativity), so the Mercury clauses are tested only as "possible".</li>
<li><b>Earth's axis:</b> the spin axis was precessed around the moving ecliptic. The precession constant was scaled for
orbital eccentricity and for the faster spin and closer Moon of the past. The resulting obliquity tracks Berger &amp;
Loutre (1991) with correlation {sky['obliquity_correlation_BL91']:.3f} over 883 kyr ({oc[7]['this_model_deg']:.2f}° against
{oc[7]['berger_loutre_deg']:.2f}° at 869 ka). The equinox from this model fixes the seasons, uncertain by about ±5° at 869 ka.</li>
<li><b>Stars:</b> the zodiac anchors moved with their full 3-D space motion (Hipparcos 2007 astrometry, catalogued radial
velocities). In 869 kyr the stars that define the nakshatras moved a long way:
{table(["Star", "Moved across the sky since the end of Treta"], star_rows)}
Punarvasu's two stars, Castor and Pollux, moved 56° and 75° and were not a pair then. "Aditi's nakshatra" can only be
defined as a formal 13°20′ segment counted from an anchor star, and the choice of anchor shifts the zodiac by tens of
degrees. All three classical anchors are therefore shown.</li>
</ul>
<h3>3.2 Rama's birth sky (Bala 1.18.8–9)</h3>
<p>The geometry that rules out <b>five</b> exalted planets holds at any epoch. Navami with the Moon in Punarvasu–Cancer puts
the Sun at 342°–357°, so neither the Sun nor Mercury can be exalted. The search therefore uses the best possible case:
Jupiter in Cancer, Saturn in Libra, Mars in Capricorn and Venus in Pisces, with the Sun at 342°–357°. Whether the navami
Moon fell inside a given window cannot be computed this far back. The chance is about the window's length divided by the
29.5-day lunar month.</p>
{table(["Zodiac anchor", "Window starts", "Days long", "Chance the navami Moon fell inside", "Sun (sidereal)", "Sun (tropical) and season", "Sea level", "Battle-sky episodes at age 30–45", "Years before the end of Treta"], anchor_rows)}
<p>The commentators' reading (Sun in Aries, plus the same four) gives:</p>
{table(["Zodiac anchor", "Window starts", "Days long", "Sun (tropical) and season"], aries_rows)}
<h3>3.3 Months and seasons in the Treta epoch</h3>
<p>The Critical Edition's month–season pairings (Caitra in bloom, Śrāvaṇa the first rains, Kārtika the campaign season,
hemanta with the Sun in the south) were tested every 500 years across the window. Precession carries the months right
round the seasons in ~25,700 years, so over 14,000 years they pass for part of the time only:</p>
{table(["Zodiac anchor", "Years in which all four pairings hold", "Those years (BCE)"], season_rows)}
{fig("T3_treta_timeline.png", "Figure T3. Sea level through the Treta window, the birth-sky windows (Spica zodiac) and the season of Chaitra.")}
<div class="key"><b>Astronomy verdict, Treta edition.</b> The four-planet birth sky does occur in the Treta window: 3–5
short windows, depending on the anchor star. With the Spica zodiac the window closest to the traditional birth estimate
(~878,000 BCE) is <b>876,021 BCE</b>, 8,919 years before the end of Treta and about 2,100 years after that estimate. It
lasts 14 days (about a 47% chance that the navami Moon fell inside it), and its Chaitra falls in late Shishira, at the
edge of spring. With
the Pushya anchor, windows in 872,724–871,870 BCE fall in Vasanta. Five exalted planets remain impossible, and the Moon,
day and lagna are beyond any computation this far back.</div>
""")
    # ---------- 4. sea, coasts, Lanka hypotheses
    tre = cs["southern_coast"]["treta_-90m"]
    out.append(f"""
<h2>4. Sea, coasts and rivers at the end of Treta</h2>
<ul>
<li>Sea level {sl['birth']:.0f} m at the birth epoch and {sl['treta_end']:.0f} m at the end of Treta (range
{geo['sea_level_range_birth_to_treta_end_m'][0]:.0f} to {geo['sea_level_range_birth_to_treta_end_m'][1]:.0f} m), during the
MIS 22 glaciation. Within ~10 kyr after the end of Treta the sea rose to about −20 m.</li>
<li>India and Sri Lanka were one landmass with its southern tip at {ll(tre['southern_tip'])}. The Wadge Bank put the cape
{tre['cape_shift_km']} km south-west of Kanyakumari.</li>
<li>The Tamraparni ran ~30 km further, across the exposed shelf, to a mouth near 8.58°N 78.39°E. The Palk Bay rivers
(Vaigai and others) flowed across what is now sea.</li>
<li>Plate motion: ~52 km south-west for every site, with no change in the distances between them. Axial tilt was 23.75°,
which moves the tropics but not the equator. True polar wander of 5.3° would be needed to put the equator × Ujjain point
on land.</li>
</ul>
{fig("T2_south_treta.png", "Figure T2. The south at the Treta sea level, with the shore points of that time.")}
<h3>4.1 The equatorial-Lanka hypothesis and the drowned islands of Chagos</h3>
<p>The full tests are in Section 8 of the historical edition and are repeated here in brief.</p>
<ul>
<li>The equatorial Maldives plateaus (Huvadhu 0.519°N 73.283°E, Fuvahmulah, Addu) were land at the equator, 950–1,100 km
from Mahendragiri (100 yojanas at 9.5–11 km). They were cut off from India by ≥ 2,286 m of sea.</li>
<li>The equator × Ujjain point was {abs(dt['plate']['depth_there_m']):,.0f} m deep.</li>
<li>The Great Chagos Bank island (~14,550 km²), Pitt Bank (~2,180 km²) and Speakers Bank (~980 km²) were land at the
Treta sea level and are drowned today.</li>
<li>No crater, break or debris marks the banks.</li>
</ul>
{fig("07_treta_equatorial_test.png", "Figure T4. The Chagos–Laccadive ridge at the Treta sea level.")}
{fig("09_chagos_drowned_islands.png", "Figure T5. Chagos at the Treta sea level and today.")}
""")
    import lemuria_text
    out.append(lemuria_text.section("4.2 Lemuria, Kumari Kandam and Mauritius", "treta"))
    # ---------- 5. comparison, limits, files
    hist = j("sill_results.json")
    out.append(f"""
<h2>5. The two editions side by side</h2>
{table(["Question", "Historical edition (text composed ~1st millennium BCE)", "Treta edition (~870,000 years ago)"], [
        ["Epoch used", "Month–season pairings ⇒ ≥ 2950 BCE; sea level near today", f"End of Treta {sky['treta_end_bce']:,} BCE; birth window 881,000–867,000 BCE"],
        ["Sea level", "0 to +1.5 m (mid/late Holocene)", f"{geo['sea_level_range_birth_to_treta_end_m'][0]:.0f} to {geo['sea_level_range_birth_to_treta_end_m'][1]:.0f} m"],
        ["Is Sri Lanka an island?", f"Yes, since ~5200 BCE (sill {hist['sill_all_m']:.0f} m)", "No: joined to India by dry land"],
        ["Setu", "Adam's Bridge: 32–46 km of 0–3 m shoal; 10:1 shape at −4 m", "Not needed for Sri Lanka; impossible (2.3 km deep) for the Maldives"],
        ["Lanka", "Sri Lanka (passes every geographic test)", "No candidate passes all tests; best equatorial land = Huvadhu plateau"],
        ["Birth horoscope", "Never satisfiable; nearest 6266 / 4498 BCE (4 exalted), both in winter", "Never satisfiable; 4-exalted windows 876,021 / 870,719 / 868,951 BCE (Spica)"],
        ["Seasons of the months", "Consistent from ~2950 BCE onward", "Consistent in about a third of the window, depending on the anchor star"],
        ["Nakshatra stars", "Essentially as today (≤ 0.1° motion)", "Moved 12–150°; Castor and Pollux not a pair"],
        ["Coordinates", "Today's coordinates (Section 7 of that edition)", "Same ground, ~52 km SW on the plate; coasts 23–88 km further out"],
        ["Kumari Kandam", "Under the sea (shelf drowned ~10–8 ka)", "~92,700 km² of South India and Sri Lanka dry, to ~7.4°N; no land beyond"],
        ["Lemuria and Mauritius", "No sunken continent in human times", "Mascarene and Chagos banks were islands; Mauritius fails the equator, meridian, distance and Setu clues"]])}
<h2>6. Limits</h2>
<ul>
<li>The N-body sky is reliable to ~1–2° for the Sun, Venus and Mars and ~0.1° for Jupiter and Saturn at 869 ka. Windows
lasting only a few days, such as 870,719 BCE, could shift or vanish within that error.</li>
<li>The precession and equinox model (validated against Berger &amp; Loutre) leaves the seasons uncertain by about ±5° at
869 ka. The Moon, the calendar day, the time of day and the lagna are not computable.</li>
<li>Sea level comes from a single model reconstruction (Bintanja &amp; van de Wal 2008), uncertain by ±10–15 m. Vertical land
motion over 869 kyr (tens of metres) is not modelled for India.</li>
<li>This edition takes the Puranic chronology as given in order to test it. It does not establish that chronology.
Language, literature and cities are not known from 870,000 years ago, when India's inhabitants were Acheulean-tool-making
early humans.</li>
</ul>
<h2>7. Files</h2>
<ul>
<li><code>data/valmiki_places_treta.kml</code>: the Treta-edition placemarks, the shore points of the time and the −90 m
coastline (Google Earth).</li>
<li><code>data/treta_sky.json</code>, <code>data/treta_geo.json</code>, <code>data/nbody_*.json</code>: all computed numbers.</li>
<li><code>scripts/nbody.py</code>, <code>nbody_calib.py</code>, <code>treta_sky.py</code>, <code>treta_geo.py</code>,
<code>map_treta.py</code>: the Treta pipeline (needs JPL DE440s, 32 MB, for the initial state).</li>
</ul>
""")
    return out


if __name__ == "__main__":
    path = ROOT / "report_treta_yuga.html"
    path.write_text(build(sections(), title="Valmiki Ramayana places — Treta-Yuga edition", edition="treta",
                          description="Treta-Yuga edition: the places of the Valmiki Ramayana on a ~870,000-year timeline, with N-body astronomy, glacial sea level and plate positions."), encoding="utf-8")
    print(path)
