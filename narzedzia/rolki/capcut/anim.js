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

// ---------- ROLKA: TikTok/CapCut – „ziomek nagrywa podcast w łazience 💀”
const B = D.B, CAP = D.CAP, SHOTS = D.SHOTS, DROP = D.DROP, END = D.END;
const YEL = '#FFE14D', LIME = '#D7FF3A';

// --- łazienka w jakości „ziemniak”: rysowana w niskiej rozdzielczości i powiększana
const low = document.createElement('canvas'); low.width = 180; low.height = 320; const lc = low.getContext('2d');
function bathroom(t) {
  lc.fillStyle = '#C9D6D3'; lc.fillRect(0, 0, 180, 320);
  lc.strokeStyle = '#9FB0AC'; lc.lineWidth = 1;
  const sh = Math.sin(t * 7) * 2, sv = Math.cos(t * 5) * 2;
  for (let x = -20; x < 200; x += 22) { lc.beginPath(); lc.moveTo(x + sh, 0); lc.lineTo(x + sh, 320); lc.stroke(); }
  for (let y = -20; y < 340; y += 22) { lc.beginPath(); lc.moveTo(0, y + sv); lc.lineTo(180, y + sv); lc.stroke(); }
  // lustro + umywalka + telefon na kubku
  lc.fillStyle = '#E8F0EF'; lc.fillRect(40 + sh, 40 + sv, 100, 90); lc.strokeStyle = '#8A9A96'; lc.strokeRect(40 + sh, 40 + sv, 100, 90);
  lc.fillStyle = '#F4F4F4'; lc.beginPath(); lc.ellipse(90 + sh, 200 + sv, 60, 18, 0, 0, 7); lc.fill(); lc.fillStyle = '#BFC9C7'; lc.fillRect(80 + sh, 210 + sv, 20, 90);
  lc.fillStyle = '#333'; lc.fillRect(76 + sh, 150 + sv, 28, 40); lc.fillStyle = '#777'; lc.fillRect(80 + sh, 154 + sv, 20, 6);
  lc.fillStyle = '#E25A3A'; lc.fillRect(118 + sh, 168 + sv, 16, 22); // kubek
  // ręcznik na wieszaku i sedes
  lc.fillStyle = '#5FA8D3'; lc.fillRect(150 + sh, 60 + sv, 26, 70); lc.fillStyle = '#4A8DB5'; lc.fillRect(150 + sh, 120 + sv, 26, 10);
  lc.fillStyle = '#FAFAFA'; lc.beginPath(); lc.ellipse(30 + sh, 280 + sv, 34, 14, 0, 0, 7); lc.fill(); lc.fillRect(4 + sh, 230 + sv, 52, 50); lc.fillStyle = '#E6E6E6'; lc.fillRect(8 + sh, 222 + sv, 44, 12);
  lc.fillStyle = '#FFFFFF'; lc.fillRect(150 + sh, 220 + sv, 18, 22); lc.fillStyle = '#DDD'; lc.fillRect(150 + sh, 228 + sv, 18, 3); // papier
  cx.save(); cx.imageSmoothingEnabled = false; cx.filter = 'contrast(.85) saturate(.7) brightness(.95)'; cx.drawImage(low, 0, 0, W, H); cx.filter = 'none'; cx.restore();
  // nakładka kamery telefonu
  cx.fillStyle = 'rgba(0,0,0,.18)'; cx.fillRect(0, 0, W, H);
  if (Math.floor(t * 2) % 2 === 0) { cx.fillStyle = '#FF3B30'; cx.beginPath(); cx.arc(SAFE.L + 20, 330, 16, 0, 7); cx.fill(); }
  txt('REC  00:0' + Math.floor(t + 3) + ':' + String(Math.floor(t * 30) % 30).padStart(2, '0'), SAFE.L + 50, 332, { font: '40px XB', col: '#fff' });
  pill('jakość: ziemniak 🥔', 700, 450, t, 0.8, '#fff', BK, 38, 0.05);
}

