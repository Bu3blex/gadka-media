// SZABLON ROLKI 1080x1920 – canvas + deterministyczne window.renderAt(t)
// Zasady: wszystko ważne w strefie SAFE (x 120–960, y 280–1580). Poza nią tylko tło i dekoracje.
const D = window.DATA;
const cv = document.getElementById('c'), cx = cv.getContext('2d');
const W = 1080, H = 1920, SAFE = { L: 120, R: 960, T: 280, B: 1580 };
const BK = '#111111', CR = '#F9EEE4', OR = '#FF592A';             // marka Gadka
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const eo = x => 1 - Math.pow(1 - clamp(x), 3);                      // ease-out
const eio = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const ob = (x, k = 1.8) => { x = clamp(x); const c3 = k + 1; return 1 + c3 * Math.pow(x - 1, 3) + k * Math.pow(x - 1, 2); }; // „pop” z przestrzeleniem
const lerp = (a, b, p) => a + (b - a) * p;
function rnd(n) { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); }

// ---------- zasoby
const IM = {}; let pending = 0;
function done() { if (--pending === 0) window.READY = true; }
function load(k, src) { pending++; const i = new Image(); i.onload = done; i.onerror = done; i.src = src; IM[k] = i; }
(D.PHOTOS || ['101', '056', '104']).forEach(n => load(n, `img/${n}.jpg`));
load('noise', 'img/noise.png'); load('logo', 'logo.png'); load('logoB', 'logo_black.png');
pending++;
Promise.all([['Light', 'Light'], ['Semi', 'SemiBold'], ['Bold', 'Bold'], ['XB', 'ExtraBold'], ['Blk', 'Black']]
  .map(([n, u]) => new FontFace(n, `url(fonts/InterDisplay-${u}.otf)`).load().then(f => document.fonts.add(f)))
  .concat([document.fonts.load('italic 600 60px Lora'), document.fonts.load('bold 60px "TeX Gyre Bonum"'), document.fonts.load('60px "TeX Gyre Chorus"')]))
  .then(done, done);

// klatki z własnych nagrań (przygotowane przez klip.sh): await frame('nazwa', i)
const FR = {};
function frame(name, i) {
  const key = name + i; if (FR[key]) return FR[key];
  const im = new Image(); im.src = `klipy/${name}/${String(i + 1).padStart(4, '0')}.jpg`;
  FR[key] = im.decode().then(() => im, () => null);
  return FR[key];
}

// ---------- pomocnicze rysowanie
function txt(s, x, y, o) {
  o = Object.assign({ font: '80px Blk', col: BK, sp: 0, a: 1, al: 'left' }, o);
  if (o.a <= 0) return;
  cx.save(); cx.globalAlpha *= o.a; cx.font = o.font; cx.fillStyle = o.col; cx.letterSpacing = o.sp + 'px';
  cx.textAlign = o.al; cx.textBaseline = 'middle';
  if (o.glow) { cx.shadowColor = o.gcol || 'rgba(255,255,255,.6)'; cx.shadowBlur = o.glow; }
  cx.fillText(s, x, y); cx.restore();
}
// kinetyczny napis: wjeżdża od dołu z maską
function kin(s, x, y, size, col, t, t0, o = {}) {
  if (t < t0) return;
  const p = eo((t - t0) / 0.35);
  cx.save(); cx.beginPath(); cx.rect(0, y - size * 0.62, W, size * 1.24); cx.clip();
  txt(s, x, y + size * 1.1 * (1 - p), Object.assign({ font: `${size}px Blk`, col }, o)); cx.restore();
}
// naklejka/pigułka z „pop”
function pill(s, x, y, t, t0, bg = OR, fg = BK, size = 50, rot = -0.04) {
  if (t < t0) return; const sc = ob((t - t0) / 0.3, 2.5);
  cx.save(); cx.translate(x, y); cx.rotate(rot); cx.scale(sc, sc);
  cx.font = `${size}px XB`; const w = cx.measureText(s).width + size * 1.4, h = size * 1.9;
  cx.fillStyle = bg; cx.beginPath(); cx.roundRect(-w / 2, -h / 2, w, h, h / 2); cx.fill();
  txt(s, 0, 3, { font: `${size}px XB`, col: fg, al: 'center' }); cx.restore();
}
// zdjęcie „cover” w prostokącie z lekkim najazdem
function photo(k, x, y, w, h, p = 0, fx = 0.5, fy = 0.5, r = 0) {
  const im = IM[k]; if (!im) return; const s = Math.max(w / im.width, h / im.height) * (1.04 + 0.06 * p);
  cx.save(); cx.beginPath(); cx.roundRect(x, y, w, h, r); cx.clip();
  cx.drawImage(im, x + w / 2 - im.width * s * fx, y + h / 2 - im.height * s * fy, im.width * s, im.height * s); cx.restore();
}
function grain(t, a = 0.07) {
  const f = Math.floor(t * 30); cx.save(); cx.globalAlpha = a; cx.globalCompositeOperation = 'overlay';
  const p = cx.createPattern(IM.noise, 'repeat'); cx.translate(-rnd(f) * 600, -rnd(f + 3) * 600); cx.fillStyle = p; cx.fillRect(0, 0, W + 600, H + 600); cx.restore();
}

