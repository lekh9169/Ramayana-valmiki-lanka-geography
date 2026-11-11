"""Build the website pages that are not reports: home (index.html), map.html, data.html, about.html,
plus the favicon and the social preview image. Reports are built by build_report.py / build_treta_report.py."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import plotlib
import rsl
import site_template
from build_report import esc, j, table

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


def ll(v):
    lat, lon = v
    return f"{abs(lat):.4f}°{'N' if lat >= 0 else 'S'}, {lon:.4f}°E"


def bce(y):
    if y > 0:
        return f"{y} CE"
    n = 1 - y
    return f"{n:,} BCE" if n >= 10000 else f"{n} BCE"


def home():
    sky, geo, sill, search, season = j("treta_sky.json"), j("treta_geo.json"), j("sill_results.json"), j("rama_birth_search.json"), j("season_test.json")
    dt, cs = j("deep_time.json"), j("chagos_scan.json")
    breach = rsl.bp_to_year(rsl.age_when_level_crossed(sill["sill_all_m"])["central_ka"])
    lahiri_h = next(r for r in search["runs"] if r["ayanamsa_offset_deg"] == 0.0)
    lahiri_t = sky["anchors"]["Spica = 180° (Lahiri / Chitra-paksha)"]
    places = {p["id"]: p for p in j("places_computed.json")}
    g = {p["id"]: p for p in geo["places"]}
    gcb = next(b for b in cs["banks"] if b["name"].startswith("Great Chagos Bank"))
    coord_rows = []
    for pid in ("ayodhya", "prayaga", "chitrakuta", "panchavati", "kishkindha", "malaya", "mahendra", "tamraparni",
                "setu_start", "setu_end", "lanka_island"):
        p, r = places[pid], g[pid]
        shore = r.get("treta_shore")
        coord_rows.append([f"<b>{esc(p['name'])}</b>", ll((p["lat"], p["lon"])), esc(p["identification"]),
                           f"{shore['km_to_sea']:.0f} km to the sea" if shore else "inland"])
    tags = [("Madurai", 9.925, 78.12, ""), ("Kanyakumari", 8.078, 77.55, ""), ("Rameswaram", 9.288, 79.317, ""),
            ("Adam's Bridge", 9.13, 79.58, "bridge"), ("Mannar", 8.98, 79.90, ""), ("Jaffna", 9.66, 80.01, ""),
            ("Trincomalee", 8.58, 81.23, ""), ("Colombo", 6.93, 79.86, ""), ("Sri Pada", 6.81, 80.50, "")]
    tag_html = "".join(f"<span class='tag {cls}' data-lat='{la}' data-lon='{lo}'>{name}</span>" for name, la, lo, cls in tags)
    treta_level = geo["sea_level_m"]["treta_end"]
    body = f"""
<section class="hero" aria-labelledby="hero-title">
  <div class="hero-inner">
    <div>
      <h1 id="hero-title">Lanka and the places of the Valmiki Ramayana, measured</h1>
      <p class="lede">The seafloor between India and Sri Lanka decides much of the story. Lower the sea and watch when
      Adam's Bridge stands dry, when Sri Lanka becomes an island, and what the coast looked like at the end of the
      Treta Yuga.</p>
      <div class="readout" aria-live="polite">
        <div class="level" id="level-value">0<small>m</small></div>
        <p class="when" id="level-when"></p>
        <p class="state" id="level-state"></p>
      </div>
      <div class="slider">
        <label for="sea">Lower the sea</label>
        <input id="sea" type="range" min="0" max="1000" step="1" value="100">
        <div class="ends"><span>+2 m</span><span>−130 m</span></div>
        <div class="jumps"><span>Jump to</span>
          <button type="button" data-level="0">Today</button>
          <button type="button" data-level="-3.5">Bridge surfaces</button>
          <button type="button" data-level="-10">Rock sill</button>
          <button type="button" data-level="{round(treta_level)}">End of Treta</button>
          <button type="button" data-level="-128">Ice age</button>
        </div>
      </div>
      <div class="hero-actions">
        <a class="btn btn-primary" href="report.html">Read the historical edition</a>
        <a class="btn btn-quiet" href="report_treta_yuga.html">Read the Treta-Yuga edition</a>
        <a class="btn btn-quiet" href="map.html">Open the map</a>
      </div>
    </div>
    <div class="relief">
      <canvas id="relief" role="img" aria-label="Relief of southern India and Sri Lanka from GEBCO 2026, flooded to the chosen sea level"></canvas>
      {tag_html}
      <span class="credit">GEBCO 2026</span>
    </div>
  </div>
