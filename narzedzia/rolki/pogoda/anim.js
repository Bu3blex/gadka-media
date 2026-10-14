// Prognoza pogody dla twórców – Gadka studio
const D = window.DATA;
const cv = document.getElementById('c'), cx = cv.getContext('2d');
const W = 1080, H = 1920;
const NAVY = '#06173F', BLUE = '#1546B8', SKY = '#3D8BFF', YEL = '#FFC72C', OR = '#FF592A', CREAM = '#F9EEE4', RED = '#E3262E';
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const eo = x => 1 - Math.pow(1 - clamp(x), 3);
const eio = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const ob = (x, k = 1.8) => { x = clamp(x); const c3 = k + 1; return 1 + c3 * Math.pow(x - 1, 3) + k * Math.pow(x - 1, 2); };
const lerp = (a, b, p) => a + (b - a) * p;
function rnd(n) { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); }

const IM = {}; let pending = 0;
function load(k, src) { pending++; const i = new Image(); i.onload = () => { if (--pending === 0) window.READY = true; }; i.src = src; IM[k] = i; }
['101', '056', '104', '034', '050'].forEach(n => load(n, `img/${n}.jpg`));
load('logo', 'logo.png'); load('logoB', 'logo_black.png');
const fonts = [['Semi', 'SemiBold'], ['Bold', 'Bold'], ['XB', 'ExtraBold'], ['Blk', 'Black'], ['Light', 'Light']];
pending++;
Promise.all(fonts.map(([n, u]) => new FontFace(n, `url(fonts/InterDisplay-${u}.otf)`).load().then(f => document.fonts.add(f)))).then(() => { if (--pending === 0) window.READY = true; });

function txt(s, x, y, o) {
  o = Object.assign({ f: 'Bold', sz: 60, col: '#fff', sp: 0, a: 1, al: 'center', bl: 'middle' }, o);
  if (o.a <= 0) return;
  cx.save(); cx.globalAlpha *= o.a; cx.font = `${o.sz}px ${o.f}`; cx.fillStyle = o.col;
  cx.letterSpacing = o.sp + 'px'; cx.textAlign = o.al; cx.textBaseline = o.bl;
  if (o.sh) { cx.shadowColor = 'rgba(0,0,0,.35)'; cx.shadowBlur = o.sh; cx.shadowOffsetY = o.sh / 3; }
  cx.fillText(s, x, y); cx.restore();
}
function rr(x, y, w, h, r) { cx.beginPath(); cx.roundRect(x, y, w, h, r); }