// ---------- ROLKA: „Zgadnij, ile kosztuje nagranie tutaj?” – teleturniej
const E = D.E, B = D.B;
const N = { a1: 79, a2: 79, a4: 79, b1: 79, c1: 90, e2: 79, hook: 151, fin: 150 };
const DARK = '#121212', CARD = '#1E1D1B';
async function full(name, lt, dim = 0) {
  const im = await frame(name, Math.min(N[name] - 1, Math.max(0, Math.floor(lt * 30)))); if (!im) return;
  const s = 1 + 0.012 * lt; cx.drawImage(im, W / 2 - W * s / 2, H / 2 - H * s / 2, W * s, H * s);
  const g = cx.createLinearGradient(0, 950, 0, H); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,.85)'); cx.fillStyle = g; cx.fillRect(0, 950, W, H - 950);
  const g2 = cx.createLinearGradient(0, 0, 0, 380); g2.addColorStop(0, 'rgba(0,0,0,.45)'); g2.addColorStop(1, 'rgba(0,0,0,0)'); cx.fillStyle = g2; cx.fillRect(0, 0, W, 380);
  if (dim) { cx.fillStyle = `rgba(0,0,0,${dim})`; cx.fillRect(0, 0, W, H); }
}
function logoTop(light = true) { const im = light ? IM.logo : IM.logoB; cx.save(); cx.shadowColor = light ? 'rgba(0,0,0,.4)' : 'transparent'; cx.shadowBlur = 20; cx.drawImage(im, 540 - 115, 165, 230, 230 * im.height / im.width); cx.restore(); }
function fitFont(s, max, size, wgt = 'Blk') { cx.font = `${size}px ${wgt}`; while (cx.measureText(s).width > max && size > 50) { size -= 4; cx.font = `${size}px ${wgt}`; } return size; }
function pow(s, y, size, col, t, t0, x = 540) {
  if (t < t0) return; const sc = ob((t - t0) / 0.3, 2.6), sh = Math.sin((t - t0) * 70) * 7 * clamp(1 - (t - t0) / 0.22);
  cx.save(); cx.translate(x + sh, y); cx.scale(sc, sc); cx.shadowColor = 'rgba(0,0,0,.6)'; cx.shadowBlur = 40;
  txt(s, 0, 0, { font: `${fitFont(s, 830, size)}px Blk`, col, al: 'center' }); cx.restore();
}
function rpill(s, x, y, h, bg, fg, font, al = 'left', a = 1) { // prosta pigułka bez animacji
  cx.save(); cx.globalAlpha *= a; cx.font = font; const w = cx.measureText(s).width + h * 0.9; const x0 = al === 'left' ? x : x - w;
  cx.fillStyle = bg; cx.beginPath(); cx.roundRect(x0, y - h / 2, w, h, h / 2); cx.fill();
  txt(s, x0 + w / 2, y + 3, { font, col: fg, al: 'center' }); cx.restore();
}
// podpowiedź: „PODPOWIEDŹ n/4” + „??? zł” + duży tytuł + podtytuł
function clue(n, title, sub, t, t0) {
  const lt = t - t0, p = eo(lt / 0.4), p2 = eo((lt - 0.18) / 0.4), p3 = eo((lt - 0.32) / 0.4);
  rpill(`PODPOWIEDŹ ${n}/4`, SAFE.L, 1150 + 14 * (1 - p), 74, OR, BK, '36px XB', 'left', p);
  const blink = 0.55 + 0.45 * Math.abs(Math.sin(t * 4));
  rpill('??? zł', SAFE.R, 1150 + 14 * (1 - p), 74, 'rgba(17,17,17,.85)', CR, '36px XB', 'right', p * blink);
  const fs = fitFont(title, SAFE.R - SAFE.L, 112);
  txt(title, SAFE.L, 1285 + 20 * (1 - p2), { font: `${fs}px Blk`, col: '#fff', a: p2 });
  txt(sub, SAFE.L, 1390 + 20 * (1 - p3), { font: `${fitFont(sub, SAFE.R - SAFE.L, 54, 'Semi')}px Semi`, col: CR, a: p3 });
}
// --- plansza: pytanie z odpowiedziami i odliczaniem
function question(t, t0) {
  const lt = t - t0, Bt = B;
  cx.fillStyle = DARK; cx.fillRect(0, 0, W, H); logoTop(true);
  const rev = t0 + 3.1;
  const p = eo(lt / 0.45);
  rpill('PYTANIE', SAFE.L, 440 + 14 * (1 - p), 70, OR, BK, '34px XB', 'left', p);
  txt('Ile kosztują', SAFE.L, 570 + 20 * (1 - p), { font: '112px Blk', col: '#fff', a: p });
  txt('2 godziny?', SAFE.L, 690 + 20 * (1 - eo((lt - 0.12) / 0.45)), { font: '112px Blk', col: OR, a: eo((lt - 0.12) / 0.45) });
  const ans = [['A', '1200 zł'], ['B', '700 zł'], ['C', '300 zł']];
  ans.forEach(([l, v], i) => {
    const ti = t0 + 0.45 + i * 0.16; if (t < ti) return;
    const q = eo((t - ti) / 0.35), y = 850 + i * 140 + 24 * (1 - q), ok = i === 2 && t >= rev, r = ok ? ob((t - rev) / 0.3, 2.2) : 1;
    const dimA = t >= rev && !ok ? 0.35 : 1;
    cx.save(); cx.globalAlpha = q * dimA; cx.translate(540, y + 55); cx.scale(r, r); cx.translate(-540, -(y + 55));
    cx.fillStyle = ok ? OR : CARD; cx.beginPath(); cx.roundRect(SAFE.L, y, SAFE.R - SAFE.L, 110, 55); cx.fill();
    cx.fillStyle = ok ? BK : '#2E2C29'; cx.beginPath(); cx.arc(SAFE.L + 55, y + 55, 38, 0, 7); cx.fill();
    txt(l, SAFE.L + 55, y + 58, { font: '44px Blk', col: ok ? OR : CR, al: 'center' });
    txt(v, SAFE.L + 120, y + 58, { font: '60px XB', col: ok ? BK : CR });
    if (ok) txt('✓', SAFE.R - 60, y + 58, { font: '64px Blk', col: BK, al: 'center' });
    cx.restore();
  });
  // odliczanie 3-2-1
  const c0 = t0 + 1.3;
  if (t >= c0 && t < rev + 0.05) {
    const k = Math.min(2, Math.floor((t - c0) / Bt)), lk = (t - c0) - k * Bt;
    cx.save(); cx.translate(540, 1350);
    cx.strokeStyle = '#2E2C29'; cx.lineWidth = 14; cx.beginPath(); cx.arc(0, 0, 92, 0, 7); cx.stroke();
    cx.strokeStyle = OR; cx.lineCap = 'round'; cx.beginPath(); cx.arc(0, 0, 92, -Math.PI / 2, -Math.PI / 2 + 2 * Math.PI * (1 - clamp((t - c0) / (rev - c0)))); cx.stroke();
    const s = ob(lk / 0.25, 2.4); cx.scale(s, s); txt(String(3 - k), 0, 6, { font: '110px Blk', col: '#fff', al: 'center' }); cx.restore();
  }
  if (t >= rev) { const q = eo((t - rev - 0.15) / 0.4); txt('Dobrze kombinujesz.', 540, 1360 + 20 * (1 - q), { font: '64px Blk', col: '#fff', al: 'center', a: q });
    txt('Sprzęt jest w cenie.', 540, 1450 + 20 * (1 - eo((t - rev - 0.3) / 0.4)), { font: '52px Semi', col: CR, al: 'center', a: eo((t - rev - 0.3) / 0.4) }); }
}
// --- finał na kremowym tle
function finale(t, t0) {
  const lt = t - t0;
  cx.fillStyle = CR; cx.fillRect(0, 0, W, H); logoTop(false);
  const r2 = (s, y, font, col, tt, o = {}) => { if (t < tt) return; const p = eo((t - tt) / 0.5); txt(s, 540, y + 24 * (1 - p), Object.assign({ font, col, a: p, al: 'center' }, o)); };
  r2('Obstawiałeś więcej?', 470, 'italic 600 64px Lora', '#5E554D', t0 + 0.05);
  r2('Zarezerwuj', 610, '132px Blk', BK, t0 + 0.2); r2('termin.', 740, '132px Light', BK, t0 + 0.32);
  if (lt > 0.6) { const p = eo((lt - 0.6) / 0.5); cx.save(); cx.globalAlpha = p; const y = 860 + 30 * (1 - p);
    cx.fillStyle = BK; cx.beginPath(); cx.roundRect(SAFE.L, y, SAFE.R - SAFE.L, 330, 40); cx.fill();
    txt('2 h', SAFE.L + 70, y + 130, { font: '120px Light', col: CR });
    txt('300 zł', SAFE.R - 70, y + 130, { font: '140px Blk', col: OR, al: 'right' });
    cx.fillStyle = '#2E2C29'; cx.fillRect(SAFE.L + 70, y + 220, SAFE.R - SAFE.L - 140, 2);
    txt('27 m²  ·  SPRZĘT W CENIE', 540, y + 275, { font: '38px Semi', col: CR, al: 'center', sp: 5 });
    cx.restore(); }
  if (lt > 1.1) { const s = ob((lt - 1.1) / 0.35, 2.2) * (1 + 0.025 * Math.sin(lt * 7)); cx.save(); cx.translate(540, 1330); cx.scale(s, s);
    cx.fillStyle = OR; cx.beginPath(); cx.roundRect(-380, -70, 760, 140, 70); cx.fill();
    txt('gadkastudio.pl  →', 0, 4, { font: '62px Blk', col: BK, al: 'center' }); cx.restore(); }
  r2('Napisz w komentarzu, ile obstawiałeś ↓', 1490, '40px Semi', '#5E554D', t0 + 1.5);
}