// --- zdjęcie na pełen ekran z „punch zoom” na każde uderzenie
function shotPhoto(k, lt, t, fx = 0.5, fy = 0.5) {
  const im = IM[k]; if (!im) return;
  const beat = ((t - DROP) / B) % 1, punch = 1 + 0.06 * Math.exp(-beat * 6);
  const s = Math.max(W / im.width, H / im.height) * (1.08 + 0.05 * lt) * punch;
  const shx = Math.sin(t * 43) * 6 * Math.exp(-beat * 5), shy = Math.cos(t * 37) * 6 * Math.exp(-beat * 5);
  cx.drawImage(im, W / 2 - im.width * s * fx + shx, H / 2 - im.height * s * fy + shy, im.width * s, im.height * s);
  const g = cx.createLinearGradient(0, H * 0.45, 0, H); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,.55)'); cx.fillStyle = g; cx.fillRect(0, 0, W, H);
}
// --- napisy CapCut: słowo po słowie, obrys, podświetlone bieżące słowo
function captions(t) {
  CAP.forEach(([t0, t1, line, hi, size]) => {
    if (t < t0 || t > t1) return;
    const words = line.split(' '), step = Math.min(0.2, (t1 - t0 - 0.4) / words.length);
    const fs = size || 104; cx.font = `${fs}px Blk`;
    // zawijanie do 840 px
    const rows = []; let row = [];
    words.forEach((w, i) => { const tst = row.concat([w]).map(x => x.w || x).join(' '); if (cx.measureText(tst).width > 840 && row.length) { rows.push(row); row = []; } row.push(w); });
    rows.push(row);
    let idx = 0; const lh = fs * 1.12, y0 = 1180 - (rows.length - 1) * lh / 2;
    rows.forEach((r, ri) => {
      const tw = cx.measureText(r.join(' ')).width; let x = 540 - tw / 2;
      r.forEach(w => {
        const ti = t0 + idx * step, ww = cx.measureText(w + ' ').width;
        if (t >= ti) {
          const age = t - ti, sc = ob(age / 0.12, 2.6), cur = (hi === 'all') ? true : (Array.isArray(hi) ? hi.includes(idx) : age < step * 1.2 && idx === Math.floor((t - t0) / step));
          cx.save(); cx.translate(x + cx.measureText(w).width / 2, y0 + ri * lh); cx.scale(sc, sc);
          cx.font = `${fs}px Blk`; cx.textAlign = 'center'; cx.textBaseline = 'middle'; cx.lineJoin = 'round';
          cx.lineWidth = fs * 0.16; cx.strokeStyle = BK; cx.shadowColor = 'rgba(0,0,0,.5)'; cx.shadowBlur = 20; cx.strokeText(w, 0, 0); cx.shadowColor = 'transparent';
          cx.fillStyle = cur ? YEL : '#fff'; cx.fillText(w, 0, 0); cx.restore();
        }
        x += ww; idx++;
      });
    });
  });
}
function echoGhosts(t, t0, t1) { // powidoki napisu „echo”
  if (t < t0 + 0.6 || t > t1) return;
  for (let k = 1; k <= 3; k++) { cx.save(); cx.globalAlpha = 0.22 / k; cx.translate(540, 1180); cx.scale(1 + 0.08 * k, 1 + 0.08 * k); cx.translate(-540, -1180);
    txt('ECHO JAK W KATEDRZE', 540, 1180 - 30 * k, { font: '96px Blk', col: '#fff', al: 'center' }); cx.restore(); }
}