</section>
<main>
  <div class="wrap">
    <h2>Two timelines, one dataset</h2>
    <p>The same bathymetry, Sanskrit text and astronomy are read twice. The historical edition follows the text's own
    month–season clues to the last few thousand years. The Treta-Yuga edition takes the Puranic chronology at its word
    and recomputes the sky and the sea for about 870,000 years ago.</p>
    <div class="split">
      <section class="historical">
        <h3>Historical edition</h3>
        <dl>
          <dt>Epoch</dt><dd>{bce(season['all_pass_span'][0])} or later</dd>
          <dt>Sea level</dt><dd>About today's</dd>
          <dt>Sri Lanka</dt><dd>An island since about {bce(breach)}</dd>
          <dt>Lanka</dt><dd>Sri Lanka</dd>
          <dt>Setu</dt><dd>Adam's Bridge: 32–46 km of shoal, 0–3 m deep</dd>
          <dt>Birth sky</dt><dd>Four planets exalted on {', '.join(m['date'].split(' (')[0] for m in lahiri_h['matches'])}</dd>
        </dl>
        <a class="go" href="report.html">Read the historical edition</a>
      </section>
      <section class="treta">
        <h3>Treta-Yuga edition</h3>
        <dl>
          <dt>Epoch</dt><dd>End of Treta, {sky['treta_end_bce']:,} BCE</dd>
          <dt>Sea level</dt><dd>{geo['sea_level_range_birth_to_treta_end_m'][0]:.0f} to {geo['sea_level_range_birth_to_treta_end_m'][1]:.0f} m</dd>
          <dt>Sri Lanka</dt><dd>Joined to India by dry land</dd>
          <dt>Lanka</dt><dd>No site passes every test; nearest equatorial land is the Huvadhu plateau</dd>
          <dt>Setu</dt><dd>Not needed for Sri Lanka; impossible across {abs(dt['sills_to_india_m']['Huvadhu atoll (equator, N)']):,} m of sea to the Maldives</dd>
          <dt>Birth sky</dt><dd>Four planets exalted in {', '.join(f"{w['start_bce']:,}" for w in lahiri_t['strict_windows'])} BCE</dd>
        </dl>
        <a class="go" href="report_treta_yuga.html">Read the Treta-Yuga edition</a>
      </section>
    </div>

    <h2>What the data show</h2>
    <ul class="findings">
      <li>Adam's Bridge is the only shallow link between India and Sri Lanka. Its crest lies 0–3 m below today's sea,
      and at the −4 m depth line it is about ten times longer than it is wide, as Valmiki's 100 × 10 yojanas says.</li>
      <li>The sea rose over the bridge about {bce(breach)}. Before that Sri Lanka was part of India and no causeway was
      needed.</li>
      <li>Rama's horoscope with five exalted planets cannot occur on any date. The ninth lunar day with the Moon in
      Punarvasu places the Sun in late Pisces, outside its exaltation sign.</li>
      <li>The month–season pairings of the Critical Edition hold only from about {bce(season['all_pass_span'][0])} onward.
      Older proposed dates put Chaitra in winter.</li>
      <li>At the end of Treta the sea stood about {abs(treta_level):.0f} m lower. The Palk Bay was dry land and the
      Tamraparni ran some 30 km further to the sea.</li>
      <li>The Surya Siddhanta's equatorial "Lanka", on Ujjain's meridian, lies under
      {abs(dt['plate']['depth_there_m']):,.0f} m of ocean and was never land.</li>
      <li>A limestone island of about {gcb['emergent_area_km2']['treta_-90m']:,.0f} km² once stood on the Great Chagos Bank. Rising sea
      level drowned it between about 10,000 and 8,000 years ago.</li>
      <li>Valmiki's distances imply a yojana anywhere from 0.3 km to 28 km. The text's numbers are poetic, not surveyed.</li>
    </ul>

    <h2>Explore the places</h2>
    <p>Every identification on one map, with the shore and coastline of the Treta epoch. Select a marker for the verse,
    the reasoning and the coordinates. <a href="map.html">Open the full map</a>.</p>
    <div id="map" class="map-preview" data-preview="true" role="region" aria-label="Preview map of the places"></div>

    <h2>Key coordinates</h2>
    {table(["Place", "Coordinates (today)", "Identification", "At the end of Treta"], coord_rows)}
    <p class="small">The full lists, with Sanskrit names, verse references and confidence, are in Section 7 of the
    historical edition and Section 1 of the Treta-Yuga edition. Download them as KML for Google Earth, GeoJSON or CSV on
    the <a href="data.html">Data</a> page.</p>
  </div>
