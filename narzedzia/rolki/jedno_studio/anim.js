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

// ---------- ROLKA: „Jedno studio. Wiele możliwości.” – minimalistycznie i z klasą
const SH = D.SHOTS, FIN = D.FIN, BAR = D.BAR;
const N = { hook: 151, a1: 79, a2: 79, a3: 80, a4: 79, e1: 79, e2: 79, fin: 150 };
async function clip(name, lt, a = 1, dy = 0, blur = 0) {
  const im = await frame(name, Math.min(N[name] - 1, Math.max(0, Math.floor(lt * 30)))); if (!im) return;
  const s = 1.0 + 0.016 * lt;
  cx.save(); cx.globalAlpha = a; cx.filter = (blur ? `blur(${blur}px) ` : '') + 'contrast(1.04) saturate(1.05) sepia(.06)';
  cx.drawImage(im, W / 2 - W * s / 2, H / 2 - H * s / 2 + dy, W * s, H * s); cx.restore();
}
function rise(s, x, y, font, col, t, t0, o = {}) { // elegancki fade + uniesienie
  if (t < t0) return; const p = eo((t - t0) / 0.6);
  txt(s, x, y + 26 * (1 - p), Object.assign({ font, col, a: p * (o.a ?? 1) }, o));
}
function label(name, t, t0, sub) { // duży napis: co to jest + dlaczego
  if (t < t0) return; const p = eo((t - t0) / 0.45);
  cx.save(); cx.globalAlpha = p;
  cx.fillStyle = OR; cx.fillRect(SAFE.L, 1300, 90 * p, 7);
  let fs = 104; cx.font = `${fs}px Blk`; while (cx.measureText(name).width > SAFE.R - SAFE.L && fs > 60) { fs -= 4; cx.font = `${fs}px Blk`; }
  txt(name, SAFE.L, 1390 + 18 * (1 - p), { font: `${fs}px Blk`, col: '#fff' });
  if (sub) { const p2 = eo((t - t0 - 0.2) / 0.45); txt(sub, SAFE.L, 1490 + 18 * (1 - p2), { font: '56px Semi', col: CR, a: p2 }); }
  cx.restore();
}
function vignette() {
  const g = cx.createLinearGradient(0, 950, 0, H); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,.8)'); cx.fillStyle = g; cx.fillRect(0, 1050, W, H - 1050);
  const g2 = cx.createLinearGradient(0, 0, 0, 520); g2.addColorStop(0, 'rgba(0,0,0,.35)'); g2.addColorStop(1, 'rgba(0,0,0,0)'); cx.fillStyle = g2; cx.fillRect(0, 0, W, 520);
}
const META = {
  a1: ['Biała kostka', 'jasny, świeży klimat'], a2: ['Ciemna zasłona', 'kameralnie i elegancko'],
  a3: ['Stół radiowy', 'jak w prawdziwym radiu'], a4: ['Lamele', 'ciepło i nowocześnie'],
  e1: ['2 kamery 4K', 'obraz gotowy do publikacji'], e2: ['Mikrofony Shure', 'brzmisz jak profesjonalista'],
};

