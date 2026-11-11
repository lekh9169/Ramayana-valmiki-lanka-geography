"""Write data/geo_notes.json: literature-derived notes used by the report (text clues, rivers,
sea-level and plate-motion commentary, source list). Numbers here come from the cited papers;
everything computed lives in the other data/*.json files."""
import json
from datetime import date
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"

TEXT_CLUES = [
    ("Ayodhya on the Sarayu", "1.5.5-6 (CE 1.5.5-6)", "present", "Capital of Kosala on the Sarayu bank"),
    ("Shringaverapura on the Ganga", "2.50.25-26 (CE 2.44.1)", "present", "Ganga crossing point below Kosala"),
    ("Bharadvaja at the Ganga-Yamuna 'sandhi'", "2.54.2-8 (CE 2.48.2-8)", "present", "The confluence (Prayaga)"),
    ("Chitrakuta '10 krosha' from Prayaga, Mandakini below", "2.54.28, 2.95.1 (CE 2.48.25-26, 2.89.1)", "present", "A hill with a river at its foot"),
    ("Panchavati 2 yojanas from Agastya, near the Godavari", "3.13.13, 3.13.21 (CE 3.12.13, 3.12.18)", "present", "Godavari bank"),
    ("Pampa lake; Matanga's ashram on its west bank; Rishyamuka 'in front'", "3.73.27-31 (CE 3.69.21-24)", "present", "Lake-hill pair in the Tungabhadra country"),
    ("Southern route: Kaveri, Malaya (Agastya), Tamraparni with crocodiles and islands, Pandya golden gate, sea, Mahendra set into the sea, island '100 yojanas long' = Ravana's land",
     "4.41.15-25 (CE 4.40.15-25)", "present", "Lanka lies beyond the Tamraparni/Pandya coast, across the sea from a mountain at the shore"),
    ("Beyond the island: Pushpitaka (+100 yojanas), Suryavan (+14), Vaidyuta, Kunjara, Rishabha, Yama's realm",
     "4.41.28-46 (CE 4.40.27-38)", "present", "Mythic cosmography: no geography south of Lanka"),
    ("Lanka 'a full 100 yojanas' away across the sea", "4.58.20-25 (CE 4.57.20-23)", "present", "Sea width = 100 yojanas (formulaic)"),
    ("Sampati's 'Vindhya' on the southern-ocean shore", "4.60.7 (CE 4.59.7)", "present", "The real Vindhyas are ~800 km from that sea: the southern geography is schematic"),
    ("Hanuman leaps 100 yojanas from Mahendra; Mainaka rises; lands on Mount Lamba; Lanka on Trikuta's summit",
     "4.67.38-40; 5.1.91-208; 5.2.1 (CE 4.66.32-34; 5.1.79-189; 5.2.1)", "present", "Launch from a coastal mountain; landing on a hill near Lanka"),
    ("Enters Lanka at dusk as the (near) full moon rises", "5.2.49-58, 5.5.5 (CE 5.2.46-55, 5.4.5)", "present", "Lunar phase only"),
    ("March at midday 'vijaya' muhurta; Moon in Uttara Phalguni, Hasta tomorrow; Sahya, Malaya, Mahendra, shore",
     "6.4.3-5, 6.4.72-98 (CE 6.4.3-4, 6.4.55-66)", "present", "No month or year; route along the Western Ghats to the southern tip"),
    ("Setu 10 yojanas wide, 100 long, built by Nala in mid-ocean from trees and rocks", "6.22.44-74 (CE 6.15.8-22)", "present", "A long, narrow, shallow crossing: ratio 10 : 1"),
    ("Day-by-day 14 + 20 + 21 + 22 + 23 yojanas, 'up to Suvela'", "6.22.66-70", "absent", "Late addition"),
    ("Suvela: Lanka seen from its summit 'as if hanging in the sky'; full-moon night", "6.37.36, 6.38.3-18 (CE 6.29.1-17)", "present", "Hill near the landing within sight of the city"),
    ("Rama's horoscope: Caitra, navami, Aditi's nakshatra, five exalted grahas, Cancer lagna, Jupiter with the Moon", "1.18.8-9", "absent (star passage 506*)", "Late interpolation; uses the Hellenistic zodiac"),
    ("Month-season pairs: Caitra in bloom; Sravana first rainy month; Kartika campaign; hemanta with the Sun in the south",
     "2.3.4; 4.26.14-17; 4.28.54-55; 3.16 (CE 2.3.4; 4.25.12-15; 4.27.34-35; 3.15)", "present", "Precession clock: fixes the epoch of the composer's sky"),
    ("Mercury on Rohini, Mars on Vishakha at Ravana's last battle", "6.103.33-36 (CE 6.90.27-30)", "present", "Weak planetary constraint"),
    ("Rahu seizes the Sun 'aparvani' (not on a new/full-moon day) before the Khara battle", "3.23.11-12 (CE 3.22.11-12)", "present", "A portent, not an observable eclipse"),
    ("'Setubandha' tirtha and Mahadeva's grace at the crossing", "6.126.19-21", "absent", "Late (Rameswaram cult)"),
]

