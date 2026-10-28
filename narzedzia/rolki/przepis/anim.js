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

// ---------- ROLKA: „Przepis na podcast” – parodia programu kulinarnego
const E = D.E;
const PAPER = '#F6EBDD', INK = '#1B1714', TOM = '#E2482E', OLV = '#6E7F3B', MUST = '#E9B23F', BRN = '#8A5A3B';
const BX = SAFE.L, BW = SAFE.R - SAFE.L, CXM = 540;

function paperBg(t) {
  cx.fillStyle = PAPER; cx.fillRect(0, 0, W, H);
  // obrus w kratkę u dołu (poza strefą – dekoracja)
  cx.save(); cx.globalAlpha = 0.13; cx.fillStyle = TOM;
  for (let x = 0; x < W; x += 90) for (let y = 1640; y < H; y += 90) if (((x + y) / 90) % 2 === 0) cx.fillRect(x, y, 90, 90);
  cx.restore();
  // ziarno/plamki
  for (let i = 0; i < 40; i++) { cx.fillStyle = `rgba(120,80,40,${0.04 + 0.04 * rnd(i)})`; cx.beginPath(); cx.arc(rnd(i) * W, rnd(i + 9) * 1640, 2 + 5 * rnd(i + 3), 0, 7); cx.fill(); }
}
function serif(s, x, y, size, col, o = {}) { txt(s, x, y, Object.assign({ font: `italic 600 ${size}px Lora`, col }, o)); }
function stroke(w = 6, col = INK) { cx.strokeStyle = col; cx.lineWidth = w; cx.lineCap = 'round'; cx.lineJoin = 'round'; }

