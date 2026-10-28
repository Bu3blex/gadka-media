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

// ---------- ROLKA: „Ty mówisz. My nagrywamy.” – ścieżka rezerwacji w 4 krokach
const E = D.E, B = D.B;
const N = { a1: 79, a2: 79, a3: 80, a4: 79, b1: 79, c1: 90, e1: 79, e2: 79 };
const DARK = '#121212', CARD = '#1E1D1B';
async function full(name, lt) {
  const im = await frame(name, Math.min(N[name] - 1, Math.max(0, Math.floor(lt * 30)))); if (!im) return;
  const s = 1 + 0.012 * lt; cx.drawImage(im, W / 2 - W * s / 2, H / 2 - H * s / 2, W * s, H * s);
  const g = cx.createLinearGradient(0, 950, 0, H); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,.82)'); cx.fillStyle = g; cx.fillRect(0, 950, W, H - 950);
  const g2 = cx.createLinearGradient(0, 0, 0, 380); g2.addColorStop(0, 'rgba(0,0,0,.45)'); g2.addColorStop(1, 'rgba(0,0,0,0)'); cx.fillStyle = g2; cx.fillRect(0, 0, W, 380);
}
function logoTop(light = true) { const im = light ? IM.logo : IM.logoB; cx.save(); cx.shadowColor = light ? 'rgba(0,0,0,.4)' : 'transparent'; cx.shadowBlur = 20; cx.drawImage(im, 540 - 115, 165, 230, 230 * im.height / im.width); cx.restore(); }
function fitFont(s, max, size, wgt = 'Blk') { cx.font = `${size}px ${wgt}`; while (cx.measureText(s).width > max && size > 50) { size -= 4; cx.font = `${size}px ${wgt}`; } return size; }
function step(n, title, sub, t, t0, y = 1330) { // duży numer kroku + tytuł + podtytuł
  if (t < t0) return; const p = eo((t - t0) / 0.45), p2 = eo((t - t0 - 0.2) / 0.45);
  cx.save(); cx.globalAlpha = p;
  cx.fillStyle = OR; cx.beginPath(); cx.arc(SAFE.L + 48, y - 120 + 16 * (1 - p), 48, 0, 7); cx.fill();
  txt(String(n), SAFE.L + 48, y - 116 + 16 * (1 - p), { font: '62px Blk', col: BK, al: 'center' });
  const fs = fitFont(title, SAFE.R - SAFE.L, 104);
  txt(title, SAFE.L, y + 18 * (1 - p), { font: `${fs}px Blk`, col: '#fff' });
  cx.restore();
  if (sub) txt(sub, SAFE.L, y + 100 + 18 * (1 - p2), { font: '54px Semi', col: CR, a: p2 });
}
function pow(s, y, size, col, t, t0) { // „POW”: z niczego, z przestrzeleniem
  if (t < t0) return; const sc = ob((t - t0) / 0.3, 2.6), sh = Math.sin((t - t0) * 70) * 7 * clamp(1 - (t - t0) / 0.22);
  cx.save(); cx.translate(540 + sh, y); cx.scale(sc, sc); cx.shadowColor = 'rgba(0,0,0,.6)'; cx.shadowBlur = 40;
  txt(s, 0, 0, { font: `${fitFont(s, 900, size)}px Blk`, col, al: 'center' }); cx.restore();
}