RIVER_NOTES = [
    ("Ayodhya / Sarayu (Ghaghara)", "Bank shifts of 4-7 km within the meander belt in 1975-2020; right-bank erosion near Ayodhya ~5 km in 1990-2003",
     "The town stands on a stable Pleistocene upland (T2, ~48-7 ka), so the site coordinate is robust. Where the river ran in Valmiki's time is uncertain by about ±5-7 km",
     "NIH Roorkee for CWC 2013; Gautam et al. 2024 (doi:10.1007/s12517-024-12104-1); Shah 2017 (doi:10.1007/s13201-016-0459-3)"),
    ("Shringaverapura / Ganga", "No shift documented; site still on the left bank; a ~2,000-yr-old brick tank fed by Ganga water; OCP levels TL-dated 1035-875 BCE",
     "Coordinate stable", "Agrawal, Bhandari, Lal & Singhvi 1981 (doi:10.1007/BF02880261); B. B. Lal 1985"),
    ("Prayaga / Ganga-Yamuna confluence", "The Ganga moved west toward the fort in 1975-2000; the confluence point moves with the seasons",
     "The 'sandhi' point is good to roughly ±1-2 km (not quantified in peer-reviewed work)", "Press reports of IIT Kanpur imagery; Pati et al. 2008 (doi:10.1007/s12524-008-0030-2, not read)"),
    ("Panchavati / Godavari at Nashik", "Bedrock (Deccan basalt) channel, incising through the Holocene; knickpoint at Gangapur",
     "Channel stable at site scale", "Kale & Rajaguru 1987 (doi:10.1038/325612a0); Kale 2002"),
    ("Pampa / Tungabhadra at Hampi", "Granite-bedrock channel; 14th-century bridge pillars and Vijayanagara anicuts still in place",
     "Channel stable at site scale", "UNESCO WHS record; field evidence (no numerical study)"),
    ("Tamraparni mouth / Korkai", "The delta has prograded 7.5-8 km in ~2,000 years and the river shifted south and east. Korkai was the port from the 3rd century BCE to the 5th century CE",
     "In the 1st millennium BCE the mouth and coast lay near Korkai (8.633°N, 78.067°E), about 7.5 km west of today's mouth",
     "Arunachalam, Sukumar et al. 2006, Curr. Sci. 91:278"),
    ("Setu, Indian end / Dhanushkodi spit", "Sand spit up to +3.5 m, mobile; the town was destroyed by the 1964 cyclone (surge 4.5-7.6 m); the cays are loose sand 7-9 m thick over calcareous sandstone",
     "During the +1.5-2 m mid-Holocene highstand (6.5-5.5 ka) most of the spit and cays were awash, so the dry Indian end was the Rameswaram island core (~79.34°E). Today's tip is 12 km further east",
     "Paul 2021, J. Indian Geomorph. 9:18; Dandabathula et al. 2024 (doi:10.1038/s41598-024-65908-2); IMD 1964"),
    ("Kaveri mouth / Poompuhar (context)", "Sangam-era structures now in 1-8 m of water; shoreline retreat ~1 m/yr at Tranquebar",
     "Coastal sites of the historic period have shifted by hundreds of metres to kilometres",
     "Sundaresh & Gaur 2011 (NIO)"),
]