// ---------- ikony pogody (środek 0,0, rozmiar ~200)
function cloud(x, y, s, col = '#fff', a = 1) {
  cx.save(); cx.globalAlpha *= a; cx.translate(x, y); cx.scale(s, s); cx.fillStyle = col;
  cx.beginPath(); cx.arc(-45, 10, 42, 0, 7); cx.arc(0, -15, 58, 0, 7); cx.arc(50, 8, 44, 0, 7); cx.fill();
  rr(-87, 10, 181, 46, 23); cx.fill(); cx.restore();
}
function sun(x, y, s, t, a = 1) {
  cx.save(); cx.globalAlpha *= a; cx.translate(x, y); cx.scale(s, s);
  const g = cx.createRadialGradient(0, 0, 10, 0, 0, 150); g.addColorStop(0, 'rgba(255,210,60,.55)'); g.addColorStop(1, 'rgba(255,210,60,0)');
  cx.fillStyle = g; cx.beginPath(); cx.arc(0, 0, 150, 0, 7); cx.fill();
  cx.rotate(t * 0.6); cx.fillStyle = YEL;
  for (let i = 0; i < 12; i++) { cx.rotate(Math.PI / 6); rr(-7, -100 - 6 * Math.sin(t * 4 + i), 14, 34, 7); cx.fill(); }
  cx.beginPath(); cx.arc(0, 0, 58, 0, 7); cx.fillStyle = '#FFB000'; cx.fill();
  cx.beginPath(); cx.arc(-8, -8, 46, 0, 7); cx.fillStyle = YEL; cx.fill();
  cx.restore();
}
function bolt(x, y, s, a = 1) {
  cx.save(); cx.globalAlpha *= a; cx.translate(x, y); cx.scale(s, s); cx.fillStyle = YEL;
  cx.beginPath(); cx.moveTo(10, -40); cx.lineTo(-25, 20); cx.lineTo(2, 20); cx.lineTo(-12, 70); cx.lineTo(32, 0); cx.lineTo(6, 0); cx.lineTo(22, -40); cx.closePath(); cx.fill();
  cx.restore();
}
function rain(x, y, s, t, a = 1) {
  cx.save(); cx.globalAlpha *= a; cx.translate(x, y); cx.scale(s, s); cx.strokeStyle = '#9CC8FF'; cx.lineWidth = 8; cx.lineCap = 'round';
  for (let i = 0; i < 5; i++) { const p = (t * 1.6 + i * 0.37) % 1; const xx = -60 + i * 30 - p * 14, yy = 60 + p * 70; cx.globalAlpha = a * (1 - p); cx.beginPath(); cx.moveTo(xx, yy); cx.lineTo(xx - 8, yy + 22); cx.stroke(); }
  cx.restore();
}
function waves(x, y, s, t, a = 1, col = '#fff') { // fale dźwięku / echo
  cx.save(); cx.translate(x, y); cx.scale(s, s); cx.strokeStyle = col; cx.lineCap = 'round';
  for (let i = 0; i < 4; i++) {
    const p = (t * 0.9 + i / 4) % 1; cx.globalAlpha = a * (1 - p); cx.lineWidth = 9 * (1 - p) + 2;
    cx.beginPath(); cx.arc(0, 0, 30 + p * 120, -0.7, 0.7); cx.stroke();
    cx.beginPath(); cx.arc(0, 0, 30 + p * 120, Math.PI - 0.7, Math.PI + 0.7); cx.stroke();
  }
  cx.restore();
}
function fog(x, y, s, t, a = 1) {
  cx.save(); cx.globalAlpha *= a; cx.translate(x, y); cx.scale(s, s); cx.strokeStyle = 'rgba(255,255,255,.9)'; cx.lineWidth = 12; cx.lineCap = 'round';
  for (let i = 0; i < 4; i++) { const o = Math.sin(t * 1.5 + i) * 18; cx.beginPath(); cx.moveTo(-90 + o + (i % 2) * 20, -30 + i * 28); cx.lineTo(80 + o - (i % 2) * 20, -30 + i * 28); cx.stroke(); }
  cx.restore();
}
function icon(kind, x, y, s, t, a = 1) {
  if (kind === 'fridge') { cloud(x, y, s, '#E8F0FF', a); waves(x, y + 15 * s, s * 0.9, t, a * 0.9, '#1546B8'); }
  if (kind === 'echo') { waves(x, y, s * 1.3, t * 1.2, a); txt('ECHO', x, y, { f: 'XB', sz: 34 * s, a, sp: 4 }); }
  if (kind === 'storm') { cloud(x, y - 20 * s, s, '#5B6B8C', a); rain(x, y - 20 * s, s, t, a); if ((t * 3) % 1 < 0.55) bolt(x + 10 * s, y + 40 * s, s, a); }
  if (kind === 'fog') { cloud(x - 20 * s, y - 30 * s, s * 0.8, '#C9D6EE', a); fog(x, y + 30 * s, s, t, a); }
  if (kind === 'sun') sun(x, y, s, t, a);
  if (kind === 'rain') { cloud(x, y - 20 * s, s, '#B9C9E6', a); rain(x, y - 20 * s, s, t, a); }
  if (kind === 'suncloud') { sun(x + 30 * s, y - 30 * s, s * 0.75, t, a); cloud(x - 15 * s, y + 15 * s, s * 0.85, '#fff', a); }
}

