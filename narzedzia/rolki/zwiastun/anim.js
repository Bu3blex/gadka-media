// Zwiastun kinowy – Gadka studio
const D = window.DATA;
const cv = document.getElementById('c'), cx = cv.getContext('2d');
const W = 1080, H = 1920, BAR = 250;
const CREAM = '#F1E9DC', OR = '#FF592A';
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const eo = x => 1 - Math.pow(1 - clamp(x), 3);
const eio = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const ob = (x, k = 1.8) => { x = clamp(x); const c3 = k + 1; return 1 + c3 * Math.pow(x - 1, 3) + k * Math.pow(x - 1, 2); };
function rnd(n) { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); }

const IM = {};
const names = ['001', '010', '019', '022', '031', '034', '037', '050', '056', '101', '102', '104', '105'];
let pending = 0;
function load(k, src) { pending++; const i = new Image(); i.onload = () => { if (--pending === 0) start(); }; i.src = src; IM[k] = i; }
names.forEach(n => load(n, `img/${n}.jpg`));
load('noise', 'img/noise.png'); load('logo', 'logo.png');
const fonts = [['Thin', 'fonts/InterDisplay-Thin.otf'], ['Light', 'fonts/InterDisplay-Light.otf'], ['Semi', 'fonts/InterDisplay-SemiBold.otf'], ['Blk', 'fonts/InterDisplay-Black.otf']];
pending++;
Promise.all(fonts.map(([n, u]) => new FontFace(n, `url(${u})`).load().then(f => document.fonts.add(f)))).then(() => { if (--pending === 0) start(); });
function start() { window.READY = true; }

function txt(s, x, y, o) {
  o = Object.assign({ f: 'Thin', sz: 80, col: CREAM, sp: 0, a: 1, al: 'center', glow: 0, sx: 1 }, o);
  if (o.a <= 0) return;
  cx.save(); cx.globalAlpha = o.a; cx.font = `${o.sz}px ${o.f}`; cx.fillStyle = o.col;
  cx.letterSpacing = o.sp + 'px'; cx.textAlign = o.al; cx.textBaseline = 'middle';
  if (o.glow) { cx.shadowColor = o.gcol || 'rgba(255,230,200,.55)'; cx.shadowBlur = o.glow; }
  cx.translate(x + (o.al === 'center' ? o.sp / 2 * o.sx : 0), y); cx.scale(o.sx, 1);
  cx.fillText(s, 0, 0); cx.restore();
}
function tw(s, f, sz, sp) { cx.save(); cx.font = `${sz}px ${f}`; cx.letterSpacing = sp + 'px'; const w = cx.measureText(s).width; cx.restore(); return w; }

