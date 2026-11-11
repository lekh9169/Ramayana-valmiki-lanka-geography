// Interactive map of both editions (Leaflet). Used full-page on map.html and as a preview on the home page.
(async function () {
  const el = document.getElementById("map");
  if (!el || !window.L) return;
  const preview = el.dataset.preview === "true";
  const map = L.map(el, { scrollWheelZoom: !preview, zoomSnap: 0.5 }).setView([14, 78.5], preview ? 4.5 : 5);

  const ocean = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}", {
    maxZoom: 13, attribution: "Basemap: Esri, GEBCO, NOAA, National Geographic, Garmin, HERE and others"
  });
  const oceanLabels = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Reference/MapServer/tile/{z}/{y}/{x}", { maxZoom: 13 });
  const osm = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18, attribution: "&copy; OpenStreetMap contributors"
  });
  ocean.addTo(map); oceanLabels.addTo(map);

  const data = await (await fetch("data/map_layers.geojson")).json();
  const colour = { high: "#2B7A87", medium: "#5FA8A0", low: "#8FA1AA" };
  const fmt = (v) => (v ? `${Math.abs(v[0]).toFixed(4)}°${v[0] >= 0 ? "N" : "S"}, ${v[1].toFixed(4)}°E` : "");
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  function popup(p, latlng) {
    let rows = `<dt>Where</dt><dd>${fmt([latlng.lat, latlng.lng])}</dd>`;
    if (p.refs) rows += `<dt>Valmiki</dt><dd>${esc(p.refs)}</dd>`;
    if (p.clue) rows += `<dt>Text says</dt><dd>${esc(p.clue)}</dd>`;
    if (p.confidence) rows += `<dt>Confidence</dt><dd>${esc(p.confidence)}</dd>`;
    if (p.plate_birth) rows += `<dt>At Rama's birth (Treta)</dt><dd>${fmt(p.plate_birth)} on the plate</dd>`;
    if (p.treta_shore) rows += `<dt>Treta shore</dt><dd>${p.treta_shore.km_to_sea} km away</dd>`;
    if (p.paleo_note) rows += `<dt>Through time</dt><dd>${esc(p.paleo_note)}</dd>`;
    return `<h4>${esc(p.name)}</h4>${p.sanskrit ? `<div class="skt">${esc(p.sanskrit)}</div>` : ""}
            <div>${esc(p.identification || "")}</div><dl>${rows}</dl>`;
  }
  function pointLayer(filter, style) {
    return L.geoJSON(data, {
      filter: (f) => f.geometry.type === "Point" && filter(f.properties),
      pointToLayer: (f, ll) => L.circleMarker(ll, style(f.properties)),
      onEachFeature: (f, layer) => layer.bindPopup(popup(f.properties, layer.getLatLng()), { maxWidth: 320 })
    });
  }
  const layers = {
    valmiki: pointLayer((p) => p.layer === "valmiki", (p) => ({ radius: 7, color: "#fff", weight: 2, fillColor: colour[p.confidence], fillOpacity: 1 })),
    tradition: pointLayer((p) => p.layer === "tradition", () => ({ radius: 5, color: "#fff", weight: 1.5, fillColor: "#A8875A", fillOpacity: 0.95 })),
    rejected: pointLayer((p) => p.layer === "rejected", () => ({ radius: 6, color: "#7C3B3B", weight: 2, fillColor: "#fff", fillOpacity: 1 })),
    treta: pointLayer((p) => p.layer === "treta", () => ({ radius: 7, color: "#fff", weight: 2, fillColor: "#B7791F", fillOpacity: 1 })),
    treta_shore: pointLayer((p) => p.layer === "treta_shore", () => ({ radius: 5, color: "#B7791F", weight: 2, fillColor: "#F3E2C2", fillOpacity: 1 })),
    treta_coast: L.geoJSON(data, { filter: (f) => f.properties.layer === "treta_coast", style: { color: "#B7791F", weight: 1.6, opacity: 0.9 } }),
    route: L.geoJSON(data, { filter: (f) => f.properties.layer === "route", style: { color: "#0B2A45", weight: 2, dashArray: "6 6", opacity: 0.75 } })
  };
  const on = preview ? ["route", "valmiki", "treta"] : ["route", "valmiki", "tradition", "treta", "treta_shore", "treta_coast"];
  on.forEach((k) => layers[k].addTo(map));

  document.querySelectorAll(".layer-toggles input").forEach((box) => {
    box.checked = on.includes(box.value);
    box.addEventListener("change", () => (box.checked ? layers[box.value].addTo(map) : map.removeLayer(layers[box.value])));
  });
  const base = document.getElementById("basemap");
  if (base) base.addEventListener("change", () => {
    if (base.value === "osm") { map.removeLayer(ocean); map.removeLayer(oceanLabels); osm.addTo(map); }
    else { map.removeLayer(osm); ocean.addTo(map); oceanLabels.addTo(map); }
  });
  document.querySelectorAll("[data-fly]").forEach((b) => b.addEventListener("click", () => {
    const [lat, lon, z] = b.dataset.fly.split(",").map(Number);
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) map.setView([lat, lon], z);
    else map.flyTo([lat, lon], z, { duration: 1.2 });
  }));
})();