// ---------- tło studia TV
function bg(t) {
  const g = cx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#0A2463'); g.addColorStop(0.55, BLUE); g.addColorStop(1, '#0A2463');
  cx.fillStyle = g; cx.fillRect(0, 0, W, H);
  // połyskujące pasy
  cx.save(); cx.globalAlpha = 0.07; cx.fillStyle = '#fff';
  for (let i = 0; i < 6; i++) { const x = ((t * 40 + i * 260) % 1560) - 300; cx.beginPath(); cx.moveTo(x, 0); cx.lineTo(x + 120, 0); cx.lineTo(x - 280, H); cx.lineTo(x - 400, H); cx.fill(); }
  cx.restore();
}
function header(t) {
  const a = clamp((t - D.INTRO) / 0.4);
  if (a <= 0) return;
  const y = 150 - 60 * (1 - eo((t - D.INTRO) / 0.5));
  cx.save(); cx.globalAlpha = a;
  rr(60, y, 620, 92, 14); cx.fillStyle = '#fff'; cx.fill();
  rr(60, y, 120, 92, 14); cx.fillStyle = OR; cx.fill();
  cx.drawImage(IM.logoB, 70, y + 26, 100, 100 * 510 / 1400);
  txt('PROGNOZA DLA TWÓRCÓW', 198, y + 47, { f: 'XB', sz: 31, col: NAVY, al: 'left', sp: 1 });
  rr(696, y, 324, 92, 14); cx.fillStyle = 'rgba(6,23,63,.75)'; cx.fill();
  if (Math.floor(t * 1.5) % 2 === 0) { cx.fillStyle = RED; cx.beginPath(); cx.arc(775, y + 46, 12, 0, 7); cx.fill(); }
  txt('NA ŻYWO', 800, y + 47, { f: 'XB', sz: 32, al: 'left', sp: 2 });
  cx.restore();
}
function ticker(t) {
  if (t < D.INTRO + 0.3) return;
  const a = clamp((t - D.INTRO - 0.3) / 0.3), y = 1745;
  cx.save(); cx.globalAlpha = a;
  cx.fillStyle = NAVY; cx.fillRect(0, y, W, 86);
  cx.fillStyle = YEL; cx.fillRect(0, y, 230, 86);
  const msg = '  MIKROFONY SHURE  ◆  DWIE KAMERY 4K  ◆  PROFESJONALNE ŚWIATŁO  ◆  PLIKI OD RĘKI  ◆  2 GODZINY ZA 300 ZŁ BRUTTO  ◆  SPRZĘT W CENIE  ◆  WARSZAWA  ◆  GADKASTUDIO.PL  ◆';
  cx.font = '38px Bold'; cx.letterSpacing = '1px';
  const mw = cx.measureText(msg).width;
  cx.beginPath(); cx.rect(230, y, W - 230, 86); cx.clip();
  const off = ((t - D.INTRO) * 170) % mw;
  cx.fillStyle = '#fff'; cx.textBaseline = 'middle';
  for (let k = 0; k < 3; k++) cx.fillText(msg, 240 - off + k * mw, y + 45);
  cx.restore();
  cx.save(); cx.globalAlpha = a; txt('PILNE', 115, y + 45, { f: 'Blk', sz: 40, col: NAVY, sp: 3 }); cx.restore();
}

