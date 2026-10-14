// Muzeum niedokończonych podcastów – Gadka studio
const D = window.DATA;
const cv = document.getElementById('c'), cx = cv.getContext('2d');
const W = 1080, H = 1920, FLOOR = 1380, OR = '#FF592A', CREAM = '#F9EEE4';
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const eo = x => 1 - Math.pow(1 - clamp(x), 3);
const eio = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
function rnd(n) { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); }

const IM = {}; let pending = 0;
function done() { if (--pending === 0) window.READY = true; }
function load(k, src) { pending++; const i = new Image(); i.onload = done; i.src = src; IM[k] = i; }
['056', '104', '034', '101', 'noise'].forEach(n => load(n, n === 'noise' ? 'img/noise.png' : `img/${n}.jpg`));
load('logoB', 'logo_black.png');
pending++;
Promise.all([...[['Semi', 'SemiBold'], ['XB', 'ExtraBold'], ['Light', 'Light'], ['Thin', 'Thin']].map(([n, u]) => new FontFace(n, `url(fonts/InterDisplay-${u}.otf)`).load().then(f => document.fonts.add(f))),
  document.fonts.load('italic 600 60px Lora'), document.fonts.load('600 60px Lora'), document.fonts.load('60px "TeX Gyre Chorus"'), document.fonts.load('60px "DejaVu Sans Mono"')]).then(done);

function txt(s, x, y, o) {
  o = Object.assign({ f: 'Semi', sz: 40, col: '#111', sp: 0, a: 1, al: 'center' }, o);
  if (o.a <= 0) return;
  cx.save(); cx.globalAlpha *= o.a; cx.font = o.font || `${o.sz}px ${o.f}`; cx.fillStyle = o.col; cx.letterSpacing = o.sp + 'px';
  cx.textAlign = o.al; cx.textBaseline = 'middle';
  if (o.glow) { cx.shadowColor = o.gcol; cx.shadowBlur = o.glow; }
  cx.fillText(s, x, y); cx.restore();
}

// ---------- kamera
const KF = D.KF; // [t, x] – przystanki (pary: przyjazd, odjazd)
function camX(t) {
  if (t <= KF[0][0]) return KF[0][1];
  for (let i = 0; i < KF.length - 1; i++) {
    const [t0, x0] = KF[i], [t1, x1] = KF[i + 1];
    if (t >= t0 && t <= t1) return x0 === x1 ? x0 : x0 + (x1 - x0) * eio((t - t0) / (t1 - t0));
  }
  return KF[KF.length - 1][1];
}
const SPLIT = D.SPLIT; // granica sal (świat)

