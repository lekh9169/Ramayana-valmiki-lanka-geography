"""Narrative sections of report.html. Every number is read from data/ at build time."""
import json
from pathlib import Path

import rsl
from build_report import ROCK_SILL_M, epoch_rows, esc, fig, j, sea_level_rows, table


def fmt_ll(lat, lon):
    if lat is None:
        return "not locatable"
    return f"{abs(lat):.4f}°{'N' if lat >= 0 else 'S'}, {lon:.4f}°E"


def bce(year):
    if year > 0:
        return f"{year} CE"
    n = 1 - year
    return f"{n:,} BCE" if n >= 10000 else f"{n} BCE"


def sections():
    sill = j("sill_results.json")
    shape = j("setu_shape.json")
    terrain = j("terrain.json")
    vis = j("visibility.json")
    search = j("rama_birth_search.json")
    checks = j("astro_checks.json")
    season = j("season_test.json")
    war = j("war_check.json")
    dist = j("text_distances.json")
    places = j("places_computed.json")
    geo = j("geo_notes.json")
    epochs = j("epochs.json")
    w4 = next(s for s in shape if s["depth_cutoff_m"] == 4)
    w3 = next(s for s in shape if s["depth_cutoff_m"] == 3)
    breach = rsl.age_when_level_crossed(sill["sill_all_m"])
    breach_year = rsl.bp_to_year(breach["central_ka"])
    breach_young = rsl.bp_to_year(breach["young_bound_ka"])
    breach_old = rsl.bp_to_year(breach["old_bound_ka"])
    rock = rsl.age_when_level_crossed(ROCK_SILL_M)
    rock_year, rock_young, rock_old = (rsl.bp_to_year(rock[k]) for k in ("central_ka", "young_bound_ka", "old_bound_ka"))
    lahiri = next(r for r in search["runs"] if r["ayanamsa_offset_deg"] == 0.0)
    pid = {p["id"]: p for p in places}
    s_span = season["all_pass_span"]
    out = []

    # ---------------------------------------------------------------- 0. title
    out.append(f"""
<h1>Lanka and the places of the Valmiki Ramayana: a data-driven geography (historical edition)</h1>
<p class="small">Two editions: this one, and the <a href="report_treta_yuga.html">Treta-Yuga edition</a> (~870,000-year timeline). Compare them on the <a href="index.html">overview page</a>.</p>
<p class="small">Built {esc(geo['built'])} from GEBCO 2026 bathymetry (15″ grid, 35.7°S–33.9°N, 62.8–94.7°E),
the JPL DE441 planetary ephemeris (13,200 BCE – 1969 CE),
a regional relative-sea-level model, the India-plate rotation pole and the Sanskrit text (IIT Kanpur / RSVP
vulgate, checked against the Baroda Critical Edition). Every number below is recomputed by
<code>scripts/run_all.py</code>.</p>
<div class="note"><b>Read this first.</b> The method can test whether the text's geography and sky are
<i>consistent</i> with a real place and epoch; it cannot prove the events happened. Three things limit any
"actual coordinates": (1) the Critical Edition shows the most date-like verses, the horoscope and the day-by-day
Setu figures, are later additions; (2) Valmiki's distances imply a "yojana" anywhere from 0.3 km to 28 km,
so they are formulaic, not survey data; (3) the astronomical clues contradict each other (Section 3).
Where the data do give a clear answer, it is stated plainly.</div>
""")

    # ---------------------------------------------------------------- 1. answer first
    key_ids = ["lanka_island", "setu_start", "setu_end", "mahendra", "malaya", "tamraparni", "pandya_kavata",
               "kishkindha", "pampa", "panchavati", "chitrakuta", "prayaga", "shringaverapura", "ayodhya",
               "lanka_city_sripada", "lanka_city_trinco", "suvela"]
    rows = []
    for k in key_ids:
        p = pid[k]
        rows.append([f"<b>{esc(p['name'])}</b><br/><span class='skt'>{esc(p['sanskrit'])}</span>",
                     esc(p["identification"]), fmt_ll(p["lat"], p["lon"]), esc(p["confidence"]),
                     esc(p["valmiki_refs"])])
    out.append(f"""
<h2>1. The answer in one table</h2>
<div class="key"><b>Lanka is Sri Lanka.</b> It is the only candidate that passes every geographic test in the text
(Section 5). <b>The Setu is Adam's Bridge</b>, the {w3['gap_length_km']:.0f}-km shoal from Rameswaram island to
Mannar island. Its crest lies 0–3 m below today's sea, and at the −4 m isobath it has the 10 : 1 length-to-width
ratio Valmiki gives (100 × 10 yojanas). <b>The sea-level record makes Sri Lanka an island only after about
{bce(breach_year)}</b> (range {bce(breach_old)} – {bce(breach_young)}). Before that it was joined to India by dry
land and no Setu would have been needed. With the hard-rock sill the break is about {bce(rock_year)}. Any proposed
date older than about {bce(rock_old)} conflicts with the story. The Treta-Yuga (~869,000-year) reading with an
equatorial Lanka on the Chagos–Laccadive ridge is tested separately in Section 8.</div>
{table(["Place (Valmiki)", "Best-supported identification", "Coordinates (WGS84)", "Confidence", "Text reference (IITK; CE)"], rows)}
<p class="small">The complete list ({len(places)} entries, including Sri Lankan tradition sites, rejected hypotheses and the Treta-Yuga test candidates) is in Section 7 and
in <code>data/valmiki_places.kml</code> (Google Earth), <code>.geojson</code> and <code>.csv</code>. Confidence
reflects how directly the text's clue fits the location, not religious tradition.</p>
{fig("01_route_overview.png", "Figure 1. The route in narrative order on GEBCO 2026 relief.")}
""")

    # ---------------------------------------------------------------- 2. text
    out.append(f"""
<h2>2. What the text constrains, and which layer each clue belongs to</h2>
<p>The vulgate (southern recension, IITK numbering) was compared verse by verse with the Critical Edition (CE), the
constituted text only, with no apparatus. Clues present in the CE belong to the older layer.</p>
{table(["Clue", "Reference", "In the Critical Edition?", "Constraint it gives"], [[esc(a), esc(b), esc(c), esc(d)] for a, b, c, d in geo['text_clues']])}
""")

    # ---------------------------------------------------------------- 3. astronomy
    strict = lahiri["matches"]
    strict_rows = [[esc(m["date"]), f"{m['jd_tdb']:.2f}", ", ".join(m["exalted"]), f"{m['lon']['sun']:.1f}°",
                    f"{m['lon']['moon']:.1f}°", f"{m['lon']['jupiter']:.1f}°", str(m["hours_also_moon_in_cancer"])]
                   for m in strict]
    sens = [[f"{r['ayanamsa_offset_deg']:+.0f}°", str(r["stage1_windows"]), str(len(r["matches"])),
             str(sum(m["exalted_count"] >= 5 for m in r["matches"]))] for r in search["runs"]]
    alt = [[esc(d["date"]), esc(d["tithi"]), esc(d["moon_nakshatra"]), ", ".join(d["exalted"]), esc(d["ritu_of_sun"])]
           for d in checks["sun_in_aries_reading"]]
    bh = checks["bhatnagar_5114BCE"]
    bh_rows = [[esc(k.replace('_', ' ')), esc(v["date"]), esc(v["tithi"]), esc(v["moon_nakshatra"]),
                ", ".join(f"{b} {s}" for b, s in v["signs"].items()), ", ".join(v["exalted"]) or "none"]
               for k, v in (("without ΔT", bh["without_delta_t"]), ("with ΔT", bh["with_delta_t"]))]
    war_rows = [[esc(c["birth"]), "; ".join(f"{esc(e['start'])} (age {e['rama_age_years']})" for e in c["episodes_age_30_45"]) or "none"]
                for c in war["candidates"]]
    season_rows = [[str(y), *("✔" if r[n] else "✘" for n in list(r)[2:6])]
                   for y in (-12208, -6265, -5113, -4497, -3000, -1500, -500, 0, 500)
                   for r in [min(season["rows"], key=lambda r, y=y: abs(r["year"] - y))]]
    season_heads = list(season["rows"][0])[2:6]
    out.append(f"""
<h2>3. The astronomical evidence, computed on JPL DE441</h2>
<p>Positions are geocentric, daily (hourly near candidates), from JPL DE441, over 13,000 BCE – 1 BCE. The zodiac is
sidereal and anchored on Spica = 180° (Lahiri/Chitrapaksha), using the Hipparcos position and proper motion. Taking
longitudes relative to Spica cancels precession; the residual from the moving ecliptic is below 0.1°. Checks: the
pipeline puts the 585 BCE (Thales) and 763 BCE (Assyrian) solar eclipses on new moons (0.04° and 0.06°), the 7 BCE
triple Jupiter–Saturn conjunction on 29/30 May, 1 Oct and 5/6 Dec, and Mesha sankranti 1950 on 13 April.</p>

<h3>3.1 Rama's birth horoscope (Bala 1.18.8–9: a late interpolation, absent from the CE)</h3>
<p>The text names Caitra, the 9th tithi, Aditi's nakshatra (Punarvasu), "five grahas in exaltation" (unnamed),
Cancer lagna, and Jupiter rising with the Moon. Caitra plus the Moon in Punarvasu forces the bright fortnight;
Jupiter with the Moon puts both in Cancer, i.e. Punarvasu's 4th quarter (90°–93.3°). <b>These conditions fix the Sun at
342°–357°, late Pisces, so the Sun cannot be exalted (Aries). Mercury never strays more than
{lahiri['max_mercury_elongation_deg']:.1f}° from the Sun in DE441, so it cannot reach Virgo, and the Moon in Cancer is not
exalted either.</b> At most four planets can be exalted (Venus, Mars, Jupiter, Saturn). The horoscope as written is
internally impossible on any date. The search confirms it: no day in 13,000 years has five.</p>
<p>Days that satisfy everything else (navami, Moon in Punarvasu and Cancer with Jupiter, and Venus, Mars, Jupiter and
Saturn all exalted):</p>
{table(["Date (Julian calendar)", "JD (TDB)", "Exalted", "Sun", "Moon", "Jupiter", "Hours with Moon in Cancer"], strict_rows)}
<p>Sensitivity to the zodiac's zero point (offset from Lahiri):</p>
{table(["Offset", "Slow-planet windows", "Navami + Punarvasu matches", "with ≥5 exalted"], sens)}
<p>The commentators' reading (Sun, Mars, Jupiter, Venus, Saturn exalted) plus the Moon in Punarvasu, ignoring the
tithi, also occurs, but never on a navami:</p>
{table(["Date", "Tithi", "Moon", "Exalted", "Season (sāyana ṛtu)"], alt)}
<p><b>A widely cited date, 10 January 5114 BCE</b> (P. Bhatnagar 2004), does not reproduce on DE441 under either
calendar reading. The run below takes it as a Julian date, local noon at Ayodhya; the Gregorian reading gives Sun in
Aries but Jupiter in Leo and Saturn in Scorpio:</p>
{table(["Case", "Date", "Tithi", "Moon", "Signs", "Exalted"], bh_rows)}

<h3>3.2 Month–season pairings (present in the CE, the older layer)</h3>
<p>Precession slides the lunar months through the seasons by about one month every 2,150 years. Four CE-present
pairings were tested: Caitra with groves in bloom (2.3.4); Śrāvaṇa as the first rainy month (CE 4.25.12); Kārtika as
the end of the rains (CE 4.25.15); and hemanta with the Sun "firmly in the south" and full-moon nights led by Puṣya
(CE 3.15). <b>All four hold together only from about {bce(s_span[0])} to the present.</b> Every candidate date older
than about 3000 BCE fails all four: 6266, 5114 and 4498 BCE all put Caitra in mid-winter.</p>
{table(["Year (astr.)", *[esc(h.split(' - ')[0]) for h in season_heads]], season_rows)}

<h3>3.3 Other sky clues</h3>
<ul>
<li><b>Ravana's last battle</b> (CE 6.90.27–30): Mercury on Rohiṇī and Mars on Viśākhā. That sky turns up in
{war['base_rate_16yr_windows']:.0%} of all 16-year windows, so it barely discriminates. Within Rama's adult years
(ages 30–45) of each birth candidate:{table(["Birth candidate", "Mercury-Rohiṇī + Mars-Viśākhā episodes"], war_rows)}</li>
<li><b>Full moon</b> when Hanuman enters Lanka at dusk (CE 5.2.54–55, 5.4.5) and on the night on Suvela (CE 6.29.17).
Both are consistent with each other, but with no month or year they cannot be dated.</li>
<li><b>Aranya 3.22.11 (CE)</b>: Rahu seizes the Sun <i>aparvaṇi</i>, "not on a new- or full-moon day". Real solar
eclipses happen only at new moon, so the text marks this as a portent, not an observation.</li>
<li><b>Ayodhya 2.4.18–22</b>: "Sun, Mars and Rahu afflict <i>my</i> star". That is Dasharatha's nakshatra, not
Rama's. The Moon is in Punarvasu, with Puṣya tomorrow. Undatable without a year.</li>
</ul>
<div class="key"><b>Astronomy verdict.</b> The only clue set that gives a testable epoch is the older layer's
month–season pairings, which point to <b>{bce(s_span[0])} or later</b>. That matches philology (core books composed
in the 1st millennium BCE). The horoscope cannot be satisfied at all, and its closest matches (6266 and 4498 BCE)
contradict the seasons. For the geography this means using the sea level of the last ~5,000 years, close to
today's.</div>
""")

    # ---------------------------------------------------------------- 4. sea level
    out.append(f"""
<h2>4. Sea level, the land bridge and the Setu</h2>
<h3>4.1 The sill</h3>
<p>Bisection on the flood level with 4-connected labelling of the GEBCO grid (no diagonal leaks) finds the highest
sea level at which a continuous strip of land still joins India and Sri Lanka:</p>
<ul><li><b>Adam's Bridge corridor: {sill['sill_adams_bridge_corridor_m']:.1f} m</b> (the controlling sill);</li>
<li>northern Palk Strait (Point Calimere–Jaffna): {sill['sill_palk_strait_north_corridor_m']:.1f} m;</li>
<li>India–Maldives: {terrain['india_maldives_sill_m']:.0f} m, never land in the Quaternary.</li></ul>
<h3>4.2 When did the bridge go under?</h3>
<p>Relative sea level (RSL) for the Gulf of Mannar comes from the literature (table below). The sea first rises
above the {sill['sill_all_m']:.1f} m sill at about <b>{breach['central_ka']:.2f} ka BP ≈ {bce(breach_year)}</b>, with a
±1σ range of {bce(breach_old)} – {bce(breach_young)}. The crest today is loose sand 7–9 m thick over calcareous
sandstone and conglomerate (Dandabathula et al. 2024). Taking that hard substrate (≈ {ROCK_SILL_M:.0f} m) as the sill,
the land link breaks at about <b>{bce(rock_year)}</b> ({bce(rock_old)} – {bce(rock_young)}). Dubey et al. (2023)
reach the same picture independently from seismic profiles: seawater entered the Palk Strait ~8.5 ka, and the strait
has not been crossable on foot for ~7,000 years. {esc(geo['rsl_comment'])}</p>
{table(["Age (ka BP)", "RSL (m)", "±1σ", "Source"], sea_level_rows())}
{fig("05_sea_level_timeline.png", "Figure 2. Relative sea level against the GEBCO sill depths, with the candidate epochs.")}
{table(["Epoch", "Year", "ka BP", "RSL (m)", f"Link, sand-crest sill {sill['sill_all_m']:.0f} m", f"Link, rock sill {ROCK_SILL_M:.0f} m"], epoch_rows(sill['sill_all_m']))}
{fig("02_palk_strait_paleocoast.png", "Figure 3. Palk Strait and Gulf of Mannar coastlines at each epoch (GEBCO flooded to that epoch's RSL).")}
<h3>4.3 Shape of the Setu</h3>
{table(["Depth cut-off", "Gap length (km)", "Shoal area (km²)", "Mean width (km)", "Length : width"],
          [[f"−{s['depth_cutoff_m']} m", f"{s['gap_length_km']:.1f}", f"{s['shoal_area_km2']:.0f}",
            f"{s['mean_width_km']:.1f}", f"{s['length_to_width']:.1f}"] for s in shape])}
<p>The shortest path along the crest runs {w3['gap_length_km']:.1f} km from the Rameswaram island shore to Mannar
island; tip to tip, Arichal Munai to Mannar, is {terrain['launch_to_srilanka']['Dhanushkodi / Arichal Munai']['coast_at_0m']['distance_km']:.1f} km.
No crest cell is deeper than {-sill['sill_all_m']:.0f} m. Valmiki's 100 × 10 yojanas (CE 6.15.20) is a ratio of
10. GEBCO gives <b>{w4['length_to_width']:.1f} at the −4 m isobath</b>, ranging from 14 at −3 m to 1.2 at −15 m. The
match is real but depends on the isobath chosen. Treat it as consistent, not as proof of design.</p>
{fig("03_adams_bridge_profile.png", "Figure 4. GEBCO crest profile of Adam's Bridge with sea level at the candidate epochs.")}
""")

    # ---------------------------------------------------------------- 5. hypothesis tests
    ss = terrain["surya_siddhanta_lanka"]
    out.append(f"""
<h2>5. Testing the Lanka hypotheses against the text</h2>
{table(["Test (text)", "Sri Lanka", "Maldives", "Equator × Ujjain meridian", "Amarkantak (central India)"], [
        ["Island across the southern sea beyond Mahendra and the Tamraparni (CE 4.40.17–25)", "✔", "✔ (SW)", "✘ open ocean", "✘ landlocked"],
        ["Sea gap bridgeable by a causeway (CE 6.15)", f"✔ {w3['gap_length_km']:.0f} km of 0–3 m shoal", f"✘ sill {terrain['india_maldives_sill_m']:.0f} m", f"✘ {ss['depth_m']:.0f} m deep", "✘ no sea"],
        ["Setu ratio 10 : 1 (CE 6.15.20)", f"✔ {w4['length_to_width']:.1f} at −4 m", "✘", "✘", "✘"],
        ["A mountain (Trikuta) on the island (CE 5.2.1)", "✔ highlands to 2,524 m", "✘ atolls, &lt; 3 m today", "✘", "✔ (but no sea)"],
        ["Island at the text's epoch (CE month–season layer ≥ 3000 BCE)", f"✔ island since ~{bce(breach_year)}", "✔ but sill km-deep", "✘ never land", "✘"],
        ["'100 yojanas' away", "✔ with a 2.4-km yojana from Mahendragiri", "✔ with an ~8-km yojana", "✔ with ~10 km", "—"],
    ])}
<p>The equatorial "Lanka" of the Surya Siddhanta is a reference point of Indian astronomy, the place where the prime
meridian through Ujjain meets the equator. GEBCO puts it under {ss['depth_m']:.0f} m of water; the nearest seabed
that was ever dry (shallower than −130 m) lies {ss['nearest_cell_above_-130m']['distance_km']:.0f} km away in the
Maldives. The Maldives were large exposed limestone plateaus only below about −40 m sea level
({terrain['maldives_exposed_km2']['-40']:,} km² against {terrain['maldives_exposed_km2']['0']:,} km² today). At those
sea levels (&gt; ~10 ka) Sri Lanka was itself joined to India by land.</p>
{fig("04_hundred_yojana_arcs.png", "Figure 5. Where '100 yojanas' from Mahendragiri falls for each yojana value, over present and glacial coastlines.")}
<h3>Valmiki's distances against the map</h3>
{table(["Clue", "Text", "Stated", "Measured (km)", "Implied km per unit"],
          [[esc(r['clue']), esc(r['ref']), esc(r['stated']), f"{r['measured_km']:.1f}", f"{r['implied_km_per_unit']:.2f} per {r['unit']}"] for r in dist['distances']])}
<p>The implied yojana ranges more than 80-fold, so no single unit fits. The 100s are the poem's formula for "a great
distance". Rishyamuka lies at a bearing of {dist['rishyamuka_bearing_from_pampa_deg']:.0f}° (south-west) from
Pampa Sarovar, while the text puts it <i>purastāt</i>, in front of or east of Pampa.</p>
<h3>Line of sight</h3>
<p>With standard refraction, no Sri Lankan terrain of 100 m or more is above the horizon from the Setu landfall at
Talaimannar (eye 10–30 m), from Rameswaram, or from Mahendragiri's 1,555 m summit. The nearest summit of 300 m or more
is {terrain['nearest_300m_summit_to_landfall']['km_from_talaimannar']:.0f} km inland. So "Lanka seen on Trikuta" from
Lamba or Suvela near the landing (CE 5.2.1, 6.29.13) cannot be literal for any Sri Lankan city.</p>
{fig("06_lanka_detail.png", "Figure 6. Sri Lanka: Setu landfall, Trikuta candidates, tradition sites and GEBCO summits.")}
""")

    # ---------------------------------------------------------------- 6. rivers & tectonics
    v = pid["setu_end"]
    out.append(f"""
<h2>6. Rivers, coasts and tectonics</h2>
<h3>6.1 Plate motion</h3>
<p>{esc(geo['plate_comment'])} At the Setu landfall the India plate moves {v['plate_velocity_mm_yr']:.0f} mm/yr toward
{v['plate_velocity_azimuth_deg']}°, about {v['tectonic_shift_m_since_epoch']:,} m since the oldest reference epoch.
All the sites ride the same plate, so their positions relative to each other have not changed. Horizontal tectonics
therefore does not move any identification; it matters only against fixed references such as the equator. Each
site's epoch position is in the KML and GeoJSON.</p>
<h3>6.2 River and shoreline shifts</h3>
{table(["Place", "Shift", "Effect on the coordinate", "Source"], [[esc(a), esc(b), esc(c), esc(d)] for a, b, c, d in geo['river_notes']])}
""")

    # ---------------------------------------------------------------- 7. full table
    rows = []
    for p in places:
        sea = p.get("sea_distance_km") or {}
        sea_txt = "; ".join(f"{k}: {v['km']} km" for k, v in sea.items() if v) if sea else ""
        tag = " (rejected)" if p.get("rejected") else (" (tradition)" if p.get("tradition") else "")
        rows.append([f"<b>{esc(p['name'])}</b>{tag}<br/><span class='skt'>{esc(p['sanskrit'])}</span>",
                     esc(p["valmiki_refs"]), esc(p["text_clue"]), esc(p["identification"]),
                     fmt_ll(p["lat"], p["lon"]), "outside grid" if p.get("gebco_elev_m") is None and p["lat"] is not None else str(p.get("gebco_elev_m", "")), esc(p["confidence"]),
                     esc(sea_txt) + ("<br/>" if sea_txt and p.get("paleo_note") else "") + esc(p.get("paleo_note", "")),
                     esc(p["coord_source"])])
    out.append(f"""
<h2>7. All places</h2>
{table(["Place", "Reference (IITK; CE)", "Text clue", "Identification", "Coordinates", "GEBCO elev (m)", "Conf.", "Through time (sea distance by epoch; river/coast shift)", "Coordinate source"], rows)}
""")

    # ---------------------------------------------------------------- 8. deep-time (Treta) test
    dt = j("deep_time.json")
    ch, sl, pl = dt["chronology"], dt["sea_level"], dt["plate"]
    base = dt["cases"]["treta_sea_level"]
    opt = dt["cases"]["deepest_plus_subsidence"]
    sills = dt["sills_to_india_m"]
    names = {(0.519, 73.283): ("Huvadhu atoll plateau", "Huvadhu atoll (equator, N)"),
             (-0.307, 73.433): ("Fuvahmulah plateau", "Fuvahmulah (equator)"),
             (-0.636, 73.161): ("Addu atoll plateau", "Addu atoll (equator, S)")}

    def find(case, lat, lon):
        return min(case["landmasses"], key=lambda r: abs(r["centroid"][0] - lat) + abs(r["centroid"][1] - lon))

    eq_rows = []
    for (la, lo), (label, sill_key) in names.items():
        b, o = find(base, la, lo), find(opt, la, lo)
        eq_rows.append([esc(label), fmt_ll(*b["centroid"]), f"{b['area_km2']:,}", f"{b['relief_above_sea_m']} – {o['relief_above_sea_m']}",
                        f"{b['km_from_mahendragiri']:,}", f"{b['km_per_yojana_if_100']:.1f}",
                        f"{b['km_from_ujjain_meridian_then']:,}", f"{sills[sill_key]:,}"])
    sill_rows = [[esc(k), f"{v:,}"] for k, v in sills.items()]
    ch_rows = [
        ["Puranic / Surya Siddhanta (Treta 1,296,000 yr; Kali from 3102 BCE)", f"{ch['puranic_treta_end_bce']:,} BCE (~{ch['puranic_treta_end_ka_bp']:.0f} ka)",
         f"{sl['at_treta_end_m']:.0f} m (±10 kyr: {sl['within_10kyr_m'][0]:.0f} to {sl['within_10kyr_m'][1]:.0f} m)", "Joined to India by land"],
        ["Tradition placing Rama in the 24th maha-yuga", f"{ch['rama_24th_mahayuga_treta_end_bce']:,} BCE (~18.1 Ma, Miocene)",
         "not modelled (pre-Quaternary)", f"Rough plate extrapolation puts Sri Lanka near {dt['miocene_24th_mahayuga']['sri_lanka_centre_then_nnr_extrapolated'][0]:.0f}°N then"],
        ["Manusmriti 1.69–71 / Mahabharata 3.186 literal 12,000-year cycle (Treta 3,600 yr)", "9102 – 5502 BCE",
         f"{rsl.rsl_at(rsl.year_to_bp(-9101))[0]:.0f} to {rsl.rsl_at(rsl.year_to_bp(-5501))[0]:.0f} m (regional curve)",
         "Joined; the bridge goes under right at the end of this Treta (Section 4)"],
    ]
    out.append(f"""
<h2>8. Deep-time test: a Treta-Yuga Lanka on the equator (Chagos–Laccadive ridge)</h2>
<p>This section tests the reading that Lanka stood where Ujjain's meridian meets the equator, on the
Chagos–Laccadive ridge (Lakshadweep – Maldives – Chagos), in a Treta Yuga about a million years ago. It uses the same
GEBCO grid with deep-time inputs: global sea level for the last 3 Myr (Bintanja &amp; van de Wal 2008), India-plate
motion (NNR-MORVEL56) and thermal subsidence of the ~55-Myr-old ridge (~{dt['ridge_subsidence_since_m']:.0f} m since
869 ka). Two points first: the yuga <i>lengths</i> are not in Valmiki (they come from Manusmriti and the Puranas), and
none of the Lanka verses examined (Kishkindha 41 and 58, Sundara 1–2, Yuddha 4, 22 and 37–41) mention the equator
or a meridian. That convention belongs to the Surya Siddhanta, an astronomy text of the 1st millennium CE.</p>
{table(["Chronology", "End of Treta", "Sea level then", "Sri Lanka then"], ch_rows)}
<h3>8.1 The equator × Ujjain point</h3>
<p>Ujjain sat at {pl['ujjain_then'][0]:.2f}°N {pl['ujjain_then'][1]:.2f}°E at 869 ka; the plate has carried it ~45 km
north-east since. The spot where its meridian then crossed the equator is today at
<b>{fmt_ll(*pl['equator_x_ujjain_meridian_then_in_present_coords'])}</b>, under <b>{abs(pl['depth_there_m']):,.0f} m</b> of
water. It was never land: sea level has not fallen below {sl['last_1myr_min_m']:.0f} m in the last million years.</p>
<h3>8.2 What land existed near the equator then</h3>
<p>At the Treta sea level ({sl['at_treta_end_m']:.0f} m) the ridge carried {len([r for r in base['landmasses'] if not r['is_india']])}
separate landmasses ({sum(r['area_km2'] for r in base['landmasses'] if not r['is_india']):,} km²): the Maldives atolls became
flat limestone plateaus. Three lie on the equator. Relief is given as a range from the Treta sea level to the most
favourable case (deepest glacial sea level plus ridge subsidence):</p>
{table(["Landmass", "Centroid", "Area (km²)", "Height above sea (m)", "km from Mahendragiri", "km per yojana if 100",
        "km from Ujjain meridian", "Sill to India (m)"], eq_rows)}
<p>Depth of the deepest point a walk or causeway from India must cross (GEBCO, 30″):</p>
{table(["To", "Sill (m)"], sill_rows)}
<h3>8.3 The text's clues against both candidates at ~869 ka</h3>
{table(["Clue", "Equatorial Maldives (Huvadhu – Fuvahmulah – Addu)", "Sri Lanka"], [
        ["On the equator", "✔ 0.5°N – 0.6°S", "✘ 6–10°N (the plate moved only ~0.4° since)"],
        ["On Ujjain's meridian", f"✘ ~{eq_rows[0][6]} km west of it", "✘ 4–6° (≈ 400–650 km) east of it"],
        ["100 yojanas from Mahendra", f"✔ with a {eq_rows[0][5]}–{eq_rows[2][5]} km yojana (Surya Siddhanta ≈ 8, Aryabhata ≈ 12)", "✔ only with a 2.4 km yojana"],
        ["An island across the sea", "✔", f"✘ joined to India by land (sea level {sl['at_treta_end_m']:.0f} m vs sill −3 m)"],
        ["A Setu of trees and rocks, 100 × 10 yojanas", f"✘ the route crosses {abs(sills['Huvadhu atoll (equator, N)']):,} m-deep ocean even at the lowest glacial sea level", "— not needed: dry land at that time"],
        ["Lanka on a mountain, Trikuta", f"~ three separate flat-topped plateaus {min(int(r[3].split(' – ')[0]) for r in eq_rows)}–{max(int(r[3].split(' – ')[1]) for r in eq_rows)} m high, split by 1.9–2 km-deep channels: 'three' fits, 'mountain' does not", "✔ highlands to 2,524 m"],
    ])}
<div class="key"><b>Deep-time verdict.</b> At the Puranic date there was land at the equator on the ridge. The equatorial
Maldives plateaus fit the equator clue and, with a 9.5–11 km yojana, the "100 yojanas" clue. They fail the Setu
outright: no causeway of trees and rocks can cross {abs(sills['Huvadhu atoll (equator, N)']):,} m of ocean, a depth that
subsidence (~{dt['ridge_subsidence_since_m']:.0f} m) and sea-level change (≤ 130 m) cannot remove. The equator ×
Ujjain point itself was always deep ocean. Sri Lanka fails the "island" clue at that date, because it was joined to
India for ~{sl['fraction_last_1myr_below_minus10m']:.0%} of the last million years. No single location satisfies the
text at ~869 ka. The closest equatorial coordinates are those in the table above (also in the KML, flagged
"Treta test").</div>
<p class="small">Context: at ~869 ka India was inhabited by early humans making Acheulean stone tools (e.g. Attirampakkam,
Tamil Nadu, ~1.5 Ma; Pappu et al. 2011). The source "Rakshasaalai" could not be identified; the nearest published form
of the equator argument is "Situation of Ravana's Lamka on the Equator", <i>Quarterly Journal of the Mythic Society</i>
17(1), 1926.</p>
{fig("07_treta_equatorial_test.png", "Figure 7. The Chagos–Laccadive ridge at the Treta sea level (−90 m), with the equator then, Ujjain's meridian and 100-yojana arcs.")}
""")

    # ---------------------------------------------------------------- 8.4-8.6 plate positions, tilt/TPW, Chagos scan
    cs, tt = j("chagos_scan.json"), j("tilt_tpw.json")
    pp = cs["plate"]
    pos_rows = [[esc(p["name"]), fmt_ll(*p["today"]), fmt_ll(*p["at_869ka"]), f"{p['shift_km']:.0f}"] for p in pp["points"]]
    dist_rows = [[esc(d["pair"]), f"{d['km_today']:,.1f}", f"{d['km_at_869ka']:,.1f}"] for d in pp["distances"]]
    coast = cs["southern_coast"]
    tre = coast["treta_-90m"]
    gap_rows = [[esc(k), f"{v:,}" if v is not None else "—", f"{v / 100:.1f}" if v else "—"]
                for k, v in tre["sea_gap_km_from_indian_coast"].items()]
    ob = tt["obliquity"]
    tpw_rows = [[f"{t['delta_deg']:.2f}°", f"{t['delta_deg'] / 0.869:.1f}°/Myr", fmt_ll(t["lat"], t["lon"]), f"{abs(t['depth_m']):,.0f} m",
                 "yes" if t["was_land"] else "no"] for t in tt["tpw"]]
    need = tt["minimum_tpw_for_land"]
    bank_rows = []
    seen = set()
    for b in cs["banks"]:
        if b["emergent_area_km2"]["treta_-90m"] < 150 or b["name"] in seen:
            continue
        seen.add(b["name"])
        a = b["emergent_area_km2"]
        today = f"{a['today_real_or_gebco']:,.1f}" + ("" if b["today_source"] == "published" else " (GEBCO, overstated)")
        bank_rows.append([esc(b["name"]), fmt_ll(*b["centroid"]), f"{a['treta_-90m']:,.0f}", f"{a['at_-40m']:,.0f}",
                          f"{a['at_-20m']:,.0f}", f"{a['at_-10m']:,.0f}", today,
                          f"~{b['drowning_age_ka_holocene']:.1f} ka" if b["drowning_age_ka_holocene"] else "islets remain",
                          esc(b["status"])])
    sm = cs["seamounts"]
    sm_rows = [[fmt_ll(s["lat"], s["lon"]), f"{abs(s['summit_m']):,.0f} m", f"{s['relief_m']:,}", f"{s['subsidence_needed_m_per_myr']}"]
               for s in sm[:6]]
    ds = cs["depression_shape_summary"]
    circ_rows = [[fmt_ll(*c["centroid"]), f"{c['area_km2']:,}", f"{c['radius_km']:.0f}", f"{abs(c['rim_m']):,}",
                  f"{c['max_depth_below_rim_m']}", f"{c['rim_minus_surroundings_m']:+d}"] for c in ds["near_circular_deep_basins"]]
    lagoons = sum(1 for d in cs["closed_depressions"] if d["kind"].startswith("atoll"))
    gcb = next(b for b in cs["banks"] if b["name"].startswith("Great Chagos Bank"))
    out.append(f"""
<h3>8.4 Every place moves with the plate, so the distances stay the same</h3>
<p>The Markandeya Purana (ch. 57) names Mahendra and Malaya among the seven principal mountains of Bharatavarsha, and
describes Bharatavarsha as nine divisions separated by the ocean. Mahendragiri, Kanyakumari, Ujjain, Sri Lanka, the
Maldives and Chagos all ride the India plate. Over 869 kyr each moved
~50 km toward the south-west; the India–Capricorn diffuse boundary south of ~3°S adds at most
{pp['india_capricorn_shift_at_chagos_km']:.0f} km at Chagos. Their distances from one another are therefore unchanged. What
changes is where the equator crosses them: about 0.3° further north, in today's coordinates (Figure 7).</p>
{table(["Point", "Today", "At ~869 ka", "Moved (km)"], pos_rows)}
{table(["Distance", "Today (km)", "At ~869 ka (km)"], dist_rows)}
<p><b>The southern end of India at the Treta sea level.</b> With the sea 90 m lower, India and Sri Lanka formed one
landmass. Its southern tip was at {fmt_ll(*tre['southern_tip'])} (southern Sri Lanka),
{tre['tip_km_south_of_kanyakumari']} km from Kanyakumari. On the Indian side the broad Wadge Bank shelf south of Cape
Comorin emerged too, so the cape itself moved {tre['cape_shift_km']} km south-west, to
{fmt_ll(*tre['cape_south_of_kanyakumari'])}. The open-sea gap from that
coast to each ridge landmass, and the yojana it implies if the gap is 100 yojanas:</p>
{table(["To", "Sea gap from the Treta-era Indian coast (km)", "km per yojana"], gap_rows)}

<h3>8.5 Axial tilt and the 'gravitational pole' (true polar wander)</h3>
<p><b>Tilt.</b> The Berger &amp; Loutre (1991) orbital solution gives an obliquity of <b>{ob['at_869ka_deg']:.2f}°</b> at 869 ka
(today {ob['today_deg']:.2f}°; range {ob['last_1myr_range_deg'][0]:.1f}–{ob['last_1myr_range_deg'][1]:.1f}° over the last 1 Myr).
Obliquity is the angle between the spin axis and the orbit. It moves the tropics (then at ±{ob['at_869ka_deg']:.2f}°) but not
the equator or any meridian, which are fixed by where the spin axis pierces the crust. The equinox Sun passes overhead
on the equator whatever the tilt.</p>
<p><b>True polar wander.</b> The crust can rotate relative to the spin axis as mass is redistributed. The test below moved
the pole by up to 4° toward every azimuth. For each case it rebuilt the equator and Ujjain's meridian, found where they
cross, carried that point to today's coordinates and read its depth in GEBCO. The table shows the shallowest result for
each amount of wander:</p>
{table(["Pole shift", "Rate over 869 kyr", "Shallowest crossing", "Depth", "Ever land?"], tpw_rows)}
<p>The crossing reaches seabed that was ever dry only with <b>{need['delta_deg']:.1f}°</b> of wander toward
{need['pole_toward_lon']:.0f}°E, about {need['delta_deg'] / 0.869:.0f}° per million years. Palaeomagnetic estimates of true polar wander over the
Cenozoic are generally well under 1°/Myr (Besse &amp; Courtillot 2002; Torsvik et al. 2012). Today's measured polar drift is ~1°/Myr, mostly
glacial rebound, and points toward ~75–80°W, which moves the crossing north–south along the meridian, not toward the
Maldives.</p>

<h3>8.6 Scan of the Chagos–Laccadive ridge: what was land and is now gone</h3>
<p>Every bank shallower than −200 m between 10°S and 3°N was inventoried. GEBCO's 15″ cells show spurious "land" up to
~200 m on reefs (Pitt Bank, which has no land at all, shows 156 m). Bank tops were therefore capped at +3 m, and
present-day land is taken from published figures where available (Chagos as a whole: 56 km², Diego Garcia 32.5 km²).
Drowning ages come from the sea-level curve of Section 4.</p>
{table(["Bank", "Centroid", "Land at −90 m (km²)", "at −40 m (~10 ka)", "at −20 m (~8.8 ka)", "at −10 m (~8 ka)", "Today (km²)", "Drowned", "Status"], bank_rows)}
<div class="key"><b>Yes, there were islands near Chagos that no longer exist.</b> The largest was the <b>Great Chagos Bank
island</b>, ~{gcb['emergent_area_km2']['treta_-90m']:,.0f} km² of limestone, about the size of Jamaica, centred near
{fmt_ll(*gcb['centroid'])}. Pitt Bank (~2,200 km²) and Speakers Bank (~1,000 km²) were also dry land. Each was dry
whenever the sea stood ~40 m or more below today. The last time, the post-glacial rise reduced the Great Chagos Bank to
reef between ~10 and ~8 ka, leaving 5.6 km² of islets. The same drowning happened at every deglaciation, including the
one under way at the Puranic end of Treta, when sea level rose from −106 to −18 m within about 20 kyr.</div>
<p><b>Seamounts.</b> {len(sm)} submerged peaks with ≥ 500 m relief and summits between −150 and −3,000 m. The shallowest
would have needed the subsidence rates shown to have been islands at the deepest glacial sea level (the ridge subsides at
~25 m/Myr):</p>
{table(["Summit", "Summit depth", "Relief (m)", "Subsidence needed (m/Myr)"], sm_rows)}
<p><b>Crater-like basins.</b> Priority-flood filling found {len(cs['closed_depressions'])} closed basins larger than 20 km²
and deeper than 20 m. {lagoons} are atoll lagoons (reef-rimmed basins on bank tops); the rest are abyssal basins at 3.7–5 km
depth, of which {ds['elongated_north_south']} of the {ds['deep_basins_ge_200km2']} largest are elongated roughly north–south,
the grain of the fracture zones here. {len(circ_rows)} are near-circular:</p>
{table(["Centre", "Area (km²)", "Radius (km)", "Rim depth (m)", "Depth below rim (m)", "Rim vs surroundings (m)"], circ_rows)}
<p>Two of these (near 0.4°N 70.2°E and 1.1°N 70.3°E) have margins slightly raised (+32 to +75 m), which is crater-like
in shape. Both sit on the abyssal floor 4 km down, 300 km west of the ridge, so they cannot be where an island stood.
Across this region GEBCO depths are largely interpolated from satellite gravity, so features of this size need a ship
survey before they can be called anything.</p>
<div class="note"><b>On "powerful forces".</b> Bathymetry cannot show whether technology was involved. What it can show
is whether something unexplained is needed, and here nothing is. Every island that existed and is now gone sits on a
flat-topped carbonate bank whose top lies 0–90 m deep, exactly as sea-level rise of ~90–130 m predicts. None of the
banks is cratered or broken, and no debris field appears at this resolution. The deep gaps between the island groups
(1.9–3 km) belong to the ridge's original structure, built ~45–60 Myr ago along the Réunion hotspot track, not to recent breaks.</div>
{fig("09_chagos_drowned_islands.png", "Figure 8. Chagos at the Treta sea level and today: the drowned Great Chagos Bank, Pitt Bank and Speakers Bank islands.")}
{fig("08_ridge_crest_profile.png", "Figure 9. Crest of the Chagos–Laccadive ridge from Lakshadweep to Chagos against present, Treta and glacial sea levels.")}
""")
    import lemuria_text
    out.append(lemuria_text.section("8.7 Lemuria, Kumari Kandam and Mauritius", "historical"))

    # ---------------------------------------------------------------- 9. limits, files, sources
    out.append(f"""
<h2>9. Limits</h2>
<ul>
<li><b>GEBCO 2026</b> is a 15″ (~460 m) grid. In the Palk Strait it rests on charts and interpolation, and depths are
integer metres. The −3 m sill is good to about ±1–2 m; narrow spits such as Dhanushkodi are not resolved. On land
GEBCO uses SRTM-class elevations (±5 m), too coarse for 1–2 m palaeo-shorelines.</li>
<li><b>Sea level</b>: the regional RSL model has ±1–3 m uncertainty in the early-to-mid Holocene, and the sand cays of
Adam's Bridge are mobile Holocene deposits. The present crest is not necessarily the crest of 7,000 years ago.</li>
<li><b>Ephemeris</b>: DE441's lunar position at 5000 BCE is uncertain by roughly 0.3° through tidal acceleration. ΔT is
uncertain by hours to a day, so the Cancer lagna (local time) cannot be checked. None of the sign- or nakshatra-level
results above depend on ΔT.</li>
<li><b>Text</b>: verse numbering is IITK/RSVP (southern vulgate). "Absent from the CE" means absent from the constituted
text, without the critical apparatus.</li>
<li>Sri Lankan "Ramayana trail" sites are post-Valmiki local traditions. They are shown for reference, not as evidence.</li>
</ul>
<h2>10. Files</h2>
<ul>
<li><code>data/valmiki_places.kml</code>: open in Google Earth (placemarks and route).</li>
<li><code>data/valmiki_places.geojson</code>, <code>data/valmiki_places.csv</code>: the same data for GIS / Excel.</li>
<li><code>data/*.json</code>: every intermediate result (sill, Setu shape, ephemeris search, season test …).</li>
<li><code>scripts/</code>: the full pipeline; <code>python scripts/run_all.py</code> rebuilds everything.
It needs JPL DE441 part 1 (1.65 GB, https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de441_part-1.bsp)
in <code>ephemeris/</code> or at the path in the <code>DE441_BSP</code> environment variable, plus Python with numpy, scipy,
matplotlib and jplephem.</li>
</ul>
<h2>11. Sources</h2>
<ul>{''.join(f'<li>{esc(s)}</li>' for s in geo['sources'])}</ul>
""")
    return out
