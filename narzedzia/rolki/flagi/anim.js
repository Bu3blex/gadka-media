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

// ---------- ROLKA: „Red flags vs green flags” – dla 18–30
const E = D.E;
const REDBG = '#FF2E2E', RED2 = '#D91E1E', GRN = '#D7FF3A', GRN2 = '#B6E000', BX = SAFE.L, BW = SAFE.R - SAFE.L, CXM = 540;

function stripes(t, c1, c2) {
  cx.fillStyle = c1; cx.fillRect(0, 0, W, H);
  cx.save(); cx.fillStyle = c2; const off = (t * 120) % 160;
  for (let i = -20; i < 30; i++) { const x = i * 160 + off; cx.beginPath(); cx.moveTo(x, 0); cx.lineTo(x + 70, 0); cx.lineTo(x + 70 - 900, H); cx.lineTo(x - 900, H); cx.fill(); }
  cx.restore();
}
// powiewająca flaga
function flag(x, y, s, col, t) {
  cx.save(); cx.translate(x, y); cx.scale(s, s);
  cx.fillStyle = BK; cx.beginPath(); cx.roundRect(-10, -20, 20, 330, 10); cx.fill();
  cx.beginPath();
  const w = 230, h = 150;
  for (let i = 0; i <= 20; i++) { const xx = 10 + w * i / 20, yy = -10 + Math.sin(i / 20 * Math.PI * 2 - t * 7) * 14 * (i / 20); i ? cx.lineTo(xx, yy) : cx.moveTo(xx, yy); }
  for (let i = 20; i >= 0; i--) { const xx = 10 + w * i / 20, yy = -10 + h + Math.sin(i / 20 * Math.PI * 2 - t * 7) * 14 * (i / 20); cx.lineTo(xx, yy); }
  cx.closePath(); cx.fillStyle = col; cx.fill(); cx.lineWidth = 9; cx.strokeStyle = BK; cx.stroke();
  cx.restore();
}
// karta neo-brutal: biała, gruby obrys, przesunięty cień
function brutalCard(x, y, w, h, rot, sc, fill = '#fff') {
  cx.save(); cx.translate(x + w / 2, y + h / 2); cx.rotate(rot); cx.scale(sc, sc);
  cx.fillStyle = BK; cx.beginPath(); cx.roundRect(-w / 2 + 18, -h / 2 + 18, w, h, 28); cx.fill();
  cx.fillStyle = fill; cx.beginPath(); cx.roundRect(-w / 2, -h / 2, w, h, 28); cx.fill(); cx.lineWidth = 8; cx.strokeStyle = BK; cx.stroke();
  return () => cx.restore();
}
function sticker(s, x, y, bg, fg, size, rot, sc = 1) {
  cx.save(); cx.translate(x, y); cx.rotate(rot); cx.scale(sc, sc);
  cx.font = `${size}px Blk`; const w = cx.measureText(s).width + size * 1.1, h = size * 1.7;
  cx.fillStyle = BK; cx.beginPath(); cx.roundRect(-w / 2 + 10, -h / 2 + 10, w, h, 18); cx.fill();
  cx.fillStyle = bg; cx.beginPath(); cx.roundRect(-w / 2, -h / 2, w, h, 18); cx.fill(); cx.lineWidth = 6; cx.strokeStyle = BK; cx.stroke();
  txt(s, 0, 3, { font: `${size}px Blk`, col: fg, al: 'center' }); cx.restore();
}
const RED = [
  ['nagrywa telefonem', 'w łazience', '„bo akustyka spoko”'],
  ['„wrzucę odcinek', 'jutro”', 'mówi od 8 miesięcy'],
  ['mikrofon', 'za 49 zł', 'echo gratis'],
  ['ma 37 wersji intro', '', 'i 0 odcinków'],
];
const GREEN = [
  ['rezerwuje 2 h', 'w studiu', 'zamiast scrollować 2 h', null],
  ['nagrywa na', '2× kamera 4K', 'i mikrofony Shure', '056'],
  ['wychodzi', 'z plikami', 'od ręki, na SSD', '104'],
  ['płaci 300 zł', 'brutto', 'sprzęt w cenie', null],
];
function flagCard(list, i, lt, dur, green, t) {
  const [a, b, sub, ph] = list[i];
  const slam = ob(lt / 0.28, 2.2), shake = Math.sin(lt * 60) * 10 * clamp(1 - lt / 0.25);
  const rot = (i % 2 ? 0.035 : -0.035);
  const out = clamp((lt - dur + 0.18) / 0.18); // wylot
  const h = ph ? 940 : 560, y = ph ? 450 : 640;
  cx.save(); cx.translate(shake + out * (i % 2 ? 1200 : -1200), 0);
  const end = brutalCard(BX, y, BW, h, rot, 1.25 - 0.25 * slam);
  txt(`${green ? 'GREEN' : 'RED'} FLAG #${i + 1}`, -BW / 2 + 50, -h / 2 + 75, { font: '40px Blk', col: green ? '#3C8A00' : RED2, sp: 2 });
  flag(BW / 2 - 140, -h / 2 + 50, 0.42, green ? GRN : REDBG, t);
  let yy = -h / 2 + (ph ? 200 : 230);
  txt(a, -BW / 2 + 50, yy, { font: '70px Blk', col: BK }); if (b) { yy += 84; txt(b, -BW / 2 + 50, yy, { font: '70px Blk', col: BK }); }
  yy += 88; txt(sub, -BW / 2 + 50, yy, { font: 'italic 600 50px Lora', col: '#555' });
  if (ph) photo(ph, -BW / 2 + 50, yy + 55, BW - 100, h / 2 - 45 - (yy + 55), lt / 3, 0.5, 0.5, 20);
  end(); cx.restore();
}