// ---------- tło
function hall(cam, t) {
  const sx = SPLIT - cam + 540;
  // ciemna sala
  cx.fillStyle = '#26252B'; cx.fillRect(0, 0, Math.min(W, Math.max(0, sx)), FLOOR);
  // jasna sala
  if (sx < W) { cx.fillStyle = CREAM; cx.fillRect(Math.max(0, sx), 0, W, FLOOR); }
  // listwa i podłoga
  const fg = cx.createLinearGradient(0, FLOOR, 0, H);
  fg.addColorStop(0, '#3A3633'); fg.addColorStop(1, '#141313');
  cx.fillStyle = fg; cx.fillRect(0, FLOOR, W, H - FLOOR);
  if (sx < W) {
    const g2 = cx.createLinearGradient(0, FLOOR, 0, H); g2.addColorStop(0, '#CDBBA6'); g2.addColorStop(1, '#8F7A66');
    cx.fillStyle = g2; cx.fillRect(Math.max(0, sx), FLOOR, W, H - FLOOR);
  }
  // deski w perspektywie (paralaksa)
  cx.save(); cx.strokeStyle = 'rgba(0,0,0,.18)'; cx.lineWidth = 3;
  for (let i = -30; i < 60; i++) {
    const wx = i * 220, x0 = wx - cam * 1.0 + 540, x1 = wx - cam * 1.9 + 540 * 1.9 - 540 * 0.9;
    if (Math.max(x0, x1) < -400 || Math.min(x0, x1) > W + 400) continue;
    cx.beginPath(); cx.moveTo(x0, FLOOR); cx.lineTo((wx - cam) * 2.2 + 540, H); cx.stroke();
  }
  cx.restore();
  cx.fillStyle = 'rgba(0,0,0,.35)'; cx.fillRect(0, FLOOR - 14, W, 14);
}
function spot(x, y, w, h, a = 1, warm = false) {
  const g = cx.createRadialGradient(x, y, 10, x, y, h);
  g.addColorStop(0, warm ? `rgba(255,236,200,${0.55 * a})` : `rgba(255,240,215,${0.42 * a})`);
  g.addColorStop(1, 'rgba(255,240,215,0)');
  cx.save(); cx.translate(x, y); cx.scale(w / h, 1); cx.translate(-x, -y);
  cx.fillStyle = g; cx.beginPath(); cx.arc(x, y, h, 0, 7); cx.fill(); cx.restore();
  // lampa
  cx.fillStyle = '#111'; cx.beginPath(); cx.roundRect(x - 30, -10, 60, 50, 10); cx.fill();
}
function plaque(x, y, title, sub, a = 1, dark = true) {
  if (a <= 0) return;
  cx.save(); cx.globalAlpha = a;
  cx.font = 'italic 600 56px Lora'; const w1 = cx.measureText(title).width; cx.font = '36px Semi'; const w2 = cx.measureText(sub).width;
  const w = Math.max(w1, w2) + 80;
  cx.fillStyle = dark ? '#EDE7DD' : '#fff'; cx.shadowColor = 'rgba(0,0,0,.35)'; cx.shadowBlur = 20; cx.shadowOffsetY = 6;
  cx.fillRect(x - w / 2, y - 85, w, 170); cx.shadowColor = 'transparent';
  txt(title, x, y - 24, { font: 'italic 600 56px Lora', col: '#161616' });
  txt(sub, x, y + 42, { f: 'Semi', sz: 36, col: '#6B6157' });
  cx.restore();
}
function guide(n, s, t, t0, t1, dark = true) {
  if (t < t0 || t > t1) return;
  const a = clamp((t - t0) / 0.3) * clamp((t1 - t) / 0.25);
  cx.save(); cx.globalAlpha = a;
  const y = 1590 + 20 * (1 - eo((t - t0) / 0.4));
  cx.fillStyle = dark ? 'rgba(0,0,0,.6)' : 'rgba(255,255,255,.75)'; cx.beginPath(); cx.roundRect(70, y - 95, 940, 200, 30); cx.fill();
  cx.fillStyle = dark ? CREAM : '#111'; cx.beginPath(); cx.roundRect(110, y - 62, 140, 60, 30); cx.fill();
  txt('🎧 ' + String(n).padStart(2, '0'), 180, y - 31, { f: 'XB', sz: 30, col: dark ? '#111' : CREAM });
  // wypisywanie
  const n2 = Math.ceil(clamp((t - t0 - 0.2) / 1.0) * s.length);
  txt(s.slice(0, n2), 110, y + 45, { font: 'italic 500 47px Lora', col: dark ? CREAM : '#111', al: 'left' });
  cx.restore();
}
function pedestal(x, top, w = 360) {
  const g = cx.createLinearGradient(x - w / 2, 0, x + w / 2, 0); g.addColorStop(0, '#E9E5DE'); g.addColorStop(1, '#BDB7AD');
  cx.fillStyle = g; cx.fillRect(x - w / 2, top, w, FLOOR + 40 - top);
  cx.fillStyle = '#F6F3EE'; cx.fillRect(x - w / 2 - 12, top - 16, w + 24, 18);
}
function frame(x, y, w, h, fill = '#fff', fr = '#111', fw = 24) {
  cx.save(); cx.shadowColor = 'rgba(0,0,0,.5)'; cx.shadowBlur = 30; cx.shadowOffsetY = 14;
  cx.fillStyle = fr; cx.fillRect(x - w / 2 - fw, y - h / 2 - fw, w + 2 * fw, h + 2 * fw); cx.restore();
  cx.fillStyle = fill; cx.fillRect(x - w / 2, y - h / 2, w, h);
}

