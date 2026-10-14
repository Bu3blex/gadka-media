// „Mamy Twój podcast” – list z żądaniem okupu, kolaż poklatkowy
const D = window.DATA;
const cv = document.getElementById('c'), cx = cv.getContext('2d');
const W = 1080, H = 1920, SW = 980, SHH = 1560;
const INK = '#1C2A6E', OR = '#FF592A';
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
function rnd(n) { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); }
const FPS_SM = 12;

const FONTS = [
  ['900', 'normal', 'Inter Display'], ['700', 'normal', 'TeX Gyre Bonum'], ['700', 'italic', 'Lora'],
  ['700', 'normal', 'TeX Gyre Heros Cn'], ['700', 'normal', 'Courier 10 Pitch'], ['700', 'normal', 'TeX Gyre Schola'],
  ['600', 'normal', 'Poppins'], ['700', 'italic', 'Liberation Serif'], ['700', 'normal', 'TeX Gyre Adventor'], ['700', 'normal', 'DejaVu Serif'],
];
const COLS = [['#111', '#fff'], ['#EFE6D2', '#111'], ['#E5322D', '#fff'], ['#FFD400', '#111'], ['#fff', '#D3172A'], ['#2B5CE6', '#fff'],
  ['#FF592A', '#111'], ['#D9D9D9', '#222'], ['#F7A8C8', '#111'], ['#0A7C4A', '#fff'], ['#fff', '#111']];

const IM = {}; let pending = 0;
function done() { if (--pending === 0) { build(); window.READY = true; } }
function load(k, src) { pending++; const i = new Image(); i.onload = done; i.src = src; IM[k] = i; }
['056', '101', '104', '034', 'noise'].forEach(n => load(n, n === 'noise' ? 'img/noise.png' : `img/${n}.jpg`));
load('logoB', 'logo_black.png');
pending++;
Promise.all([...FONTS.map(f => document.fonts.load(`${f[1]} ${f[0]} 60px "${f[2]}"`, 'ĄŁŻ')), document.fonts.load('60px "TeX Gyre Chorus"', 'ąż'), document.fonts.load('bold 60px "Courier 10 Pitch"')]).then(done);

// ---------- tekstury
let paper, desk;
function build() {
  paper = document.createElement('canvas'); paper.width = SW; paper.height = SHH;
  const p = paper.getContext('2d');
  p.fillStyle = '#F5F0E5'; p.fillRect(0, 0, SW, SHH);
  for (let i = 0; i < 90; i++) { // zagniecenia
    p.fillStyle = rnd(i) > 0.5 ? 'rgba(255,255,255,.22)' : 'rgba(120,100,70,.05)';
    p.beginPath(); const x = rnd(i * 3) * SW, y = rnd(i * 5) * SHH;
    p.moveTo(x, y); p.lineTo(x + (rnd(i * 7) - .5) * 600, y + (rnd(i * 11) - .5) * 600); p.lineTo(x + (rnd(i * 13) - .5) * 600, y + (rnd(i * 17) - .5) * 600); p.fill();
  }
  p.strokeStyle = 'rgba(120,100,70,.12)'; p.lineWidth = 2;
  p.beginPath(); p.moveTo(0, SHH / 3); p.lineTo(SW, SHH / 3 + 10); p.moveTo(0, 2 * SHH / 3); p.lineTo(SW, 2 * SHH / 3 - 8); p.stroke();
  p.globalCompositeOperation = 'multiply'; p.globalAlpha = 0.12; p.drawImage(IM.noise, 0, 0, SW, SHH); p.drawImage(IM.noise, 300, 600);
  desk = document.createElement('canvas'); desk.width = W; desk.height = H;
  const d = desk.getContext('2d');
  const g = d.createRadialGradient(W / 2, H / 2, 200, W / 2, H / 2, 1200); g.addColorStop(0, '#4A3B32'); g.addColorStop(1, '#1E1714');
  d.fillStyle = g; d.fillRect(0, 0, W, H);
  for (let i = 0; i < 40; i++) { d.strokeStyle = `rgba(0,0,0,${0.08 + 0.1 * rnd(i)})`; d.lineWidth = 2 + 6 * rnd(i * 3); d.beginPath(); const y = i * 50 + rnd(i) * 30; d.moveTo(0, y); d.bezierCurveTo(300, y + 40 * rnd(i * 5), 700, y - 40 * rnd(i * 7), W, y + 20); d.stroke(); }
  d.globalCompositeOperation = 'overlay'; d.globalAlpha = 0.35; for (let x = 0; x < W; x += 600) for (let y = 0; y < H; y += 600) d.drawImage(IM.noise, x, y);
}

