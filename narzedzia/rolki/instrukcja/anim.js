// Instrukcja nagrania podcastu – model GADKA
const D = window.DATA;
const cv = document.getElementById('c'), cx = cv.getContext('2d');
const W = 1080, H = 1920, PAPER = '#FAF9F5', K = '#111', OR = '#FF592A';
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const eo = x => 1 - Math.pow(1 - clamp(x), 3);
const eio = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const ob = (x, k = 1.8) => { x = clamp(x); const c3 = k + 1; return 1 + c3 * Math.pow(x - 1, 3) + k * Math.pow(x - 1, 2); };

const IM = {}; let pending = 0;
function done() { if (--pending === 0) window.READY = true; }
pending++; const lg = new Image(); lg.onload = done; lg.src = 'logo_black.png'; IM.logo = lg;
pending++;
Promise.all([['Semi', 'SemiBold'], ['XB', 'ExtraBold'], ['Blk', 'Black'], ['Light', 'Light']].map(([n, u]) => new FontFace(n, `url(fonts/InterDisplay-${u}.otf)`).load().then(f => document.fonts.add(f)))).then(done);

function txt(s, x, y, o) {
  o = Object.assign({ f: 'XB', sz: 60, col: K, sp: 0, a: 1, al: 'center' }, o);
  if (o.a <= 0) return;
  cx.save(); cx.globalAlpha *= o.a; cx.font = `${o.sz}px ${o.f}`; cx.fillStyle = o.col; cx.letterSpacing = o.sp + 'px';
  cx.textAlign = o.al; cx.textBaseline = 'middle'; cx.fillText(s, x, y); cx.restore();
}
// ---------- rysik
const LW = 7;
function st() { cx.lineWidth = LW; cx.strokeStyle = K; cx.lineCap = 'round'; cx.lineJoin = 'round'; }
function ln(...p) { st(); cx.beginPath(); p.forEach(([x, y], i) => i ? cx.lineTo(x, y) : cx.moveTo(x, y)); cx.stroke(); }
function circ(x, y, r, fill = '#fff') { st(); cx.beginPath(); cx.arc(x, y, r, 0, 7); if (fill) { cx.fillStyle = fill; cx.fill(); } cx.stroke(); }
function box(x, y, w, h, r = 8, fill = '#fff') { st(); cx.beginPath(); cx.roundRect(x, y, w, h, r); if (fill) { cx.fillStyle = fill; cx.fill(); } cx.stroke(); }
// odsłanianie elementu „rysowanego” – wycieranie od lewej + pop
function reveal(t, t0, bx, fn, dur = 0.35) {
  if (t < t0) return;
  const p = eo((t - t0) / dur);
  cx.save(); cx.beginPath(); cx.rect(bx[0] - 30, bx[1] - 30, (bx[2] + 60) * p, bx[3] + 60); cx.clip(); fn(); cx.restore();
}