</main>"""
    return site_template.page(site_template.SITE_NAME + ": a data-driven geography", body, "home",
                              "Where was Lanka? GEBCO 2026 bathymetry, JPL astronomy and the Sanskrit text locate Lanka, "
                              "the Setu and Rama's route on two timelines.", body_class="home", leaflet=True,
                              scripts=("hero.js", "map.js"))


def map_page():
    toggles = [("valmiki", "Places in Valmiki's text", "<span class='sw' style='background:#2B7A87'></span>"),
               ("tradition", "Later Sri Lankan traditions", "<span class='sw' style='background:#A8875A'></span>"),
               ("rejected", "Tested and rejected locations", "<span class='sw' style='background:#fff;box-shadow:0 0 0 2px #7C3B3B'></span>"),
               ("treta", "Treta-Yuga candidates and drowned islands", "<span class='sw' style='background:#B7791F'></span>"),
               ("treta_shore", "Shore at the end of Treta", "<span class='sw' style='background:#F3E2C2;box-shadow:0 0 0 2px #B7791F'></span>"),
               ("treta_coast", "Coastline at −90 m (end of Treta)", "<span class='ln' style='border-color:#B7791F'></span>"),
               ("route", "Narrative route", "<span class='ln' style='border-color:#0B2A45;border-top-style:dashed'></span>")]
    toggle_html = "".join(f"<label><input type='checkbox' value='{k}'> {sw} {label}</label>" for k, label, sw in toggles)
    flies = [("North India", "25.6,81.8,6.5"), ("Kishkindha (Hampi)", "15.34,76.48,11"), ("Palk Strait", "9.15,79.55,9"),
             ("Equatorial Maldives", "0.1,73.3,8"), ("Chagos", "-6.3,71.9,8"), ("Mauritius and the Mascarenes", "-15,59.5,6"), ("Whole region", "10,78,4.5")]
    fly_html = "".join(f"<button type='button' class='btn btn-quiet' style='color:var(--abyss);border-color:var(--rule)' data-fly='{v}'>{n}</button> " for n, v in flies)
    body = f"""<main class="map-main">
<div class="map-shell">
  <aside class="map-panel">
    <h1>Map of the places</h1>
    <p>Both editions on one map. Blue markers are today's identifications of places named in the text. Ochre shows the
    Treta-Yuga world: the shore and coastline at a sea level about 90 m lower, the equatorial candidates and the drowned
    banks of Chagos. Select any marker for its verse and coordinates.</p>
    <div class="layer-toggles">{toggle_html}</div>
    <p><label for="basemap">Base map</label><br>
    <select id="basemap"><option value="ocean">Ocean relief (Esri)</option><option value="osm">Streets (OpenStreetMap)</option></select></p>
    <p>Go to</p>
    <p style="display:flex;flex-wrap:wrap;gap:.4rem">{fly_html}</p>
    <p class="small">Marker shade shows confidence: darker for a direct textual fit, greyer for a weaker one. Coordinates are
    WGS84. The base map is for orientation only; every computed layer comes from GEBCO 2026.</p>
  </aside>
  <div id="map" role="region" aria-label="Map of the places of the Valmiki Ramayana"></div>
