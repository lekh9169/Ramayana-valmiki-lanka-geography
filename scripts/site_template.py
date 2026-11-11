"""Shared page shell for the website: head, top bar, footer with the required data attributions."""
import hashlib
import html
from datetime import date
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "assets"


def v(name):
    """Asset URL with a content hash, so browsers and GitHub Pages never serve a stale copy after an update."""
    digest = hashlib.sha1((ASSETS / name).read_bytes()).hexdigest()[:10]
    return f"assets/{name}?v={digest}"

SITE_NAME = "Lanka and the places of the Valmiki Ramayana"
NAV = [("index.html", "home", "Overview"), ("report.html", "historical", "Historical edition"),
       ("report_treta_yuga.html", "treta", "Treta-Yuga edition"), ("map.html", "map", "Map"),
       ("data.html", "data", "Data"), ("about.html", "about", "Method and sources")]
FONTS = ("<link rel='preconnect' href='https://fonts.googleapis.com'>"
         "<link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>"
         "<link href='https://fonts.googleapis.com/css2?family=Hind:wght@400;500;600&family=Tiro+Devanagari+Sanskrit"
         "&display=swap' rel='stylesheet'>")
LEAFLET = ("<link rel='stylesheet' href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css' crossorigin=''>",
           "<script src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js' crossorigin=''></script>")
GEBCO_CITATION = "GEBCO Compilation Group (2026) GEBCO 2026 Grid (doi: 10.5285/4f68d5c7-45eb-f999-e063-7086abc036fa)"


def page(title, body, active, description, body_class="", leaflet=False, scripts=()):
    nav = "".join(f"<a href='{href}'{' aria-current=\"page\"' if key == active else ''}>{label}</a>"
                  for href, key, label in NAV)
    head_extra = LEAFLET[0] if leaflet else ""
    tail = (LEAFLET[1] if leaflet else "") + "".join(f"<script src='{v(s)}' defer></script>" for s in ("site.js", *scripts))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<meta name="description" content="{html.escape(description)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:image" content="assets/og.png">
<title>{html.escape(title)}</title>
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
{FONTS}
<link rel="stylesheet" href="{v('site.css')}">
{head_extra}
</head>
<body class="{body_class}">
<header class="topbar">
  <div class="topbar-inner">
    <a class="brand" href="index.html">Lanka <span>&amp;</span> the Valmiki places</a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav">Menu</button>
    <nav class="nav" id="site-nav" aria-label="Site">{nav}</nav>
  </div>
</header>
{body}
<footer class="footer">
  <div class="footer-inner">
    <div>
      <p>Bathymetry and land elevation: {html.escape(GEBCO_CITATION)}. The GEBCO Grid must not be used for navigation
      or for any purpose involving safety at sea. This site is an independent study and is not endorsed by GEBCO,
      the IHO or the IOC.</p>
      <p>Planetary positions from JPL DE441/DE440s (NASA). Sea-level reconstructions from NOAA's World Data Service
      for Paleoclimatology. Site coordinates from Wikipedia, &copy; OpenStreetMap contributors and Indian district
      portals. Full credits on <a href="about.html">Method and sources</a>.</p>
    </div>
    <div>
      <p>Two readings of one dataset: a <a href="report.html">historical edition</a> and a
      <a href="report_treta_yuga.html">Treta-Yuga edition</a>. Every number on this site is recomputed by the scripts in
      this repository.</p>
      <p>Built {date.today().strftime('%d %B %Y')}.</p>
    </div>
  </div>
</footer>
{tail}
</body>
</html>
"""


def report_shell(sections_html, edition):
    """Wrap a long report in the two-column layout with a contents panel."""
    badge = {"historical": "Historical edition", "treta": "Treta-Yuga edition"}[edition]
    return f"""<main class="edition-{edition}">
  <div class="wrap report-grid">
    <nav class="toc" aria-label="On this page"><p>On this page</p><ol></ol></nav>
    <article class="report-body"><span class="edition-badge">{badge}</span>
      <details class="toc-mobile"><summary>On this page</summary><ol></ol></details>{sections_html}</article>
  </div>
</main>"""
