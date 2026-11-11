# Lanka and the places of the Valmiki Ramayana, measured

A data-driven geography of the Valmiki Ramayana. It tests where Lanka, the Setu and the places on Rama's route can be,
using GEBCO 2026 bathymetry, JPL ephemerides, sea-level reconstructions, plate motion and the Sanskrit text checked
against the Baroda Critical Edition.

The website presents two readings of the same data:

- **Historical edition** (`report.html`). The text's own month–season pairings date its sky to about 2950 BCE or
  later. Sea level is then close to today's, and Lanka is Sri Lanka, reached over Adam's Bridge.
- **Treta-Yuga edition** (`report_treta_yuga.html`). This takes the Puranic chronology, with the end of Treta in
  867,102 BCE. It recomputes the sky with an N-body integration, and the sea, coasts and plate positions for about
  870,000 years ago.

The home page (`index.html`) has an interactive relief of the Palk Strait. `map.html` puts every place of both editions
on one map. `data.html` lists every download.

## Run it locally

The site is static. Serve the folder with any web server, for example:

```bash
python -m http.server 8000
```

then open http://localhost:8000.

## Rebuild the analysis

```bash
pip install numpy scipy matplotlib pillow jplephem rebound
python scripts/run_all.py
```

Inputs that are not in this repository:

| Input | Where to get it | How the scripts find it |
|---|---|---|
| GEBCO 2026 GeoTIFF, 62.76–94.68°E, 35.67°S–33.94°N | https://download.gebco.net/ | `GEBCO_TIF`, or a `GEBCO_*` folder next to this one |
| JPL DE441 part 1 (1.65 GB) | https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/ | `DE441_BSP`, or `ephemeris/` |
| JPL DE440s (32 MB) | same | `DE440S_BSP`, or `ephemeris/` |

If an ephemeris is missing, `run_all.py` skips the steps that need it and reuses the saved results in `data/`.

## Layout

| Path | Contents |
|---|---|
| `index.html`, `report*.html`, `map.html`, `data.html`, `about.html` | the website (built by the scripts) |
| `assets/` | styles, scripts, the hero relief and the social image |
| `data/` | KML, GeoJSON, CSV and every computed result (JSON) |
| `data/paleo/` | NOAA sea-level and orbital data files used |
| `maps/` | figures |
| `scripts/` | the full pipeline; `run_all.py` runs it in order |

## Data credits

- GEBCO Compilation Group (2026) GEBCO 2026 Grid (doi: 10.5285/4f68d5c7-45eb-f999-e063-7086abc036fa). It is in the
  public domain and must not be used for navigation or for any purpose involving safety at sea. This project is not
  endorsed by GEBCO, the IHO or the IOC.
- NASA JPL DE441 and DE440s ephemerides, and JPL Horizons.
- NOAA World Data Service for Paleoclimatology: Bintanja & van de Wal (2008), Spratt & Lisiecki (2016), and Berger &
  Loutre (1991).
- Hipparcos new reduction (van Leeuwen 2007) and the Pulkovo radial velocities, via VizieR.
- Site coordinates: Wikipedia, © OpenStreetMap contributors (ODbL) and Indian district government portals.
- Valmiki Ramayana text: IIT Kanpur / RSVP and the GRETIL Critical Edition e-text.

The full source list is on `about.html` and in `data/geo_notes.json`.

## Limits

The method tests whether the text's geography and sky are consistent with a real place and time. It does not prove that
the events happened. Both editions state their uncertainties in full.