// ---------- ludzik (stopy w 0,0; wysokość ~300)
function person(x, y, s, o = {}) {
  const pose = o.pose || 'stand', face = o.face || 'smile';
  cx.save(); cx.translate(x, y); cx.scale(s * (o.flip ? -1 : 1), s);
  if (pose === 'sit') {
    ln([-20, -110], [-20, -60], [40, -60], [40, 0]); ln([20, -110], [20, -60], [75, -60], [75, 0]);
  } else if (pose === 'walk') {
    ln([-15, -110], [-45, 0]); ln([15, -110], [40, -10], [55, 0]);
  } else { ln([-20, -110], [-25, 0]); ln([20, -110], [25, 0]); }
  // tułów
  st(); cx.beginPath(); cx.moveTo(-42, -105); cx.bezierCurveTo(-50, -200, -40, -235, 0, -235); cx.bezierCurveTo(40, -235, 50, -200, 42, -105); cx.closePath(); cx.fillStyle = '#fff'; cx.fill(); cx.stroke();
  // ręce
  const A = o.arms || (pose === 'happy' ? 'up' : 'down');
  if (A === 'up') { ln([-38, -200], [-90, -270]); ln([38, -200], [90, -270]); }
  else if (A === 'front') { ln([-38, -195], [10, -160], [60, -175]); ln([38, -195], [70, -165]); }
  else if (A === 'talk') { ln([38, -195], [80, -150], [110, -190]); ln([-38, -195], [-50, -130]); }
  else if (A === 'give') { ln([38, -195], [100, -175]); ln([-38, -195], [-50, -130]); }
  else { ln([-38, -195], [-55, -120]); ln([38, -195], [55, -120]); }
  // głowa
  const hy = pose === 'sad' ? -282 : -290, tilt = pose === 'sad' ? 0.25 : 0;
  cx.save(); cx.translate(0, hy); cx.rotate(tilt);
  circ(0, 0, 46);
  cx.fillStyle = K; cx.beginPath(); cx.arc(-15, -6, 5, 0, 7); cx.arc(15, -6, 5, 0, 7); cx.fill();
  st(); cx.lineWidth = 5; cx.beginPath();
  if (face === 'smile') cx.arc(0, 8, 16, 0.15 * Math.PI, 0.85 * Math.PI);
  else if (face === 'big') { cx.arc(0, 6, 18, 0, Math.PI); cx.closePath(); cx.fillStyle = K; cx.fill(); }
  else cx.arc(0, 30, 16, 1.2 * Math.PI, 1.8 * Math.PI);
  cx.stroke();
  if (o.phones) { st(); cx.beginPath(); cx.arc(0, 0, 56, Math.PI * 1.05, Math.PI * 1.95); cx.stroke(); box(-62, -12, 18, 34, 6, K); box(44, -12, 18, 34, 6, K); }
  cx.restore();
  cx.restore();
}
function mic(x, y, s, rot = 0) { cx.save(); cx.translate(x, y); cx.rotate(rot); cx.scale(s, s); box(-22, -70, 44, 90, 22, '#fff'); for (let i = 0; i < 3; i++) ln([-14, -50 + i * 16], [14, -50 + i * 16]); ln([0, 20], [0, 45]); cx.restore(); }
function micArm(x0, y0, x1, y1) { ln([x0, y0], [x0, y0 - 140], [x1, y1 + 50]); mic(x1, y1 + 10, 0.8, 0.5 * Math.sign(x1 - x0)); }
function camera(x, y, s) {
  cx.save(); cx.translate(x, y); cx.scale(s, s);
  ln([0, -150], [-55, 0]); ln([0, -150], [55, 0]); ln([0, -150], [0, 0]);
  box(-60, -230, 120, 80, 12); box(60, -215, 40, 50, 6); circ(0, -190, 24); circ(0, -190, 8, K);
  cx.restore();
}
function light(x, y, s) {
  cx.save(); cx.translate(x, y); cx.scale(s, s);
  ln([0, -260], [-45, 0]); ln([0, -260], [45, 0]); ln([0, -260], [0, -300]);
  st(); cx.beginPath(); cx.moveTo(-70, -390); cx.lineTo(70, -390); cx.lineTo(40, -300); cx.lineTo(-40, -300); cx.closePath(); cx.fillStyle = '#fff'; cx.fill(); cx.stroke();
  cx.restore();
}
function table(x, y, w = 360) { box(x - w / 2, y - 130, w, 20, 6); ln([x - w / 2 + 40, y - 110], [x - w / 2 + 40, y]); ln([x + w / 2 - 40, y - 110], [x + w / 2 - 40, y]); }
function chair(x, y, flip) { const f = flip ? -1 : 1; ln([x - 50 * f, y - 230], [x - 50 * f, y - 70], [x + 30 * f, y - 70]); ln([x - 40 * f, y - 70], [x - 40 * f, y]); ln([x + 20 * f, y - 70], [x + 20 * f, y]); }
function fridge(x, y, s) { cx.save(); cx.translate(x, y); cx.scale(s, s); box(-70, -340, 140, 340, 14); ln([-70, -230], [70, -230]); ln([45, -300], [45, -260]); ln([45, -200], [45, -140]); cx.restore(); }
function waves(x, y, s, t, n = 3, dir = 1) {
  cx.save(); cx.translate(x, y); cx.scale(s * dir, s); st(); cx.lineWidth = 5;
  for (let i = 0; i < n; i++) { const r = 20 + i * 22 + (t * 30) % 22; cx.globalAlpha = 1 - (r - 20) / (n * 22 + 22); cx.beginPath(); cx.arc(0, 0, r, -0.6, 0.6); cx.stroke(); }
  cx.restore();
}
function ssd(x, y, s) { cx.save(); cx.translate(x, y); cx.scale(s, s); box(-55, -80, 110, 160, 12); box(-30, -55, 60, 26, 4, OR); txt('SSD', 0, 30, { sz: 30 }); cx.restore(); }
function clock(x, y, s, t = 0) { cx.save(); cx.translate(x, y); cx.scale(s, s); circ(0, 0, 60); const a = t * 3; ln([0, 0], [0, -40]); ln([0, 0], [32 * Math.cos(a), 32 * Math.sin(a)]); cx.restore(); }
function headphones(x, y, s) { cx.save(); cx.translate(x, y); cx.scale(s, s); st(); cx.beginPath(); cx.arc(0, 0, 55, Math.PI, 0); cx.stroke(); box(-72, -10, 30, 56, 10, K); box(42, -10, 30, 56, 10, K); cx.restore(); }
function badge(x, y, ok, p) { // ✓ / ✕ w kółku
  const s = ob(p, 2.6); if (p <= 0) return;
  cx.save(); cx.translate(x, y); cx.scale(s, s);
  cx.fillStyle = ok ? '#fff' : OR; cx.strokeStyle = ok ? K : OR; cx.lineWidth = 9;
  cx.beginPath(); cx.arc(0, 0, 70, 0, 7); cx.fill(); cx.stroke();
  cx.lineCap = 'round'; cx.lineWidth = 16; cx.strokeStyle = ok ? K : '#fff'; cx.beginPath();
  if (ok) { cx.moveTo(-32, 2); cx.lineTo(-8, 28); cx.lineTo(34, -26); } else { cx.moveTo(-26, -26); cx.lineTo(26, 26); cx.moveTo(26, -26); cx.lineTo(-26, 26); }
  cx.stroke(); cx.restore();
}
function stepNum(n, x, y, t, t0) { const p = ob((t - t0) / 0.3, 2.2); if (t < t0) return; cx.save(); cx.translate(x, y); cx.scale(p, p); txt(String(n), 0, 0, { f: 'Blk', sz: 150 }); cx.restore(); }
function bubble(x, y, w, h, t, t0) {
  if (t < t0) return; const s = ob((t - t0) / 0.3, 2);
  cx.save(); cx.translate(x, y); cx.scale(s, s); box(-w / 2, -h / 2, w, h, 30);
  st(); cx.beginPath(); cx.moveTo(-20, h / 2); cx.lineTo(-40, h / 2 + 34); cx.lineTo(10, h / 2); cx.fillStyle = '#fff'; cx.fill(); cx.stroke();
  cx.fillStyle = '#fff'; cx.fillRect(-18, h / 2 - 6, 26, 10);
  st(); cx.lineWidth = 6; for (let i = 0; i < 2; i++) { cx.beginPath(); for (let k = 0; k <= 20; k++) { const xx = -w / 2 + 30 + k * (w - 60) / 20, yy = -14 + i * 28 + Math.sin(k * 1.3 + t * 8) * 5; k ? cx.lineTo(xx, yy) : cx.moveTo(xx, yy); } cx.stroke(); }
  cx.restore();
}
function footer(page) {
  txt('GADKA · AA-300', 60, 1800, { f: 'Semi', sz: 28, al: 'left', col: '#777', sp: 2 });
  txt(page + '/6', 1020, 1800, { f: 'XB', sz: 34, al: 'right' });
}

