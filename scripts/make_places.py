"""Write data/places.json: every place with its Valmiki reference (IITK/RSVP numbering, CE in
brackets), the text clue, the best-supported identification and the coordinate source.
Coordinates were verified against Wikipedia / OpenStreetMap / district government pages.
"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
WP, OSM = "Wikipedia", "OpenStreetMap"

P = []


def add(id, name, short, sanskrit, refs, clue, ident, lat, lon, conf, src, **kw):
    P.append(dict(id=id, name=name, short=short, sanskrit=sanskrit, valmiki_refs=refs, text_clue=clue,
                  identification=ident, lat=lat, lon=lon, confidence=conf, coord_source=src, **kw))


# ---- North: Kosala to Chitrakuta -------------------------------------------------------
add("ayodhya", "Ayodhya", "Ayodhya", "अयोध्या", "1.5.5-6 (CE 1.5.5-6)",
    "Capital of Kosala, a great country on the bank of the Sarayu",
    "Ayodhya, Uttar Pradesh: Ram Janmabhoomi site on the right bank of the Sarayu (Ghaghara)",
    26.7956, 82.1943, "high", f"{WP} (Ram Mandir); OSM polygon 26.7939, 82.1942",
    route_order=1, on_overview=True, label_dx=0.3, label_dy=0.15, river="Sarayu (Ghaghara)")
add("shringaverapura", "Shringaverapura", "Shringaverapura", "शृङ्गवेरपुर", "2.50.25-26 (CE 2.44.1)",
    "Guha's town on the Ganga where Rama crossed the river",
    "Shringverpur (Singraur), Prayagraj district: excavated site on the Ganga bank",
    25.5873, 81.6418, "high", f"{WP}; OSM Shri Ram Ghat 25.5895, 81.6394",
    route_order=2, river="Ganga")
add("prayaga", "Prayaga (Bharadvaja's ashram)", "Prayaga", "प्रयाग / भरद्वाजाश्रम", "2.54.2-8 (CE 2.48.2-8)",
    "Bharadvaja's hermitage at the joining (sandhi) of the Ganga and Yamuna, reached by evening",
    "Bharadwaj Ashram, Colonelganj, Prayagraj (proxy: Bharadwaj Park); confluence = Triveni Sangam",
    25.4575, 81.8585, "high", f"{OSM} (Bharadwaj Park, proxy); Sangam {OSM} 25.4222, 81.8923",
    route_order=3, on_overview=True, label_dx=0.3, label_dy=-0.25, river="Ganga-Yamuna confluence",
    alternatives=[{"name": "Triveni Sangam (confluence point, migrates seasonally)", "lat": 25.4222, "lon": 81.8923}])
add("chitrakuta", "Chitrakuta", "Chitrakuta", "चित्रकूट", "2.54.28 (CE 2.48.25-26); 2.95.1 (CE 2.89.1)",
    "Hill 'ten krosha from here' (Prayaga) with the Mandakini river below it",
    "Kamadgiri hill, Chitrakoot (Kamta Nath temple); Mandakini at Ramghat",
    25.1714, 80.8532, "high", f"{OSM} (Kamta Nath Mandir)",
    route_order=4, on_overview=True, label_dx=-1.6, label_dy=0.1, river="Mandakini",
    alternatives=[{"name": "Ramghat on the Mandakini", "lat": 25.1776, "lon": 80.8704}])
add("atri", "Atri and Anasuya's ashram", "Atri ashram", "अत्र्याश्रम", "Ayodhya 117-119 (vulgate)",
    "Hermitage of Atri and Anasuya after leaving Chitrakuta",
    "Sati Anusuya ashram, Chitrakoot", 25.0733, 80.8674, "medium", OSM, route_order=5)
add("sharabhanga", "Sharabhanga's ashram", "Sharabhanga", "शरभङ्गाश्रम", "Aranya 5 (vulgate)",
    "Hermitage in the Dandaka forest", "Sarbhanga Ashram village, Satna district (village-centre proxy)",
    24.9114, 80.9246, "low", f"{OSM} (village boundary centre)", route_order=6)
# ---- Dandaka / Godavari ---------------------------------------------------------------------
add("panchavati", "Panchavati", "Panchavati", "पञ्चवटी", "3.13.13, 3.13.21, 3.15.12 (CE 3.12.13, 3.12.18, 3.14.12)",
    "Two yojanas from Agastya's ashram, near the Godavari, by a madhuka forest and a hill",
    "Panchavati, Nashik (Sita Gufa / Kalaram temple) on the Godavari",
    20.0067, 73.7936, "medium", OSM, route_order=7, on_overview=True, label_dx=0.3, river="Godavari",
    alternatives=[{"name": "Parnasala, Telangana (Godavari)", "lat": 17.9320, "lon": 80.8960,
                   "note": "Bhadrachalam tradition"}])
add("agastya_ashram", "Agastya's ashram (north)", "Agastya (Akole)", "अगस्त्याश्रम", "3.11-13 (CE 3.11-12)",
    "Two yojanas from Panchavati", "Agasti temple, Akole, on the Pravara (tradition only)",
    19.5490, 74.0023, "low", OSM)
add("janasthana", "Janasthana", "Janasthana", "जनस्थान", "Aranya 18-30",
    "Khara's district around Panchavati", "Nashik region (no specific site; city centre as stand-in)",
    19.9975, 73.7898, "low", f"{WP} (Nashik)")
# ---- Kishkindha ----------------------------------------------------------------------------
add("pampa", "Pampa lake and Matanga's ashram", "Pampa", "पम्पा", "3.73.10, 3.73.27-31 (CE 3.69.21-24); 4.1",
    "Lake reached travelling west from Kabandha; Matanga's ashram on its west bank; Rishyamuka 'in front of' it",
    "Pampa Sarovar near Hampi / Anegundi", 15.3538, 76.4774, "medium", f"{WP}; OSM 15.3537, 76.4775",
    route_order=8, on_overview=True, label_dx=0.3, label_dy=0.25, river="Tungabhadra (Pampa)")
add("rishyamuka", "Rishyamuka hill", "Rishyamuka", "ऋष्यमूक", "3.73.31 (CE 3.69.24); Kishkindha 1-5",
    "Sugriva's refuge hill near Pampa", "Rishyamukha hill across the Tungabhadra from Hampi",
    15.3408, 76.4667, "medium", OSM, route_order=9)
add("kishkindha", "Kishkindha", "Kishkindha", "किष्किन्धा", "Kishkindha 11-14; 4.27.26 (vulgate)",
    "Vali and Sugriva's cave-city near Rishyamuka and Prasravana", "Anegundi on the Tungabhadra",
    15.3527, 76.4919, "medium", WP, route_order=10, on_overview=True, label_dx=0.3, label_dy=-0.3,
    river="Tungabhadra")
add("prasravana", "Prasravana hill on Malyavat", "Prasravana", "प्रस्रवण / माल्यवत्", "4.27.1, 4.28.1 (CE 4.26.1, 4.27.1)",
    "Rama's monsoon camp on the back of Malyavat, not far from Kishkindha",
    "Malyavanta Raghunatha temple hill, Hampi", 15.3245, 76.4878, "medium", OSM, route_order=11)
# ---- The south -------------------------------------------------------------------------------
add("malaya", "Malaya mountain (Agastya's peak)", "Malaya / Agastya Mala", "मलय", "4.41.16 (CE 4.40.16); 6.4.97 (CE 6.4.65)",
    "Agastya seated on the summit of Malaya, south of the Kaveri, before the Tamraparni",
    "Agastya Mala (Pothigai), 1,868 m, southern Western Ghats", 8.6163, 77.2457, "high", WP,
    route_order=12, on_overview=True, label_dx=-2.9, label_dy=0.1)
add("tamraparni", "Tamraparni river (mouth)", "Tamraparni", "ताम्रपर्णी", "4.41.17-18 (CE 4.40.17-18)",
    "Great river with crocodiles, island-studded, entering the sea; crossed after Malaya",
    "Thamirabarani river mouth at Punnakayal, Thoothukudi district", 8.6413, 78.1273, "high", WP,
    coastal=True, on_overview=True, label_dx=0.3, label_dy=-0.25, river="Thamirabarani")
add("pandya_kavata", "Golden gate (kavata) of the Pandyas", "Pandya gate (Korkai)", "पाण्ड्यकवाट",
    "4.41.19 (CE 4.40.19)", "Golden pearl-studded gate of the Pandyas, after the Tamraparni and before the sea",
    "Korkai, the early-historic Pandya pearl port near the Thamirabarani mouth (now inland)",
    8.6333, 78.0667, "medium", f"{WP} (arc-minute precision)", coastal=True, river="Thamirabarani delta",
    alternatives=[{"name": "Madurai (translator's gloss)", "lat": 9.9195, "lon": 78.1193,
                   "note": "RSVP translator's identification"}])
add("mahendra", "Mahendra mountain", "Mahendra", "महेन्द्र",
    "4.41.20-21 (CE 4.40.20-21); 4.67.38-40 (CE 4.66.32-34); 6.4.95-96 (CE 6.4.63-64)",
    "Set by Agastya at the sea, 'plunging into the ocean'; Hanuman's launch point; Rama climbs it and sees the sea",
    "Mahendragiri, Tirunelveli-Kanyakumari border: summit 1,654 m (GEBCO 1,555 m)",
    8.3883, 77.5214, "high", WP, route_order=13, on_overview=True, label_dx=0.3, label_dy=-0.35,
    alternatives=[{"name": "Mahendragiri, Odisha (the Puranic Mahendra kula-parvata)", "lat": 18.9744, "lon": 84.3681,
                   "note": "fits Kishkindha 41's east-coast list, not the southern-sea episode"}])
add("ocean_shore", "Southern ocean shore (army camp)", "Kanyakumari", "दक्षिणसमुद्रतीर", "4.64.4 (CE 4.63.4); 6.4.97-98",
    "The army reaches the shore forest (velavana) of the southern ocean after Mahendra",
    "Kanyakumari (Cape Comorin), the shore nearest Mahendragiri", 8.0780, 77.5505, "medium",
    f"{OSM} (cape tip)", coastal=True)
add("setu_start", "Setu: Indian end", "Setu (Dhanushkodi)", "सेतु", "6.22.61-74 (CE 6.15.8-22); 6.126.19-21 (vulgate only)",
    "Causeway 100 yojanas long and 10 wide built by Nala 'in the middle of the ocean'",
    "Arichal Munai, tip of the Dhanushkodi spit: western end of Adam's Bridge (Rama Setu)",
    9.1504, 79.4491, "high", f"{OSM} (road-end monument; spit tip migrates)", coastal=True,
    route_order=14, on_overview=True, label_dx=-2.7, label_dy=0.35,
    alternatives=[{"name": "Ramanathaswamy temple, Rameswaram ('Setubandha', vulgate 6.126 only)", "lat": 9.2881, "lon": 79.3173},
                  {"name": "Thiruppullani / Darbhasayanam (mainland tradition)", "lat": 9.2827, "lon": 78.8244},
                  {"name": "Devipattinam / Navapashanam (mainland tradition)", "lat": 9.4719, "lon": 78.8934},
                  {"name": "Kodiakkarai Ramar Padam (Point Calimere tradition)", "lat": 10.3320, "lon": 79.8424}])
add("setu_end", "Setu: Lanka end", "Setu (Talaimannar)", "सेतु", "6.22.70 (vulgate: 'up to Suvela'; absent CE)",
    "The causeway reaches the far shore", "Talaimannar, west tip of Mannar island: eastern end of Adam's Bridge",
    9.1055, 79.7307, "high", f"{OSM}; pier 9.1087, 79.7303", coastal=True, route_order=15,
    on_overview=True, on_lanka_map=True, label_dx=0.3, label_dy=0.25, lk_dx=-0.75, lk_dy=0.07)
# ---- Lanka -------------------------------------------------------------------------------------
add("lanka_island", "Lanka (the island)", "Lanka = Sri Lanka", "लङ्का द्वीप",
    "4.41.24-25 (CE 4.40.24-25); 4.58.19-20 (CE 4.57.19-20); 5.2.1 (CE 5.2.1)",
    "Island beyond Mahendra across the southern ocean, 'a full 100 yojanas' away, itself '100 yojanas long'",
    "Sri Lanka (geographic centre): the only island off the Tamraparni/Pandya coast joined to it by a shoal",
    7.8731, 80.7718, "high", "Sri Lanka centroid (Wikipedia)", route_order=16, on_overview=True, on_lanka_map=True,
    label_dx=0.35, label_dy=0.0, lk_dx=0.08, lk_dy=-0.16)
add("lanka_city_sripada", "Lanka city on Trikuta: candidate A", "Trikuta? (Sri Pada)", "त्रिकूटशिखरे लङ्का",
    "5.2.1 (CE 5.2.1); 6.39.18-20 (CE 6.30.18-20)",
    "City on the summit of Trikuta, seen from Suvela 'as if hanging in the sky'",
    "Central highlands: Sri Pada (Adam's Peak), fabled as Trikuta; 2,243 m", 6.8094, 80.4997, "low", WP,
    on_lanka_map=True, lk_dx=-0.95, lk_dy=-0.05)
add("lanka_city_trinco", "Lanka city on Trikuta: candidate B", "Trikuta? (Trincomalee)", "त्रिकूट / Trikonamalai",
    "5.2.1; 6.39.18-20", "Name-based link Trikuta ~ Tiru-kona-malai",
    "Koneswaram on Swami Rock, Trincomalee (GEBCO ~30 m: not a mountain)", 8.5825, 81.2456, "low", WP,
    coastal=True, on_lanka_map=True, lk_dx=-0.15, lk_dy=0.1)
add("lamba", "Lamba peak (Hanuman's landing)", "Lamba", "लम्ब", "5.1.208 (CE 5.1.189)",
    "Hanuman lands on a peak of Mount Lamba, with ketaka, uddalaka and coconut trees",
    "Not identifiable: no Sri Lankan terrain of 100 m or more is in line of sight from the Setu landfall (GEBCO)",
    None, None, "low", "-")
add("suvela", "Suvela mountain", "Suvela", "सुवेल", "6.37.36, 6.38.3-18 (CE 6.29.1-17)",
    "Rama's first camp in Lanka; Lanka visible from its summit; a full-moon night",
    "Not identified by any source; the nearest hills of 300 m or more are ~148 km from the Setu landfall (GEBCO)",
    None, None, "low", "-")
# Sri Lankan tradition sites (post-Valmiki local traditions, shown for reference)
for id_, nm, sh, lat, lon, note, dx, dy, src in [
        ("ashoka_vatika", "Ashoka Vatika tradition: Seetha Amman temple", "Ashoka Vatika (trad.)", 6.9332, 80.8105, "Sita Eliya / Hakgala", 0.06, 0.05, WP),
        ("ravana_ella", "Ravana Ella falls / cave tradition", "Ravana Ella (trad.)", 6.8408, 81.0544, "Ella", 0.06, -0.08, WP),
        ("kelaniya", "Vibhishana tradition: Kelaniya Raja Maha Vihara", "Kelaniya (trad.)", 6.9531, 79.9185, "near Colombo", 0.06, 0.03, WP),
        ("ritigala", "Ritigala (Sanjivani tradition)", "Ritigala (trad.)", 8.1090, 80.6568, "766 m isolated massif", 0.06, 0.03, OSM),
        ("sigiriya", "Sigiriya (Ravana-palace folk tradition)", "Sigiriya (trad.)", 7.9569, 80.7597, "5th-century CE fortress", 0.06, 0.04, WP),
        ("ussangoda", "Ussangoda (Hanuman-fire tradition)", "Ussangoda (trad.)", 6.1000, 80.9894, "south coast", 0.06, 0.03, WP),
        ("rumassala", "Rumassala (Sanjivani tradition)", "Rumassala (trad.)", 6.0153, 80.2386, "Galle", 0.06, 0.03, OSM),
        ("wariyapola", "Wariyapola (Pushpaka airfield tradition)", "Wariyapola (trad.)", 7.6333, 80.2333, "Kurunegala", -0.7, 0.03, WP)]:
    add(id_, nm, sh, "", "(post-Valmiki local tradition)", "Sri Lankan Ramayana-trail tradition",
        f"{nm}: {note}", lat, lon, "low", src, on_lanka_map=True, lk_dx=dx, lk_dy=dy, tradition=True)
# ---- Rejected hypotheses (tested, for comparison) -------------------------------------------
add("lanka_surya_siddhanta", "Surya Siddhanta 'Lanka' (equator on Ujjain's meridian)", "Equatorial 'Lanka'", "लङ्का (सिद्धान्त)",
    "(astronomical convention, not Valmiki)", "Zero point of Indian astronomy: equator on the meridian of Ujjain",
    "Open ocean, 4,128 m deep (GEBCO): never land at any Quaternary sea level", 0.0, 75.7665, "low",
    "Derived: Ujjain Jantar Mantar longitude (Wikipedia)", rejected=True)
add("lanka_maldives", "Maldives hypothesis", "Maldives", "", "-",
    "Proposed on long-yojana distance readings", "Male atoll: separated from India by a 2,592 m deep sill (GEBCO)",
    4.1750, 73.5090, "low", "Wikipedia (Male)", rejected=True)
add("lanka_amarkantak", "Central-India hypothesis (M. V. Kibe)", "Amarkantak", "", "-",
    "Lanka at the Narmada source in the Amarkantak hills", "Amarkantak plateau: landlocked, ~700 km from the sea",
    22.6733, 81.7595, "low", WP, rejected=True)

# ---- Treta-Yuga (~869 ka) equatorial hypothesis: candidates from deep_time.py (GEBCO at -90 m) --------
add("treta_equator_point", "Equator x Ujjain meridian at the Puranic end of Treta (~869 ka)", "Treta equatorial point", "लङ्का (त्रेता)",
    "(astronomical convention; Surya Siddhanta)", "Lanka placed where Ujjain's meridian meets the equator",
    "Today's location of that point after India-plate motion since 869 ka: open ocean, 4,308 m deep (GEBCO)",
    0.2959, 75.7911, "low", "Computed: NNR-MORVEL56 rotation of (0°, Ujjain's then-longitude)", rejected=True, treta=True)
add("treta_huvadhu", "Equatorial ridge candidate A: Huvadhu atoll plateau", "Huvadhu (Treta test)", "",
    "Treta hypothesis (equatorial Lanka on the Chagos-Laccadive ridge)",
    "Largest land within 300 km of the equator at the Treta sea level (-90 m)",
    "Huvadhu atoll (Maldives) as an exposed limestone plateau: 3,737 km2, ~216 m above the Treta sea; "
    "949 km from Mahendragiri (100 yojanas at 9.5 km); 2,286 m-deep sill to India",
    0.519, 73.283, "low", "Computed from GEBCO 2026 at -90 m (centroid)", treta=True)
add("treta_fuvahmulah", "Equatorial ridge candidate B: Fuvahmulah plateau", "Fuvahmulah (Treta test)", "",
    "Treta hypothesis", "Second equatorial landmass at the Treta sea level",
    "Fuvahmulah (Maldives): 39 km2, ~109 m above the Treta sea; 1,065 km from Mahendragiri; channel to Huvadhu 1,995 m deep",
    -0.307, 73.433, "low", "Computed from GEBCO 2026 at -90 m (centroid)", treta=True)
add("treta_addu", "Equatorial ridge candidate C: Addu atoll plateau", "Addu (Treta test)", "",
    "Treta hypothesis", "Third equatorial landmass at the Treta sea level",
    "Addu atoll (Maldives): 206 km2, ~151 m above the Treta sea; 1,104 km from Mahendragiri; channel to Fuvahmulah 1,901 m deep",
    -0.636, 73.161, "low", "Computed from GEBCO 2026 at -90 m (centroid)", treta=True)

# ---- Islands of the Chagos-Laccadive ridge that existed at the Treta / glacial sea level and are now drowned -------
add("drowned_great_chagos", "Drowned island: Great Chagos Bank", "Great Chagos Bank (drowned)", "",
    "Treta / glacial-era land (chagos_scan.py)", "Land at -90 m that is now reef and lagoon",
    "~14,550 km2 limestone island at the Treta sea level (-90 m); reduced to reef ~10-8 ka by post-glacial sea-level rise; 5.6 km2 of islets today",
    -6.20, 71.90, "low", "Computed from GEBCO 2026 (bank centroid region)", treta=True, drowned=True)
add("drowned_pitt_bank", "Drowned island: Pitt Bank", "Pitt Bank (drowned)", "",
    "Treta / glacial-era land (chagos_scan.py)", "Land at -90 m that is now wholly submerged",
    "~2,180 km2 at -90 m; drowned ~7.3 ka; no land today", -7.05, 71.33, "low", "Computed from GEBCO 2026", treta=True, drowned=True)
add("drowned_speakers_bank", "Drowned island: Speakers Bank", "Speakers Bank (drowned)", "",
    "Treta / glacial-era land (chagos_scan.py)", "Land at -90 m that is now submerged",
    "~980 km2 at -90 m; drowned ~8.1 ka; negligible land today", -4.88, 72.33, "low", "Computed from GEBCO 2026", treta=True, drowned=True)
add("circular_basin_1", "Near-circular abyssal basin (unexplained in GEBCO)", "Circular basin 0.37N", "",
    "Bathymetric anomaly (chagos_scan.py)", "Closed, near-circular basin with a slightly raised margin",
    "~2,000 km2, 466 m deep below its rim at ~4,000 m depth; margin +32 m; needs a ship survey (GEBCO here is gravity-interpolated)",
    0.373, 70.207, "low", "Computed from GEBCO 2026", treta=True)
add("circular_basin_2", "Near-circular abyssal basin (unexplained in GEBCO)", "Circular basin 1.06N", "",
    "Bathymetric anomaly (chagos_scan.py)", "Closed, near-circular basin with a slightly raised margin",
    "~1,600 km2, 459 m deep below its rim at ~4,100 m depth; margin +75 m; needs a ship survey",
    1.056, 70.292, "low", "Computed from GEBCO 2026", treta=True)

# ---- Lemuria / Kumari Kandam / Mauritius (lemuria_mauritius.py; Mascarenes from NOAA ETOPO 2022) ----------------
add("kumari_wadge_bank", "Kumari Kandam test: Wadge Bank shelf south of Kanyakumari", "Wadge Bank (drowned)", "குமரிக்கண்டம்",
    "(Tamil tradition of lands lost south of Kumari)", "Land said to have stretched south of Kanyakumari before the sea took it",
    "Real drowned land: ~8,600 km2 of shelf south of Kanyakumari was dry at the Treta sea level (-90 m), reaching only to "
    "~7.4 N; beyond it the sea floor falls to 2,400 m at 6 N and 4,800 m at the equator (GEBCO)",
    7.60, 77.40, "low", "Computed from GEBCO 2026 (shelf centre)", treta=True, drowned=True)
add("palk_bay_plain", "Drowned plain of the Palk Bay", "Palk Bay plain (drowned)", "",
    "Treta / glacial-era land", "Dry land joining India and Sri Lanka at low sea level",
    "~26,000 km2 of plain between India and Sri Lanka, dry whenever the sea stood more than ~10 m below today",
    9.60, 79.55, "low", "Computed from GEBCO 2026", treta=True, drowned=True)
add("mauritius", "Mauritius (tested as Lanka)", "Mauritius", "", "(modern proposal; not in Valmiki)",
    "Island proposed by some as Lanka",
    "Volcanic island < 9 Myr old over the buried microcontinent 'Mauritia'; 20 S, 3,804 km from Mahendragiri "
    "(100 yojanas = 38 km each); the three-peaked Trois Mamelles is a coincidence of shape",
    -20.20, 57.55, "low", "Wikipedia (Mauritius)", rejected=True, treta=True)
add("reunion", "Reunion (Mascarene hotspot island)", "Reunion", "", "(context)", "Active hotspot volcano of the Mascarenes",
    "Summit 3,070 m; 4,039 km from Mahendragiri; barely larger at the Treta sea level", -21.12, 55.53, "low",
    "Wikipedia (Reunion)", treta=True)
add("drowned_saya_de_malha", "Drowned island: Saya de Malha Bank", "Saya de Malha (drowned)", "", "Treta / glacial-era land",
    "Bank that was a large island at low sea level",
    "~18,500 km2 of land at the Treta sea level (-90 m), ~29,000 km2 at -128 m; no land today (NOAA ETOPO 2022)",
    -10.50, 61.30, "low", "Computed from NOAA ETOPO 2022", treta=True, drowned=True)
add("drowned_nazareth_bank", "Drowned island: Nazareth Bank", "Nazareth Bank (drowned)", "", "Treta / glacial-era land",
    "Bank that was a large island at low sea level", "~15,000 km2 of land at -90 m; no land today (NOAA ETOPO 2022)",
    -14.50, 60.60, "low", "Computed from NOAA ETOPO 2022", treta=True, drowned=True)

# Epoch notes: how each coordinate shifts through time (rivers, coasts, sea level). Sources in geo_notes.json.
PALEO = {
    "ayodhya": "Town on a stable Pleistocene upland; the Sarayu (Ghaghara) channel swings 4-7 km within its meander belt, so the river bank of Valmiki's time is uncertain by about ±5-7 km",
    "shringaverapura": "No river shift documented: still on the Ganga's left bank; occupation TL-dated from c. 1035-875 BCE",
    "prayaga": "The confluence point moves seasonally and the Ganga moved west toward the fort in 1975-2000; the 'sandhi' is good to about ±1-2 km",
    "panchavati": "Godavari incised in Deccan basalt at Nashik: channel stable at site scale",
    "pampa": "Tungabhadra in a granite-bedrock gorge: stable at site scale",
    "kishkindha": "Tungabhadra in a granite-bedrock gorge: stable at site scale",
    "tamraparni": "Delta prograded 7.5-8 km in ~2,000 yr. In the 1st millennium BCE the mouth was near Korkai, about 7.5 km west of today's (epoch coordinate 8.633°N, 78.067°E)",
    "pandya_kavata": "Korkai was a coastal pearl port from the 3rd century BCE to the 5th century CE; now about 7.5 km inland",
    "setu_start": "Spit and cays are mobile sand up to +3.5 m. During the +1.5-2 m highstand (6.5-5.5 ka) they were mostly awash, so the dry Indian end was the Rameswaram island core near 9.227°N, 79.340°E",
    "setu_end": "Mannar island is a low sand-and-reef island; its west tip migrates with the littoral drift",
    "ocean_shore": "Rocky cape: shoreline essentially fixed through the Holocene (GEBCO: <1 km change between -10 m and +1.5 m)",
    "lanka_island": "Joined to India by land until sea level rose above the bridge sill (crest ~-3 m: c. 5200 BCE; rock ~-10 m: c. 6000 BCE)",
}
EPOCH_COORD = {"tamraparni": (8.6333, 78.0667), "setu_start": (9.2271, 79.3396)}
for p in P:
    if p["id"] in PALEO:
        p["paleo_note"] = PALEO[p["id"]]
    if p["id"] in EPOCH_COORD:
        p["epoch_lat"], p["epoch_lon"] = EPOCH_COORD[p["id"]]

if __name__ == "__main__":
    (DATA / "places.json").write_text(json.dumps(P, indent=1, ensure_ascii=False), encoding="utf-8")
    print(len(P), "places")
