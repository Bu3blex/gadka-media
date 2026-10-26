// „Twoje podsumowanie roku jako podcaster” – Gadka studio
const D = window.DATA;
const cv = document.getElementById('c'), cx = cv.getContext('2d');
const W = 1080, H = 1920;
const OR = '#FF592A', CR = '#F9EEE4', BK = '#111111', VI = '#5B3CFF', PK = '#FF9EC9', LM = '#D7FF3A';
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const eo = x => 1 - Math.pow(1 - clamp(x), 3);
const eio = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const ob = (x, k = 1.8) => { x = clamp(x); const c3 = k + 1; return 1 + c3 * Math.pow(x - 1, 3) + k * Math.pow(x - 1, 2); };
function rnd(n) { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); }

const IM = {}; let pending = 0;
function done() { if (--pending === 0) window.READY = true; }
function load(k, src) { pending++; const i = new Image(); i.onload = done; i.src = src; IM[k] = i; }
['056', '104', '101', '034', 'noise'].forEach(n => load(n, n === 'noise' ? 'img/noise.png' : `img/${n}.jpg`));
load('logo', 'logo.png'); load('logoB', 'logo_black.png');
pending++;
Promise.all([['Semi', 'SemiBold'], ['Bold', 'Bold'], ['XB', 'ExtraBold'], ['Blk', 'Black']].map(([n, u]) => new FontFace(n, `url(fonts/InterDisplay-${u}.otf)`).load().then(f => document.fonts.add(f)))).then(done);

function txt(s, x, y, o) {
  o = Object.assign({ f: 'Blk', sz: 80, col: BK, sp: 0, a: 1, al: 'left', bl: 'middle' }, o);
  if (o.a <= 0) return;
  cx.save(); cx.globalAlpha *= o.a; cx.font = `${o.sz}px ${o.f}`; cx.fillStyle = o.col; cx.letterSpacing = o.sp + 'px';
  cx.textAlign = o.al; cx.textBaseline = o.bl; cx.fillText(s, x, y); cx.restore();
}
// słowo wjeżdżające od dołu z maską (kinetyczna typografia)
function kin(s, x, y, sz, col, t, t0, o = {}) {
  if (t < t0) return;
  const p = eo((t - t0) / 0.35);
  cx.save(); cx.beginPath(); cx.rect(0, y - sz * 0.62, W, sz * 1.24); cx.clip();
  txt(s, x, y + sz * 1.1 * (1 - p), Object.assign({ sz, col }, o));
  cx.restore();
}
function rr(x, y, w, h, r) { cx.beginPath(); cx.roundRect(x, y, w, h, r); }

// ---------- kształty dekoracyjne
function blob(x, y, r, col, t, seed) {
  cx.save(); cx.fillStyle = col; cx.beginPath();
  for (let i = 0; i <= 40; i++) {
    const a = i / 40 * Math.PI * 2, rr2 = r * (1 + 0.12 * Math.sin(a * 3 + t * 1.6 + seed) + 0.07 * Math.sin(a * 5 - t * 2.1 + seed * 2));
    i ? cx.lineTo(x + rr2 * Math.cos(a), y + rr2 * Math.sin(a)) : cx.moveTo(x + rr2 * Math.cos(a), y + rr2 * Math.sin(a));
  }
  cx.fill(); cx.restore();
}
function star(x, y, r, col, rot) {
  cx.save(); cx.translate(x, y); cx.rotate(rot); cx.fillStyle = col; cx.beginPath();
  for (let i = 0; i < 16; i++) { const rr2 = i % 2 ? r * 0.55 : r; const a = i / 16 * Math.PI * 2; cx.lineTo(rr2 * Math.cos(a), rr2 * Math.sin(a)); }
  cx.fill(); cx.restore();
}
function squiggle(x, y, w, col, t, lw = 22) {
  cx.save(); cx.strokeStyle = col; cx.lineWidth = lw; cx.lineCap = 'round'; cx.beginPath();
  for (let i = 0; i <= 60; i++) { const xx = x + w * i / 60, yy = y + Math.sin(i / 60 * Math.PI * 4 + t * 4) * 34; i ? cx.lineTo(xx, yy) : cx.moveTo(xx, yy); }
  cx.stroke(); cx.restore();
}
function rings(x, y, r, col, t) {
  cx.save(); cx.strokeStyle = col; cx.lineWidth = 18;
  for (let i = 0; i < 4; i++) { cx.beginPath(); cx.arc(x, y, r + i * 42 + Math.sin(t * 3 + i) * 6, 0, 7); cx.stroke(); }
  cx.restore();
}
function grain(t) {
  const f = Math.floor(t * 30);
  cx.save(); cx.globalAlpha = 0.07; cx.globalCompositeOperation = 'overlay';
  const p = cx.createPattern(IM.noise, 'repeat'); cx.translate(-rnd(f) * 600, -rnd(f + 3) * 600); cx.fillStyle = p; cx.fillRect(0, 0, W + 600, H + 600);
  cx.restore();
}
function header(t, col) { // stały nagłówek „podsumowanie”
  txt('PODSUMOWANIE 2026', 130, 470, { f: 'XB', sz: 34, col, sp: 4 });
  cx.save(); cx.globalAlpha = 0.9;
  const n = D.SC.length - 3; // pasek postępu
  for (let i = 0; i < n; i++) {
    const t0 = D.SC[i], t1 = D.SC[i + 1], p = clamp((t - t0) / (t1 - t0));
    rr(130 + i * (800 / n), 410, 800 / n - 10, 8, 4); cx.fillStyle = col; cx.globalAlpha = 0.25; cx.fill();
    rr(130 + i * (800 / n), 410, (800 / n - 10) * p, 8, 4); cx.globalAlpha = 1; cx.fill();
  }
  cx.restore();
}