// ---------- strony
const PAGES = [
  (t) => { // okładka
    cx.drawImage(IM.logo, 540 - 330, 190, 660, 660 * 510 / 1400);
    txt('INSTRUKCJA NAGRANIA', 540, 520, { f: 'Blk', sz: 70, sp: 1, a: clamp(t / 0.15) });
    txt('PODCASTU', 540, 610, { f: 'Blk', sz: 70, sp: 1, a: clamp((t - 0.1) / 0.15) });
    const g = 1420;
    cx.save(); cx.translate(540, 1440); cx.scale(1.3, 1.3); cx.translate(-540, -1420);
    reveal(t, 0.25, [140, 1000, 800, 420], () => { light(220, g, 1.0); });
    reveal(t, 0.45, [330, 1100, 420, 330], () => { chair(390, g, false); chair(690, g, true); person(400, g, 0.95, { pose: 'sit' }); person(680, g, 0.95, { pose: 'sit', flip: true }); table(540, g, 300); micArm(500, g - 130, 482, g - 250); micArm(580, g - 130, 598, g - 250); });
    reveal(t, 0.7, [800, 1150, 200, 280], () => camera(880, g, 0.9));
    ln([170, g + 6], [910, g + 6]);
    cx.restore();
    // ikony na okładce
    reveal(t, 1.0, [150, 1560, 800, 160], () => {
      clock(260, 1640, 0.8, 1.2); txt('2 h', 360, 1640, { f: 'Blk', sz: 64, al: 'left' });
      txt('·', 540, 1640, { f: 'Blk', sz: 64 });
      txt('300 zł', 610, 1640, { f: 'Blk', sz: 64, al: 'left', col: OR });
    });
    footer(1);
  },
  (t) => { // źle / dobrze
    txt('ZANIM ZACZNIESZ', 540, 210, { f: 'Blk', sz: 60, sp: 2 });
    box(70, 290, 940, 690, 30, '#fff'); box(70, 1020, 940, 690, 30, '#fff');
    const g1 = 890, g2 = 1620;
    reveal(t, 0.15, [100, 330, 880, 600], () => {
      fridge(260, g1, 1.25); waves(360, g1 - 330, 1.3, t);
      table(620, g1, 320); person(700, g1, 1.0, { pose: 'sad', face: 'sad' });
      box(560, g1 - 175, 60, 40, 6); // telefon
      waves(790, g1 - 300, 1.2, t, 3, 1); waves(560, g1 - 300, 1.2, t, 3, -1);
      txt('BZZZ', 260, g1 - 400, { f: 'Blk', sz: 44 }); txt('echo… echo…', 830, g1 - 420, { f: 'XB', sz: 34 });
    });
    badge(900, 380, false, (t - 0.8) / 0.35);
    reveal(t, 1.6, [100, 1060, 880, 600], () => {
      light(190, g2, 0.95);
      chair(640, g2, true); person(620, g2, 1.0, { pose: 'sit', flip: true, phones: true, face: 'big', arms: 'talk' });
      table(470, g2, 260); micArm(430, g2 - 130, 505, g2 - 260); camera(880, g2, 0.85);
    });
    badge(900, 1110, true, (t - 2.3) / 0.35);
    footer(2);
  },
  (t) => { // części
    txt('W ZESTAWIE', 540, 210, { f: 'Blk', sz: 64, sp: 2 });
    const cells = [
      [() => mic(0, 30, 1.3), '2×', 'mikrofon Shure'], [() => camera(0, 110, 0.75), '2×', 'kamera 4K'],
      [() => light(0, 150, 0.6), '1×', 'światło'], [() => headphones(0, 10, 1.1), '2×', 'słuchawki'],
      [() => ssd(0, 10, 1.1), '1×', 'pliki od ręki'], [() => clock(0, 10, 1.3, t), '2 h', 'w studiu'],
    ];
    cells.forEach(([fn, q, lab], i) => {
      const x = 80 + (i % 2) * 470, y = 300 + Math.floor(i / 2) * 470, t0 = 0.2 + i * 0.4;
      if (t < t0) return;
      const s = ob((t - t0) / 0.35, 2);
      cx.save(); cx.translate(x + 210, y + 210); cx.scale(s, s); cx.translate(-(x + 210), -(y + 210));
      box(x, y, 420, 420, 26, '#fff');
      cx.save(); cx.translate(x + 210, y + 175); fn(); cx.restore();
      txt(q, x + 40, y + 60, { f: 'Blk', sz: 64, al: 'left', col: OR });
      txt(lab, x + 210, y + 365, { f: 'XB', sz: 40 });
      cx.restore();
    });
    txt('wszystko w cenie', 540, 1760, { f: 'Blk', sz: 56, col: OR, a: clamp((t - 2.8) / 0.3) });
    footer(3);
  },
  (t) => { // krok 1 i 2
    box(70, 160, 940, 780, 30, '#fff'); box(70, 980, 940, 780, 30, '#fff');
    stepNum(1, 170, 280, t, 0.1);
    reveal(t, 0.3, [180, 350, 720, 520], () => {
      box(200, 400, 680, 440, 24); ln([200, 470], [880, 470]);
      [235, 270, 305].forEach(x => circ(x, 435, 9, '#fff'));
      box(330, 420, 500, 34, 17); txt('gadkastudio.pl', 580, 438, { f: 'Semi', sz: 26 });
      txt('Rezerwuj', 540, 600, { f: 'XB', sz: 40, a: 0 });
    });
    if (t > 0.6) {
      const press = t > 1.45 && t < 1.65;
      box(370, 620, 340, 100, 50, press ? K : OR);
      txt('REZERWUJ', 540, 672, { f: 'Blk', sz: 44, col: '#fff' });
      // kursor
      const p = eio((t - 0.7) / 0.7), cxp = 800 - 180 * p, cyp = 820 - 120 * p;
      cx.save(); cx.translate(cxp, cyp); cx.scale(press ? 0.9 : 1, press ? 0.9 : 1); cx.fillStyle = '#fff'; st();
      cx.beginPath(); cx.moveTo(0, 0); cx.lineTo(0, 70); cx.lineTo(18, 54); cx.lineTo(32, 84); cx.lineTo(44, 78); cx.lineTo(30, 49); cx.lineTo(54, 48); cx.closePath(); cx.fill(); cx.stroke(); cx.restore();
    }
    stepNum(2, 170, 1100, t, 1.9);
    const g = 1690;
    reveal(t, 2.1, [150, 1150, 800, 560], () => {
      box(700, g - 420, 200, 420, 10); circ(865, g - 210, 10, K); txt('GADKA', 800, g - 370, { f: 'Blk', sz: 34 });
      ln([120, g], [960, g]);
    });
    if (t > 2.4) {
      const p = eio((t - 2.4) / 1.1), x = 230 + 380 * p;
      person(x, g, 0.95, { pose: Math.floor(t * 6) % 2 ? 'walk' : 'stand', face: 'big' });
      if (t > 2.4) for (let i = 0; i < 3; i++) ln([x - 90 - i * 10, g - 220 + i * 50], [x - 150 - i * 10, g - 220 + i * 50]);
    }
    txt('Warszawa', 330, 1270, { f: 'XB', sz: 44, a: clamp((t - 2.6) / 0.3) });
    footer(4);
  },
  (t) => { // krok 3 i 4
    box(70, 160, 940, 900, 30, '#fff'); box(70, 1100, 940, 660, 30, '#fff');
    stepNum(3, 170, 280, t, 0.1);
    const g = 960;
    reveal(t, 0.3, [100, 380, 880, 600], () => {
      chair(330, g, false); chair(750, g, true);
      person(340, g, 0.95, { pose: 'sit', phones: true, face: 'big', arms: 'talk' });
      person(740, g, 0.95, { pose: 'sit', phones: true, flip: true, face: 'smile' });
      table(540, g, 320); micArm(470, g - 130, 430, g - 255); micArm(610, g - 130, 650, g - 255);
    });
    bubble(260, 470, 260, 120, t, 0.9); bubble(800, 450, 260, 120, t, 1.5);
    // nagrywanie
    if (t > 0.9 && Math.floor(t * 2) % 2 === 0) { cx.fillStyle = OR; cx.beginPath(); cx.arc(860, 230, 18, 0, 7); cx.fill(); txt('REC', 890, 232, { f: 'Blk', sz: 36, al: 'left', col: OR }); }
    stepNum(4, 170, 1220, t, 2.2);
    const g2 = 1700;
    reveal(t, 2.4, [250, 1250, 700, 460], () => {
      person(780, g2, 0.95, { pose: 'happy', face: 'big' });
    });
    if (t > 2.6) {
      const p = eio((t - 2.6) / 0.6);
      ssd(380 + 260 * p, 1480 - 40 * Math.sin(p * Math.PI), 1.0);
      ln([300, 1600], [560, 1600]); ln([520, 1575], [560, 1600], [520, 1625]);
    }
    txt('pliki od ręki', 400, 1310, { f: 'XB', sz: 46, a: clamp((t - 2.9) / 0.3) });
    footer(5);
  },
  (t) => { // gotowe
    const g = 980;
    reveal(t, 0.05, [300, 520, 480, 500], () => person(540, g, 1.45, { pose: 'happy', face: 'big' }));
    for (let i = 0; i < 6; i++) { // gwiazdki
      const a = i / 6 * Math.PI * 2 + 0.3, p = eo((t - 0.4 - i * 0.05) / 0.4), r = 300 + 40 * Math.sin(t * 3 + i);
      if (p <= 0) continue;
      cx.save(); cx.translate(540 + r * Math.cos(a) * p, 640 + r * 0.8 * Math.sin(a) * p); cx.rotate(t * 2 + i); cx.fillStyle = i % 2 ? OR : K;
      cx.beginPath(); for (let k = 0; k < 10; k++) { const rr = k % 2 ? 12 : 30; cx.lineTo(rr * Math.cos(k * Math.PI / 5), rr * Math.sin(k * Math.PI / 5)); } cx.fill(); cx.restore();
    }
    ln([300, g + 6], [780, g + 6]);
    const s = ob((t - 0.6) / 0.4, 2.4);
    cx.save(); cx.translate(540, 1150); cx.scale(s, s); txt('GOTOWE.', 0, 0, { f: 'Blk', sz: 150 }); cx.restore();
    const a = clamp((t - 1.2) / 0.3);
    box(140, 1270, 800, 250, 30, OR); cx.save(); cx.globalAlpha = a; cx.restore();
    txt('2 h w studiu · 300 zł', 540, 1350, { f: 'Blk', sz: 62, col: '#fff', a });
    txt('brutto · sprzęt w cenie', 540, 1440, { f: 'XB', sz: 48, col: '#fff', a });
    const a2 = clamp((t - 1.8) / 0.3);
    cx.save(); cx.globalAlpha = a2; cx.drawImage(IM.logo, 540 - 200, 1560, 400, 400 * 510 / 1400); cx.restore();
    txt('gadkastudio.pl', 540, 1760, { f: 'XB', sz: 50, a: a2 });
  },
];

