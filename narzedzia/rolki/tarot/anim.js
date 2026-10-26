// Tarot dla podcasterów – Gadka studio
const D = window.DATA;
const cv = document.getElementById('c'), cx = cv.getContext('2d');
const W = 1080, H = 1920, GOLD = '#E8C27A', GOLD2 = '#B8893E', NAVY = '#0E0B24', INK = '#1A1538', OR = '#FF592A', CR = '#F9EEE4';
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const eo = x => 1 - Math.pow(1 - clamp(x), 3);
const eio = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const ob = (x, k = 1.8) => { x = clamp(x); const c3 = k + 1; return 1 + c3 * Math.pow(x - 1, 3) + k * Math.pow(x - 1, 2); };
const lerp = (a, b, p) => a + (b - a) * p;
function rnd(n) { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); }

const IM = {}; let pending = 0;
function done() { if (--pending === 0) window.READY = true; }
function load(k, src) { pending++; const i = new Image(); i.onload = done; i.src = src; IM[k] = i; }
['fotel', '056', '101', 'noise'].forEach(n => load(n, n === 'noise' ? 'img/noise.png' : `img/${n}.jpg`));
load('logo', 'logo.png');
pending++;
Promise.all([...[['Semi', 'SemiBold'], ['XB', 'ExtraBold'], ['Blk', 'Black'], ['Light', 'Light']].map(([n, u]) => new FontFace(n, `url(fonts/InterDisplay-${u}.otf)`).load().then(f => document.fonts.add(f))),
  document.fonts.load('bold 60px "TeX Gyre Bonum"'), document.fonts.load('italic 600 60px Lora')]).then(done);

function txt(s, x, y, o) {
  o = Object.assign({ font: '60px Semi', col: GOLD, sp: 0, a: 1, al: 'center' }, o);
  if (o.a <= 0) return;
  cx.save(); cx.globalAlpha *= o.a; cx.font = o.font; cx.fillStyle = o.col; cx.letterSpacing = o.sp + 'px';
  cx.textAlign = o.al; cx.textBaseline = 'middle';
  if (o.glow) { cx.shadowColor = o.gcol || 'rgba(232,194,122,.7)'; cx.shadowBlur = o.glow; }
  cx.fillText(s, x, y); cx.restore();
}
function gstroke(w = 5) { cx.strokeStyle = GOLD; cx.lineWidth = w; cx.lineCap = 'round'; cx.lineJoin = 'round'; }

// ---------- tło: noc, gwiazdy, dym, świece
function bg(t) {
  const g = cx.createRadialGradient(540, 900, 100, 540, 900, 1300); g.addColorStop(0, '#231C4F'); g.addColorStop(1, '#07051A');
  cx.fillStyle = g; cx.fillRect(0, 0, W, H);
  for (let i = 0; i < 90; i++) {
    const x = rnd(i) * W, y = rnd(i + 50) * H, tw = 0.4 + 0.6 * Math.abs(Math.sin(t * (1 + rnd(i + 9) * 2) + i));
    cx.fillStyle = `rgba(255,236,200,${0.5 * tw})`; cx.beginPath(); cx.arc(x, y, 1 + 2.2 * rnd(i + 3), 0, 7); cx.fill();
  }
  // dym
  for (let i = 0; i < 7; i++) {
    const x = (rnd(i + 20) * W + t * (20 + 15 * rnd(i))) % (W + 400) - 200, y = 300 + rnd(i + 30) * 1400 + Math.sin(t * 0.4 + i) * 60, r = 260 + 160 * rnd(i + 40);
    const sg = cx.createRadialGradient(x, y, 0, x, y, r); sg.addColorStop(0, 'rgba(160,140,255,.08)'); sg.addColorStop(1, 'rgba(160,140,255,0)');
    cx.fillStyle = sg; cx.fillRect(x - r, y - r, 2 * r, 2 * r);
  }
  candle(110, 1880, t, 1); candle(970, 1860, t, 2);
}
function candle(x, y, t, s) {
  const fl = 0.85 + 0.15 * Math.sin(t * 13 + s) * Math.sin(t * 7.3 + s * 2);
  const g = cx.createRadialGradient(x, y - 260, 10, x, y - 260, 520 * fl); g.addColorStop(0, 'rgba(255,170,80,.35)'); g.addColorStop(1, 'rgba(255,170,80,0)');
  cx.fillStyle = g; cx.fillRect(x - 600, y - 800, 1200, 1200);
  cx.fillStyle = '#EDE3CF'; cx.fillRect(x - 34, y - 220, 68, 240);
  cx.save(); cx.translate(x, y - 240); cx.scale(1, fl);
  const fg = cx.createRadialGradient(0, -20, 2, 0, -20, 40); fg.addColorStop(0, '#FFF6D0'); fg.addColorStop(0.5, '#FFB347'); fg.addColorStop(1, 'rgba(255,120,40,0)');
  cx.fillStyle = fg; cx.beginPath(); cx.ellipse(0, -24, 18, 42, 0, 0, 7); cx.fill(); cx.restore();
}

