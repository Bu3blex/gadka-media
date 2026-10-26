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

// ---------- ROLKA: „Ty o 2:37 w nocy” – nocne szukanie w wyszukiwarce
const E = D.E;  // znaczniki czasu z render.py
const UI = '#1E1E26', UI2 = '#2A2A35', TXT = '#ECE8F5', DIM = '#8C88A0', RED = '#FF4D4D', VI = '#7B61FF';
const BX = SAFE.L, BW = SAFE.R - SAFE.L;

function nightBg(t) {
  const g = cx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#0B0B14'); g.addColorStop(1, '#15122A');
  cx.fillStyle = g; cx.fillRect(0, 0, W, H);
  const r = cx.createRadialGradient(540, 760, 50, 540, 760, 900); r.addColorStop(0, 'rgba(123,97,255,.16)'); r.addColorStop(1, 'rgba(123,97,255,0)');
  cx.fillStyle = r; cx.fillRect(0, 0, W, H);
}
function clockTxt(t) {
  if (t < E.Q3 + 1.6) return '02:37'; if (t < E.TWIST) return '03:58'; return '03:59';
}
function statusBar(t, a) {
  if (a <= 0) return;
  cx.save(); cx.globalAlpha = a;
  txt(clockTxt(t), BX, 330, { font: '40px XB', col: TXT });
  // księżyc
  cx.fillStyle = '#FFD86B'; cx.beginPath(); cx.arc(SAFE.R - 30, 330, 22, 0, 7); cx.fill();
  cx.fillStyle = '#0D0C18'; cx.beginPath(); cx.arc(SAFE.R - 18, 322, 20, 0, 7); cx.fill();
  cx.restore();
}
function magnifier(x, y, s = 1, col = DIM) {
  cx.save(); cx.translate(x, y); cx.scale(s, s); cx.strokeStyle = col; cx.lineWidth = 5; cx.lineCap = 'round';
  cx.beginPath(); cx.arc(-4, -4, 13, 0, 7); cx.stroke(); cx.beginPath(); cx.moveTo(6, 6); cx.lineTo(16, 16); cx.stroke(); cx.restore();
}
// pasek wyszukiwania z wpisywanym tekstem
function searchBar(q, t, t0, y = 470, a = 1) {
  const n = Math.max(0, Math.min(q.length, Math.floor((t - t0) / 0.065)));
  cx.save(); cx.globalAlpha = a;
  cx.fillStyle = UI; cx.beginPath(); cx.roundRect(BX, y - 64, BW, 128, 64); cx.fill();
  cx.strokeStyle = 'rgba(123,97,255,.55)'; cx.lineWidth = 3; cx.stroke();
  magnifier(BX + 58, y, 1.1);
  const shown = t < t0 ? '' : q.slice(0, n);
  let fs = 50; cx.font = `${fs}px Semi`; while (cx.measureText(shown).width > BW - 150 && fs > 30) { fs -= 2; cx.font = `${fs}px Semi`; }
  if (!shown) txt('Szukaj…', BX + 100, y + 2, { font: '50px Semi', col: DIM });
  else txt(shown, BX + 100, y + 2, { font: `${fs}px Semi`, col: TXT });
  if (Math.floor(t * 2.2) % 2 === 0 || (t > t0 && n < q.length)) { cx.font = `${fs}px Semi`; const w = cx.measureText(shown).width; cx.fillStyle = VI; cx.fillRect(BX + 104 + w, y - 30, 5, 60); }
  cx.restore();
  return n >= q.length;
}
function sugList(items, t, t0, hi, hiT, y0 = 640) {
  items.forEach((s, i) => {
    const ti = t0 + i * 0.28; if (t < ti) return;
    const p = eo((t - ti) / 0.3), y = y0 + i * 150 + 20 * (1 - p);
    const sel = hi === i && t > hiT;
    cx.save(); cx.globalAlpha = p;
    cx.fillStyle = sel ? VI : UI; cx.beginPath(); cx.roundRect(BX, y, BW, 128, 30); cx.fill();
    magnifier(BX + 50, y + 64, 0.9, sel ? '#fff' : DIM);
    const [a, b] = s;
    cx.font = '44px Semi'; const wa = cx.measureText(a).width;
    txt(a, BX + 90, y + 66, { font: '44px Semi', col: sel ? '#E6E0FF' : DIM });
    txt(b, BX + 90 + wa, y + 66, { font: '44px XB', col: '#fff' });
    cx.restore();
  });
}
function card(x, y, w, h, t, t0, col = UI) {
  if (t < t0) return 0; const p = eo((t - t0) / 0.35);
  cx.save(); cx.globalAlpha = p; cx.translate(0, 40 * (1 - p));
  cx.fillStyle = col; cx.beginPath(); cx.roundRect(x, y, w, h, 34); cx.fill(); cx.restore(); return p;
}