// ---------- ikony składników (środek 0,0, ok. 220 px)
const ICONS = {
  bulb() { cx.fillStyle = MUST; cx.beginPath(); cx.arc(0, -25, 70, 0, 7); cx.fill(); stroke(); cx.stroke();
    cx.fillStyle = '#ccc'; cx.fillRect(-32, 45, 64, 40); cx.strokeRect(-32, 45, 64, 40); cx.beginPath(); cx.moveTo(-32, 65); cx.lineTo(32, 65); cx.stroke();
    for (let i = 0; i < 5; i++) { const a = -Math.PI / 2 + (i - 2) * 0.55; cx.beginPath(); cx.moveTo(Math.cos(a) * 92, -25 + Math.sin(a) * 92); cx.lineTo(Math.cos(a) * 118, -25 + Math.sin(a) * 118); cx.stroke(); } },
  guest() { cx.fillStyle = '#fff'; cx.beginPath(); cx.roundRect(-95, -80, 190, 120, 40); cx.fill(); stroke(); cx.stroke();
    cx.beginPath(); cx.moveTo(-30, 40); cx.lineTo(-55, 85); cx.lineTo(5, 40); cx.fillStyle = '#fff'; cx.fill(); cx.stroke();
    cx.fillStyle = INK; [-40, 0, 40].forEach(x => { cx.beginPath(); cx.arc(x, -20, 11, 0, 7); cx.fill(); }); },
  mic() { cx.fillStyle = '#2B2B2B'; cx.beginPath(); cx.roundRect(-40, -110, 80, 150, 40); cx.fill(); stroke(); cx.stroke();
    stroke(4, '#777'); for (let i = 0; i < 4; i++) { cx.beginPath(); cx.moveTo(-30, -85 + i * 24); cx.lineTo(30, -85 + i * 24); cx.stroke(); }
    stroke(); cx.beginPath(); cx.moveTo(0, 40); cx.lineTo(0, 90); cx.moveTo(-45, 90); cx.lineTo(45, 90); cx.stroke(); },
  cam() { cx.fillStyle = '#2B2B2B'; cx.beginPath(); cx.roundRect(-95, -55, 150, 110, 18); cx.fill(); stroke(); cx.stroke();
    cx.fillStyle = '#444'; cx.beginPath(); cx.moveTo(55, -25); cx.lineTo(100, -50); cx.lineTo(100, 50); cx.lineTo(55, 25); cx.closePath(); cx.fill(); cx.stroke();
    cx.fillStyle = TOM; cx.beginPath(); cx.arc(-65, -32, 9, 0, 7); cx.fill(); cx.fillStyle = '#88A8C8'; cx.beginPath(); cx.arc(-20, 0, 28, 0, 7); cx.fill(); cx.stroke();
    txt('4K', 20, -30, { font: '30px Blk', col: '#fff', al: 'center' }); },
  light() { cx.fillStyle = '#fff'; cx.beginPath(); cx.moveTo(-80, -90); cx.lineTo(80, -90); cx.lineTo(55, 10); cx.lineTo(-55, 10); cx.closePath(); cx.fill(); stroke(); cx.stroke();
    stroke(); cx.beginPath(); cx.moveTo(0, 10); cx.lineTo(0, 90); cx.moveTo(-40, 90); cx.lineTo(40, 90); cx.stroke();
    cx.fillStyle = MUST; for (let i = 0; i < 3; i++) { cx.save(); cx.translate(-60 + i * 60, 50 + (i % 2) * 20); cx.beginPath(); for (let k = 0; k < 8; k++) { const r = k % 2 ? 6 : 16, a = k / 8 * Math.PI * 2; cx.lineTo(Math.cos(a) * r, Math.sin(a) * r); } cx.fill(); cx.restore(); } },
  clock() { cx.fillStyle = '#fff'; cx.beginPath(); cx.arc(0, 0, 90, 0, 7); cx.fill(); stroke(); cx.stroke();
    stroke(8); cx.beginPath(); cx.moveTo(0, 0); cx.lineTo(0, -60); cx.moveTo(0, 0); cx.lineTo(42, 18); cx.stroke();
    txt('2 h', 0, 50, { font: '34px Blk', col: TOM, al: 'center' }); },
};
const ING = [
  ['1', 'pomysł', 'bulb'], ['1', 'gość (albo dwóch)', 'guest'], ['2×', 'mikrofon Shure', 'mic'],
  ['2×', 'kamera 4K', 'cam'], ['szczypta', 'profesjonalnego światła', 'light'], ['2', 'godziny w studiu', 'clock'],
];
function pot(t, x = CXM, y = 1330) {
  // para
  stroke(8, 'rgba(255,255,255,.95)');
  for (let i = 0; i < 3; i++) { const ox = -110 + i * 110, ph = t * 2 + i; cx.globalAlpha = 0.7; cx.beginPath();
    for (let k = 0; k <= 20; k++) { const yy = y - 190 - k * 9, xx = x + ox + Math.sin(ph + k * 0.45) * 16; k ? cx.lineTo(xx, yy) : cx.moveTo(xx, yy); } cx.stroke(); }
  cx.globalAlpha = 1;
  cx.fillStyle = '#2E2A28'; cx.beginPath(); cx.moveTo(x - 260, y - 170); cx.lineTo(x + 260, y - 170); cx.lineTo(x + 230, y + 120); cx.quadraticCurveTo(x, y + 170, x - 230, y + 120); cx.closePath(); cx.fill();
  cx.fillStyle = '#4A4440'; cx.beginPath(); cx.ellipse(x, y - 170, 270, 46, 0, 0, 7); cx.fill();
  cx.fillStyle = TOM; cx.beginPath(); cx.ellipse(x, y - 168, 238, 32, 0, 0, 7); cx.fill();   // „zupa”
  cx.fillStyle = '#2E2A28'; cx.beginPath(); cx.roundRect(x - 330, y - 140, 80, 34, 16); cx.fill(); cx.beginPath(); cx.roundRect(x + 250, y - 140, 80, 34, 16); cx.fill();
  cx.fillStyle = 'rgba(255,255,255,.08)'; cx.beginPath(); cx.moveTo(x - 200, y - 130); cx.lineTo(x - 150, y - 130); cx.lineTo(x - 175, y + 90); cx.lineTo(x - 210, y + 80); cx.fill();
  txt('GADKA', x, y - 30, { font: '56px Blk', col: PAPER, al: 'center', sp: 6 });
}
function splash(x, y, t, t0) {
  if (t < t0 || t > t0 + 0.6) return; const p = (t - t0) / 0.6;
  for (let i = 0; i < 10; i++) { const a = Math.PI + (i / 9) * Math.PI, r = 40 + 170 * eo(p);
    cx.fillStyle = `rgba(226,72,46,${1 - p})`; cx.beginPath(); cx.arc(x + Math.cos(a) * r, y + Math.sin(a) * r * 0.8 + 140 * p * p, 12 * (1 - p) + 4, 0, 7); cx.fill(); }
}