// ---------- plan mieszkania
const ROOMS = [
  { n: 'KUCHNIA', x: 110, y: 420, w: 390, h: 380, ic: 'fridge' },
  { n: 'ŁAZIENKA', x: 500, y: 420, w: 230, h: 380, ic: 'echo' },
  { n: 'SYPIALNIA', x: 730, y: 420, w: 240, h: 560, ic: 'fog' },
  { n: 'SALON', x: 110, y: 800, w: 620, h: 600, ic: 'storm' },
  { n: 'PRZEDPOKÓJ', x: 730, y: 980, w: 240, h: 420, ic: null },
];
const FC = [ // prognozy pokojów
  { r: 0, title: 'Szum lodówki', stat: '100%', sub: 'szans na buczenie w tle' },
  { r: 1, title: 'Silny pogłos', stat: '4,2 s', sub: 'echa po każdym zdaniu' },
  { r: 3, title: 'Burza z wiertarką', stat: '8:00', sub: 'sąsiad zaczyna punktualnie' },
  { r: 2, title: 'Mgła wymówek', stat: '∞', sub: 'front „od jutra” bez zmian' },
];
function plan(t, draw) {
  // isobary
  cx.save(); cx.strokeStyle = 'rgba(255,255,255,.28)'; cx.lineWidth = 4; cx.setLineDash([18, 14]); cx.lineDashOffset = -t * 40;
  for (let i = 0; i < 5; i++) {
    cx.beginPath();
    for (let x = 40; x <= 1040; x += 20) { const y = 470 + i * 220 + Math.sin(x / 160 + i + t * 0.5) * 60; x === 40 ? cx.moveTo(x, y) : cx.lineTo(x, y); }
    cx.stroke();
  }
  cx.restore();
  // ściany – rysowanie
  cx.save(); cx.strokeStyle = '#fff'; cx.lineWidth = 12; cx.lineJoin = 'round';
  ROOMS.forEach((r, i) => {
    const p = clamp(draw * 1.6 - i * 0.15);
    if (p <= 0) return;
    cx.fillStyle = 'rgba(255,255,255,.07)'; cx.globalAlpha = p; cx.fillRect(r.x, r.y, r.w, r.h); cx.globalAlpha = 1;
    const per = 2 * (r.w + r.h);
    cx.setLineDash([per * p, per]); cx.strokeRect(r.x, r.y, r.w, r.h);
  });
  cx.setLineDash([]);
  // drzwi
  if (draw > 0.8) {
    cx.globalAlpha = clamp((draw - 0.8) / 0.2); cx.lineWidth = 4; cx.strokeStyle = 'rgba(255,255,255,.7)';
    [[300, 800, 0], [615, 800, 0], [730, 1150, 1]].forEach(([x, y, v]) => {
      cx.fillStyle = BLUE; if (v) cx.fillRect(x - 8, y - 45, 16, 90); else cx.fillRect(x - 45, y - 8, 90, 16);
      cx.beginPath(); if (v) cx.arc(x, y - 45, 90, 0, Math.PI / 2); else cx.arc(x - 45, y, 90, -Math.PI / 2, 0); cx.stroke();
    });
    cx.globalAlpha = 1;
  }
  cx.restore();
  ROOMS.forEach((r, i) => { const a = clamp(draw * 2 - 1 - i * 0.1); txt(r.n, r.x + 22, r.y + 40, { f: 'XB', sz: r.w < 300 ? 25 : 30, al: 'left', sp: 2, a: a * 0.85 }); });
}
function planIcons(t, focus) {
  ROOMS.forEach((r, i) => {
    if (!r.ic) return;
    const k = FC.findIndex(f => f.r === i), t0 = D.ROOM[k];
    const a = clamp((t - t0 + 0.2) / 0.3);
    if (a <= 0) return;
    const s = (r.w < 300 ? 0.75 : 1.0) * ob((t - t0 + 0.2) / 0.45, 2.2);
    icon(r.ic, r.x + r.w / 2, r.y + r.h / 2 + 20, s, t, a);
  });
  // niż motywacji
  const a = Math.max(clamp((t - D.MAP - 0.9) / 0.4) * clamp((D.ROOM[0] - t + 0.2) / 0.3), clamp((t - D.ROOM[3] - D.RDUR - 0.3) / 0.3));
  if (a > 0) {
    cx.save(); cx.globalAlpha = a;
    txt('N', 250, 1230, { f: 'Blk', sz: 130, col: RED, sh: 10 });
    txt('NIŻ MOTYWACJI', 250, 1315, { f: 'XB', sz: 34, col: '#fff', sp: 2 });
    cx.restore();
  }
}
function fcCard(t, k) {
  const f = FC[k], t0 = D.ROOM[k], t1 = k < 3 ? D.ROOM[k + 1] : D.ROOM[3] + D.RDUR;
  const lt = t - t0;
  if (lt < 0 || t > t1) return;
  const pin = eo(lt / 0.4), pout = clamp((t1 - t) / 0.25);
  const y = 1430 + 300 * (1 - pin);
  cx.save(); cx.globalAlpha = pout;
  rr(60, y, 960, 270, 34); cx.fillStyle = 'rgba(255,255,255,.96)'; cx.shadowColor = 'rgba(0,0,0,.35)'; cx.shadowBlur = 40; cx.fill(); cx.shadowBlur = 0;
  rr(60, y, 960, 64, [34, 34, 0, 0]); cx.fillStyle = YEL; cx.fill();
  txt('⚠ OSTRZEŻENIE · ' + ROOMS[f.r].n, 100, y + 34, { f: 'XB', sz: 32, col: NAVY, al: 'left', sp: 2 });
  txt(f.title, 100, y + 135, { f: 'XB', sz: 60, col: NAVY, al: 'left' });
  txt(f.sub, 100, y + 205, { f: 'Semi', sz: 38, col: '#4A5B80', al: 'left' });
  const sc = ob((lt - 0.25) / 0.4, 2.5);
  cx.save(); cx.translate(940, y + 165); cx.scale(sc, sc);
  txt(f.stat, 0, 0, { f: 'Blk', sz: f.stat === '∞' ? 150 : 104, col: RED, al: 'right' });
  cx.restore();
  cx.restore();
}