SOURCES = [
    "GEBCO Compilation Group (2026) GEBCO 2026 Grid (doi: 10.5285/4f68d5c7-45eb-f999-e063-7086abc036fa). Public domain; not for navigation.",
    "Park, R. S., Folkner, W. M., Williams, J. G., Boggs, D. H. (2021) The JPL Planetary and Lunar Ephemerides DE440 and DE441. AJ 161:105. doi:10.3847/1538-3881/abd414.",
    "van Leeuwen, F. (2007) Validation of the new Hipparcos reduction. A&A 474:653 (Spica position and proper motion).",
    "Lambeck, K., Rouby, H., Purcell, A., Sun, Y., Sambridge, M. (2014) Sea level and global ice volumes from the LGM to the Holocene. PNAS 111:15296. doi:10.1073/pnas.1411762111. (1-kyr values via the CRAN 'tabs' dataset; Table S3 not retrieved.)",
    "Ranasinghe, Ambillapitiya, Li, Shen, Ranasinghe & Liu (2025) Quaternary Science Reviews 362:109403. doi:10.1016/j.quascirev.2025.109403 (Sri Lanka mid-Holocene highstand; abstract).",
    "Banerjee, P. K. (2000) Holocene and Late Pleistocene relative sea level fluctuations along the east coast of India. Marine Geology 167:243. doi:10.1016/S0025-3227(00)00028-1 (abstract).",
    "Katupotha, J. (1988) Radiocarbon 30:125. doi:10.1017/S0033822200043964; Katupotha (c. 1995) NARESA report RG/92/E/01.",
    "Dubey, K. M., Chaubey, A. K., Gaur, A. S., Joglekar, M. V. (2023) Quaternary Research 111:166. doi:10.1017/qua.2022.41 (Palk Strait seismic study; abstract).",
    "Dandabathula, G. et al. (2024) ICESat-2 bathymetry of Adam's Bridge. Scientific Reports 14:14896. doi:10.1038/s41598-024-65908-2.",
    "Paul, A. (2021) Evolution of carbonate landforms, Gulf of Mannar. J. Indian Geomorphology 9:18-43.",
    "Arunachalam, B., Sukumar, B. et al. (2006) Reconstruction of the ancient port Korkai. Current Science 91(3):278-280.",
    "Sundaresh & Gaur, A. S. (2011) Marine archaeological explorations off Poompuhar (NIO).",
    "Argus, D. F., Gordon, R. G., DeMets, C. (2011) Geologically current motion of 56 plates relative to the no-net-rotation reference frame. G-cubed 12:Q11001. doi:10.1029/2011GC003751.",
    "Altamimi, Z. et al. (2023) ITRF2020 plate motion model. GRL 50:e2023GL106373. doi:10.1029/2023GL106373.",
    "Jade, S. et al. (2017) Scientific Reports 7:11439. doi:10.1038/s41598-017-11697-w (rigid India incl. Sri Lanka).",
    "Morrison, L. V., Stephenson, F. R. (2004) J. Hist. Astron. 35:327; Stephenson, Morrison & Hohenkerk (2016) Proc. R. Soc. A 472:20160404.",
    "NIH Roorkee for CWC (2013) Morphological study of the Ghaghara; Gautam et al. (2024) Arab. J. Geosci. doi:10.1007/s12517-024-12104-1.",
    "Agrawal, D. P., Bhandari, N., Lal, B. B., Singhvi, A. K. (1981) Proc. Indian Acad. Sci. (EPS) 90:161 (Shringaverapura TL dates).",
    "Kale, V. S., Rajaguru, S. N. (1987) Nature 325:612 (Godavari).",
    "Valmiki Ramayana, RSVP text and translation via IIT Kanpur: https://heritage.iitk.ac.in/VRAM/ (API /api/VRAM/); valmikiramayan.net.",
    "Ramayana Critical Edition (Baroda), constituted text, GRETIL: https://gretil.sub.uni-goettingen.de/ (Tokunaga / Smith).",
    "Goldman, R. P. (trans.), Ramayana Book I notes (Clay Sanskrit Library): horoscope = star passage 506*.",
    "Weber, A. (1872) Indian Antiquary 1 (horoscope absent from the Bengal recension); Mak, B. (2023) on the Yavanajataka's date.",
    "Claims tested: Bhatnagar, P. (2004) Dating the Era of Lord Ram (10 Jan 5114 BCE); Oak, N. (2014) The Historic Rama (c. 12,209 BCE); Kibe, M. V. (Amarkantak Lanka).",
    "Bintanja, R., van de Wal, R. S. W. (2008) North American ice-sheet dynamics and the onset of 100,000-year glacial cycles. Nature 454:869 (3-Myr sea level; NOAA WDC Paleo #2011-119).",
    "Spratt, R. M., Lisiecki, L. E. (2016) A Late Pleistocene sea level stack. Climate of the Past 12:1079 (0-798 ka cross-check).",
    "Stein, C. A., Stein, S. (1992) A model for the global variation in oceanic depth and heat flow with lithospheric age. Nature 359:123 (ridge subsidence form).",
    "Pappu, S. et al. (2011) Early Pleistocene presence of Acheulian hominins in South India. Science 331:1596.",
    "Manusmriti 1.69-71 and Mahabharata 3.186 (12,000-year yuga cycle); Surya Siddhanta 1.15-17 (4,320,000-year maha-yuga; Lanka at the equator on Ujjain's meridian).",
    "Anonymous (1926) Situation of Ravana's Lamka on the Equator. Quarterly Journal of the Mythic Society 17(1).",
    "Berger, A., Loutre, M. F. (1991) Insolation values for the climate of the last 10 million years. Quaternary Science Reviews 10:297 (obliquity; NOAA orbit91 file).",
    "Besse, J., Courtillot, V. (2002) Apparent and true polar wander and the geometry of the geomagnetic field over the last 200 Myr. JGR 107(B11):2300; Torsvik, T. H. et al. (2012) Phanerozoic polar wander, palaeogeography and dynamics. Earth-Science Reviews 114:325.",
    "DeMets, C., Gordon, R. G., Royer, J.-Y. (2005) Motion between the Indian, Capricorn and Somalian plates. GJI 161:445 (India-Capricorn diffuse boundary).",
    "Wikipedia: Great Chagos Bank (12,642 km2 structure, ~5.6 km2 of land), Pitt Bank (wholly submerged), Speakers Bank (negligible land), Chagos Archipelago (56.13 km2 land; Diego Garcia 32.5 km2).",
    "Markandeya Purana ch. 57: Bharatavarsha in nine divisions separated by the ocean; seven kula-parvatas incl. Mahendra and Malaya (Sanskrit text via vedapath.app / enjoylearningsanskrit.com).",
    "NOAA NCEI (2022) ETOPO 2022 15 Arc-Second Global Relief Model. doi:10.25921/fd45-gt74 (Mauritius and Mascarene subset via ERDDAP).",
    "Torsvik, T. H. et al. (2013) A Precambrian microcontinent in the Indian Ocean. Nature Geoscience 6:223 (Mauritia).",
    "Ashwal, L. D., Wiedenbeck, M., Torsvik, T. H. (2017) Archaean zircons in Miocene oceanic hotspot rocks establish ancient continental crust beneath Mauritius. Nature Communications 8:14086.",
    "Sclater, P. L. (1864) The mammals of Madagascar. Quarterly Journal of Science 1:213 (the 'Lemuria' proposal).",
    "Ramaswamy, S. (2004) The Lost Land of Lemuria: Fabulous Geographies, Catastrophic Histories. University of California Press.",
    "Site coordinates: Wikipedia ({{coord}}), OpenStreetMap (Nominatim), district government (nic.in) pages, as listed per place.",
]

