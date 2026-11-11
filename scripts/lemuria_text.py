"""Shared report section: Lemuria, Kumari Kandam and Mauritius (numbers from data/lemuria_mauritius.json)."""
from build_report import esc, fig, j, table

# present-day land areas from published figures (the 1' relief overstates reef 'land'): Wikipedia, Nov 2026
PUBLISHED_LAND_KM2 = {"Mauritius": 1865, "Reunion": 2512, "Rodrigues": 108, "Saya de Malha Bank": 0, "Nazareth Bank": 0,
                      "Cargados Carajos (St Brandon)": 1.3}


def section(heading, edition):
    lm = j("lemuria_mauritius.json")
    kk, mas, lem = lm["kumari_kandam"], lm["mascarenes"], lm["lemuria"]
    t, g = kk["treta_-90m"], kk["glacial_-128m"]
    depth_rows = [[esc(k.replace("N 77.5E", "°N, 77.5°E")), f"{abs(v):,.0f} m"] for k, v in kk["ocean_depth_south_of_kanyakumari_m"].items()]
    mas_rows = []
    for r in mas:
        if not r.get("centroid"):
            continue
        mas_rows.append([esc(r["name"]), f"{PUBLISHED_LAND_KM2.get(r['name'], r['land_today_km2']):,}",
                         f"{r['land_treta_-90m_km2']:,.0f}", f"{r['land_glacial_-128m_km2']:,.0f}",
                         f"{r['km_from_mahendragiri']:,}", f"{r['km_per_yojana_if_100']:.0f}",
                         f"{r['km_from_equator']:,}", f"{r['km_from_ujjain_meridian']:,}"])
    mau = next(r for r in mas if r["name"] == "Mauritius")
    banks_128 = sum(r["land_glacial_-128m_km2"] for r in mas
                   if r.get("centroid") and ("Bank" in r["name"] or r["name"].startswith("Cargados")))
    focus = ("At the Puranic end of Treta the sea stood about 90 m lower, so the numbers that matter are those for −90 m."
             if edition == "treta" else
             "For the historical edition the sea stood near today's level and none of this land existed. The −90 m and "
             "−128 m columns show what the Treta and glacial readings would add.")
    return f"""
<h3>{heading}</h3>
<p><b>Where the ideas come from.</b> "Lemuria" was proposed in 1864 by the zoologist Philip Sclater. He wanted a sunken land
bridge to explain why lemur-like primates lived in Madagascar and South Asia. Continental drift made it unnecessary:
India and Madagascar were once joined and separated about 88 million years ago. Tamil tradition separately remembers
Pandya lands south of Kumari lost to the sea, among them Kapatapuram and the older Madurai. In the 19th and 20th
centuries the two ideas were merged as "Kumari Kandam" (Ramaswamy 2004). Some readers link Valmiki's "golden gate
(kavāṭa) of the Pandyas" (Kishkindha 41.19) to Kapatapuram by its name. {focus}</p>
<p><b>Kumari Kandam on the data.</b> The land south of India and around Sri Lanka that is sea today but was dry at low sea
level (GEBCO 2026):</p>
{table(["", "At −90 m (end of Treta)", "At −128 m (ice-age low)"], [
        ["Land of South India and Sri Lanka now under the sea", f"{t['land_now_under_sea_km2']:,} km²", f"{g['land_now_under_sea_km2']:,} km²"],
        ["of which the Palk Bay and Strait", f"{t['of_which_palk_bay_strait_km2']:,} km²", f"{g['of_which_palk_bay_strait_km2']:,} km²"],
        ["of which south of Kanyakumari (Wadge Bank)", f"{t['of_which_south_of_kanyakumari_km2']:,} km²", f"{g['of_which_south_of_kanyakumari_km2']:,} km²"],
        ["Southernmost dry land below Kanyakumari", f"{t['southernmost_land_below_india_lat']:.2f}°N", f"{g['southernmost_land_below_india_lat']:.2f}°N"]])}
<p>Beyond that shelf the sea floor falls away fast:</p>
{table(["Directly south of Kanyakumari", "Depth today"], depth_rows)}
<div class="key"><b>Kumari Kandam verdict.</b> A real lost land existed: about {g['land_now_under_sea_km2']:,} km² of plains,
including the whole Palk Bay, roughly the size of Sri Lanka itself. But it reached only about 80 km south of Kanyakumari.
Past {g['southernmost_land_below_india_lat']:.1f}°N the floor is ocean basin, 2–5 km deep, and it was never land in the age of
humans.</div>
<p><b>Lemuria on the data.</b> At the lowest sea level of the last million years, the whole Chagos–Laccadive ridge held
{lem['chagos_laccadive_land_at_-128m_km2']:,} km² of land in {lem['chagos_laccadive_landmasses']} separate pieces. The
Mascarene banks added about {banks_128:,.0f} km² at the same sea level (table below). Between them the open ocean has a median depth of
{abs(lem['median_depth_of_open_ocean_12S_5N_64_80E_m']):,} m. Between the Mascarene banks and Chagos the floor never rises
above {abs(lm['mascarene_to_chagos_sill_m']):,} m, and between India and the Maldives above 2,592 m. That is an archipelago
of drowned limestone banks, not a continent.</p>
<p><b>Mauritius.</b> Mauritius lies west of the GEBCO subset, so it was tested on NOAA ETOPO 2022 (1′). The banks of
the Mascarene Plateau were large islands at low sea level. Mauritius and Réunion, steep volcanoes, barely change.</p>
{table(["Island or bank", "Land today (km²)", "at −90 m", "at −128 m", "km from Mahendragiri", "km per yojana if 100", "km from equator", "km from Ujjain's meridian"], mas_rows)}
{table(["Clue", "Mauritius"], [
        ["On the equator", f"✘ {mau['km_from_equator']:,} km south of it (20°S)"],
        ["On Ujjain's meridian", f"✘ {mau['km_from_ujjain_meridian']:,} km west of it"],
        ["100 yojanas from Mahendra", f"✘ needs a {mau['km_per_yojana_if_100']:.0f}-km yojana, three times any traditional value"],
        ["An island across the sea", "✔"],
        ["A mountain (Trikuta)", "✔ volcanic peaks to 828 m; the three-peaked Trois Mamelles is a coincidence of shape (a French colonial name)"],
        ["A Setu of trees and rocks", f"✘ the sea between it and India is never shallower than {abs(lm['mascarene_to_chagos_sill_m']):,} m"]])}
<p><b>The real lost continent.</b> Zircon grains 660 million to over 3 billion years old, found in Mauritian sand and lava,
show that a fragment of ancient continental crust, named Mauritia, lies buried beneath Mauritius and the Mascarene
Plateau (Torsvik et al. 2013; Ashwal et al. 2017). It broke away from Madagascar between 84 and 61 million years ago and
was buried by hotspot lavas; Mauritius itself is less than 9 million years old. So the Indian Ocean does hide a sunken
piece of continent. It sank tens of millions of years before any human lived, and it lies 3,800 km from Mahendragiri at
20°S.</p>
{fig("11_kumari_kandam.png", "Kumari Kandam tested: the shelf that was dry at the ice-age low (sand), and the ocean depths beyond it.")}
{fig("10_mascarenes_mauritius.png", "Mauritius and the Mascarene banks at the Treta sea level and today (NOAA ETOPO 2022).")}
"""