// ---------- sceny
function alertScene(t) {
  // ostrzeżenie – hook
  const fl = Math.floor(t * 4) % 2;
  cx.fillStyle = fl ? '#B5121B' : RED; cx.fillRect(0, 0, W, H);
  cx.save(); cx.globalAlpha = 0.18; cx.fillStyle = '#000';
  for (let i = -4; i < 30; i++) { const x = i * 110 + (t * 80) % 110; cx.beginPath(); cx.moveTo(x, 0); cx.lineTo(x + 55, 0); cx.lineTo(x - 245, 300); cx.lineTo(x - 300, 300); cx.fill(); cx.beginPath(); cx.moveTo(x, 1620); cx.lineTo(x + 55, 1620); cx.lineTo(x - 245, 1920); cx.lineTo(x - 300, 1920); cx.fill(); }
  cx.restore();
  cx.fillStyle = YEL; cx.fillRect(0, 300, W, 16); cx.fillRect(0, 1604, W, 16);
  const s = ob(t / 0.35, 2);
  cx.save(); cx.translate(W / 2, 560); cx.scale(s, s);
  // trójkąt
  cx.fillStyle = YEL; cx.beginPath(); cx.moveTo(0, -150); cx.lineTo(160, 120); cx.lineTo(-160, 120); cx.closePath(); cx.lineJoin = 'round'; cx.lineWidth = 30; cx.strokeStyle = YEL; cx.stroke(); cx.fill();
  txt('!', 0, 30, { f: 'Blk', sz: 210, col: '#111' });
  cx.restore();
  const a2 = clamp((t - 0.15) / 0.2);
  txt('OSTRZEŻENIE', W / 2, 820, { f: 'Blk', sz: 118, sp: 2, a: a2, sh: 10 });
  txt('III STOPNIA', W / 2, 935, { f: 'Blk', sz: 118, col: YEL, sp: 2, a: a2, sh: 10 });
  const a3 = clamp((t - 0.6) / 0.25);
  rr(90, 1050, 900, 360, 30); cx.save(); cx.globalAlpha = a3; cx.fillStyle = 'rgba(0,0,0,.35)'; cx.fill(); cx.restore();
  txt('dla osób nagrywających', W / 2, 1130, { f: 'Semi', sz: 50, a: a3 });
  txt('podcast w domu', W / 2, 1195, { f: 'Semi', sz: 50, a: a3 });
  txt('echo · lodówka · wiertarka', W / 2, 1310, { f: 'XB', sz: 58, col: YEL, a: a3 });
}