function hook(t) {
  paperBg(t);
  kin('PRZEPIS NA', BX, 560, 64, TOM, t, 0.0, { font: '64px XB', sp: 8 });
  if (t > 0.15) { const p = eo((t - 0.15) / 0.45); cx.save(); cx.globalAlpha = p; cx.translate(0, 40 * (1 - p)); serif('podcast,', BX - 6, 720, 190, INK); serif('który wreszcie', BX, 880, 92, INK); serif('wyjdzie.', BX, 980, 92, OLV); cx.restore(); }
  if (t > 1.3) { // pieczątka-ostrzeżenie
    const s = ob((t - 1.3) / 0.3, 3); cx.save(); cx.translate(540, 1260); cx.rotate(-0.06); cx.scale(s, s);
    cx.strokeStyle = TOM; cx.lineWidth = 10; cx.beginPath(); cx.roundRect(-370, -125, 740, 250, 24); cx.stroke();
    txt('UWAGA:', 0, -55, { font: '58px Blk', col: TOM, al: 'center', sp: 6 });
    txt('NIE PRZYGOTOWYWAĆ', 0, 15, { font: '58px Blk', col: TOM, al: 'center' });
    txt('W KUCHNI!', 0, 82, { font: '62px Blk', col: TOM, al: 'center' });
    cx.restore(); }
}

function ingredients(t) {
  paperBg(t);
  const lt = t - E.ING;
  txt('Składniki', BX, 360, { font: 'italic 600 84px Lora', col: INK });
  cx.fillStyle = TOM; cx.fillRect(BX, 420, 160, 8);
  const k = Math.min(ING.length - 1, Math.floor(lt / E.STEP_ING));
  const lk = lt - k * E.STEP_ING;
  // licznik
  txt(`${k + 1}/${ING.length}`, SAFE.R, 362, { font: '52px Blk', col: OLV, al: 'right' });
  // etykieta bieżącego składnika
  const [q, name, ic] = ING[k];
  const la = clamp(lk / 0.25) * clamp((E.STEP_ING - lk) / 0.2 + (k === ING.length - 1 ? 1 : 0));
  cx.save(); cx.globalAlpha = la;
  txt(q, CXM, 560, { font: `${q.length > 3 ? 70 : 110}px Blk`, col: TOM, al: 'center' });
  serif(name, CXM, 680, name.length > 18 ? 62 : 76, INK, { al: 'center' });
  cx.restore();
  pot(t);
  // ikona wpada do garnka
  const fall = clamp((lk - 0.15) / 0.6);
  if (lk > 0.15 && fall < 1) {
    const y = lerp(820, 1170, fall * fall), sc = 1 - 0.45 * fall * fall;
    cx.save(); cx.translate(CXM, y); cx.rotate(Math.sin(fall * 3) * 0.3); cx.scale(sc, sc); ICONS[ic](); cx.restore();
  }
  splash(CXM, 1165, t, E.ING + k * E.STEP_ING + 0.75);
}