window.renderAt = async function (t) {
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.globalAlpha = 1;
  let shot = SHOTS[0]; SHOTS.forEach(s => { if (t >= s[0]) shot = s; });
  const lt = t - shot[0];
  if (shot[1] === 'bath') bathroom(t);
  else if (shot[1] === 'black') { cx.fillStyle = BK; cx.fillRect(0, 0, W, H); }
  else if (shot[1] === 'orange') { cx.fillStyle = OR; cx.fillRect(0, 0, W, H);
    const beat = ((t - DROP) / B) % 1; cx.save(); cx.translate(540, 900); cx.scale(1 + 0.05 * Math.exp(-beat * 6), 1 + 0.05 * Math.exp(-beat * 6)); cx.translate(-540, -900);
    txt('2H = 300 ZŁ', 540, 860, { font: '150px Blk', col: '#fff', al: 'center' }); txt('brutto · sprzęt w cenie', 540, 1000, { font: '58px XB', col: BK, al: 'center' }); cx.restore(); }
  else shotPhoto(shot[1], lt, t, shot[2] || 0.5, shot[3] || 0.5);
  if (shot[1] === 'bath') echoGhosts(t, D.ECHO[0], D.ECHO[1]);
  // błysk na cięciach po dropie
  const fl = clamp(1 - lt / 0.1); if (shot[0] >= DROP && fl > 0) { cx.fillStyle = `rgba(255,255,255,${0.6 * fl})`; cx.fillRect(0, 0, W, H); }
  // przesunięcie RGB na dropie
  if (t > DROP && t < DROP + 0.25) { cx.save(); cx.globalCompositeOperation = 'screen'; cx.globalAlpha = 0.35; cx.drawImage(cv, 14, 0); cx.restore(); }
  captions(t);
  if (t >= END) { // plansza końcowa
    const p = clamp((t - END) / 0.3); cx.fillStyle = `rgba(0,0,0,${0.6 * p})`; cx.fillRect(0, 0, W, H);
    if (t > END + 0.2) { cx.save(); cx.globalAlpha = clamp((t - END - 0.2) / 0.3); cx.drawImage(IM.logo, 540 - 260, 520, 520, 520 * IM.logo.height / IM.logo.width); cx.restore(); }
    if (t > END + 0.4) { txt('2h · 300 zł brutto · Warszawa', 540, 1260, { font: '52px XB', col: '#fff', al: 'center', a: clamp((t - END - 0.4) / 0.3) }); }
    if (t > END + 0.6) pill('gadkastudio.pl', 540, 1420, t, END + 0.6, LIME, BK, 60, -0.03);
  }
  grain(t, 0.08);
  if (window.SAFE_BOX) { cx.strokeStyle = '#00E5FF'; cx.lineWidth = 6; cx.strokeRect(SAFE.L, SAFE.T, SAFE.R - SAFE.L, SAFE.B - SAFE.T); }
  if (t > D.TOTAL - 0.35) { cx.fillStyle = `rgba(0,0,0,${clamp((t - D.TOTAL + 0.35) / 0.35)})`; cx.fillRect(0, 0, W, H); }
};

// okładka – kwadrat y 420–1500, x 100–980
window.renderCover = function () {
  cx.setTransform(1, 0, 0, 1, 0, 0); bathroom(0.4);
  cx.fillStyle = 'rgba(0,0,0,.25)'; cx.fillRect(0, 0, W, H);
  const lines = [['ZIOMEK', '#fff'], ['NAGRYWA', '#fff'], ['PODCAST', '#fff'], ['W ŁAZIENCE', YEL]];
  lines.forEach(([s, c], i) => { cx.save(); cx.font = '128px Blk'; cx.textAlign = 'center'; cx.textBaseline = 'middle'; cx.lineJoin = 'round'; cx.lineWidth = 22; cx.strokeStyle = BK;
    cx.strokeText(s, 540, 720 + i * 140); cx.fillStyle = c; cx.fillText(s, 540, 720 + i * 140); cx.restore(); });
  txt('💀', 540, 1340, { font: '150px "Noto Color Emoji"', al: 'center' });
  cx.drawImage(IM.logo, 540 - 130, 1420, 260, 260 * IM.logo.height / IM.logo.width);
};
