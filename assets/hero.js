// The home-page relief: GEBCO 2026 elevation for the Palk Strait, flooded in the browser to any sea level.
// Elevation is packed into palk_relief.png (R*256 + G - 32768 metres; B = hillshade). On load the sea drains
// once from today's level to the Treta-epoch level, pausing where Adam's Bridge surfaces; then the slider takes over.
(async function () {
  const canvas = document.getElementById("relief");
  if (!canvas) return;
  const slider = document.getElementById("sea");
  const levelEl = document.getElementById("level-value");
  const whenEl = document.getElementById("level-when");
  const stateEl = document.getElementById("level-state");
  const bridgeTag = document.querySelector(".tag.bridge");

  const meta = await (await fetch("assets/hero_meta.json")).json();
  const img = new Image();
  await new Promise((resolve, reject) => { img.onload = resolve; img.onerror = reject; img.src = "assets/palk_relief.png"; });
  const W = meta.width, H = meta.height;
  canvas.width = W; canvas.height = H;
  const ctx = canvas.getContext("2d", { willReadFrequently: false });
  const off = document.createElement("canvas");
  off.width = W; off.height = H;
  const octx = off.getContext("2d");
  octx.drawImage(img, 0, 0);
  const src = octx.getImageData(0, 0, W, H).data;
  const n = W * H;
  const elev = new Int16Array(n);
  const shade = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    elev[i] = src[i * 4] * 256 + src[i * 4 + 1] - 32768;
    shade[i] = src[i * 4 + 2] / 255;
  }
  const out = ctx.createImageData(W, H);
  const px = out.data;

  // colour ramps: water by depth below the chosen sea level, land by height above it
  const water = [[0, [158, 214, 204]], [8, [93, 176, 180]], [40, [43, 122, 135]], [250, [22, 74, 107]], [1500, [14, 52, 84]], [4500, [11, 42, 69]]];
  const land = [[0, [205, 196, 160]], [150, [170, 172, 128]], [600, [137, 131, 98]], [1500, [118, 100, 80]], [2500, [222, 214, 200]]];
  const shelf = [227, 201, 143];  // ground that is sea today but dry at this level
  function ramp(stops, v) {
    if (v <= stops[0][0]) return stops[0][1];
    for (let k = 1; k < stops.length; k++) {
      if (v <= stops[k][0]) {
        const [a, ca] = stops[k - 1], [b, cb] = stops[k], t = (v - a) / (b - a);
        return [ca[0] + (cb[0] - ca[0]) * t, ca[1] + (cb[1] - ca[1]) * t, ca[2] + (cb[2] - ca[2]) * t];
      }
    }
    return stops[stops.length - 1][1];
  }
  const waterLUT = new Uint8ClampedArray(4600 * 3), landLUT = new Uint8ClampedArray(2700 * 3);
  for (let d = 0; d < 4600; d++) waterLUT.set(ramp(water, d).map(Math.round), d * 3);
  for (let h = 0; h < 2700; h++) landLUT.set(ramp(land, h).map(Math.round), h * 3);

  function draw(level) {
    for (let i = 0; i < n; i++) {
      const e = elev[i], s = shade[i], o = i * 4;
      if (e > level) {
        let r, g, b;
        if (e <= 0) { r = shelf[0]; g = shelf[1]; b = shelf[2]; }
        else { const k = Math.min(e - Math.max(level, 0), 2699) * 3; r = landLUT[k]; g = landLUT[k + 1]; b = landLUT[k + 2]; }
        const f = 0.55 + 0.45 * s;
        px[o] = r * f; px[o + 1] = g * f; px[o + 2] = b * f;
      } else {
        const k = Math.min(Math.round(level - e), 4599) * 3, f = 0.88 + 0.12 * s;
        px[o] = waterLUT[k] * f; px[o + 1] = waterLUT[k + 1] * f; px[o + 2] = waterLUT[k + 2] * f;
      }
      px[o + 3] = 255;
    }
    ctx.putImageData(out, 0, 0);
  }

  // where the slider's sea level sits in time
  const rows = meta.sea_levels.rows;
  function fmtYear(y) {
    if (y === null || y === undefined) return "";
    if (y > 0) return y + " CE";
    const bce = 1 - y;
    return (bce >= 10000 ? bce.toLocaleString("en-US") : String(bce)) + " BCE";
  }
  function describe(level) {
    const treta = meta.sea_levels.treta_level;
    let when;
    if (level >= 0.5) when = "Higher than today: the mid-Holocene highstand, about 4000–3500 BCE.";
    else if (level > -0.5) when = "Today's coastline.";
    else {
      const row = rows.reduce((a, b) => (Math.abs(b.level - level) < Math.abs(a.level - level) ? b : a));
      when = row.year !== null ? `The sea last stood this low around ${fmtYear(row.year)}.` : "Lower than any time in the last 20,000 years.";
      if (Math.abs(level - treta) <= 2) when += ` It also stood here at the Puranic end of Treta, ${meta.sea_levels.treta_end_bce.toLocaleString("en-US")} BCE.`;
    }
    const joined = level < -3;
    return { when, joined };
  }

  let shownJoined = null;
  function update(level, fromUser) {
    draw(level);
    const sign = level > 0 ? "+" : level < 0 ? "−" : "";
    levelEl.innerHTML = `${sign}${Math.abs(level).toFixed(level % 1 === 0 ? 0 : 1)}<small>m</small>`;
    const d = describe(level);
    whenEl.textContent = d.when;
    stateEl.textContent = d.joined ? "India and Sri Lanka are joined by dry land across Adam's Bridge."
                                   : "Sri Lanka is an island. Adam's Bridge lies under shallow water.";
    stateEl.classList.toggle("joined", d.joined);
    if (shownJoined === false && d.joined && bridgeTag) {
      bridgeTag.classList.remove("surfacing"); void bridgeTag.offsetWidth; bridgeTag.classList.add("surfacing");
    }
    shownJoined = d.joined;
    if (fromUser) slider.setAttribute("aria-valuetext", `${sign}${Math.abs(level)} metres. ${d.when}`);
  }

  // place name tags
  document.querySelectorAll(".relief .tag").forEach((t) => {
    const lat = +t.dataset.lat, lon = +t.dataset.lon;
    t.style.left = ((lon - meta.west) / (meta.east - meta.west)) * 100 + "%";
    t.style.top = ((meta.north - lat) / (meta.north - meta.south)) * 100 + "%";
  });

  // the slider is stretched where the shallow changes happen: 0-100 = +2..0 m, 100-400 = 0..-10 m,
  // 400-700 = -10..-40 m, 700-1000 = -40..-130 m
  const knots = [[0, 2], [100, 0], [400, -10], [700, -40], [1000, -130]];
  function toLevel(pos) {
    for (let k = 1; k < knots.length; k++) if (pos <= knots[k][0]) {
      const [p0, l0] = knots[k - 1], [p1, l1] = knots[k];
      return Math.round((l0 + (l1 - l0) * (pos - p0) / (p1 - p0)) * 2) / 2;
    }
    return -130;
  }
  function toPos(level) {
    for (let k = 1; k < knots.length; k++) if (level >= knots[k][1]) {
      const [p0, l0] = knots[k - 1], [p1, l1] = knots[k];
      return Math.round(p0 + (p1 - p0) * (level - l0) / (l1 - l0));
    }
    return 1000;
  }
  const jumps = [...document.querySelectorAll(".jumps button")];
  function setLevel(level, fromUser) {
    slider.value = toPos(level);
    jumps.forEach((b) => b.setAttribute("aria-pressed", String(+b.dataset.level === level)));
    update(level, fromUser);
  }
  slider.addEventListener("input", () => { cancelAnimationFrame(anim); const l = toLevel(+slider.value);
    jumps.forEach((b) => b.setAttribute("aria-pressed", String(+b.dataset.level === l))); update(l, true); });
  jumps.forEach((b) => b.addEventListener("click", () => { cancelAnimationFrame(anim); setLevel(+b.dataset.level, true); }));

  // one orchestrated moment: the sea drains to the Treta level, pausing as the bridge surfaces
  const target = meta.sea_levels.treta_level;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let anim = 0;
  if (reduce) { setLevel(-3.5); return; }
  setLevel(0);
  const t0 = performance.now() + 700;
  const legs = [[0, -3.5, 1600], [-3.5, -3.5, 900], [-3.5, target, 3200]];
  function step(now) {
    let t = now - t0;
    if (t < 0) { anim = requestAnimationFrame(step); return; }
    for (const [a, b, dur] of legs) {
      if (t <= dur) {
        const u = t / dur, ease = u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2;
        const level = Math.round((a + (b - a) * ease) * 2) / 2;
        slider.value = toPos(level); update(level);
        anim = requestAnimationFrame(step);
        return;
      }
      t -= dur;
    }
    setLevel(Math.round(target));
  }
  anim = requestAnimationFrame(step);
})();