const STEPS = [
  ['1', 'Zarezerwuj termin', 'na gadkastudio.pl', null],
  ['2', 'Nagrywajcie 2 h', 'sprzęt już czeka w studiu', '101'],
  ['3', 'Podawaj od razu', 'pliki na SSD, zaraz po nagraniu', '034'],
];
function steps(t) {
  paperBg(t);
  const lt = t - E.STEPS;
  txt('Przygotowanie', BX, 360, { font: 'italic 600 84px Lora', col: INK });
  cx.fillStyle = TOM; cx.fillRect(BX, 420, 160, 8);
  STEPS.forEach(([n, a, b, ph], i) => {
    const ti = i * 1.9; if (lt < ti) return;
    const p = eo((lt - ti) / 0.45), y = 520 + i * 350;
    cx.save(); cx.translate(220 * (1 - p), 0); cx.globalAlpha = p;
    cx.fillStyle = '#fff'; cx.shadowColor = 'rgba(80,40,10,.18)'; cx.shadowBlur = 30; cx.shadowOffsetY = 10;
    cx.beginPath(); cx.roundRect(BX, y, BW, 300, 34); cx.fill(); cx.shadowColor = 'transparent';
    cx.fillStyle = [TOM, OLV, MUST][i]; cx.beginPath(); cx.arc(BX + 95, y + 150, 58, 0, 7); cx.fill();
    txt(n, BX + 95, y + 154, { font: '72px Blk', col: '#fff', al: 'center' });
    const tx = BX + 190, tw = ph ? 380 : 600;
    txt(a, tx, y + 110, { font: `${ph ? 46 : 54}px XB`, col: INK });
    const words = b.split(' '); let line = '', ly = y + 190;
    cx.font = '40px Semi';
    words.forEach(w => { const tst = line ? line + ' ' + w : w; if (cx.measureText(tst).width > tw && line) { txt(line, tx, ly, { font: '40px Semi', col: '#6B5E52' }); line = w; ly += 50; } else line = tst; });
    txt(line, tx, ly, { font: '40px Semi', col: '#6B5E52' });
    if (ph) photo(ph, SAFE.R - 230, y + 40, 190, 220, lt / 4, 0.5, 0.5, 22);
    cx.restore();
  });
}

function serve(t) {
  paperBg(t);
  const lt = t - E.SERVE;
  kin('Gotowe!', BX, 400, 120, INK, t, E.SERVE, { font: 'italic 600 120px Lora' });
  // talerz ze studiem
  const s = ob(lt / 0.5, 1.6);
  cx.save(); cx.translate(CXM, 940); cx.scale(s, s);
  cx.fillStyle = 'rgba(80,40,10,.15)'; cx.beginPath(); cx.ellipse(0, 30, 380, 380, 0, 0, 7); cx.fill();
  cx.fillStyle = '#fff'; cx.beginPath(); cx.arc(0, 0, 380, 0, 7); cx.fill(); cx.strokeStyle = '#E6D8C6'; cx.lineWidth = 6; cx.beginPath(); cx.arc(0, 0, 320, 0, 7); cx.stroke();
  cx.save(); cx.beginPath(); cx.arc(0, 0, 300, 0, 7); cx.clip(); photo('104', -300, -300, 600, 600, lt / 3, 0.5, 0.55); cx.restore();
  cx.restore();
  // sztućce
  if (lt > 0.3) { const a = clamp((lt - 0.3) / 0.3); cx.save(); cx.globalAlpha = a; stroke(14, '#9A9A9A');
    cx.beginPath(); cx.moveTo(BX + 10, 700); cx.lineTo(BX + 10, 1180); cx.stroke(); cx.beginPath(); cx.moveTo(SAFE.R - 10, 700); cx.lineTo(SAFE.R - 10, 1180); cx.stroke(); cx.restore(); }
  pill('podawać od razu', 560, 1430, t, E.SERVE + 0.8, TOM, '#fff', 54, -0.04);
}