let FR = 0; // klatka poklatkowa
const jit = (s, a = 1) => (rnd(s * 7.13 + FR * 13.37) - 0.5) * 2 * a;

// ---------- elementy
function ransom(str, x, y, sz, t0, lt, seed, step = 0.08, fit = 1) {
  const chars = [...str]; const items = []; let tw = 0;
  chars.forEach((c, i) => {
    if (c === ' ') { items.push({ sp: true, w: sz * 0.35 }); tw += sz * 0.35; return; }
    const sd = seed * 31 + i * 7.7;
    const f = FONTS[Math.floor(rnd(sd) * FONTS.length)], col = COLS[Math.floor(rnd(sd + 1.3) * COLS.length)];
    const s = sz * (0.82 + 0.3 * rnd(sd + 2.1));
    cx.font = `${f[1]} ${f[0]} ${s}px "${f[2]}"`;
    const w = cx.measureText(c).width + s * 0.28;
    items.push({ c, f, col, s, w, sd }); tw += w + 6;
  });
  if (tw > 850 && fit === 1) return ransom(str, x, y, sz * 850 / tw, t0, lt, seed, step, 0);
  let xx = x - tw / 2, k = 0;
  items.forEach(it => {
    if (it.sp) { xx += it.w; return; }
    const at = t0 + k * step; k++;
    if (lt >= at) {
      const age = lt - at, pop = age < 1 / FPS_SM ? 1.25 : 1;
      cx.save(); cx.translate(xx + it.w / 2 + jit(it.sd, 1.2), y + (rnd(it.sd + 4) - .5) * sz * 0.16 + jit(it.sd + 1, 1.2));
      cx.rotate((rnd(it.sd + 3) - .5) * 0.22 + jit(it.sd + 2, 0.01)); cx.scale(pop, pop);
      const h = it.s * 1.15, w = it.w;
      cx.shadowColor = 'rgba(0,0,0,.28)'; cx.shadowBlur = 6; cx.shadowOffsetX = 3; cx.shadowOffsetY = 4;
      cx.fillStyle = it.col[0]; cx.beginPath();
      cx.moveTo(-w / 2 + rnd(it.sd + 5) * 6, -h / 2 + rnd(it.sd + 6) * 6); cx.lineTo(w / 2 - rnd(it.sd + 7) * 6, -h / 2 + rnd(it.sd + 8) * 8);
      cx.lineTo(w / 2 - rnd(it.sd + 9) * 4, h / 2 - rnd(it.sd + 10) * 6); cx.lineTo(-w / 2 + rnd(it.sd + 11) * 6, h / 2 - rnd(it.sd + 12) * 4); cx.closePath(); cx.fill();
      cx.shadowColor = 'transparent';
      cx.fillStyle = it.col[1]; cx.font = `${it.f[1]} ${it.f[0]} ${it.s}px "${it.f[2]}"`; cx.textAlign = 'center'; cx.textBaseline = 'middle';
      cx.fillText(it.c, 0, it.s * 0.04);
      cx.restore();
    }
    xx += it.w + 6;
  });
  return t0 + k * step;
}
function hand(s, x, y, sz, t0, lt, o = {}) { // pismo odręczne, wypisywane
  if (lt < t0) return;
  const n = Math.ceil(clamp((lt - t0) / (o.dur || 0.9)) * s.length);
  cx.save(); cx.translate(x, y); cx.rotate(o.rot || -0.03);
  cx.font = `${sz}px "TeX Gyre Chorus"`; cx.fillStyle = o.col || INK; cx.textAlign = o.al || 'center'; cx.textBaseline = 'middle';
  // wypisanie od lewej – przycinanie
  const full = cx.measureText(s).width, part = cx.measureText(s.slice(0, n)).width;
  const x0 = (o.al === 'left') ? 0 : -full / 2;
  cx.beginPath(); cx.rect(x0 - 20, -sz, part + 30, sz * 2); cx.clip();
  cx.fillText(s, 0, 0); cx.restore();
}
function tape(x, y, w, h, rot, sd) {
  cx.save(); cx.translate(x, y); cx.rotate(rot); cx.fillStyle = 'rgba(232,222,186,.82)';
  cx.beginPath(); cx.moveTo(-w / 2, -h / 2);
  for (let i = 0; i <= 6; i++) cx.lineTo(-w / 2 + w * i / 6, -h / 2 + (i % 2) * 3);
  for (let i = 0; i <= 5; i++) cx.lineTo(w / 2 + (i % 2 ? 6 : 0), -h / 2 + h * i / 5);
  for (let i = 6; i >= 0; i--) cx.lineTo(-w / 2 + w * i / 6, h / 2 - (i % 2) * 3);
  for (let i = 5; i >= 0; i--) cx.lineTo(-w / 2 - (i % 2 ? 6 : 0), -h / 2 + h * i / 5);
  cx.fill(); cx.restore();
}
function polaroid(k, x, y, w, rot, t0, lt, cap, sd, fx = 0.5) {
  if (lt < t0) return;
  const age = lt - t0, sc = age < 1 / FPS_SM ? 1.18 : age < 2 / FPS_SM ? 1.05 : 1;
  const h = w * 1.18, ph = w * 0.86, m = w * 0.07;
  cx.save(); cx.translate(x + jit(sd, 1.5), y + jit(sd + 1, 1.5)); cx.rotate(rot + jit(sd + 2, 0.006)); cx.scale(sc, sc);
  cx.shadowColor = 'rgba(0,0,0,.35)'; cx.shadowBlur = 18; cx.shadowOffsetY = 8;
  cx.fillStyle = '#FDFCF8'; cx.fillRect(-w / 2, -h / 2, w, h); cx.shadowColor = 'transparent';
  const im = IM[k], s = Math.max((w - 2 * m) / im.width, ph / im.height), iw = im.width * s, ih = im.height * s;
  cx.save(); cx.beginPath(); cx.rect(-w / 2 + m, -h / 2 + m, w - 2 * m, ph); cx.clip();
  cx.filter = 'contrast(1.08) saturate(1.1) sepia(0.12)';
  cx.drawImage(im, -w / 2 + m + (w - 2 * m) / 2 - iw * fx, -h / 2 + m + ph / 2 - ih / 2, iw, ih); cx.filter = 'none'; cx.restore();
  if (cap) { cx.font = `${w * 0.13}px "TeX Gyre Chorus"`; cx.fillStyle = INK; cx.textAlign = 'center'; cx.textBaseline = 'middle'; cx.fillText(cap, 0, -h / 2 + m + ph + (h - ph - m) / 2); }
  tape(-w / 2 + 20, -h / 2 + 5, 150, 46, -0.6, sd); tape(w / 2 - 20, -h / 2 + 5, 150, 46, 0.6, sd + 1);
  cx.restore();
}
function strip(s, x, y, t0, lt, sd, sz = 60) {
  if (lt < t0) return;
  const age = lt - t0, sc = age < 1 / FPS_SM ? 1.12 : 1;
  cx.save(); cx.translate(x + jit(sd, 1), y + jit(sd + 1, 1)); cx.rotate((rnd(sd) - .5) * 0.06); cx.scale(sc, sc);
  cx.font = `bold ${sz}px "Courier 10 Pitch"`; const w = cx.measureText(s).width + 50;
  cx.shadowColor = 'rgba(0,0,0,.25)'; cx.shadowBlur = 6; cx.shadowOffsetY = 4;
  cx.fillStyle = '#FFFDF6'; cx.beginPath(); cx.moveTo(-w / 2, -sz * 0.75);
  for (let i = 0; i <= 12; i++) cx.lineTo(-w / 2 + w * i / 12, -sz * 0.75 + (rnd(sd + i) - .5) * 5);
  cx.lineTo(w / 2, sz * 0.75); for (let i = 12; i >= 0; i--) cx.lineTo(-w / 2 + w * i / 12, sz * 0.75 + (rnd(sd + i + 20) - .5) * 5); cx.fill();
  cx.shadowColor = 'transparent'; cx.fillStyle = '#151515'; cx.textAlign = 'center'; cx.textBaseline = 'middle'; cx.fillText(s, 0, 3);
  cx.restore();
}
function arrow(pts, t0, lt, dur = 0.5) {
  if (lt < t0) return;
  const p = clamp((lt - t0) / dur), n = Math.max(2, Math.floor(pts.length * p));
  cx.save(); cx.strokeStyle = INK; cx.lineWidth = 7; cx.lineCap = 'round'; cx.lineJoin = 'round';
  cx.beginPath(); pts.slice(0, n).forEach(([x, y], i) => i ? cx.lineTo(x, y) : cx.moveTo(x, y)); cx.stroke();
  if (p >= 1) { const [x1, y1] = pts[pts.length - 1], [x0, y0] = pts[pts.length - 2], a = Math.atan2(y1 - y0, x1 - x0);
    cx.beginPath(); cx.moveTo(x1 - 34 * Math.cos(a - 0.5), y1 - 34 * Math.sin(a - 0.5)); cx.lineTo(x1, y1); cx.lineTo(x1 - 34 * Math.cos(a + 0.5), y1 - 34 * Math.sin(a + 0.5)); cx.stroke(); }
  cx.restore();
}
function circleInk(x, y, rx, ry, t0, lt) {
  if (lt < t0) return; const p = clamp((lt - t0) / 0.4);
  cx.save(); cx.strokeStyle = '#D3172A'; cx.lineWidth = 8; cx.lineCap = 'round'; cx.beginPath();
  for (let i = 0; i <= 60 * p; i++) { const a = -0.4 + i / 60 * Math.PI * 2.15, r = 1 + 0.04 * Math.sin(i); cx.lineTo(x + rx * r * Math.cos(a), y + ry * r * Math.sin(a)); }
  cx.stroke(); cx.restore();
}