function grain(t, a = 0.13) {
  const f = Math.floor(t * 30);
  cx.save(); cx.globalAlpha = a; cx.globalCompositeOperation = 'overlay';
  const p = cx.createPattern(IM.noise, 'repeat');
  cx.translate(-rnd(f) * 600, -rnd(f + 9) * 600); cx.fillStyle = p; cx.fillRect(0, 0, W + 600, H + 600);
  cx.restore();
  // kurz i rysy
  cx.save();
  for (let k = 0; k < 3; k++) if (rnd(f * 3 + k) > 0.72) {
    cx.globalAlpha = 0.25 + 0.3 * rnd(f + k * 7); cx.fillStyle = rnd(f + k) > 0.5 ? '#fff' : '#000';
    cx.beginPath(); cx.arc(rnd(f * 5 + k) * W, rnd(f * 11 + k) * H, 1.5 + 3 * rnd(f * 13 + k), 0, 7); cx.fill();
  }
  if (rnd(f * 17) > 0.86) { cx.globalAlpha = 0.18; cx.fillStyle = '#fff'; cx.fillRect(rnd(f * 19) * W, 0, 2, H); }
  cx.restore();
}
function vignette(a = 0.75) {
  const g = cx.createRadialGradient(W / 2, H / 2, 300, W / 2, H / 2, 1150);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(0,0,0,${a})`);
  cx.fillStyle = g; cx.fillRect(0, 0, W, H);
}
function bars() { cx.fillStyle = '#000'; cx.fillRect(0, 0, W, BAR); cx.fillRect(0, H - BAR, W, BAR); }

// zdjęcie w kadrze kinowym: mode {fx0,fx1,z0,z1,fy}
function shot(k, p, m) {
  const im = IM[k], top = BAR, h = H - 2 * BAR;
  const z = m.z0 + (m.z1 - m.z0) * p;
  const s = h / im.height * z, w = im.width * s, hh = im.height * s;
  const fx = m.fx0 + (m.fx1 - m.fx0) * p, fy = m.fy || 0.5;
  let x = W / 2 - fx * w, y = top + h / 2 - fy * hh;
  x = Math.min(0, Math.max(W - w, x)); y = Math.min(top, Math.max(top + h - hh, y));
  cx.save(); cx.beginPath(); cx.rect(0, top, W, h); cx.clip();
  cx.filter = 'contrast(1.18) saturate(1.12) brightness(0.92)';
  cx.drawImage(im, x, y, w, hh); cx.filter = 'none';
  // look: chłodne cienie, ciepłe światła
  cx.globalCompositeOperation = 'soft-light'; cx.fillStyle = 'rgba(0,95,120,0.55)'; cx.fillRect(0, top, W, h);
  cx.globalCompositeOperation = 'overlay'; cx.fillStyle = 'rgba(255,140,60,0.10)'; cx.fillRect(0, top, W, h);
  cx.globalCompositeOperation = 'source-over';
  cx.restore();
}
function shade(a) { // przyciemnienie pod napisem
  const g = cx.createLinearGradient(0, 700, 0, 1220);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(.5, `rgba(0,0,0,${a})`); g.addColorStop(1, 'rgba(0,0,0,0)');
  cx.fillStyle = g; cx.fillRect(0, 700, W, 520);
}
// napis zwiastunowy z wejściem/wyjściem
function title(lines, t, t0, t1, o = {}) {
  if (t < t0 || t > t1) return;
  const a = clamp((t - t0) / 0.35) * clamp((t1 - t) / 0.3);
  const sc = 1 + 0.035 * (t - t0) / (t1 - t0);
  const sz = o.sz || 76, gap = o.gap || sz * 1.45, y0 = (o.y || 960) - (lines.length - 1) * gap / 2;
  cx.save(); cx.translate(W / 2, o.y || 960); cx.scale(sc, sc); cx.translate(-W / 2, -(o.y || 960));
  lines.forEach((l, i) => txt(l, W / 2, y0 + i * gap, { f: o.f || 'Light', sz, sp: o.sp ?? 16, a, glow: 22, col: o.col || CREAM }));
  cx.restore();
}
function caption(s, t, t0, t1) {
  if (t < t0 || t > t1) return;
  const a = clamp((t - t0) / 0.08) * clamp((t1 - t) / 0.1);
  cx.save(); cx.globalAlpha = a;
  cx.font = '44px Semi'; cx.letterSpacing = '1px';
  const w = cx.measureText(s).width;
  cx.fillStyle = 'rgba(0,0,0,.82)'; cx.fillRect(W / 2 - w / 2 - 22, 1395, w + 44, 76);
  cx.fillStyle = '#fff'; cx.textAlign = 'center'; cx.textBaseline = 'middle'; cx.fillText(s, W / 2, 1434);
  cx.restore();
}

// ---------- sceny
function ratingCard(t) {
  const G = '#17663A';
  cx.fillStyle = G; cx.fillRect(0, 0, W, H);
  const fl = 0.04 * Math.sin(t * 50) * rnd(Math.floor(t * 30));
  cx.strokeStyle = '#EAF3E6'; cx.lineWidth = 7; cx.strokeRect(70, 200, W - 140, H - 400);
  const c = '#F2F7EE';
  txt('ZWIASTUN', W / 2, 345, { f: 'Blk', sz: 128, col: c, sp: 6 });
  txt('DOZWOLONY DO EMISJI', W / 2, 455, { f: 'Semi', sz: 48, col: c, sp: 8 });
  cx.fillStyle = c; cx.fillRect(160, 525, W - 320, 4);
  txt('DLA WIDZÓW, KTÓRZY', W / 2, 615, { f: 'Semi', sz: 58, col: c, sp: 2 });
  txt('SWÓJ PODCAST ZACZYNAJĄ', W / 2, 690, { f: 'Semi', sz: 58, col: c, sp: 2 });
  cx.lineWidth = 9; cx.strokeStyle = c; cx.strokeRect(185, 775, W - 370, 230);
  txt('OD JUTRA', W / 2, 892, { f: 'Blk', sz: 138, col: c, sp: 2 });
  cx.fillRect(160, 1075, W - 320, 4);
  txt('ZAWIERA:', W / 2, 1150, { f: 'Semi', sz: 44, col: c, sp: 10 });
  txt('sceny ambitne · zero wymówek', W / 2, 1230, { f: 'Light', sz: 50, col: c });
  txt('drastycznie niską cenę', W / 2, 1302, { f: 'Light', sz: 50, col: c });
  txt('GADKASTUDIO.PL', W / 2, 1620, { f: 'Semi', sz: 38, col: c, sp: 12 });
  cx.fillStyle = `rgba(0,0,0,${0.08 + fl})`; cx.fillRect(0, 0, W, H);
}

function rec(t, t0) { // nakładka kamery
  const lt = t - t0;
  cx.save(); cx.strokeStyle = 'rgba(255,255,255,.9)'; cx.lineWidth = 5;
  const m = 70, T = BAR + 60, B = H - BAR - 60, L = 50;
  [[m, T, 1, 1], [W - m, T, -1, 1], [m, B, 1, -1], [W - m, B, -1, -1]].forEach(([x, y, dx, dy]) => {
    cx.beginPath(); cx.moveTo(x, y + dy * L); cx.lineTo(x, y); cx.lineTo(x + dx * L, y); cx.stroke();
  });
  if (Math.floor(lt * 2.4) % 2 === 0) { cx.fillStyle = '#ff2b2b'; cx.beginPath(); cx.arc(m + 40, T + 50, 13, 0, 7); cx.fill(); }
  cx.restore();
  txt('REC', 175, BAR + 110, { f: 'Semi', sz: 38, col: '#fff', al: 'left', sp: 3 });
  txt('4K · 25P', W - 110, BAR + 110, { f: 'Semi', sz: 38, col: '#fff', al: 'right', sp: 3 });
  const fr = Math.floor(lt * 25);
  txt(`00:00:${String(12 + Math.floor(lt)).padStart(2, '0')}:${String(fr % 25).padStart(2, '0')}`, W / 2, H - BAR - 110, { f: 'Semi', sz: 36, col: '#fff', sp: 4 });
}

function logoSlam(t) {
  const lt = t - D.LOGO;
  const p = eo(lt / 0.5);
  const w = 820 * (1.25 - 0.25 * p) * (1 + 0.02 * lt);
  const h = w * 510 / 1400, y = 800;
  // flara
  const fa = clamp(1 - lt / 1.2) * 0.9 + 0.12;
  const fw = 200 + 1400 * eo(lt / 0.6);
  const g = cx.createLinearGradient(W / 2 - fw / 2, 0, W / 2 + fw / 2, 0);
  g.addColorStop(0, 'rgba(255,120,60,0)'); g.addColorStop(.5, `rgba(255,200,160,${fa})`); g.addColorStop(1, 'rgba(255,120,60,0)');
  cx.fillStyle = g; cx.fillRect(W / 2 - fw / 2, y - 3, fw, 6);
  const rg = cx.createRadialGradient(W / 2, y, 0, W / 2, y, 420);
  rg.addColorStop(0, `rgba(255,110,50,${0.35 * fa})`); rg.addColorStop(1, 'rgba(255,110,50,0)');
  cx.fillStyle = rg; cx.fillRect(0, y - 420, W, 840);
  cx.save(); cx.globalAlpha = clamp(lt / 0.12);
  cx.shadowColor = 'rgba(255,120,60,.6)'; cx.shadowBlur = 40 * clamp(1 - lt / 1.5) + 8;
  cx.drawImage(IM.logo, W / 2 - w / 2, y - h / 2, w, h); cx.restore();
}

function billing(t) {
  const a = clamp((t - D.BILL) / 0.6);
  if (a <= 0) return;
  const L = [
    'GADKA STUDIO PREZENTUJE  TWÓJ PIERWSZY ODCINEK',
    'W ROLACH GŁÓWNYCH  TY · TWÓJ GOŚĆ · MIKROFONY SHURE',
    'ZDJĘCIA  DWIE KAMERY 4K   ŚWIATŁO  PROFESJONALNE',
    'SCENARIUSZ  JESZCZE GO NIE MASZ   PLIKI  OD RĘKI',
    'LOKALIZACJA  WARSZAWA   CZAS  2 GODZINY   BUDŻET  300 ZŁ',
  ];
  L.forEach((l, i) => txt(l, W / 2, 1468 + i * 44, { f: 'Light', sz: 40, col: '#BDB6AC', sx: 0.58, a, sp: 1 }));
}

function soon(t) {
  if (t < D.SOON) return;
  const a = clamp((t - D.SOON) / 0.5), y = 1130;
  const s = 'WKRÓTCE.', sz = 86, sp = 26;
  const ww = tw(s, 'Thin', sz, sp);
  const dim = t > D.TOMO ? 0.45 : 1;
  txt(s, W / 2, y, { sz, sp, a: a * dim, glow: 18 });
  if (t > D.STRIKE) {
    const p = eo((t - D.STRIKE) / 0.22);
    cx.fillStyle = OR; cx.save(); cx.translate(W / 2 - ww / 2 - 10, y + 4); cx.rotate(-0.06);
    cx.fillRect(0, -5, (ww + 20) * p, 10); cx.restore();
  }
  if (t > D.TOMO) {
    const lt = t - D.TOMO, sc = ob(lt / 0.35, 2.5);
    cx.save(); cx.translate(W / 2, 1265); cx.scale(sc, sc); cx.rotate(-0.03);
    txt('JUŻ JUTRO.', 0, 0, { f: 'Blk', sz: 128, col: OR, sp: 2, glow: 30, gcol: 'rgba(255,90,40,.6)' });
    cx.restore();
    txt('rezerwuj: gadkastudio.pl', W / 2, 1375, { f: 'Semi', sz: 40, col: CREAM, a: clamp((lt - 0.4) / 0.4), sp: 2 });
  }
}

window.renderAt = function (t) {
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.filter = 'none'; cx.globalAlpha = 1; cx.globalCompositeOperation = 'source-over';
  cx.fillStyle = '#000'; cx.fillRect(0, 0, W, H);
  if (t < D.CARD) { ratingCard(t); grain(t, 0.16); vignette(0.45); return; }

  // ---- czarne plansze
  title(['W ŚWIECIE,'], t, D.T1, D.T2 - 0.1);
  title(['GDZIE KAŻDY', 'NAGRYWA PODCAST…'], t, D.T2, D.J1 - 0.15);
  title(['…W KUCHNI.'], t, D.J1, D.J2 - 0.15, { sz: 82 });
  caption('[szum lodówki]', t, D.J1 + 0.45, D.J2 - 0.15);
  if (t > D.J2 && t < D.ONE - 0.1) {
    title(['…Z ECHEM', 'JAK W KATEDRZE.'], t, D.J2, D.ONE - 0.15);
    // echo – powidoki
    for (let k = 1; k <= 3; k++) {
      const lt = t - D.J2 - 0.35 * k; if (lt < 0) continue;
      const a = 0.28 / k * clamp(1 - lt / 1.2) * clamp((D.ONE - 0.15 - t) / 0.3);
      const sc = 1 + 0.06 * k + 0.05 * lt;
      cx.save(); cx.translate(W / 2, 960); cx.scale(sc, sc); cx.translate(-W / 2, -960);
      txt('…Z ECHEM', W / 2, 960 - 55, { sz: 76, sp: 16, a }); txt('JAK W KATEDRZE.', W / 2, 960 + 55, { sz: 76, sp: 16, a });
      cx.restore();
    }
    caption('[echo]  [echo]  [echo]', t, D.J2 + 0.5, D.ONE - 0.15);
  }
  title(['JEDNO', 'MIEJSCE.'], t, D.ONE, D.SH - 0.05, { sz: 110, sp: 34 });

  // ---- ujęcia
  const S = D.SHOTS;
  for (let i = 0; i < S.length; i++) {
    const [t0, k, fx0, fx1, z0, z1, label] = S[i];
    const t1 = i + 1 < S.length ? S[i + 1][0] : D.BLK;
    if (t >= t0 && t < t1) {
      const p = (t - t0) / (t1 - t0);
      if (k === 'black') { /* nic */ }
      else shot(k, p, { fx0, fx1, z0, z1 });
      if (k === '037') rec(t, t0);
      if (label) { shade(0.75 * clamp((t - t0 - 0.2) / 0.3)); title(label.split('|'), t, t0 + 0.2, t1 + 0.05, { sz: 74, sp: 14 }); }
      // błysk na cięciu w montażu
      if (t0 >= D.MON) { const fl = clamp(1 - (t - t0) / 0.07); if (fl > 0) { cx.fillStyle = `rgba(255,245,230,${0.55 * fl})`; cx.fillRect(0, BAR, W, H - 2 * BAR); } }
      // wejście pierwszego ujęcia z czerni
      if (i === 0) { cx.fillStyle = `rgba(0,0,0,${1 - clamp((t - t0) / 0.5)})`; cx.fillRect(0, 0, W, H); }
    }
  }

  // ---- cisza i cena
  title(['A ILE TO KOSZTUJE?'], t, D.ILE, D.PRICE - 0.08, { sz: 58, sp: 10 });
  if (t >= D.PRICE && t < D.LOGO - 0.05) {
    const lt = t - D.PRICE, a = clamp((D.LOGO - 0.05 - t) / 0.25);
    const sc = (1.18 - 0.18 * eo(lt / 0.35)) * (1 + 0.025 * lt);
    cx.save(); cx.translate(W / 2, 900); cx.scale(sc, sc);
    txt('300 ZŁ', 0, 0, { f: 'Blk', sz: 270, col: CREAM, a, glow: 40 * clamp(1 - lt / 1.5) + 10 });
    cx.restore();
    txt('ZA 2 GODZINY · SPRZĘT W CENIE', W / 2, 1110, { f: 'Light', sz: 46, sp: 8, a: a * clamp((lt - 0.45) / 0.4) });
    txt('cena brutto', W / 2, 1185, { f: 'Light', sz: 36, sp: 4, col: '#9E978D', a: a * clamp((lt - 0.8) / 0.4) });
  }
  if (t >= D.LOGO) { logoSlam(t); billing(t); soon(t); }

  bars();
  grain(t, t > D.SH && t < D.BLK ? 0.14 : 0.1);
  vignette(0.55);
  // zaciemnienie końcowe
  if (t > D.TOTAL - 0.6) { cx.fillStyle = `rgba(0,0,0,${clamp((t - D.TOTAL + 0.6) / 0.6)})`; cx.fillRect(0, 0, W, H); }
};