window.renderAt = function (t) {
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.globalAlpha = 1;
  const P = D.P; let i = 0; while (i + 1 < P.length && t >= P[i + 1]) i++;
  cx.fillStyle = '#D8D4CA'; cx.fillRect(0, 0, W, H);
  // przewracanie strony: nowa wjeżdża z prawej przez 0.35 s
  const lt = t - P[i], fp = eio(lt / 0.35);
  if (i > 0 && fp < 1) {
    cx.save(); cx.translate(-300 * fp, 0); cx.fillStyle = PAPER; cx.fillRect(0, 0, W, H); PAGES[i - 1](99); cx.restore();
    cx.fillStyle = `rgba(0,0,0,${0.25 * fp})`; cx.fillRect(0, 0, W, H);
  }
  const off = i > 0 ? W * (1 - fp) : 0;
  cx.save(); cx.translate(off, 0);
  cx.shadowColor = 'rgba(0,0,0,.3)'; cx.shadowBlur = 50; cx.fillStyle = PAPER; cx.fillRect(0, 0, W, H); cx.shadowColor = 'transparent';
  PAGES[i](lt);
  cx.restore();
  if (t > D.TOTAL - 0.5) { cx.fillStyle = `rgba(0,0,0,${clamp((t - D.TOTAL + 0.5) / 0.5)})`; cx.fillRect(0, 0, W, H); }
};