// ---------- sceny (lt = czas od początku sceny)
const SCENES = [
  { bg: OR, fg: BK, draw(lt, t) { // hak
    blob(880, 1350, 300 * eo(lt / 0.5), VI, t, 1); star(220, 1450, 120 * ob(lt / 0.5), CR, t * 0.8);
    squiggle(560, 1650, 420, BK, t);
    kin('Twoje', 130, 760, 170, BK, lt, 0.0);
    kin('podsumowanie', 130, 940, 112, BK, lt, 0.12);
    kin('roku 2026', 130, 1110, 170, CR, lt, 0.24);
    if (lt > 0.7) { const s = ob((lt - 0.7) / 0.35, 2.5); cx.save(); cx.translate(560, 1300); cx.rotate(-0.06); cx.scale(s, s);
      rr(-300, -62, 600, 124, 62); cx.fillStyle = BK; cx.fill(); txt('…jako podcaster', 0, 3, { f: 'XB', sz: 56, col: CR, al: 'center' }); cx.restore(); }
  } },
  { bg: BK, fg: CR, draw(lt, t) { // licznik
    header(t, CR);
    kin('W tym roku', 130, 700, 96, CR, lt, 0.05);
    kin('nagrane odcinki:', 130, 820, 96, CR, lt, 0.15);
    const stop = 1.25;
    let n = lt < stop ? Math.floor(rnd(Math.floor(lt * 22)) * 98) + 1 : 0;
    if (lt > 0.35) {
      const land = lt > stop ? ob((lt - stop) / 0.3, 3) : 1;
      cx.save(); cx.translate(540, 1180); cx.scale(land, land);
      txt(String(n), 0, 0, { sz: 520, col: lt > stop ? OR : CR, al: 'center' }); cx.restore();
    }
    if (lt > stop + 0.25) { const s = ob((lt - stop - 0.25) / 0.3, 2.5); cx.save(); cx.translate(540, 1460); cx.rotate(0.04); cx.scale(s, s);
      rr(-250, -55, 500, 110, 55); cx.fillStyle = PK; cx.fill(); txt('tak, zero.', 0, 3, { f: 'XB', sz: 56, col: BK, al: 'center' }); cx.restore(); }
  } },
  { bg: CR, fg: BK, draw(lt, t) { // top słowa
    header(t, BK);
    blob(980, 620, 150, PK, t, 3);
    kin('Twoje top 3', 130, 640, 100, BK, lt, 0.05);
    kin('słowa roku:', 130, 765, 100, OR, lt, 0.15);
    const L = ['„od jutra”', '„jak kupię mikrofon”', '„mam pomysł”'];
    L.forEach((s, i) => {
      const t0 = 0.6 + i * 0.5; if (lt < t0) return;
      const p = eo((lt - t0) / 0.35), y = 1010 + i * 210;
      cx.save(); cx.translate(-300 * (1 - p), 0); cx.globalAlpha = p;
      rr(130, y - 85, 810, 170, 34); cx.fillStyle = i === 0 ? OR : '#fff'; cx.fill();
      txt(String(i + 1), 185, y + 4, { sz: 110, col: i === 0 ? CR : OR });
      txt(s, 280, y + 4, { f: 'XB', sz: s.length > 14 ? 50 : 66, col: BK });
      cx.restore();
    });
  } },
  { bg: VI, fg: CR, draw(lt, t) { // gatunek
    header(t, CR);
    rings(860, 1500, 120, 'rgba(255,255,255,.18)', t);
    kin('Twój gatunek', 130, 680, 100, CR, lt, 0.05);
    kin('roku:', 130, 805, 100, CR, lt, 0.15);
    if (lt > 0.55) { const s = ob((lt - 0.55) / 0.4, 2.2); cx.save(); cx.translate(540, 1110); cx.rotate(-0.05); cx.scale(s, s);
      txt('PLANOWANIE', 0, 0, { sz: 122, col: LM, al: 'center' }); cx.restore(); }
    if (lt > 1.1) txt('99% słuchania samego siebie w głowie', 540, 1280, { f: 'Bold', sz: 42, col: CR, al: 'center', a: clamp((lt - 1.1) / 0.3) });
  } },
  { bg: OR, fg: BK, draw(lt, t) { // wykres
    header(t, BK);
    kin('Godziny', 130, 640, 100, BK, lt, 0.05);
    kin('w tym roku:', 130, 765, 100, CR, lt, 0.15);
    const bars = [['tutoriale', 147, BK], ['porównywanie mikrofonów', 63, BK], ['nagrywanie', 0, CR]];
    bars.forEach(([lab, v, col], i) => {
      const t0 = 0.5 + i * 0.35, y = 980 + i * 230; if (lt < t0) return;
      const p = eo((lt - t0) / 0.6), w = 560 * v / 147 * p;
      txt(lab, 130, y - 60, { f: 'XB', sz: 44, col: BK, a: clamp((lt - t0) / 0.2) });
      rr(130, y - 20, Math.max(w, 14), 90, 20); cx.fillStyle = col; cx.fill();
      txt(String(Math.round(v * p)) + ' h', 130 + Math.max(w, 14) + 24, y + 26, { sz: 64, col: i === 2 ? CR : BK });
    });
  } },
  { bg: BK, fg: CR, draw(lt, t) { // osobowość
    header(t, CR);
    kin('Twoja osobowość', 130, 640, 92, CR, lt, 0.05);
    kin('podcastowa:', 130, 760, 100, CR, lt, 0.15);
    if (lt > 0.45) {
      const p = ob((lt - 0.45) / 0.5, 1.8);
      cx.save(); cx.translate(540, 1210); cx.rotate(-0.04 + 0.04 * (1 - p)); cx.scale(p, p);
      rr(-390, -320, 780, 640, 46); cx.fillStyle = PK; cx.fill();
      star(300, -250, 70, OR, t);
      txt('Wieczny', -340, -190, { sz: 110, col: BK });
      txt('Zapowiadacz', -340, -80, { sz: 110, col: BK });
      cx.fillStyle = BK; cx.fillRect(-340, 0, 680, 5);
      txt('supermoc: „już prawie zaczynam”', -340, 80, { f: 'Bold', sz: 38, col: BK });
      txt('słabość: mikrofon w koszyku od marca', -340, 150, { f: 'Bold', sz: 38, col: BK });
      txt('rzadkość: bardzo częsty', -340, 220, { f: 'Bold', sz: 38, col: BK });
      cx.restore();
    }
  } },
  { bg: CR, fg: BK, draw(lt, t) { // zwrot akcji
    const sh = Math.sin(lt * 50) * 6 * clamp(1 - lt / 0.4);
    cx.save(); cx.translate(sh, 0);
    kin('Ale rok', 130, 820, 180, BK, lt, 0.05);
    kin('2027', 130, 1030, 250, OR, lt, 0.25);
    kin('może wyglądać', 130, 1230, 100, BK, lt, 0.45);
    kin('zupełnie inaczej.', 130, 1350, 100, BK, lt, 0.6);
    cx.restore();
  } },
  { bg: BK, fg: CR, draw(lt, t) { // studio
    const ph = [['101', -0.05, 430, 720], ['056', 0.05, 650, 1040], ['104', -0.03, 430, 1360]];
    ph.forEach(([k, rot, x, y], i) => {
      const t0 = i * 0.35; if (lt < t0) return;
      const s = ob((lt - t0) / 0.4, 1.6), w = 560, h = 380, im = IM[k];
      cx.save(); cx.translate(x, y); cx.rotate(rot); cx.scale(s, s);
      cx.fillStyle = '#fff'; cx.shadowColor = 'rgba(0,0,0,.5)'; cx.shadowBlur = 40; cx.fillRect(-w / 2 - 14, -h / 2 - 14, w + 28, h + 28); cx.shadowColor = 'transparent';
      const sc = Math.max(w / im.width, h / im.height) * (1.05 + 0.04 * lt);
      cx.beginPath(); cx.rect(-w / 2, -h / 2, w, h); cx.clip();
      cx.drawImage(im, -im.width * sc / 2, -im.height * sc / 2, im.width * sc, im.height * sc);
      cx.restore();
    });
    const tags = [['mikrofony Shure', 640, 520, OR, BK], ['2× kamera 4K', 330, 1000, LM, BK], ['profesjonalne światło', 600, 1490, PK, BK], ['pliki od ręki', 720, 1230, CR, BK]];
    tags.forEach(([s, x, y, bg, fg], i) => {
      const t0 = 1.0 + i * 0.35; if (lt < t0) return;
      const sc = ob((lt - t0) / 0.3, 2.6);
      cx.save(); cx.translate(x, y); cx.rotate((i % 2 ? 1 : -1) * 0.05); cx.scale(sc, sc);
      cx.font = '46px XB'; const w = cx.measureText(s).width + 64;
      rr(-w / 2, -48, w, 96, 48); cx.fillStyle = bg; cx.fill();
      txt(s, 0, 3, { f: 'XB', sz: 46, col: fg, al: 'center' }); cx.restore();
    });
  } },
  { bg: OR, fg: BK, draw(lt, t) { // finał
    blob(900, 520, 220, VI, t, 5); star(170, 1700, 110, CR, t);
    kin('Podsumowanie', 130, 700, 104, BK, lt, 0.05);
    kin('2027 zaczyna się', 130, 825, 96, BK, lt, 0.15);
    kin('w Gadka studio.', 130, 950, 96, CR, lt, 0.25);
    if (lt > 0.7) { const s = ob((lt - 0.7) / 0.35, 2.4); cx.save(); cx.translate(540, 1210); cx.rotate(-0.03); cx.scale(s, s);
      rr(-400, -90, 800, 180, 40); cx.fillStyle = BK; cx.fill();
      txt('2 h · 300 zł', 0, -18, { sz: 80, col: CR, al: 'center' });
      txt('brutto · sprzęt w cenie', 0, 52, { f: 'Bold', sz: 40, col: CR, al: 'center' }); cx.restore(); }
    if (lt > 1.2) { cx.save(); cx.globalAlpha = clamp((lt - 1.2) / 0.3); cx.drawImage(IM.logoB, 540 - 200, 1350, 400, 400 * 510 / 1400); cx.restore();
      txt('gadkastudio.pl', 540, 1540, { f: 'XB', sz: 54, col: BK, al: 'center', a: clamp((lt - 1.4) / 0.3) }); }
  } },
];