const SCENES2 = {
  hook(t) {
    nightBg(t);
    kin('Ty, w łóżku,', BX, 640, 96, TXT, t, 0.0);
    kin('o godzinie:', BX, 750, 96, TXT, t, 0.12);
    if (t > 0.35) { const s = ob((t - 0.35) / 0.35, 2.4); cx.save(); cx.translate(540, 1010); cx.scale(s, s);
      cx.shadowColor = 'rgba(123,97,255,.8)'; cx.shadowBlur = 50; txt('02:37', 0, 0, { font: '260px Blk', col: '#fff', al: 'center' }); cx.restore(); }
    if (t > 0.9) pill('i jedno pytanie…', 540, 1260, t, 0.9, VI, '#fff', 46);
  },
};

window.renderAt = async function (t) {
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.globalAlpha = 1;
  if (t < E.UI) { SCENES2.hook(t); grain(t); return; }
  nightBg(t);
  const ua = clamp((t - E.UI) / 0.3);
  statusBar(t, ua);
  if (t < E.FIN) {
    // --- zapytanie 1
    if (t < E.Q2) {
      searchBar('jak zacząć podcast', t, E.Q1, 470, ua);
      sugList([['jak zacząć podcast ', 'bez sprzętu'], ['jak zacząć podcast ', 'i nie odpuścić'], ['jak zacząć podcast ', 'od jutra']], t, E.Q1 + 1.35, 2, E.Q1 + 2.6);
      if (t > E.Q1 + 2.8) pill('klasyk.', 760, 1180, t, E.Q1 + 2.8, '#FFD86B', BK, 60, 0.06);
    }
    // --- zapytanie 2: koszty
    else if (t < E.Q3) {
      searchBar('ile kosztuje sprzęt do podcastu', t, E.Q2);
      const t1 = E.Q2 + 2.1;
      if (card(BX, 620, BW, 860, t, t1) > 0) {
        const L = [['2× mikrofon Shure', 'ok. 3 300 zł'], ['2× kamera 4K', 'ok. 3 850 zł'], ['oświetlenie', 'ok. 1 200 zł'], ['wygłuszenie', 'ok. 1 500 zł']];
        L.forEach(([a, b], i) => { const ti = t1 + 0.25 + i * 0.3; if (t < ti) return; const al = clamp((t - ti) / 0.2);
          txt(a, BX + 50, 720 + i * 125, { font: '48px Semi', col: TXT, a: al }); txt(b, SAFE.R - 50, 720 + i * 125, { font: '48px XB', col: TXT, al: 'right', a: al }); });
        if (t > t1 + 1.5) { cx.fillStyle = '#3A3A48'; cx.fillRect(BX + 50, 1235, BW - 100, 3);
          txt('razem:', BX + 50, 1340, { font: '50px Semi', col: DIM });
          const s = ob((t - t1 - 1.5) / 0.35, 2.6); cx.save(); cx.translate(SAFE.R - 50, 1340); cx.scale(s, s);
          txt('≈ 9 850 zł', 0, 0, { font: '100px Blk', col: RED, al: 'right' }); cx.restore(); }
        if (t > t1 + 2.0) pill('…na start.', 700, 1520, t, t1 + 2.0, RED, '#fff', 56, -0.05);
      }
    }
    // --- zapytanie 3: wygłuszanie
    else if (t < E.TWIST) {
      searchBar('jak wygłuszyć pokój w bloku', t, E.Q3);
      const t1 = E.Q3 + 1.9;
      if (card(BX, 620, BW, 700, t, t1) > 0) {
        txt('Poradnik: wygłuszanie', BX + 50, 730, { font: '54px XB', col: TXT });
        txt('Krok 1 z 47', BX + 50, 870, { font: '110px Blk', col: '#FFD86B' });
        txt('pianki · panele · dywany · koce…', BX + 50, 990, { font: '44px Semi', col: DIM });
        cx.fillStyle = UI2; cx.beginPath(); cx.roundRect(BX + 50, 1080, BW - 100, 36, 18); cx.fill();
        cx.fillStyle = VI; cx.beginPath(); cx.roundRect(BX + 50, 1080, (BW - 100) * 0.02, 36, 18); cx.fill();
        txt('postęp: 2%', BX + 50, 1190, { font: '46px Semi', col: DIM });
      }
      if (t > t1 + 1.0) pill('jest 03:58.', 600, 1440, t, t1 + 1.0, '#FFD86B', BK, 60, 0.05);
    }
    // --- zwrot i wynik: Gadka studio
    else {
      const lt = t - E.TWIST;
      if (lt < 0.9) { kin('A może…', BX, 900, 150, '#FFD86B', t, E.TWIST); }
      else {
        searchBar('studio podcastowe warszawa', t, E.TWIST + 0.9);
        const t1 = E.RES;
        if (t > t1 - 0.5 && t < t1) { cx.fillStyle = VI; cx.fillRect(BX, 545, BW * eo((t - t1 + 0.5) / 0.5), 6); }
        if (card(BX, 590, BW, 960, t, t1, '#F9EEE4') > 0) {
          cx.save(); cx.globalAlpha = clamp((t - t1) / 0.3);
          cx.drawImage(IM.logoB, BX + 50, 630, 230, 230 * IM.logoB.height / IM.logoB.width);
          txt('studio podcastowe · Warszawa', BX + 50, 760, { font: '38px Semi', col: '#5A524A' });
          photo('101', BX + 50, 810, (BW - 120) / 2, 300, (t - t1) / 4, 0.5, 0.5, 20);
          photo('104', BX + 70 + (BW - 120) / 2, 810, (BW - 120) / 2, 300, (t - t1) / 4, 0.5, 0.5, 20);
          cx.restore();
          const chips = [['2 h · 300 zł brutto', OR, '#fff'], ['sprzęt w cenie', BK, CR], ['mikrofony Shure', '#fff', BK], ['2× kamera 4K', '#fff', BK], ['pliki od ręki', '#fff', BK]];
          let cxp = BX + 50, cyp = 1180;
          chips.forEach(([s, bg, fg], i) => {
            cx.font = '38px XB'; const w = cx.measureText(s).width + 56;
            if (cxp + w > SAFE.R - 50) { cxp = BX + 50; cyp += 86; }
            const ti = t1 + 0.4 + i * 0.22;
            if (t > ti) { const sc = ob((t - ti) / 0.3, 2.4); cx.save(); cx.translate(cxp + w / 2, cyp); cx.scale(sc, sc);
              cx.fillStyle = bg; cx.beginPath(); cx.roundRect(-w / 2, -34, w, 68, 34); cx.fill();
              if (bg === '#fff') { cx.strokeStyle = '#D8CBBE'; cx.lineWidth = 2; cx.stroke(); }
              txt(s, 0, 2, { font: '38px XB', col: fg, al: 'center' }); cx.restore(); }
            cxp += w + 16;
          });
          const tb = t1 + 1.8;
          if (t > tb) { const press = t > E.TAP && t < E.TAP + 0.18 ? 0.94 : 1, pulse = 1 + 0.03 * Math.sin(t * 8);
            cx.save(); cx.translate(540, 1460); cx.scale(press * pulse, press * pulse);
            cx.fillStyle = BK; cx.beginPath(); cx.roundRect(-330, -50, 660, 100, 50); cx.fill();
            txt('Zarezerwuj', 0, 3, { font: '48px Blk', col: '#fff', al: 'center' }); cx.restore(); }
          if (t > E.TAP - 0.6) { // palec/kursor
            const p = eio((t - E.TAP + 0.6) / 0.6); cx.save(); cx.globalAlpha = 0.9; cx.fillStyle = 'rgba(255,255,255,.85)';
            cx.beginPath(); cx.arc(lerp(860, 600, p), lerp(1620, 1475, p), 34, 0, 7); cx.fill(); cx.restore(); }
        }
      }
    }
  }
  // --- finał
  if (t >= E.FIN) {
    const lt = t - E.FIN, ir = eio(lt / 0.45);
    cx.save(); cx.beginPath(); cx.arc(600, 1475, 2400 * ir, 0, 7); cx.clip(); cx.fillStyle = OR; cx.fillRect(0, 0, W, H);
    kin('Mniej szukania.', BX, 560, 92, BK, lt, 0.25);
    kin('Więcej nagrywania.', BX, 670, 86, CR, lt, 0.4);
    if (lt > 0.9) { cx.save(); cx.globalAlpha = clamp((lt - 0.9) / 0.3); cx.drawImage(IM.logoB, 540 - 210, 800, 420, 420 * IM.logoB.height / IM.logoB.width); cx.restore(); }
    txt('Wpadnij do studia', 540, 1040, { font: '60px XB', col: BK, al: 'center', a: clamp((lt - 1.2) / 0.3) });
    txt('i nagraj, co chcesz!', 540, 1115, { font: '60px XB', col: BK, al: 'center', a: clamp((lt - 1.2) / 0.3) });
    if (lt > 1.6) { const s = ob((lt - 1.6) / 0.35, 2.2); cx.save(); cx.translate(540, 1300); cx.scale(s, s);
      cx.fillStyle = BK; cx.beginPath(); cx.roundRect(-390, -85, 780, 170, 40); cx.fill();
      txt('2 h · 300 zł brutto', 0, -20, { font: '64px Blk', col: '#fff', al: 'center' }); txt('sprzęt w cenie · Warszawa', 0, 45, { font: '38px Semi', col: CR, al: 'center' }); cx.restore(); }
    txt('gadkastudio.pl', 540, 1480, { font: '60px XB', col: BK, al: 'center', a: clamp((lt - 2.0) / 0.3) });
    cx.restore();
  }
  grain(t);
  if (window.SAFE_BOX) { cx.strokeStyle = '#00E5FF'; cx.lineWidth = 6; cx.strokeRect(SAFE.L, SAFE.T, SAFE.R - SAFE.L, SAFE.B - SAFE.T); }
  if (t > D.TOTAL - 0.4) { cx.fillStyle = `rgba(0,0,0,${clamp((t - D.TOTAL + 0.4) / 0.4)})`; cx.fillRect(0, 0, W, H); }
};