// ---------- eksponaty (x = pozycja na ekranie)
function ex1(x, t) { // mikrofon w kartonie
  spot(x, 0, 380, 1250);
  pedestal(x, 1000);
  cx.save(); cx.translate(x, 740); cx.scale(1.35, 1.35);
  cx.fillStyle = '#B8875A'; cx.fillRect(-150, -170, 300, 360); cx.fillStyle = '#A2734A'; cx.fillRect(-150, -170, 300, 40);
  cx.fillStyle = '#F2EBDD'; cx.fillRect(-110, -110, 220, 230);
  // mikrofon na pudełku
  cx.fillStyle = '#222'; cx.beginPath(); cx.roundRect(-35, -90, 70, 130, 35); cx.fill(); cx.fillRect(-8, 40, 16, 50); cx.fillRect(-45, 88, 90, 14);
  cx.strokeStyle = '#555'; cx.lineWidth = 4; for (let i = 0; i < 4; i++) { cx.beginPath(); cx.moveTo(-28, -70 + i * 20); cx.lineTo(28, -70 + i * 20); cx.stroke(); }
  txt('USB MIC', 0, 150, { f: 'XB', sz: 30, col: '#222', sp: 3 });
  // folia – połysk
  const sh = cx.createLinearGradient(-150, -170, 150, 190); sh.addColorStop(0.3, 'rgba(255,255,255,0)'); sh.addColorStop(0.45 + 0.05 * Math.sin(t * 2), 'rgba(255,255,255,.45)'); sh.addColorStop(0.6, 'rgba(255,255,255,0)');
  cx.fillStyle = sh; cx.fillRect(-150, -170, 300, 360);
  cx.restore();
}
function ex2(x, t) { // final_final_v7.mp3
  spot(x, 0, 420, 1200);
  frame(x, 640, 560, 720, '#F4F1EA');
  cx.save(); cx.translate(x, 640);
  txt('final_final_v7.mp3', 0, -270, { font: 'bold 34px "DejaVu Sans Mono"', col: '#222' });
  cx.strokeStyle = '#222'; cx.lineWidth = 4; cx.beginPath();
  for (let i = 0; i <= 200; i++) { const xx = -230 + i * 2.3; let a = 6 * Math.sin(i * 0.9) * rnd(i); if (i > 40 && i < 60) a = 90 * Math.sin(i * 2.1); if (i > 120 && i < 130) a = 120 * Math.sin(i * 3); cx.lineTo(xx, a); }
  cx.stroke();
  txt('BZZZ', -60, -160, { f: 'XB', sz: 40, col: '#C33' }); txt('echo', 150, 170, { f: 'XB', sz: 40, col: '#C33' });
  txt('12:04', 0, 280, { font: '30px "DejaVu Sans Mono"', col: '#666' });
  cx.restore();
}
function ex3(x, t) { // lista pomysłów
  spot(x, 0, 420, 1200);
  frame(x, 640, 560, 740, '#FFFDF4', '#8A6A44', 22);
  cx.save(); cx.translate(x, 640); cx.strokeStyle = 'rgba(70,120,200,.35)'; cx.lineWidth = 2;
  for (let i = 0; i < 12; i++) { cx.beginPath(); cx.moveTo(-260, -300 + i * 56); cx.lineTo(260, -300 + i * 56); cx.stroke(); }
  cx.strokeStyle = 'rgba(220,60,60,.5)'; cx.beginPath(); cx.moveTo(-200, -360); cx.lineTo(-200, 360); cx.stroke();
  const L = ['podcast o kawie', 'o finansach', 'z kumplem', 'true crime?', 'o rowerach', 'o podcastach', 'o motywacji', 'o odkładaniu'];
  L.forEach((s, i) => {
    const y = -310 + i * 82;
    txt(s, -180, y, { font: '56px "TeX Gyre Chorus"', col: '#1C2A6E', al: 'left' });
    cx.save(); cx.font = '56px "TeX Gyre Chorus"'; const w = cx.measureText(s).width; cx.restore();
    cx.strokeStyle = '#1C2A6E'; cx.lineWidth = 4; cx.beginPath(); cx.moveTo(-185, y + 4); cx.lineTo(-175 + w, y - 2); cx.stroke();
  });
  cx.restore();
}
function ex4(x, t) { // neon „od jutra”
  const fl = (rnd(Math.floor(t * 14)) > 0.88) ? 0.35 : 1;
  const g = cx.createRadialGradient(x, 640, 20, x, 640, 520); g.addColorStop(0, `rgba(255,60,170,${0.35 * fl})`); g.addColorStop(1, 'rgba(255,60,170,0)');
  cx.fillStyle = g; cx.fillRect(x - 600, 100, 1200, 1200);
  cx.fillStyle = '#1A191E'; cx.beginPath(); cx.roundRect(x - 380, 480, 760, 330, 30); cx.fill();
  cx.strokeStyle = 'rgba(255,255,255,.12)'; cx.lineWidth = 3; cx.stroke();
  for (let k = 0; k < 3; k++) txt('od jutra', x, 640, { font: '200px "TeX Gyre Chorus"', col: fl < 1 ? '#7A2B5A' : '#FFD6EE', glow: [60, 30, 10][k] * fl, gcol: '#FF3CAA' });
  // kabel
  cx.strokeStyle = '#111'; cx.lineWidth = 6; cx.beginPath(); cx.moveTo(x + 300, 810); cx.bezierCurveTo(x + 320, 1000, x + 380, 1200, x + 420, FLOOR); cx.stroke();
}
function exitDoor(x, t) {
  cx.fillStyle = '#111'; cx.fillRect(x - 210, 560, 420, FLOOR - 560);
  const g = cx.createLinearGradient(x - 200, 0, x + 200, 0); g.addColorStop(0, '#FFF6EA'); g.addColorStop(1, '#FFE2C2');
  const op = eio((t - D.DOOR) / 0.6);
  cx.fillStyle = g; cx.fillRect(x - 190, 580, 380, FLOOR - 580);
  cx.fillStyle = '#3A3633'; cx.fillRect(x - 190, 580, 380 * (1 - op), FLOOR - 580);
  // światło zza drzwi
  if (op > 0) { const lg = cx.createRadialGradient(x, 1000, 50, x, 1000, 800); lg.addColorStop(0, `rgba(255,220,170,${0.5 * op})`); lg.addColorStop(1, 'rgba(255,220,170,0)'); cx.fillStyle = lg; cx.fillRect(x - 900, 200, 1800, 1700); }
  // znak wyjścia
  cx.fillStyle = '#0B8A43'; cx.beginPath(); cx.roundRect(x - 200, 400, 400, 120, 14); cx.fill();
  txt('WYJŚCIE', x - 40, 462, { f: 'XB', sz: 52, col: '#fff', sp: 3 });
  cx.strokeStyle = '#fff'; cx.lineWidth = 9; cx.lineCap = 'round'; cx.beginPath(); cx.moveTo(x + 110, 462); cx.lineTo(x + 165, 462); cx.moveTo(x + 145, 440); cx.lineTo(x + 167, 462); cx.lineTo(x + 145, 484); cx.stroke();
}
function photoEx(x, k, t, fx = 0.5) {
  spot(x, 0, 460, 1250, 1, true);
  const w = 760, h = 560, y = 660;
  frame(x, y, w + 60, h + 60, '#fff', '#1A1A1A', 14);
  const im = IM[k], s = Math.max(w / im.width, h / im.height);
  cx.save(); cx.beginPath(); cx.rect(x - w / 2, y - h / 2, w, h); cx.clip();
  cx.drawImage(im, x - im.width * s * fx, y - im.height * s / 2, im.width * s, im.height * s); cx.restore();
}
function finalWall(x, t, lt) {
  spot(x, 0, 520, 1300, 1, true);
  cx.drawImage(IM.logoB, x - 300, 280, 600, 600 * 510 / 1400);
  const a = clamp(lt / 0.4);
  cx.save(); cx.globalAlpha = a;
  cx.fillStyle = '#fff'; cx.shadowColor = 'rgba(0,0,0,.25)'; cx.shadowBlur = 30; cx.shadowOffsetY = 10;
  cx.fillRect(x - 420, 600, 840, 560); cx.shadowColor = 'transparent';
  txt('Twój podcast. Nagrany.', x, 690, { font: 'italic 600 54px Lora', col: '#111' });
  txt('Gadka studio · Warszawa', x, 770, { f: 'Semi', sz: 36, col: '#6B6157' });
  cx.fillStyle = '#E2D6C6'; cx.fillRect(x - 330, 820, 660, 3);
  const b = clamp((lt - 0.5) / 0.4);
  txt('2 h · 300 zł', x, 905, { f: 'XB', sz: 84, col: OR, a: b });
  txt('brutto · sprzęt w cenie', x, 990, { f: 'Semi', sz: 40, col: '#111', a: b });
  txt('wstęp: gadkastudio.pl', x, 1080, { f: 'XB', sz: 44, col: '#111', a: clamp((lt - 1.0) / 0.4) });
  cx.restore();
}