// ---------- sceny (współrzędne lokalne kartki, środek 0,0)
const SC = [
  (lt) => { // hak
    ransom('MAMY', 0, -420, 175, 0.0, lt, 1, 0.07);
    ransom('TWÓJ', 0, -190, 175, 0.4, lt, 2, 0.07);
    ransom('PODCAST.', 0, 50, 150, 0.8, lt, 3, 0.07);
    hand('spokojnie,', 0, 330, 100, 2.1, lt, { dur: 0.5 });
    hand('jest cały i zdrowy.', 0, 450, 100, 2.6, lt, { dur: 0.8 });
  },
  (lt) => {
    ransom('LEŻAŁ', 0, -600, 120, 0.15, lt, 11, 0.06);
    ransom('W SZUFLADZIE', 0, -440, 105, 0.5, lt, 12, 0.05);
    ransom('OD 2 LAT.', 0, -280, 120, 1.15, lt, 13, 0.06);
    polaroid('056', 40, 260, 560, 0.05, 1.9, lt, 'dowód, że żyje', 14);

  },
  (lt) => {
    ransom('WARUNKI', 0, -620, 120, 0.1, lt, 21, 0.06);
    ransom('UWOLNIENIA:', 0, -460, 105, 0.55, lt, 22, 0.05);
    const L = ['→ 2 godziny w studiu', '→ mikrofony Shure', '→ dwie kamery 4K', '→ profesjonalne światło', '→ pliki od ręki'];
    L.forEach((s, i) => strip(s, 0, -230 + i * 150, 1.3 + i * 0.55, lt, 23 + i * 5));
    hand('i żadnych wymówek!', 60, 560, 92, 4.2, lt, { dur: 0.8, col: '#D3172A' });
  },
  (lt) => {
    ransom('TU GO', 0, -650, 115, 0.1, lt, 31, 0.06);
    ransom('TRZYMAMY:', 0, -500, 115, 0.45, lt, 32, 0.06);
    polaroid('101', -175, -150, 440, -0.09, 1.2, lt, 'wygłuszone', 33, 0.35);
    polaroid('104', 205, 180, 440, 0.08, 1.8, lt, 'ma światło', 34);
    polaroid('034', -150, 500, 440, -0.04, 2.4, lt, 'nie narzeka', 35, 0.45);
    hand('Warszawa', 240, 560, 96, 3.0, lt, { dur: 0.6, rot: -0.12 });
  },
  (lt) => {
    ransom('OKUP:', 0, -520, 150, 0.1, lt, 41, 0.08);
    ransom('300 ZŁ', 0, -150, 230, 0.75, lt, 42, 0.12);
    circleInk(0, -150, 470, 200, 1.9, lt);
    hand('brutto, za 2 godziny', 0, 200, 92, 2.3, lt, { dur: 0.7 });
    hand('sprzęt w cenie', 0, 320, 92, 2.9, lt, { dur: 0.6 });
    strip('płatne przy przekazaniu', 0, 560, 3.6, lt, 47, 54);
  },
  (lt) => {
    ransom('NIE MÓW', 0, -620, 130, 0.1, lt, 51, 0.06);
    ransom('NIKOMU.', 0, -450, 140, 0.55, lt, 52, 0.07);
    hand('…albo oznacz kogoś,', 0, -230, 84, 1.5, lt, { dur: 0.7 });
    hand('kto też ma podcast', 0, -125, 84, 2.1, lt, { dur: 0.6 });
    hand('w szufladzie', 0, -20, 84, 2.6, lt, { dur: 0.5 });
    if (lt > 3.2) { // naklejka z logo
      const age = lt - 3.2, sc = age < 1 / FPS_SM ? 1.25 : 1;
      cx.save(); cx.translate(0 + jit(61, 1), 280 + jit(62, 1)); cx.rotate(-0.06); cx.scale(sc, sc);
      cx.shadowColor = 'rgba(0,0,0,.3)'; cx.shadowBlur = 14; cx.shadowOffsetY = 6;
      cx.fillStyle = OR; cx.beginPath(); cx.roundRect(-330, -140, 660, 280, 40); cx.fill(); cx.shadowColor = 'transparent';
      cx.drawImage(IM.logoB, -260, -95, 520, 520 * 510 / 1400);
      cx.restore();
      tape(-300, 160, 160, 50, -0.5, 63);
    }
    strip('przekazanie: gadkastudio.pl', 0, 560, 3.8, lt, 64, 50);
  },
];

