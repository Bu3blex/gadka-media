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

// ---------- SCENY: każda dostaje lokalny czas lt (od startu sceny) i globalny t
const SCENES = [
  { bg: OR, draw(lt, t) {
    kin('Hak w pierwszej', SAFE.L, 760, 96, BK, lt, 0.0);
    kin('sekundzie.', SAFE.L, 875, 96, CR, lt, 0.12);
    pill('…i naklejka', 540, 1100, lt, 0.6, BK, CR);
  } },
  { bg: BK, async draw(lt, t) {
    photo('101', SAFE.L, 500, SAFE.R - SAFE.L, 700, lt / 3, 0.5, 0.5, 30);
    // własne nagranie: const im = await frame('klipA', Math.floor(lt * 30)); if (im) cx.drawImage(im, 0, 0, W, H);
    kin('2 h · 300 zł brutto', SAFE.L, 1340, 84, CR, lt, 0.3);
  } },
];

window.renderAt = async function (t) {
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.globalAlpha = 1;
  const S = D.SC; let i = 0; while (i + 1 < S.length && t >= S[i + 1]) i++;
  const lt = t - S[i];
  // przejście: nowa scena wchodzi kołem z rogu
  const iris = i > 0 ? eio(lt / 0.42) : 1;
  if (iris < 1) { cx.fillStyle = SCENES[i - 1].bg; cx.fillRect(0, 0, W, H); await SCENES[i - 1].draw(t - S[i - 1], t); }
  cx.save();
  if (iris < 1) { cx.beginPath(); cx.arc(i % 2 ? W : 0, H, 2300 * iris, 0, 7); cx.clip(); }
  cx.fillStyle = SCENES[i].bg; cx.fillRect(0, 0, W, H); await SCENES[i].draw(lt, t);
  cx.restore();
  grain(t);
  if (window.SAFE_BOX) { cx.strokeStyle = '#00E5FF'; cx.lineWidth = 6; cx.strokeRect(SAFE.L, SAFE.T, SAFE.R - SAFE.L, SAFE.B - SAFE.T); }
  if (t > D.TOTAL - 0.4) { cx.fillStyle = `rgba(0,0,0,${clamp((t - D.TOTAL + 0.4) / 0.4)})`; cx.fillRect(0, 0, W, H); }
};

// okładka 1080x1920 – wszystko w kwadracie y 420–1500, x 100–980
window.renderCover = function () {
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.fillStyle = OR; cx.fillRect(0, 0, W, H);
  txt('ROLKA · TEMAT', 100, 500, { font: '38px Bold', col: BK });
  cx.drawImage(IM.logoB, 980 - 190, 470, 190, 190 * IM.logoB.height / IM.logoB.width);
  txt('WIELKI', 100, 860, { font: '200px Blk', col: BK }); txt('HAK.', 100, 1060, { font: '200px Blk', col: CR });
  txt('▶  gadkastudio.pl', 100, 1420, { font: '38px Bold', col: BK });
};