if __name__ == "__main__":
    notes = {
        "built": date.today().isoformat(),
        "text_clues": TEXT_CLUES,
        "river_notes": RIVER_NOTES,
        "sources": SOURCES,
        "rsl_comment": (
            "Before 9 ka the curve follows Lambeck et al. (2014) global ice-equivalent sea level. It then blends into "
            "the far-field regional record: modern level reached ~6.5 ka, a highstand of +1.5 to 2 m at 6.5-5.5 cal ka "
            "(Ranasinghe et al. 2025, Sri Lanka; Gulf of Mannar corals and microatolls), and a fall to the present after "
            "~4 ka. Regional sea level is assumed to sit 2-3 m above global sea level in the early Holocene because of "
            "hydro-isostasy; this is a model assumption, so the uncertainty is widened there."),
        "plate_comment": (
            "India-plate pole NNR-MORVEL56 (Argus, Gordon & DeMets 2011): 50.37°N, 3.29°W, 0.544 ± 0.010°/Myr. GNSS "
            "agrees: 54.8 mm/yr toward 050° at Bangalore and 56.9 mm/yr toward 051° at Colombo. The Bangalore-Colombo "
            "baseline changes by only -0.02 ± 0.28 mm/yr, so India and Sri Lanka move as one rigid block (Jade et al. "
            "2017). Vertical rates are within ±0.5 mm/yr, and last-interglacial corals at only +0.8 to 3.6 m in the "
            "Palk Strait argue against significant uplift."),
    }
    (DATA / "geo_notes.json").write_text(json.dumps(notes, indent=1, ensure_ascii=False), encoding="utf-8")
    print("geo_notes.json written")