</div>
</main>"""
    return site_template.page("Map — " + site_template.SITE_NAME, body, "map",
                              "Interactive map of the places of the Valmiki Ramayana on both timelines.",
                              body_class="map-page", leaflet=True, scripts=("map.js",))


def data_page():
    files = [("data/valmiki_places.kml", "Google Earth file, historical edition: every place with its verse, identification and route."),
             ("data/valmiki_places_treta.kml", "Google Earth file, Treta-Yuga edition: the same places, the shore points of the time and the −90 m coastline."),
             ("data/valmiki_places.geojson", "All places as GeoJSON, for QGIS or web maps."),
             ("data/map_layers.geojson", "Every layer of the map on this site in one GeoJSON file."),
             ("data/valmiki_places.csv", "Spreadsheet of the places, historical edition."),
             ("data/valmiki_places_treta.csv", "Spreadsheet of the places with their plate positions and shores at the end of Treta."),
             ("data/rama_birth_search.json", "JPL DE441 search for the birth configuration, 13,000 BCE to 1 BCE."),
             ("data/treta_sky.json", "N-body sky of the Treta window: birth windows, seasons and star motions."),
             ("data/sill_results.json", "Depth of the India–Sri Lanka land bridge."),
             ("data/chagos_scan.json", "Scan of the Chagos–Laccadive ridge: drowned banks, seamounts and closed basins."),
             ("data/lemuria_mauritius.json", "Kumari Kandam, Lemuria and Mauritius tests: drowned shelf, Mascarene banks, ocean depths."),
             ("data/etopo/etopo2022_mascarene_1min.asc", "NOAA ETOPO 2022 relief of Mauritius and the Mascarene banks (1 arc-minute, Esri ASCII)."),
             ("data/rsl_curve.csv", "Relative sea-level curve used for the last 21,000 years, with sources."),
             ("data/geo_notes.json", "Verse table, river and coast notes, and the source list used by the reports.")]
    items = []
    for f, what in files:
        size = (ROOT / f).stat().st_size
        items.append(f"<li><a href='{f}' download>{Path(f).name}</a><span class='size'>{size / 1024:,.0f} KB</span><span class='what'>{esc(what)}</span></li>")
    figs = sorted((ROOT / "maps").glob("*.png"))
    fig_items = "".join(f"<li><a href='maps/{p.name}'>{p.name}</a><span class='size'>{p.stat().st_size / 1024:,.0f} KB</span></li>" for p in figs)
    body = f"""<main><div class="wrap">
<h1>Data</h1>
<p>Everything behind the two editions, ready to open in Google Earth, a GIS or a spreadsheet. Coordinates are WGS84
decimal degrees.</p>
<ul class="downloads">{''.join(items)}</ul>
<h2>Figures</h2>
<ul class="downloads">{fig_items}</ul>
<h2>Rebuild everything</h2>
<p>The <code>scripts</code> folder holds the full pipeline. With Python, numpy, scipy, matplotlib, jplephem and rebound
installed, and the GEBCO 2026 GeoTIFF on disk, run <code>python scripts/run_all.py</code>. Steps that need the JPL
ephemerides (DE441, 1.65 GB; DE440s, 32 MB) are skipped if those files are absent, and the saved results are reused.</p>
</div></main>"""
    return site_template.page("Data — " + site_template.SITE_NAME, body, "data",
                              "Downloads: KML, GeoJSON and CSV of the places, and every computed result.")


def about_page():
    geo = j("geo_notes.json")
    sources = "".join(f"<li>{esc(s)}</li>" for s in geo["sources"])
    body = f"""<main><div class="wrap prose">