window.renderAt = function (t) {
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.globalAlpha = 1; cx.shadowColor = 'transparent';
  const cam = camX(t), X = wx => wx - cam + 540;
  hall(cam, t);
  const E = D.EX;
  // sala 1 – tytuł
  if (X(0) > -700) {
    const on = clamp((t - 0.25) / 0.1);
    spot(X(0), 0, 520 * on, 1300, on);
    txt('MUZEUM', X(0), 560, { f: 'Thin', sz: 110, col: CREAM, sp: 30, a: on });
    txt('niedokończonych', X(0), 700, { font: 'italic 600 96px Lora', col: CREAM, a: on });
    txt('podcastów', X(0), 810, { font: 'italic 600 96px Lora', col: CREAM, a: on });
    txt('ekspozycja stała · wstęp wolny', X(0), 950, { f: 'Semi', sz: 36, col: '#A9A39A', sp: 3, a: clamp((t - 0.9) / 0.4) });
  }
  const show = (wx, fn) => { const x = X(wx); if (x > -700 && x < W + 700) fn(x); };
  show(E[0], x => { ex1(x, t); plaque(x, 1180, 'Mikrofon USB, nieotwarty', '2023 · karton, folia, motywacja', 1); });
  show(E[1], x => { ex2(x, t); plaque(x, 1180, 'Pierwszy odcinek', '2024 · plik audio, wersja siódma', 1); });
  show(E[2], x => { ex3(x, t); plaque(x, 1180, 'Lista pomysłów', '2021–dziś · długopis, papier', 1); });
  show(E[3], x => { ex4(x, t); plaque(x, 1180, 'Od jutra', 'neon · czas nieokreślony', 1); });
  show(E[4], x => exitDoor(x, t));
  // sala 2
  show(E[5] - 600, x => { txt('NOWA EKSPOZYCJA', x - 0, 620, { f: 'Thin', sz: 70, col: '#111', sp: 16 }); txt('→', x, 740, { f: 'Light', sz: 90, col: OR }); });
  show(E[5], x => { photoEx(x, '056', t); plaque(x, 1180, 'Mikrofony Shure', 'stan: działają', 1, false); });
  show(E[6], x => { photoEx(x, '104', t); plaque(x, 1180, 'Dwie kamery 4K i światło', 'gotowe, zanim przyjdziesz', 1, false); });
  show(E[7], x => { photoEx(x, '034', t, 0.5); plaque(x, 1180, 'Pliki od ręki', 'na SSD, zaraz po nagraniu', 1, false); });
  show(E[8], x => finalWall(x, t, t - D.FIN));
  // audioprzewodnik
  D.G.forEach(([n, s, t0, t1, dk]) => guide(n, s, t, t0, t1, dk));
  // ciemność na starcie + klik światła
  if (t < 0.25) { cx.fillStyle = '#000'; cx.fillRect(0, 0, W, H); }
  // winieta
  const vg = cx.createRadialGradient(540, 900, 400, 540, 900, 1300); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, `rgba(0,0,0,${cam < D.SPLIT - 300 ? 0.55 : 0.2})`);
  cx.fillStyle = vg; cx.fillRect(0, 0, W, H);
  // przejście przez drzwi – jasny błysk
  const fl = clamp(1 - Math.abs(t - D.WALK) / 0.35);
  if (fl > 0) { cx.fillStyle = `rgba(255,246,232,${fl})`; cx.fillRect(0, 0, W, H); }
  if (t > D.TOTAL - 0.5) { cx.fillStyle = `rgba(0,0,0,${clamp((t - D.TOTAL + 0.5) / 0.5)})`; cx.fillRect(0, 0, W, H); }
};