// ---------- karta tarota (środek 0,0, w x h)
function ornament(w, h) {
  gstroke(4); cx.strokeRect(-w / 2 + 22, -h / 2 + 22, w - 44, h - 44);
  gstroke(2); cx.strokeRect(-w / 2 + 34, -h / 2 + 34, w - 68, h - 68);
  for (const [sx, sy] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) { cx.save(); cx.translate(sx * (w / 2 - 34), sy * (h / 2 - 34)); cx.fillStyle = GOLD; cx.beginPath(); cx.arc(0, 0, 9, 0, 7); cx.fill(); cx.restore(); }
}
function cardBack(w, h, t) {
  cx.fillStyle = INK; cx.beginPath(); cx.roundRect(-w / 2, -h / 2, w, h, 24); cx.fill();
  ornament(w, h);
  // słońce/oko
  cx.save(); const s = w / 560; cx.scale(s, s); gstroke(5 / s);
  cx.beginPath(); cx.arc(0, 0, 90, 0, 7); cx.stroke();
  for (let i = 0; i < 16; i++) { const a = i / 16 * Math.PI * 2 + t * 0.2; cx.beginPath(); cx.moveTo(Math.cos(a) * 115, Math.sin(a) * 115); cx.lineTo(Math.cos(a) * (150 + (i % 2) * 40), Math.sin(a) * (150 + (i % 2) * 40)); cx.stroke(); }
  cx.beginPath(); cx.ellipse(0, 0, 55, 30, 0, 0, 7); cx.stroke(); cx.fillStyle = GOLD; cx.beginPath(); cx.arc(0, 0, 16, 0, 7); cx.fill();
  cx.restore();
}
function illMic(t) { // mikrofon w pajęczynach (mieści się w |x|<190)
  gstroke(6);
  cx.beginPath(); cx.roundRect(-55, -160, 110, 190, 55); cx.stroke();
  for (let i = 0; i < 4; i++) { cx.beginPath(); cx.moveTo(-45, -120 + i * 28); cx.lineTo(45, -120 + i * 28); cx.stroke(); }
  cx.beginPath(); cx.moveTo(0, 30); cx.lineTo(0, 100); cx.moveTo(-65, 100); cx.lineTo(65, 100); cx.stroke();
  gstroke(2); const ax = 170, ay = -190; // pajęczyna w rogu
  for (let i = 0; i < 5; i++) { const a = Math.PI * 0.5 + i * Math.PI * 0.125; cx.beginPath(); cx.moveTo(ax, ay); cx.lineTo(ax + Math.cos(a) * 130, ay + Math.sin(a) * 130); cx.stroke(); }
  for (let r = 35; r <= 125; r += 30) { cx.beginPath(); cx.arc(ax, ay, r, Math.PI * 0.5, Math.PI * 1.0); cx.stroke(); }
  const sx = 115 + Math.sin(t * 2) * 5, sy = -80 + Math.sin(t * 1.3) * 18;
  cx.beginPath(); cx.moveTo(sx, sy); cx.lineTo(ax - 20, ay + 20); cx.stroke();
  cx.fillStyle = GOLD; cx.beginPath(); cx.arc(sx, sy, 8, 0, 7); cx.fill();
}
function illEcho(t) { // ucho i fale echa
  gstroke(6); cx.save(); cx.translate(-40, 0);
  cx.beginPath(); cx.moveTo(-40, 120); cx.bezierCurveTo(-140, 60, -140, -170, -10, -180); cx.bezierCurveTo(110, -185, 120, -40, 40, 10); cx.bezierCurveTo(0, 40, 20, 100, -40, 120); cx.stroke();
  cx.beginPath(); cx.moveTo(-40, -80); cx.bezierCurveTo(-20, -130, 50, -120, 40, -60); cx.stroke();
  for (let i = 0; i < 3; i++) { const r = 30 + ((t * 60 + i * 35) % 100); cx.globalAlpha = 1 - r / 140; cx.beginPath(); cx.arc(120, -40, r, -0.7, 0.7); cx.stroke(); }
  cx.restore(); cx.globalAlpha = 1;
}
function illStudio(t) { // duże łukowe okno z prawdziwym studiem
  const top = -330, bot = 150, hw = 185;
  const arch = () => { cx.beginPath(); cx.moveTo(-hw, bot); cx.lineTo(-hw, top + hw); cx.arc(0, top + hw, hw, Math.PI, 0); cx.lineTo(hw, bot); cx.closePath(); };
  cx.save(); arch(); cx.clip();
  const im = IM['fotel'], s = (bot - top) / im.height * 1.55, iw = im.width * s, ih = im.height * s;
  cx.drawImage(im, -iw * 0.66, (top + bot) / 2 - ih * 0.56, iw, ih);
  const g = cx.createLinearGradient(0, top, 0, bot); g.addColorStop(0, 'rgba(255,170,90,.10)'); g.addColorStop(0.75, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(20,10,5,.35)'); cx.fillStyle = g; cx.fillRect(-hw, top, 2 * hw, bot - top);
  cx.restore();
  gstroke(6); arch(); cx.stroke();
  gstroke(2); cx.beginPath(); cx.moveTo(-hw - 14, bot + 14); cx.lineTo(-hw - 14, top + hw); cx.arc(0, top + hw, hw + 14, Math.PI, 0); cx.lineTo(hw + 14, bot + 14); cx.lineTo(-hw - 14, bot + 14); cx.stroke();
}
const CARDS = [
  { num: 'I', label: 'PRZESZŁOŚĆ', title: 'MIKROFON', title2: 'W SZUFLADZIE', sub: 'kupiony z motywacją,|odłożony z kurzem', ill: illMic, face: INK, iy: -70 },
  { num: 'II', label: 'TERAŹNIEJSZOŚĆ', title: 'ECHO', title2: '', sub: 'każde nagranie brzmi|jak z łazienki', ill: illEcho, face: INK, iy: -70 },
  { num: 'III', label: 'PRZYSZŁOŚĆ', title: 'NAGRANIE', title2: 'W STUDIU', sub: 'mikrofony Shure,|dwie kamery 4K i światło', ill: illStudio, face: '#2A1A12', iy: 0 },
];
function cardFace(c, w, h, t, glow) {
  cx.fillStyle = c.face; cx.beginPath(); cx.roundRect(-w / 2, -h / 2, w, h, 24); cx.fill();
  if (glow) { const g = cx.createRadialGradient(0, -60, 20, 0, -60, 420); g.addColorStop(0, `rgba(255,120,50,${0.35 * glow})`); g.addColorStop(1, 'rgba(255,120,50,0)'); cx.fillStyle = g; cx.fillRect(-w / 2, -h / 2, w, h); }
  ornament(w, h);
  const s = w / 560; cx.save(); cx.scale(s, s);
  txt(c.num, 0, -380, { font: 'bold 56px "TeX Gyre Bonum"' });
  cx.save(); cx.translate(0, c.iy); c.ill(t); cx.restore();
  const ty = c.ill === illStudio ? 235 : 215;
  txt(c.title, 0, c.title2 ? ty : ty + 25, { font: `bold ${c.title.length > 6 ? 58 : 70}px "TeX Gyre Bonum"`, sp: 2 });
  if (c.title2) txt(c.title2, 0, ty + 66, { font: 'bold 44px "TeX Gyre Bonum"', sp: 2 });
  txt(c.label, 0, 375, { font: '26px Semi', sp: 7, col: GOLD2 });
  cx.restore();
}
function card(i, x, y, w, rot, flip, t, glow = 0, alpha = 1, sc = 1) {
  if (alpha <= 0) return;
  const h = w * 940 / 560;
  const sx = Math.cos(flip * Math.PI);
  cx.save(); cx.globalAlpha = alpha; cx.translate(x, y); cx.rotate(rot); cx.scale((Math.abs(sx) + 0.0001) * sc, sc);
  cx.shadowColor = glow ? 'rgba(255,140,60,.8)' : 'rgba(0,0,0,.6)'; cx.shadowBlur = glow ? 80 * glow : 40; cx.shadowOffsetY = 12;
  cx.fillStyle = INK; cx.beginPath(); cx.roundRect(-w / 2, -h / 2, w, h, 24); cx.fill(); cx.shadowColor = 'transparent';
  if (sx > 0) cardBack(w, h, t); else cardFace(CARDS[i], w, h, t, glow);
  cx.restore();
}
const ROW = [[285, 1130], [540, 1130], [795, 1130]], RW = 250, CW = 580, CY = 900;
function sparkle(x, y, t, t0, n = 40, rad = 520) {
  if (t < t0 || t > t0 + 1.6) return;
  const p = (t - t0) / 1.6;
  for (let i = 0; i < n; i++) {
    const a = rnd(i) * Math.PI * 2, r = 60 + rad * eo(p) * (0.4 + 0.6 * rnd(i + 7));
    cx.fillStyle = `rgba(255,${200 + 40 * rnd(i)},140,${1 - p})`; cx.beginPath(); cx.arc(x + Math.cos(a) * r, y + Math.sin(a) * r, 3 + 4 * rnd(i + 2), 0, 7); cx.fill();
  }
}
const LABEL = 'italic 600 58px Lora', SUB = 'italic 600 54px Lora';

window.renderAt = function (t) {
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.globalAlpha = 1; cx.shadowColor = 'transparent';
  bg(t);
  const R = D.R; // [start, flip, odejście]
  if (t < R[0][0] + 0.3) {
    const a = clamp(t / 0.3) * clamp((R[0][0] + 0.3 - t) / 0.3);
    txt('Wyciągnij kartę.', 540, 470, { font: 'italic 600 100px Lora', col: CR, a, glow: 30 });
    txt('Sprawdzimy, co czeka', 540, 610, { font: 'bold 60px "TeX Gyre Bonum"', col: GOLD, a });
    txt('Twój podcast.', 540, 685, { font: 'bold 60px "TeX Gyre Bonum"', col: GOLD, a });
  }
  let front = -1;
  for (let i = 0; i < 3; i++) { if (t >= R[i][0]) front = i; }
  const falling = i => i < 2 && t >= R[i][2];
  [0, 1, 2].filter(i => i !== front && !falling(i)).concat(front >= 0 && !falling(front) ? [front] : []).concat([0, 1].filter(falling)).forEach(i => {
    const [s, f, b] = R[i];
    const deal = eo((t - 0.25 - i * 0.18) / 0.5);
    let x = lerp(540, ROW[i][0], deal), y = lerp(2300, ROW[i][1], deal), w = RW, rot = (i - 1) * 0.08 * deal, flip = 0, glow = 0, al = 1, sc = 1;
    if (t >= s) {
      const p = eio((t - s) / 0.55); x = lerp(ROW[i][0], 540, p); y = lerp(ROW[i][1], CY, p); w = lerp(RW, CW, p); rot = lerp((i - 1) * 0.08, 0, p);
      flip = eio((t - f) / 0.5);
      if (i === 2) glow = clamp((t - f + 0.6) / 0.6) * (0.7 + 0.3 * Math.sin(t * 5));
    }
    if (t >= b) { // karta znika
      const p = eio((t - b) / 0.45);
      if (i < 2) { if (t > b + 0.95) return; const q = clamp((t - b) / 0.9); y = CY + 1700 * q * q; rot = (i ? 0.6 : -0.6) * q * q; x = 540 + (i ? 120 : -120) * q; }
      else { al = 1 - p; sc = 1 + 0.25 * p; glow = 1; }
    }
    card(i, x, y, w, rot, flip, t, glow, al, sc);
  });
  const labels = ['Karta pierwsza:|przeszłość', 'Karta druga:|teraźniejszość', 'Karta trzecia:|przyszłość'];
  for (let i = 0; i < 3; i++) {
    const [s, f, b] = R[i];
    const tEnd = i === 2 ? D.KN : b;
    const a = clamp((t - f - 0.35) / 0.3) * clamp((tEnd - t) / 0.25);
    if (a > 0) CARDS[i].sub.split('|').forEach((l, k) => txt(l, 540, 1478 + k * 64, { font: SUB, col: CR, a }));
    const la = clamp((t - s - 0.2) / 0.3) * clamp((tEnd - t) / 0.25);
    if (la > 0) { const [l1, l2] = labels[i].split('|'); txt(l1 + ' ' + l2, 540, 345, { font: LABEL, col: GOLD, a: la, glow: 20 }); }
  }
  sparkle(540, CY, t, R[2][1] + 0.25, 60);
  // „Karty nie kłamią.” nad dużą kartą, potem karta znika
  if (t > D.KN && t < R[2][2] + 0.4) {
    const a = clamp((t - D.KN) / 0.35) * clamp((R[2][2] + 0.4 - t) / 0.3);
    txt('Karty nie kłamią.', 540, 345, { font: 'italic 600 84px Lora', col: CR, a, glow: 30 });
  }
  sparkle(540, CY, t, R[2][2], 90, 650);
  // finał: Gadka studio i zaproszenie
  const E = D.END;
  if (t > E) {
    const a = clamp((t - E) / 0.4);
    cx.save(); cx.globalAlpha = a; const lw = 620 * (0.9 + 0.1 * eo((t - E) / 0.6)); cx.shadowColor = 'rgba(255,160,80,.5)'; cx.shadowBlur = 40;
    cx.drawImage(IM.logo, 540 - lw / 2, 520, lw, lw * 510 / 1400); cx.restore();
    const b2 = clamp((t - E - 0.5) / 0.4);
    txt('Twoja przyszłość', 540, 860, { font: 'italic 600 80px Lora', col: CR, a: b2, glow: 20 });
    txt('zaczyna się u nas.', 540, 955, { font: 'italic 600 80px Lora', col: CR, a: b2, glow: 20 });
    txt('Wpadnij do studia', 540, 1060, { font: 'bold 56px "TeX Gyre Bonum"', col: GOLD, a: clamp((t - E - 0.9) / 0.4) });
    txt('i nagraj, co chcesz!', 540, 1128, { font: 'bold 56px "TeX Gyre Bonum"', col: GOLD, a: clamp((t - E - 0.9) / 0.4) });
    if (t > E + 1.3) {
      const p = ob((t - E - 1.3) / 0.4, 2);
      cx.save(); cx.translate(540, 1320); cx.scale(p, p);
      cx.fillStyle = OR; cx.beginPath(); cx.roundRect(-390, -90, 780, 180, 40); cx.fill();
      txt('2 h · 300 zł brutto', 0, -22, { font: '64px Blk', col: '#fff' });
      txt('sprzęt w cenie · Warszawa', 0, 46, { font: '38px Semi', col: CR });
      cx.restore();
    }
    txt('gadkastudio.pl', 540, 1505, { font: '60px XB', col: GOLD, a: clamp((t - E - 1.7) / 0.4) });
  }
  const f = Math.floor(t * 30); cx.save(); cx.globalAlpha = 0.06; cx.globalCompositeOperation = 'overlay';
  const pat = cx.createPattern(IM.noise, 'repeat'); cx.translate(-rnd(f) * 600, -rnd(f + 3) * 600); cx.fillStyle = pat; cx.fillRect(0, 0, W + 600, H + 600); cx.restore();
  if (window.SAFE) { cx.strokeStyle = '#00E5FF'; cx.lineWidth = 6; cx.strokeRect(120, 280, 840, 1300); }
  if (t > D.TOTAL - 0.5) { cx.fillStyle = `rgba(0,0,0,${clamp((t - D.TOTAL + 0.5) / 0.5)})`; cx.fillRect(0, 0, W, H); }
};

// ---------- okładka (wszystko w kwadracie y 420–1500, x 100–980)
window.renderCover = function () {
  const t = 2.0;
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.globalAlpha = 1;
  bg(t);
  // poświata za kartą
  const g = cx.createRadialGradient(540, 930, 40, 540, 930, 520); g.addColorStop(0, 'rgba(255,150,70,.45)'); g.addColorStop(1, 'rgba(255,150,70,0)');
  cx.fillStyle = g; cx.fillRect(0, 300, W, 1300);
  // dwie karty za plecami + główna karta
  card(0, 400, 960, 300, -0.22, 0, t);
  card(1, 680, 960, 300, 0.22, 0, t);
  card(2, 540, 930, 360, 0, 1, t, 0.9);
  for (let i = 0; i < 40; i++) { const a = rnd(i) * 7, r = 260 + 220 * rnd(i + 5); cx.fillStyle = `rgba(255,220,150,${0.4 + 0.5 * rnd(i + 9)})`; cx.beginPath(); cx.arc(540 + Math.cos(a) * r, 930 + Math.sin(a) * r * 1.2, 2 + 4 * rnd(i + 2), 0, 7); cx.fill(); }
  txt('Co mówią karty', 540, 475, { font: 'italic 600 92px Lora', col: CR, glow: 30 });
  txt('o Twoim podcaście?', 540, 1345, { font: 'italic 600 84px Lora', col: CR, glow: 30 });
  cx.drawImage(IM.logo, 540 - 120, 1410, 240, 240 * 510 / 1400);
};