// --- plansza: kalendarz
function calendar(t, t0) {
  const lt = t - t0;
  cx.fillStyle = DARK; cx.fillRect(0, 0, W, H); logoTop(true);
  step(1, 'Rezerwujesz termin', 'online, w minutę', t, t0 + 0.05, 480);
  const x0 = SAFE.L, y0 = 780, cw = (SAFE.R - SAFE.L) / 7, chh = 80;
  const p = eo((lt - 0.2) / 0.5);
  cx.save(); cx.globalAlpha = p; cx.translate(0, 30 * (1 - p));
  cx.fillStyle = CARD; cx.beginPath(); cx.roundRect(x0 - 20, y0 - 90, SAFE.R - SAFE.L + 40, 610, 32); cx.fill();
  txt('LISTOPAD', x0 + 20, y0 - 36, { font: '38px XB', col: CR, sp: 4 });
  ['Pn', 'Wt', 'Śr', 'Cz', 'Pt', 'So', 'Nd'].forEach((d, i) => txt(d, x0 + cw * i + cw / 2, y0 + 30, { font: '32px Semi', col: '#8E877F', al: 'center' }));
  for (let d = 1; d <= 30; d++) {
    const idx = d + 5, col = idx % 7, row = Math.floor(idx / 7), x = x0 + cw * col + cw / 2, y = y0 + 95 + row * chh;   // 1 listopada 2026 = niedziela
    const sel = d === 12 && lt > 1.0;
    if (sel) { const s = ob((lt - 1.0) / 0.3, 2.4); cx.save(); cx.translate(x, y); cx.scale(s, s); cx.fillStyle = OR; cx.beginPath(); cx.arc(0, 0, 38, 0, 7); cx.fill(); cx.restore(); }
    txt(String(d), x, y + 2, { font: `${sel ? 44 : 40}px ${sel ? 'Blk' : 'Semi'}`, col: sel ? BK : (col >= 5 ? '#8E877F' : CR), al: 'center' });
  }
  cx.restore();
  // godziny
  const slots = ['10:00', '14:00', '18:00'];
  slots.forEach((s2, i) => { const ti = t0 + 1.4 + i * 0.12; if (t < ti) return; const q = eo((t - ti) / 0.35), sel = i === 2 && lt > 2.0;
    const w = 250, x = x0 + i * (w + 45), y = 1330 + 20 * (1 - q);
    cx.save(); cx.globalAlpha = q; cx.fillStyle = sel ? OR : CARD; cx.beginPath(); cx.roundRect(x, y, w, 96, 48); cx.fill();
    txt(s2, x + w / 2, y + 50, { font: '46px XB', col: sel ? BK : CR, al: 'center' }); cx.restore(); });
  if (lt > 2.15) txt('✓  2 h · 300 zł', x0, 1520, { font: '50px XB', col: OR, a: eo((lt - 2.15) / 0.3) });
}
// --- plansza: pliki na SSD
function ssd(t, t0) {
  const lt = t - t0;
  cx.fillStyle = CR; cx.fillRect(0, 0, W, H); logoTop(false);
  const p = ob(lt / 0.45, 1.6);
  cx.save(); cx.translate(540, 820); cx.rotate(-0.08 + 0.08 * eo(lt / 0.6)); cx.scale(p, p);
  cx.fillStyle = 'rgba(0,0,0,.12)'; cx.beginPath(); cx.roundRect(-190, -250, 400, 520, 46); cx.fill();
  cx.fillStyle = '#1B1B1B'; cx.beginPath(); cx.roundRect(-200, -270, 400, 520, 46); cx.fill();
  cx.fillStyle = OR; cx.beginPath(); cx.roundRect(-140, -200, 280, 110, 18); cx.fill();
  txt('SSD', 0, -142, { font: '72px Blk', col: BK, al: 'center' });
  txt('podcast_odc01.mp4', 0, 60, { font: '34px Semi', col: CR, al: 'center' }); txt('audio_final.wav', 0, 115, { font: '34px Semi', col: '#9A938B', al: 'center' });
  cx.fillStyle = '#3A3A3A'; cx.beginPath(); cx.roundRect(-140, 170, 280, 16, 8); cx.fill();
  cx.fillStyle = OR; cx.beginPath(); cx.roundRect(-140, 170, 280 * clamp((lt - 0.3) / 1.0), 16, 8); cx.fill();
  cx.restore();
  // napis kroku na jasnym tle
  if (t >= t0 + 0.2) { const q = eo((t - t0 - 0.2) / 0.45);
    cx.save(); cx.globalAlpha = q; cx.fillStyle = OR; cx.beginPath(); cx.arc(SAFE.L + 48, 1210, 48, 0, 7); cx.fill(); txt('4', SAFE.L + 48, 1214, { font: '62px Blk', col: BK, al: 'center' }); cx.restore();
    txt('Wychodzisz z plikami', SAFE.L, 1330 + 18 * (1 - q), { font: `${fitFont('Wychodzisz z plikami', SAFE.R - SAFE.L, 104)}px Blk`, col: BK, a: q });
    txt('od ręki, na dysku SSD', SAFE.L, 1430, { font: '54px Semi', col: '#5E554D', a: eo((t - t0 - 0.4) / 0.45) }); }
}
// --- finał: wezwanie do rezerwacji
function finale(t, t0) {
  const lt = t - t0;
  cx.fillStyle = OR; cx.fillRect(0, 0, W, H);
  logoTop(false);
  const r2 = (s, y, font, col, tt, o = {}) => { if (t < tt) return; const p = eo((t - tt) / 0.5); txt(s, 540, y + 24 * (1 - p), Object.assign({ font, col, a: p, al: 'center' }, o)); };
  r2('Zarezerwuj', 520, '130px Blk', BK, t0 + 0.1); r2('termin.', 650, '130px Light', BK, t0 + 0.25);
  if (lt > 0.6) { const p = eo((lt - 0.6) / 0.5); cx.save(); cx.globalAlpha = p;
    cx.fillStyle = BK; cx.beginPath(); cx.roundRect(SAFE.L, 780 + 30 * (1 - p), SAFE.R - SAFE.L, 420, 40); cx.fill();
    txt('2 godziny', 540, 870 + 30 * (1 - p), { font: '72px Light', col: CR, al: 'center' });
    txt('300 zł', 540, 1010 + 30 * (1 - p), { font: '170px Blk', col: OR, al: 'center' });
    txt('27 m²  ·  SPRZĘT W CENIE', 540, 1135 + 30 * (1 - p), { font: '40px Semi', col: CR, al: 'center', sp: 5 });
    cx.restore(); }
  if (lt > 1.2) { const s = ob((lt - 1.2) / 0.35, 2.2) * (1 + 0.025 * Math.sin(lt * 7)); cx.save(); cx.translate(540, 1340); cx.scale(s, s);
    cx.fillStyle = '#fff'; cx.beginPath(); cx.roundRect(-380, -70, 760, 140, 70); cx.fill();
    txt('gadkastudio.pl  →', 0, 4, { font: '62px Blk', col: BK, al: 'center' }); cx.restore(); }
  r2('Warszawa', 1490, '42px Semi', BK, t0 + 1.5, { sp: 6 });
}