// okładka – wszystko w kwadracie y 420–1500, x 100–980
window.renderCover = function () {
  cx.setTransform(1, 0, 0, 1, 0, 0); nightBg(0);
  txt('Ty, o godzinie:', 100, 500, { font: '76px Blk', col: TXT });
  cx.save(); cx.shadowColor = 'rgba(123,97,255,.9)'; cx.shadowBlur = 60; txt('02:37', 540, 760, { font: '300px Blk', col: '#fff', al: 'center' }); cx.restore();
  cx.fillStyle = UI; cx.beginPath(); cx.roundRect(100, 980, 880, 120, 60); cx.fill(); cx.strokeStyle = 'rgba(123,97,255,.7)'; cx.lineWidth = 4; cx.stroke();
  magnifier(160, 1040, 1.2); txt('jak zacząć podcast', 205, 1042, { font: '52px Semi', col: TXT }); cx.fillStyle = VI; cx.fillRect(660, 1012, 5, 58);
  cx.save(); cx.translate(700, 1250); cx.rotate(-0.05); cx.fillStyle = OR; cx.beginPath(); cx.roundRect(-260, -60, 520, 120, 60); cx.fill();
  txt('…od jutra?', 0, 3, { font: '58px Blk', col: '#fff', al: 'center' }); cx.restore();
  cx.drawImage(IM.logo, 100, 1395, 220, 220 * IM.logo.height / IM.logo.width);
  grain(0.3);
};