window.renderAt = function (t) {
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.globalAlpha = 1;
  const S = D.SC; let i = 0; while (i + 1 < S.length && t >= S[i + 1]) i++;
  const lt = t - S[i];
  // poprzednia scena pod spodem, nowa wchodzi kołem z rogu
  const iris = i > 0 ? eio(lt / 0.42) : 1;
  if (iris < 1) { cx.fillStyle = SCENES[i - 1].bg; cx.fillRect(0, 0, W, H); SCENES[i - 1].draw(t - S[i - 1], t); }
  cx.save();
  if (iris < 1) { const cxp = i % 2 ? 1080 : 0, cyp = i % 3 === 0 ? 0 : 1920; cx.beginPath(); cx.arc(cxp, cyp, 2300 * iris, 0, 7); cx.clip(); }
  cx.fillStyle = SCENES[i].bg; cx.fillRect(0, 0, W, H);
  SCENES[i].draw(lt, t);
  cx.restore();
  grain(t);
  if (window.SAFE) { cx.strokeStyle = '#00E5FF'; cx.lineWidth = 6; cx.strokeRect(120, 280, 840, 1300); }
  if (t > D.TOTAL - 0.4) { cx.fillStyle = `rgba(0,0,0,${clamp((t - D.TOTAL + 0.4) / 0.4)})`; cx.fillRect(0, 0, W, H); }
};