function liveCam(t) {
  const lt = t - D.LIVE;
  const pin = eo(lt / 0.5);
  // mini mapa miasta w tle
  cx.save(); cx.globalAlpha = 0.25; cx.strokeStyle = '#9CC0FF'; cx.lineWidth = 6;
  for (let i = 0; i < 9; i++) { cx.beginPath(); cx.moveTo(-100, 300 + i * 190 + Math.sin(i) * 60); cx.lineTo(1180, 380 + i * 170 - Math.cos(i) * 70); cx.stroke(); }
  for (let i = 0; i < 7; i++) { cx.beginPath(); cx.moveTo(80 + i * 170, 250); cx.lineTo(20 + i * 190 + Math.sin(i * 2) * 50, 1750); cx.stroke(); }
  cx.restore();
  // okno kamery
  const x = 70, y = 330 + 140 * (1 - pin), w = 940, h = 660;
  cx.save(); cx.globalAlpha = pin;
  rr(x - 10, y - 10, w + 20, h + 20, 40); cx.fillStyle = '#fff'; cx.shadowColor = 'rgba(0,0,0,.4)'; cx.shadowBlur = 50; cx.fill(); cx.shadowBlur = 0;
  rr(x, y, w, h, 32); cx.save(); cx.clip();
  const seq = ['101', '056', '104', '034'], dur = (D.FCST - D.LIVE) / seq.length;
  const idx = Math.min(seq.length - 1, Math.floor(lt / dur)), p = (lt - idx * dur) / dur;
  const im = IM[seq[idx]], s = Math.max(w / im.width, h / im.height) * (1.06 + 0.06 * p);
  cx.drawImage(im, x + w / 2 - im.width * s / 2 + (p - 0.5) * 40, y + h / 2 - im.height * s / 2, im.width * s, im.height * s);
  if (p < 0.08 && idx > 0) { cx.fillStyle = `rgba(255,255,255,${0.6 * (1 - p / 0.08)})`; cx.fillRect(x, y, w, h); }
  cx.restore();
  rr(x + 30, y + 30, 360, 66, 33); cx.fillStyle = 'rgba(0,0,0,.6)'; cx.fill();
  if (Math.floor(t * 1.5) % 2 === 0) { cx.fillStyle = RED; cx.beginPath(); cx.arc(x + 70, y + 63, 13, 0, 7); cx.fill(); }
  txt('KAMERA NA ŻYWO', x + 98, y + 64, { f: 'XB', sz: 30, al: 'left', sp: 2 });
  cx.restore();
  // pin + nazwa
  const a2 = clamp((lt - 0.4) / 0.4);
  cx.save(); cx.globalAlpha = a2;
  rr(70, 1040, 940, 120, 26); cx.fillStyle = '#fff'; cx.fill();
  cx.fillStyle = OR; cx.beginPath(); cx.arc(140, 1090, 26, Math.PI, 0); cx.lineTo(140, 1135); cx.closePath(); cx.fill();
  cx.fillStyle = '#fff'; cx.beginPath(); cx.arc(140, 1090, 10, 0, 7); cx.fill();
  txt('GADKA STUDIO', 190, 1080, { f: 'Blk', sz: 50, col: NAVY, al: 'left' });
  txt('Warszawa · studio podcastowe', 190, 1130, { f: 'Semi', sz: 32, col: '#4A5B80', al: 'left' });
  cx.restore();
  icon('sun', 905, 1060, 0.95 * ob((lt - 0.6) / 0.5, 2), t, clamp((lt - 0.6) / 0.3));
  // statystyki
  const st = [['☀', 'Bezchmurnie', 'zero echa'], ['🎙', 'Cisza: 100%', 'wygłuszone studio'], ['✓', 'Sprzęt w cenie', 'Shure · 4K · światło']];
  st.forEach(([ic, a, b], i) => {
    const aa = clamp((lt - 1.0 - i * 0.35) / 0.3), yy = 1215 + i * 165 + 30 * (1 - eo((lt - 1.0 - i * 0.35) / 0.4));
    if (aa <= 0) return;
    cx.save(); cx.globalAlpha = aa;
    rr(70, yy, 940, 140, 26); cx.fillStyle = 'rgba(6,23,63,.72)'; cx.fill();
    cx.fillStyle = YEL; cx.beginPath(); cx.arc(150, yy + 70, 44, 0, 7); cx.fill();
    if (i === 0) { sun(150, yy + 70, 0.32, t); }
    else if (i === 1) { txt('dB', 150, yy + 72, { f: 'Blk', sz: 34, col: NAVY }); }
    else { cx.strokeStyle = NAVY; cx.lineWidth = 9; cx.lineCap = 'round'; cx.beginPath(); cx.moveTo(130, yy + 72); cx.lineTo(146, yy + 88); cx.lineTo(172, yy + 54); cx.stroke(); }
    txt(a, 220, yy + 52, { f: 'XB', sz: 48, al: 'left' });
    txt(b, 220, yy + 102, { f: 'Semi', sz: 34, col: '#BFD3FF', al: 'left' });
    cx.restore();
  });
}