<h1>Method and sources</h1>
<p>This is an independent, reproducible study. It asks whether the geography and the sky described in the Valmiki
Ramayana fit a real place and time. It tests that against measured data, and says plainly where the data cannot decide.</p>
<h2>How it was done</h2>
<ul>
<li><b>The text.</b> The geographic and astronomical verses were collected from the IIT Kanpur / RSVP edition and
checked against the Baroda Critical Edition. That separates the older layer of the poem from later additions.</li>
<li><b>The seafloor.</b> GEBCO 2026 at 15 arc-seconds gives the depth of the land bridge, the shape of Adam's Bridge,
coastlines at any sea level and a scan of the Chagos–Laccadive ridge.</li>
<li><b>Sea level.</b> A regional curve for the last 21,000 years (Lambeck et al. 2014 and Indian Ocean records), and
Bintanja &amp; van de Wal (2008) for the last 3 million years.</li>
<li><b>The sky, historical edition.</b> JPL DE441 positions every day from 13,000 BCE to 1 BCE, with a sidereal zodiac
anchored on Spica.</li>
<li><b>The sky, Treta-Yuga edition.</b> A REBOUND N-body integration from JPL DE440s back to 881,000 BCE. Its
relativistic drift was calibrated against DE441 through JPL Horizons. Earth's axis was precessed and checked against
Berger &amp; Loutre (1991), and anchor stars were moved with their Hipparcos space motions.</li>
<li><b>Tectonics.</b> India-plate motion from NNR-MORVEL56; true polar wander and axial tilt tested separately.</li>
</ul>
<h2>What it can and cannot say</h2>
<p>The method tests consistency. It cannot prove that events happened, and it does not date the poem. The Moon's
position, the calendar day and the time of day are beyond computation for the Treta epoch. Both editions list their
limits in full.</p>
<h2>Attribution and licences of the data</h2>
<ul>
<li>{esc(site_template.GEBCO_CITATION)}. The GEBCO Grid is in the public domain; it must not be used for navigation or
for any purpose involving safety at sea. This site is not endorsed by GEBCO, the IHO or the IOC.</li>
<li>Coordinates of sites: Wikipedia ({{{{coord}}}} data), &copy; OpenStreetMap contributors (ODbL) and Indian district
government portals, as listed per place.</li>
<li>Map tiles: Esri World Ocean Base and Reference; OpenStreetMap.</li>
<li>Paleoclimate data: NOAA World Data Service for Paleoclimatology (public domain).</li>
<li>Relief of Mauritius and the Mascarene banks: NOAA NCEI ETOPO 2022 (doi:10.25921/fd45-gt74), free to use and redistribute.</li>
<li>Ephemerides: NASA JPL (DE441, DE440s; Horizons).</li>
</ul>
<h2>Sources</h2>
<ul>{sources}</ul>
</div></main>"""
    return site_template.page("Method and sources — " + site_template.SITE_NAME, body, "about",
                              "How the study was done, its limits, and the sources and licences of its data.")


def favicon_and_og():
    (ASSETS / "favicon.svg").write_text(
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='14' fill='#0B2A45'/>"
        "<path d='M10 40c8-6 14-6 22 0s14 6 22 0' fill='none' stroke='#E3C98F' stroke-width='5' stroke-linecap='round'/>"
        "<circle cx='22' cy='24' r='5' fill='#9ED6CC'/><circle cx='42' cy='24' r='5' fill='#9ED6CC'/></svg>", encoding="utf-8")
    fig = plt.figure(figsize=(12, 6.3), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    plotlib.relief(ax, 6.6, 10.4, 76.7, 83.9, sea_level=-3.5, step=2, land_max=2200, sea_min=-4000)
    ax.set_axis_off()
    fig.text(0.04, 0.12, "Lanka and the places of the\nValmiki Ramayana, measured", fontsize=34, color="white",
             family="serif", va="bottom")
    fig.savefig(ASSETS / "og.png", dpi=100)
    plt.close(fig)


if __name__ == "__main__":
    for name, html_text in (("index.html", home()), ("map.html", map_page()), ("data.html", data_page()), ("about.html", about_page())):
        (ROOT / name).write_text(html_text, encoding="utf-8")
        print(ROOT / name)
    favicon_and_og()
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