// ---------- okładka (wszystko w kwadracie y 420–1500, x 100–980)
window.renderCover = function () {
  const t = 1.3;
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.globalAlpha = 1;
  cx.fillStyle = VI; cx.fillRect(0, 0, W, H);
  blob(800, 1000, 260, PK, t, 2);
  star(230, 1150, 105, OR, 0.3);
  txt('Twoje podsumowanie', 100, 500, { sz: 80, col: CR });
  txt('roku 2026:', 100, 592, { sz: 80, col: LM });
  cx.save(); cx.translate(560, 1000); cx.rotate(-0.05);
  cx.shadowColor = 'rgba(0,0,0,.35)'; cx.shadowBlur = 40; cx.shadowOffsetY = 20;
  txt('0', 0, 0, { sz: 560, col: LM, al: 'center' }); cx.restore();
  txt('nagranych odcinków', 540, 1310, { f: 'Blk', sz: 84, col: CR, al: 'center' });
  cx.save(); cx.translate(330, 1440); cx.rotate(-0.05);
  rr(-230, -50, 460, 100, 50); cx.fillStyle = BK; cx.fill();
  txt('…jako podcaster', 0, 3, { f: 'XB', sz: 48, col: CR, al: 'center' }); cx.restore();
  cx.drawImage(IM.logo, 980 - 230, 1405, 230, 230 * 510 / 1400);
  grain(0.5);
};