function forecast(t) {
  const lt = t - D.FCST;
  txt('PROGNOZA NA NAJBLIŻSZE DNI', W / 2, 360, { f: 'XB', sz: 50, sp: 2, a: clamp(lt / 0.3) });
  const days = [
    ['PON', 'rain', 'od poniedziałku', '12°'], ['WT', 'storm', 'nie mam sprzętu', '9°'],
    ['ŚR', 'fog', 'echo w pokoju', '7°'], ['CZW', 'sun', 'NAGRYWASZ', ''],
  ];
  days.forEach((d, i) => {
    const t0 = 0.35 + i * 0.75, p = eo((lt - t0) / 0.4);
    if (lt < t0) return;
    const last = i === 3;
    const y = 450 + i * 300, x = 70 + 200 * (1 - p);
    const big = last ? ob((lt - t0) / 0.5, 2) : 1;
    cx.save(); cx.globalAlpha = clamp((lt - t0) / 0.25);
    cx.translate(x + 470, y + 130); cx.scale(big, big); cx.translate(-(x + 470), -(y + 130));
    rr(x, y, 940, 260, 34);
    cx.fillStyle = last ? OR : 'rgba(255,255,255,.12)'; cx.fill();
    if (!last) { cx.strokeStyle = 'rgba(255,255,255,.3)'; cx.lineWidth = 3; cx.stroke(); }
    txt(d[0], x + 50, y + 130, { f: 'Blk', sz: 62, al: 'left', col: last ? '#fff' : '#BFD3FF' });
    icon(d[1], x + 300, y + 130, 0.62, t);
    txt(d[2], x + 420, y + (last ? 105 : 130), { f: last ? 'Blk' : 'Bold', sz: last ? 58 : 44, al: 'left', col: '#fff' });
    if (last) txt('Gadka studio · 2 h · 300 zł', x + 420, y + 170, { f: 'Semi', sz: 36, al: 'left', col: CREAM });
    txt(d[3], x + 900, y + 130, { f: 'Blk', sz: last ? 66 : 58, al: 'right', col: last ? '#fff' : 'rgba(255,255,255,.55)' });
    cx.restore();
    // przekreślenie starych dni
    if (!last && lt > 3.0 + i * 0.12) {
      const q = eo((lt - 3.0 - i * 0.12) / 0.2);
      cx.fillStyle = 'rgba(6,23,63,.45)'; rr(x, y, 940, 260, 34); cx.save(); cx.globalAlpha = q; cx.fill(); cx.restore();
      cx.strokeStyle = YEL; cx.lineWidth = 10; cx.lineCap = 'round'; cx.beginPath(); cx.moveTo(x + 400, y + 135); cx.lineTo(x + 400 + 430 * q, y + 125); cx.stroke();
    }
  });
}