window.renderAt = async function (t) {
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.globalAlpha = 1; cx.fillStyle = BK; cx.fillRect(0, 0, W, H);
  let i = 0; while (i + 1 < SH.length && t >= SH[i + 1][0]) i++;
  const [t0, name] = SH[i], lt = t - t0;
  if (t < FIN) {
    // miękkie przejście: poprzednie ujęcie gaśnie, nowe wjeżdża z delikatnym uniesieniem
    if (name === 'board') { // hak: plansza z ceną
      cx.fillStyle = BK; cx.fillRect(0, 0, W, H);
      rise('2 godziny.', SAFE.L, 820, '150px Light', CR, t, 0.0);
      rise('300 zł.', SAFE.L, 1010, '230px Blk', OR, t, 0.3);
      rise('STUDIO PODCASTOWE  ·  WARSZAWA', SAFE.L, 1190, '36px Semi', CR, t, 0.7, { sp: 6 });
      cx.save(); cx.globalAlpha = 0.95; cx.drawImage(IM.logo, SAFE.R - 170, 322, 170, 170 * IM.logo.height / IM.logo.width); cx.restore();
      grain(t, 0.045); return;
    }
    const p = i > 0 && SH[i - 1][1] !== 'board' ? eio(lt / 0.45) : 1;
    if (p < 1) await clip(SH[i - 1][1], t - SH[i - 1][0]);
    if (name === 'hook') { // trzy kadry odsłaniają się po kolei na uderzenia
      for (let k = 0; k < 3; k++) {
        const w = eio((t - k * 0.1) / 0.16); if (w <= 0) continue;
        cx.save(); cx.beginPath(); cx.rect(0, k * 640, W * w, 640 + (k === 2 ? 0 : 1)); cx.clip(); await clip('hook', lt); cx.restore();
      }
      const g = cx.createLinearGradient(0, 1250, 0, H); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,.55)'); cx.fillStyle = g; cx.fillRect(0, 1250, W, H - 1250);
    } else { await clip(name, lt, p, 40 * (1 - p)); vignette(); }
    if (name === 'hook') {
      const tp = 0.42; // cena wybucha na środku
      if (t >= tp) { const sc = ob((t - tp) / 0.32, 2.6), sh = Math.sin((t - tp) * 70) * 8 * clamp(1 - (t - tp) / 0.25);
        cx.save(); cx.fillStyle = `rgba(0,0,0,${0.45 * clamp((t - tp) / 0.2)})`; cx.fillRect(0, 0, W, H); cx.restore();
        cx.save(); cx.translate(540 + sh, 930); cx.scale(sc, sc);
        cx.shadowColor = 'rgba(0,0,0,.6)'; cx.shadowBlur = 40;
        txt('2 godziny', 0, -150, { font: '120px Light', col: '#fff', al: 'center' });
        txt('300 zł', 0, 40, { font: '235px Blk', col: OR, al: 'center' }); cx.restore(); }
      if (t >= tp + 0.55) { const p = eo((t - tp - 0.55) / 0.4); cx.save(); cx.globalAlpha = p;
        cx.fillStyle = CR; cx.beginPath(); cx.roundRect(540 - 400, 1215 + 20 * (1 - p), 800, 110, 55); cx.fill();
        txt('Wynajmij studio podcastowe', 540, 1272 + 20 * (1 - p), { font: '54px XB', col: BK, al: 'center' }); cx.restore(); }
    } else {
      const [lab, top] = META[name];
      label(lab, t, t0 + 0.2, top);
    }
    cx.save(); cx.globalAlpha = 0.97; cx.shadowColor = 'rgba(0,0,0,.4)'; cx.shadowBlur = 20; cx.drawImage(IM.logo, 540 - 115, 165, 230, 230 * IM.logo.height / IM.logo.width); cx.restore();
  } else {
    const lf = t - FIN;
    await clip('fin', lf, 1, 0, 18);
    cx.fillStyle = `rgba(10,10,10,${0.5 + 0.2 * clamp(lf / 0.6)})`; cx.fillRect(0, 0, W, H);
    if (lf > 0.15) { const p = eo((lf - 0.15) / 0.7); cx.save(); cx.globalAlpha = p; const lw = 440; cx.drawImage(IM.logo, 540 - lw / 2, 470 + 20 * (1 - p), lw, lw * IM.logo.height / IM.logo.width); cx.restore(); }
    rise('2 godziny', 540, 830, '96px Light', CR, t, FIN + 0.6, { al: 'center' });
    rise('300 zł', 540, 990, '200px Blk', OR, t, FIN + 0.9, { al: 'center' });
    rise('27 m²  ·  SPRZĘT W CENIE', 540, 1135, '40px Semi', CR, t, FIN + 1.3, { al: 'center', sp: 6 });
    if (lf > 1.7) { const p = eo((lf - 1.7) / 0.6); cx.fillStyle = OR; cx.fillRect(540 - 60 * p, 1240, 120 * p, 4); }
    rise('gadkastudio.pl', 540, 1330, '52px Semi', CR, t, FIN + 1.9, { al: 'center', sp: 3 });
    rise('Warszawa', 540, 1400, '34px Light', 'rgba(249,238,228,.75)', t, FIN + 2.1, { al: 'center', sp: 6 });
  }
  grain(t, 0.045);
  if (window.SAFE_BOX) { cx.strokeStyle = '#00E5FF'; cx.lineWidth = 6; cx.strokeRect(SAFE.L, SAFE.T, SAFE.R - SAFE.L, SAFE.B - SAFE.T); }
  if (t > D.TOTAL - 0.5) { cx.fillStyle = `rgba(0,0,0,${clamp((t - D.TOTAL + 0.5) / 0.5)})`; cx.fillRect(0, 0, W, H); }
};

// okładka – kwadrat y 420–1500, x 100–980
window.renderCover = async function () {
  cx.setTransform(1, 0, 0, 1, 0, 0);
  await clip('hook', 1.2); vignette();
  cx.fillStyle = 'rgba(0,0,0,.42)'; cx.fillRect(0, 0, W, H);
  txt('Jedno studio.', 100, 860, { font: '128px Light', col: CR });
  txt('Wiele możliwości.', 100, 1000, { font: '92px Semi', col: OR });
  cx.fillStyle = OR; cx.fillRect(100, 1110, 90, 5);
  txt('2 H · 300 ZŁ BRUTTO', 100, 1180, { font: '40px Semi', col: CR, sp: 6 });
  cx.drawImage(IM.logo, 100, 470, 240, 240 * IM.logo.height / IM.logo.width);
};