window.renderAt = async function (t) {
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.globalAlpha = 1;
  if (t < E.R) { // hak
    stripes(t, REDBG, RED2);
    flag(220, 500, 0.9 * ob(t / 0.4, 2), REDBG, t);
    if (t > 0.15) { const s = ob((t - 0.15) / 0.3, 2.5); cx.save(); cx.translate(CXM, 1060); cx.rotate(-0.05); cx.scale(s, s);
      cx.font = '230px Blk'; cx.textAlign = 'center'; cx.textBaseline = 'middle'; cx.lineWidth = 10; cx.strokeStyle = BK; cx.fillStyle = '#fff';
      cx.fillText('RED', 0, -120); cx.strokeText('RED', 0, -120); cx.fillText('FLAGS', 0, 100); cx.strokeText('FLAGS', 0, 100); cx.restore(); }
    if (t > 0.7) sticker('u kogoś, kto „robi podcast”', CXM, 1400, '#fff', BK, 46, 0.04, ob((t - 0.7) / 0.3, 2.5));
  } else if (t < E.SW) { // czerwone flagi
    stripes(t, REDBG, RED2);
    const k = Math.min(3, Math.floor((t - E.R) / E.RD)); flagCard(RED, k, t - E.R - k * E.RD, E.RD, false, t);
  } else if (t < E.G) { // zmiana
    const lt = t - E.SW, p = eio(lt / 0.5);
    stripes(t, lt < 0.5 ? REDBG : GRN, lt < 0.5 ? RED2 : GRN2);
    cx.save(); cx.beginPath(); cx.arc(CXM, 900, 2300 * p, 0, 7); cx.clip(); stripes(t, GRN, GRN2); cx.restore();
    kin('a teraz', BX, 620, 110, BK, t, E.SW + 0.1);
    flag(330, 760, 1.0, lt < 0.4 ? REDBG : GRN, t);
    if (lt > 0.45) { const s = ob((lt - 0.45) / 0.3, 2.5); cx.save(); cx.translate(CXM, 1260); cx.rotate(0.04); cx.scale(s, s);
      cx.font = '170px Blk'; cx.textAlign = 'center'; cx.textBaseline = 'middle'; cx.fillStyle = BK; cx.fillText('GREEN', 0, -90); cx.fillText('FLAGS', 0, 80); cx.restore(); }
  } else if (t < E.FIN) { // zielone flagi
    stripes(t, GRN, GRN2);
    const k = Math.min(3, Math.floor((t - E.G) / E.GD)); flagCard(GREEN, k, t - E.G - k * E.GD, E.GD, true, t);
  } else { // finał
    const lt = t - E.FIN;
    cx.fillStyle = OR; cx.fillRect(0, 0, W, H);
    flag(200, 470, 0.8, GRN, t);
    kin('Bądź', BX + 250, 560, 110, BK, t, E.FIN + 0.05);
    kin('green flagiem.', BX, 720, 100, '#fff', t, E.FIN + 0.2);
    if (lt > 0.7) { cx.save(); cx.globalAlpha = clamp((lt - 0.7) / 0.3); cx.drawImage(IM.logoB, CXM - 220, 850, 440, 440 * IM.logoB.height / IM.logoB.width); cx.restore(); }
    if (lt > 1.0) sticker('2 h · 300 zł brutto', CXM, 1130, '#fff', BK, 64, -0.03, ob((lt - 1.0) / 0.3, 2.4));
    txt('Wpadnij do studia', CXM, 1300, { font: '58px Blk', col: BK, al: 'center', a: clamp((lt - 1.3) / 0.3) });
    txt('i nagraj, co chcesz!', CXM, 1370, { font: '58px Blk', col: BK, al: 'center', a: clamp((lt - 1.3) / 0.3) });
    txt('gadkastudio.pl · Warszawa', CXM, 1500, { font: '48px XB', col: '#fff', al: 'center', a: clamp((lt - 1.6) / 0.3) });
  }
  grain(t, 0.06);
  if (window.SAFE_BOX) { cx.strokeStyle = '#00E5FF'; cx.lineWidth = 6; cx.strokeRect(SAFE.L, SAFE.T, SAFE.R - SAFE.L, SAFE.B - SAFE.T); }
  if (t > D.TOTAL - 0.4) { cx.fillStyle = `rgba(0,0,0,${clamp((t - D.TOTAL + 0.4) / 0.4)})`; cx.fillRect(0, 0, W, H); }
};

// okładka – kwadrat y 420–1500, x 100–980
window.renderCover = function () {
  cx.setTransform(1, 0, 0, 1, 0, 0);
  cx.fillStyle = REDBG; cx.fillRect(0, 0, W, 960); cx.fillStyle = GRN; cx.fillRect(0, 960, W, 960);
  cx.fillStyle = BK; cx.fillRect(0, 952, W, 16);
  flag(170, 520, 0.95, REDBG, 0.3); flag(760, 1060, 0.95, GRN, 1.1);
  cx.save(); cx.font = '150px Blk'; cx.textBaseline = 'middle'; cx.lineWidth = 8; cx.strokeStyle = BK; cx.fillStyle = '#fff';
  cx.fillText('RED', 430, 640); cx.strokeText('RED', 430, 640); cx.fillText('FLAGS', 100, 820); cx.strokeText('FLAGS', 100, 820);
  cx.fillStyle = BK; cx.fillText('GREEN', 100, 1150); cx.fillText('FLAGS', 100, 1320); cx.restore();
  sticker('podcast edition', 690, 1430, '#fff', BK, 44, -0.04);
};
