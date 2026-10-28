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

// ---------- ROLKA: jasny, magazynowy layout z oknami wideo
const E = D.E, B = D.B;
const N = { a1: 79, a2: 79, a3: 80, a4: 79, b1: 79, b2: 80, b3: 79, b4: 79, c1: 90, c2: 126, e1: 79, e2: 79 };
const PAPER = CR, INK = '#151413', MUTE = '#5E554D';
const NAMES = { a1: 'BIAŁA KOSTKA', a2: 'CIEMNA ZASŁONA', a3: 'STÓŁ RADIOWY', a4: 'LAMELE', b1: 'CIEMNA ZASŁONA', b2: 'BIAŁA KOSTKA', b3: 'LAMELE', b4: 'STÓŁ RADIOWY', c1: 'LAMELE', c2: 'CIEMNA ZASŁONA' };

// wideo w zaokrąglonym oknie; reveal 0..1 = otwieranie maską od środka
async function win(name, lt, x, y, w, h, reveal = 1, fy = 0.42, r = 34) {
  if (reveal <= 0) return;
  const im = await frame(name, Math.min(N[name] - 1, Math.max(0, Math.floor(lt * 30)))); if (!im) return;
  const rw = w * (0.86 + 0.14 * reveal), rh = h * reveal, rx = x + (w - rw) / 2, ry = y + (h - rh) / 2;
  cx.save(); cx.beginPath(); cx.roundRect(rx, ry, rw, rh, r); cx.clip();
  const s = Math.max(w / im.width, h / im.height) * (1.03 + 0.012 * lt);
  cx.drawImage(im, x + w / 2 - im.width * s / 2, y + h * 0.5 - im.height * s * fy, im.width * s, im.height * s);
  cx.restore();
}
function head2(a, b, t, t0, y = 420, size = 96) { // nagłówek: czarny + pomarańczowy, wjazd
  for (const [s, i, font, col] of [[a, 0, `${size}px Blk`, INK], [b, 1, `${Math.round(size * 0.86)}px Light`, OR]]) {
    if (!s) continue; const ti = t0 + i * 0.18; if (t < ti) continue; const p = eo((t - ti) / 0.5);
    cx.save(); cx.beginPath(); cx.rect(0, y + i * size * 1.05 - size * 0.7, W, size * 1.4); cx.clip();
    txt(s, SAFE.L, y + i * size * 1.05 + size * 1.1 * (1 - p), { font, col }); cx.restore();
  }
}
function tag(s, x, y, t, t0, light = true) { // etykieta w oknie
  if (t < t0) return; const p = eo((t - t0) / 0.4);
  cx.save(); cx.globalAlpha = p; cx.font = '32px Semi'; cx.letterSpacing = '5px'; const w = cx.measureText(s).width + 56; cx.letterSpacing = '0px';
  cx.fillStyle = light ? 'rgba(249,238,228,.92)' : 'rgba(21,20,19,.75)'; cx.beginPath(); cx.roundRect(x, y - 30, w, 60, 30); cx.fill();
  txt(s, x + 28, y + 2, { font: '32px Semi', col: light ? INK : CR, sp: 5 }); cx.restore();
}
function footerLogo(a = 1) { cx.save(); cx.globalAlpha = a; cx.drawImage(IM.logoB, SAFE.L, 1590 - 70, 200, 200 * IM.logoB.height / IM.logoB.width); cx.restore();
  txt('gadkastudio.pl', SAFE.R, 1556, { font: '32px Semi', col: MUTE, al: 'right', sp: 2, a }); }

// montaż naprzemienny: plansza (krem) ↔ nagranie w pełnym kadrze (bez przycinania)
async function full(name, lt) {
  const im = await frame(name, Math.min(N[name] - 1, Math.max(0, Math.floor(lt * 30)))); if (!im) return;
  const s = 1.0 + 0.012 * lt; // bardzo delikatny najazd, kadr zostaje cały
  cx.drawImage(im, W / 2 - W * s / 2, H / 2 - H * s / 2, W * s, H * s);
  const g = cx.createLinearGradient(0, 1150, 0, H); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,.55)'); cx.fillStyle = g; cx.fillRect(0, 1150, W, H - 1150);
}
function vlabel(s, t, t0) {
  if (t < t0) return; const p = eo((t - t0) / 0.5);
  cx.save(); cx.globalAlpha = p; cx.fillStyle = OR; cx.fillRect(SAFE.L, 1445, 70 * p, 5);
  txt(s, SAFE.L, 1505 + 12 * (1 - p), { font: '56px Semi', col: CR, sp: 8 }); cx.restore();
}
function boardHead(a, b, t, t0, y = 860, size = 120) { cx.font = `${size}px Blk`; while (cx.measureText(a).width > SAFE.R - SAFE.L && size > 60) { size -= 4; cx.font = `${size}px Blk`; } head2(a, b, t, t0, y, size); }