function sheet(i, lt, base) {
  const rot = [-0.02, 0.025, -0.015, 0.02, -0.025, 0.012][i];
  const k = Math.floor(lt * FPS_SM), slide = base ? 0 : Math.max(0, 4 - k) / 4; // wjazd w 4 klatkach
  const ox = [0, 30, -25, 20, -30, 10][i];
  cx.save(); cx.translate(540 + ox * slide + jit(i * 99, base ? 0 : 0.8), 960 + 1700 * slide * slide + jit(i * 98, base ? 0 : 0.8)); cx.rotate(rot + slide * 0.12);
  cx.shadowColor = 'rgba(0,0,0,.5)'; cx.shadowBlur = 40; cx.shadowOffsetY = 14;
  cx.drawImage(paper, -SW / 2, -SHH / 2); cx.shadowColor = 'transparent';
  SC[i](base ? 99 : lt);
  cx.restore();
}

window.renderAt = function (t) {
  const tq = Math.floor(t * FPS_SM) / FPS_SM; FR = Math.floor(t * FPS_SM);
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.globalAlpha = 1; cx.filter = 'none';
  cx.drawImage(desk, 0, 0);
  const S = D.S;
  let i = 0; while (i + 1 < S.length && tq >= S[i + 1]) i++;
  if (i > 0) sheet(i - 1, 0, true);
  sheet(i, tq - S[i], false);
  // lekkie migotanie światła jak w animacji poklatkowej
  cx.fillStyle = `rgba(0,0,0,${0.03 + 0.03 * rnd(FR)})`; cx.fillRect(0, 0, W, H);
  if (t > D.TOTAL - 0.5) { cx.fillStyle = `rgba(0,0,0,${clamp((t - D.TOTAL + 0.5) / 0.5)})`; cx.fillRect(0, 0, W, H); }
};