window.renderAt = async function (t) {
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.globalAlpha = 1; cx.fillStyle = BK; cx.fillRect(0, 0, W, H);
  if (t < E.C1) { // hak: pytanie na trzech planach
    await full('hook', t + 0.5, 0.42 * clamp(t / 0.15)); logoTop(true);
    pow('Ile kosztuje', 800, 140, '#fff', t, 0.08);
    pow('nagranie tutaj?', 960, 124, OR, t, 0.5);
    if (t > 1.05) { const p = eo((t - 1.05) / 0.4); cx.save(); cx.globalAlpha = p; cx.fillStyle = CR; cx.beginPath(); cx.roundRect(540 - 390, 1110 + 20 * (1 - p), 780, 110, 55); cx.fill();
      txt('Studio podcastowe · Warszawa', 540, 1167 + 20 * (1 - p), { font: '50px XB', col: BK, al: 'center' }); cx.restore(); }
    if (t > 1.6) txt('Zgadnij, zanim zobaczysz cenę ↓', 540, 1320, { font: '46px Semi', col: CR, al: 'center', a: eo((t - 1.6) / 0.4) });
  } else if (t < E.C2) { await full('b1', t - E.C1); logoTop(true); clue(1, '2 kamery 4K', 'i profesjonalne światło', t, E.C1); }
  else if (t < E.C3) { await full('e2', t - E.C2); logoTop(true); clue(2, 'Mikrofony Shure', 'brzmisz jak w radiu', t, E.C2); }
  else if (t < E.C4) { const lt = t - E.C3, d = (E.C4 - E.C3) / 3, k = Math.min(2, Math.floor(lt / d)); await full(['a1', 'a2', 'a4'][k], lt - k * d + 0.3); logoTop(true); clue(3, 'Klimat do wyboru', 'zmieniasz scenografię, nie studio', t, E.C3); }
  else if (t < E.Q) { await full('c1', t - E.C4 + 0.2); logoTop(true); clue(4, 'Pliki od ręki', 'wychodzisz z nagraniem na SSD', t, E.C4); }
  else if (t < E.REV) question(t, E.Q);
  else if (t < E.FIN) { // odpowiedź: POW
    const lt = t - E.REV; await full('fin', lt + 1.0, 0.5); logoTop(true);
    pow('2 godziny', 700, 120, '#fff', t, E.REV + 0.02);
    pow('300 zł', 900, 260, OR, t, E.REV + 0.25);
    if (lt > 0.8) { const p = eo((lt - 0.8) / 0.4); cx.save(); cx.globalAlpha = p; cx.fillStyle = CR; cx.beginPath(); cx.roundRect(540 - 380, 1090 + 20 * (1 - p), 760, 110, 55); cx.fill();
      txt('27 m² · sprzęt w cenie', 540, 1147 + 20 * (1 - p), { font: '54px XB', col: BK, al: 'center' }); cx.restore(); }
  } else finale(t, E.FIN);
  grain(t, 0.04);
  if (window.SAFE_BOX) { cx.strokeStyle = '#00E5FF'; cx.lineWidth = 6; cx.strokeRect(SAFE.L, SAFE.T, SAFE.R - SAFE.L, SAFE.B - SAFE.T); }
  if (t > D.TOTAL - 0.4) { cx.fillStyle = `rgba(0,0,0,${clamp((t - D.TOTAL + 0.4) / 0.4)})`; cx.fillRect(0, 0, W, H); }
};

// okładka – kwadrat y 420–1500, x 100–980
window.renderCover = async function () {
  cx.setTransform(1, 0, 0, 1, 0, 0); await full('fin', 1.5, 0.5);
  cx.drawImage(IM.logo, 540 - 130, 470, 260, 260 * IM.logo.height / IM.logo.width);
  txt('Ile kosztuje', 540, 800, { font: '140px Blk', col: '#fff', al: 'center' });
  txt('nagranie', 540, 950, { font: '140px Blk', col: '#fff', al: 'center' });
  txt('tutaj?', 540, 1100, { font: '140px Blk', col: OR, al: 'center' });
  cx.fillStyle = CR; cx.beginPath(); cx.roundRect(540 - 330, 1260, 660, 110, 55); cx.fill();
  txt('Zgadnij cenę ↓', 540, 1317, { font: '60px Blk', col: BK, al: 'center' });
};