window.renderAt = async function (t) {
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.globalAlpha = 1; cx.fillStyle = PAPER; cx.fillRect(0, 0, W, H);
  const S = D.SEG; let i = 0; while (i + 1 < S.length && t >= S[i + 1][0]) i++;
  const [t0, kind, a, b] = S[i], lt = t - t0;
  if (kind === 'V') {
    await full(a, lt); vlabel(b, t, t0 + 0.2);
    cx.save(); cx.globalAlpha = 0.95; cx.drawImage(IM.logo, SAFE.R - 170, 322, 170, 170 * IM.logo.height / IM.logo.width); cx.restore();
  } else if (kind === 'P') {
    boardHead(a, b, t, t0 + 0.05, 860, 120);
    footerLogo(1);
  } else if (kind === 'SPEC') {
    head2('Sprzęt', 'w cenie.', t, t0 + 0.05, 620, 120);
    const rows = [['Kamery', '2 × 4K'], ['Mikrofony', 'Shure'], ['Światło', 'profesjonalne']];
    rows.forEach(([x1, x2], k) => { const ti = t0 + 0.45 + k * 0.25; if (t < ti) return; const p = eo((t - ti) / 0.5), yy = 1000 + k * 120;
      cx.fillStyle = 'rgba(21,20,19,.2)'; cx.fillRect(SAFE.L, yy - 60, (SAFE.R - SAFE.L) * p, 2);
      txt(x1, SAFE.L, yy, { font: '52px Light', col: MUTE, a: p }); txt(x2, SAFE.R, yy, { font: '56px Blk', col: k === 0 ? OR : INK, al: 'right', a: p }); });
    footerLogo(1);
  } else if (kind === 'PRICE') {
    const rr2 = (s, y, font, col, tt0, o = {}) => { if (t < tt0) return; const p = eo((t - tt0) / 0.5); txt(s, SAFE.L, y + 24 * (1 - p), Object.assign({ font, col, a: p }, o)); };
    rr2('2 godziny.', 760, '140px Light', INK, t0 + 0.05);
    rr2('300 zł.', 950, '230px Blk', OR, t0 + 0.3);
    rr2('BRUTTO  ·  SPRZĘT W CENIE', 1120, '38px Semi', INK, t0 + 0.7, { sp: 6 });
    footerLogo(1);
  } else { // finał
    const lf = lt;
    if (lf > 0.05) { const p = eo((lf - 0.05) / 0.6); cx.save(); cx.globalAlpha = p; const lw = 500; cx.drawImage(IM.logoB, 540 - lw / 2, 560 + 20 * (1 - p), lw, lw * IM.logoB.height / IM.logoB.width); cx.restore(); }
    const rr2 = (s, y, font, col, tt0, o = {}) => { if (t < tt0) return; const p = eo((t - tt0) / 0.6); txt(s, 540, y + 24 * (1 - p), Object.assign({ font, col, a: p, al: 'center' }, o)); };
    rr2('Wpadnij do studia', 900, '72px XB', INK, t0 + 0.4);
    rr2('i nagraj, co chcesz.', 985, '72px Light', INK, t0 + 0.55);
    if (lf > 0.9) { const p = eo((lf - 0.9) / 0.6); cx.fillStyle = OR; cx.fillRect(540 - 60 * p, 1090, 120 * p, 4); }
    rr2('gadkastudio.pl', 1180, '52px Semi', INK, t0 + 1.0, { sp: 3 });
    rr2('Warszawa', 1250, '38px Light', MUTE, t0 + 1.15, { sp: 6 });
  }
  grain(t, 0.035);
  if (window.SAFE_BOX) { cx.strokeStyle = '#00E5FF'; cx.lineWidth = 6; cx.strokeRect(SAFE.L, SAFE.T, SAFE.R - SAFE.L, SAFE.B - SAFE.T); }
  if (t > D.TOTAL - 0.5) { cx.fillStyle = `rgba(249,238,228,${clamp((t - D.TOTAL + 0.5) / 0.5)})`; cx.fillRect(0, 0, W, H); }
};

// okładka – kwadrat y 420–1500, x 100–980
window.renderCover = async function () {
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.fillStyle = PAPER; cx.fillRect(0, 0, W, H);
  txt('Jeden podcast.', 100, 640, { font: '128px Blk', col: INK }); txt('Wiele', 100, 790, { font: '118px Light', col: OR }); txt('scenografii.', 100, 920, { font: '118px Light', col: OR });
  cx.fillStyle = OR; cx.fillRect(100, 1050, 100, 5);
  txt('2 H · 300 ZŁ BRUTTO · SPRZĘT W CENIE', 100, 1130, { font: '36px Semi', col: INK, sp: 4 });
  cx.drawImage(IM.logoB, 100, 1330, 280, 280 * IM.logoB.height / IM.logoB.width);
  txt('gadkastudio.pl', 980, 1400, { font: '38px Semi', col: MUTE, al: 'right', sp: 2 });
};