function finale(t) {
  const lt = t - E.FIN;
  cx.fillStyle = OR; cx.fillRect(0, 0, W, H);
  // karta przepisu
  const p = eo(lt / 0.5);
  cx.save(); cx.translate(0, 80 * (1 - p)); cx.globalAlpha = p;
  cx.fillStyle = PAPER; cx.beginPath(); cx.roundRect(BX, 330, BW, 760, 40); cx.fill();
  cx.drawImage(IM.logoB, CXM - 210, 380, 420, 420 * IM.logoB.height / IM.logoB.width);
  const rows = [['czas', '2 h'], ['koszt', '300 zł brutto'], ['sprzęt', 'w cenie'], ['trudność', 'bardzo łatwa']];
  rows.forEach(([a, b], i) => { const y = 600 + i * 110; serif(a + ':', BX + 70, y, 56, '#6B5E52'); txt(b, SAFE.R - 70, y, { font: '58px Blk', col: i === 1 ? TOM : INK, al: 'right' });
    if (i < 3) { cx.fillStyle = '#E3D3BF'; cx.fillRect(BX + 70, y + 52, BW - 140, 3); } });
  cx.restore();
  txt('Wpadnij do studia', CXM, 1210, { font: '64px Blk', col: BK, al: 'center', a: clamp((lt - 0.7) / 0.3) });
  txt('i nagraj, co chcesz!', CXM, 1290, { font: '64px Blk', col: '#fff', al: 'center', a: clamp((lt - 0.85) / 0.3) });
  txt('gadkastudio.pl · Warszawa', CXM, 1440, { font: '52px XB', col: BK, al: 'center', a: clamp((lt - 1.2) / 0.3) });
}

window.renderAt = async function (t) {
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.globalAlpha = 1;
  const order = [['hook', 0, hook], ['ING', E.ING, ingredients], ['STEPS', E.STEPS, steps], ['SERVE', E.SERVE, serve], ['FIN', E.FIN, finale]];
  let i = 0; while (i + 1 < order.length && t >= order[i + 1][1]) i++;
  const lt = t - order[i][1], iris = i > 0 ? eio(lt / 0.45) : 1;
  if (iris < 1) order[i - 1][2](t);
  cx.save();
  if (iris < 1) { cx.beginPath(); cx.arc(i % 2 ? W : 0, i === 4 ? H : 0, 2300 * iris, 0, 7); cx.clip(); }
  order[i][2](t);
  cx.restore();
  grain(t, 0.06);
  if (window.SAFE_BOX) { cx.strokeStyle = '#00E5FF'; cx.lineWidth = 6; cx.strokeRect(SAFE.L, SAFE.T, SAFE.R - SAFE.L, SAFE.B - SAFE.T); }
  if (t > D.TOTAL - 0.4) { cx.fillStyle = `rgba(0,0,0,${clamp((t - D.TOTAL + 0.4) / 0.4)})`; cx.fillRect(0, 0, W, H); }
};

// okładka – kwadrat y 420–1500, x 100–980
window.renderCover = function () {
  cx.setTransform(1, 0, 0, 1, 0, 0); paperBg(1);
  txt('PRZEPIS NA', 100, 490, { font: '60px XB', col: TOM, sp: 8 });
  serif('podcast,', 92, 640, 180, INK); serif('który wreszcie', 100, 790, 86, INK); serif('wyjdzie.', 100, 880, 86, OLV);
  cx.save(); cx.translate(540, 990); cx.scale(0.56, 0.56); pot(1.0, 0, 330); cx.restore();
  cx.save(); cx.translate(540, 1395); cx.rotate(-0.05); cx.strokeStyle = TOM; cx.lineWidth = 8; cx.beginPath(); cx.roundRect(-380, -70, 760, 140, 20); cx.stroke();
  txt('NIE W KUCHNI!', 0, 4, { font: '72px Blk', col: TOM, al: 'center' }); cx.restore();
  cx.drawImage(IM.logoB, 980 - 200, 470, 200, 200 * IM.logoB.height / IM.logoB.width);
  grain(0.3, 0.06);
};