window.renderAt = async function (t) {
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.globalAlpha = 1; cx.fillStyle = BK; cx.fillRect(0, 0, W, H);
  if (t < E.CAL) { // hak
    await full('e1', t); logoTop(true);
    cx.fillStyle = `rgba(0,0,0,${0.35 * clamp((t - 0.2) / 0.2)})`; cx.fillRect(0, 0, W, H);
    pow('Ty mówisz.', 860, 150, '#fff', t, 0.15);
    pow('My nagrywamy.', 1030, 130, OR, t, 0.75);
    if (t > 1.3) { const p = eo((t - 1.3) / 0.4); cx.save(); cx.globalAlpha = p; cx.fillStyle = CR; cx.beginPath(); cx.roundRect(540 - 400, 1180 + 20 * (1 - p), 800, 110, 55); cx.fill();
      txt('Wynajmij studio podcastowe', 540, 1237 + 20 * (1 - p), { font: '54px XB', col: BK, al: 'center' }); cx.restore(); }
  } else if (t < E.KLIM) calendar(t, E.CAL);
  else if (t < E.NAGR) { // krok 2: szybki przegląd klimatów
    const lt = t - E.KLIM, seq = ['a1', 'a2', 'a3', 'a4'], names = ['biała kostka', 'ciemna zasłona', 'stół radiowy', 'lamele'];
    const k = Math.min(3, Math.floor(lt / (E.NAGR - E.KLIM) * 4)), lk = lt - k * (E.NAGR - E.KLIM) / 4;
    await full(seq[k], lk + 0.3); logoTop(true);
    step(2, 'Wybierasz klimat', null, t, E.KLIM + 0.05);
    txt(names[k], SAFE.L, 1430, { font: '58px Semi', col: CR, a: eo(lk / 0.2) });
  } else if (t < E.SSD) { // krok 3: nagrywasz
    const lt = t - E.NAGR, half = (E.SSD - E.NAGR) / 2;
    if (lt < half) await full('b1', lt); else await full('e2', lt - half);
    logoTop(true);
    step(3, 'Nagrywasz', lt < half ? '2 kamery 4K, profesjonalne światło' : 'mikrofony Shure, czysty dźwięk', t, E.NAGR + 0.05);
  } else if (t < E.FREE) ssd(t, E.SSD);
  else if (t < E.FIN) { // luz
    await full('c1', t - E.FREE + 0.2); logoTop(true);
    pow('To naprawdę tyle.', 1300, 104, '#fff', t, E.FREE + 0.15);
    if (t > E.FREE + 0.7) txt('Zero ogarniania sprzętu.', 540, 1430, { font: '56px Semi', col: CR, al: 'center', a: eo((t - E.FREE - 0.7) / 0.4) });
  } else finale(t, E.FIN);
  grain(t, 0.04);
  if (window.SAFE_BOX) { cx.strokeStyle = '#00E5FF'; cx.lineWidth = 6; cx.strokeRect(SAFE.L, SAFE.T, SAFE.R - SAFE.L, SAFE.B - SAFE.T); }
  if (t > D.TOTAL - 0.4) { cx.fillStyle = `rgba(0,0,0,${clamp((t - D.TOTAL + 0.4) / 0.4)})`; cx.fillRect(0, 0, W, H); }
};

// okładka – kwadrat y 420–1500, x 100–980
window.renderCover = async function () {
  cx.setTransform(1, 0, 0, 1, 0, 0); await full('e1', 1.2);
  cx.fillStyle = 'rgba(0,0,0,.45)'; cx.fillRect(0, 0, W, H);
  cx.drawImage(IM.logo, 540 - 130, 470, 260, 260 * IM.logo.height / IM.logo.width);
  txt('Ty mówisz.', 540, 860, { font: '150px Blk', col: '#fff', al: 'center' });
  txt('My nagrywamy.', 540, 1020, { font: '128px Blk', col: OR, al: 'center' });
  cx.fillStyle = CR; cx.beginPath(); cx.roundRect(540 - 330, 1200, 660, 110, 55); cx.fill();
  txt('2 h · 300 zł', 540, 1257, { font: '62px Blk', col: BK, al: 'center' });
};