function endCard(t) {
  const lt = t - D.END;
  cx.fillStyle = OR; cx.beginPath(); cx.arc(W / 2, 960, 2400 * eo(lt / 0.6), 0, 7); cx.fill();
  sun(W / 2, 520, 1.5 * ob((lt - 0.2) / 0.6, 1.6), t, clamp((lt - 0.2) / 0.3));
  txt('PROGNOZA NA JUTRO:', W / 2, 820, { f: 'XB', sz: 50, sp: 4, col: NAVY, a: clamp((lt - 0.4) / 0.3) });
  const s = ob((lt - 0.6) / 0.5, 2.4);
  cx.save(); cx.translate(W / 2, 950); cx.scale(s, s); txt('NAGRYWASZ.', 0, 0, { f: 'Blk', sz: 140, col: '#fff', sh: 14 }); cx.restore();
  const a = clamp((lt - 1.2) / 0.4);
  txt('2 h w studiu · 300 zł brutto', W / 2, 1105, { f: 'Bold', sz: 50, col: NAVY, a });
  txt('sprzęt w cenie', W / 2, 1170, { f: 'Bold', sz: 50, col: NAVY, a });
  const a2 = clamp((lt - 1.7) / 0.4);
  cx.save(); cx.globalAlpha = a2; const lw = 520; cx.drawImage(IM.logoB, W / 2 - lw / 2, 1300, lw, lw * 510 / 1400); cx.restore();
  // logo jest kremowo-pomarańczowe – podkład
  txt('gadkastudio.pl', W / 2, 1560, { f: 'XB', sz: 52, col: '#fff', a: a2 });
}

window.renderAt = function (t) {
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.globalAlpha = 1; cx.globalCompositeOperation = 'source-over'; cx.setLineDash([]);
  if (t < D.INTRO) { alertScene(t); return; }
  bg(t);
  if (t < D.LIVE) {
    // kamera po planie
    const cam = [[540, 900, 1]];
    let cxx = 540, cyy = 910, z = 0.95;
    const tgt = k => { const r = ROOMS[FC[k].r]; return [r.x + r.w / 2, r.y + r.h / 2 + 30, r.w < 300 ? 1.75 : 1.4]; };
    for (let k = 0; k < 4; k++) {
      const p = eio((t - D.ROOM[k] + 0.15) / 0.6);
      if (p > 0) { const [a, b, c] = tgt(k); cxx = lerp(cxx, a, p); cyy = lerp(cyy, b, p); z = lerp(z, c, p); }
    }
    const pb = eio((t - D.ROOM[3] - D.RDUR + 0.1) / 0.6);
    if (pb > 0) { cxx = lerp(cxx, 540, pb); cyy = lerp(cyy, 910, pb); z = lerp(z, 0.95, pb); }
    // wylot do miasta
    const po = eio((t - D.LIVE + 0.7) / 0.7);
    z *= 1 - 0.7 * po;
    const intro = eo((t - D.INTRO) / 0.6);
    cx.save(); cx.globalAlpha = 1 - po;
    cx.translate(540, 920); cx.scale(z * (0.85 + 0.15 * intro), z * (0.85 + 0.15 * intro)); cx.rotate(-0.25 * po); cx.translate(-cxx, -cyy);
    plan(t, clamp((t - D.MAP) / 1.0));
    planIcons(t);
    cx.restore();
    for (let k = 0; k < 4; k++) fcCard(t, k);
    // tytuł wejścia
    const ta = clamp((t - D.INTRO) / 0.3) * clamp((D.MAP + 0.9 - t) / 0.3);
    if (ta > 0) {
      cx.save(); cx.globalAlpha = ta;
      const s = ob((t - D.INTRO) / 0.5, 2);
      cx.translate(W / 2, 1520); cx.scale(s, s);
      rr(-430, -90, 860, 180, 30); cx.fillStyle = YEL; cx.fill();
      txt('POGODA', 0, -22, { f: 'Blk', sz: 80, col: NAVY, sp: 4 });
      txt('w Twoim mieszkaniu', 0, 48, { f: 'Bold', sz: 40, col: NAVY });
      cx.restore();
    }
  } else if (t < D.FCST) liveCam(t);
  else if (t < D.END) forecast(t);
  if (t < D.END + 0.6) { header(t); ticker(t); }
  if (t >= D.END) endCard(t);
  // przejścia: biały błysk
  [D.INTRO, D.LIVE, D.FCST].forEach(x => { const f = clamp(1 - Math.abs(t - x) / 0.08); if (f > 0) { cx.fillStyle = `rgba(255,255,255,${0.7 * f})`; cx.fillRect(0, 0, W, H); } });
  if (t > D.TOTAL - 0.5) { cx.fillStyle = `rgba(0,0,0,${clamp((t - D.TOTAL + 0.5) / 0.5)})`; cx.fillRect(0, 0, W, H); }
};
