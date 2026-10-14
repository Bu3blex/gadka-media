// „POV: od roku mówisz, że zaczniesz podcast” – rolka Gadka studio. renderAt(t) deterministycznie.
const D = window.DATA;
const stage = document.getElementById('stage');
const OR = '#FF592A', CR = '#F9EEE4', BK = '#000';
const cl = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const oC = t => 1 - Math.pow(1 - cl(t), 3);
const oE = t => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * cl(t)));
const oB = (t, c1 = 1.8) => { t = cl(t); const c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); };
function hash(i, j) { const x = Math.sin(i * 127.1 + j * 311.7) * 43758.5453; return x - Math.floor(x); }

const NOTIFS = [
  ['💬', '#34C759', 'Mama', 'Synku, a ten podcast to kiedy?'],
  ['📅', '#fff', 'Kalendarz', 'Nagrać 1. odcinek · przełożone 14 razy'],
  ['💬', '#34C759', 'Kuba', 'bro, nagrywamy w końcu czy nie?'],
  ['🎙️', '#FF3B30', 'Dyktafon', 'Nowe nagranie: intro_v27_FINAL_final'],
  ['💬', '#34C759', 'Ania', 'pamiętasz, jak mówiłeś „od stycznia”?'],
  ['🔋', '#FFCC00', 'Bateria', '5%. Może jednak nie telefonem?'],
  ['📦', '#8E6E53', 'Kurier', 'Mikrofon za 49 zł: dostawa za 46 dni'],
  ['💬', '#34C759', 'Szef', 'To ty miałeś robić podcast firmowy?'],
  ['💬', '#34C759', 'Kuba', '???'],
  ['💬', '#34C759', 'Mama', 'halo'],
  ['💬', '#34C759', 'Ania', 'podcast??'],
  ['💬', '#34C759', 'Kuba', '🫠'],
  ['📞', '#34C759', 'Mama', 'Połączenie przychodzące…'],
  ['💬', '#34C759', 'Szef', 'pilne'],
];

function card(n, y, k, extra = '') {
  const [ic, col, app, body] = n;
  return `<div class="card" style="top:${y}px;transform:translateY(${(1 - oB(k)) * -60}px) scale(${0.88 + 0.12 * oB(k)});opacity:${cl(k * 4)};${extra}">
    <div class="ic" style="background:${col}">${ic}</div>
    <div class="tx"><div class="hd"><span>${app}</span><span>teraz</span></div><div class="bd">${body}</div></div></div>`;
}
function pov(op = 1) {
  return `<div class="stk" style="top:640px;opacity:${op}"><span style="display:inline-block;background:${CR};color:#000;font-family:IDB;font-size:58px;line-height:1.18;padding:26px 40px;border-radius:26px;white-space:normal;width:900px">POV: od roku mówisz,<br>że zaczniesz podcast</span></div>`;
}
function lockscreen(t, blur = 0, dim = 0) {
  return `<img class="abs" src="img/wall.jpg" style="left:0;top:0;width:1080px;height:1920px;filter:brightness(${0.62 - dim}) saturate(1.2)">
  <div class="abs" style="left:0;top:0;width:1080px;height:1920px;filter:blur(${blur}px)">
   <div class="stk" style="top:250px;color:#fff;font-family:PopM;font-size:44px;opacity:.9">wtorek, 13 października</div>
   <div class="stk" style="top:300px;color:#fff;font-family:'Inter';font-weight:700;font-size:250px;letter-spacing:-6px;opacity:.95">23:48</div>
  </div>`;
}

// ---------------------------------------------------------------- sceny
function sceneNotifs(t) {
  const NT = D.N;
  let h = lockscreen(t);
  // narastający wstrząs
  const heat = cl((t - 2.0) / 2.2);
  const sx = (hash(Math.floor(t * 60), 1) - .5) * 30 * heat * heat, sy = (hash(Math.floor(t * 60), 2) - .5) * 30 * heat * heat;
  stage.style.transform = `translate(${sx}px,${sy}px) rotate(${(hash(Math.floor(t * 60), 3) - .5) * 1.4 * heat}deg)`;
  // stos: najnowsze na górze
  const shown = NT.map((x, i) => [x, i]).filter(([x]) => t >= x);
  let y = 860;
  for (let j = shown.length - 1; j >= 0; j--) {
    const [x, i] = shown[j]; const k = (t - x) / 0.28;
    h += card(NOTIFS[i], y, k);
    const hgt = NOTIFS[i][3].length > 28 ? 224 : 168;
    y += (hgt + 18) * oC((t - x) / 0.22);
  }
  h += pov();
  // licznik powiadomień
  if (shown.length > 3) h += `<div class="abs" style="left:880px;top:612px;width:120px;height:120px;border-radius:60px;background:#FF3B30;color:#fff;font:800 60px Inter;display:flex;align-items:center;justify-content:center;transform:scale(${1 + 0.25 * (1 - cl((t - shown[shown.length - 1][0]) / 0.15))}) rotate(8deg)">${shown.length}</div>`;
  return h;
}
function sceneFreeze(t) {
  // zamrożenie: wszystko rozmyte; wjeżdża jedno powiadomienie od Gadki
  stage.style.transform = '';
  const lt = t - D.FREEZE;
  let h = lockscreen(t, 14, 0.3);
  let y = 860; const NT = D.N;
  for (let i = NT.length - 1; i >= 0; i--) { h += card(NOTIFS[i], y, 1, `filter:blur(${10 + 10 * cl(lt / .2)}px);opacity:.45`); y += (NOTIFS[i][3].length > 28 ? 224 : 168) + 18; }
  if (t >= D.GADKA) {
    const k = (t - D.GADKA) / 0.35;
    h += `<div class="abs" style="left:0;top:0;width:1080px;height:1920px;background:rgba(0,0,0,${0.35 * cl(k)})"></div>`;
    h += `<div class="card" style="top:${760}px;left:50px;width:980px;transform-origin:50% 50%;padding:34px 36px;background:rgba(255,255,255,.88);color:#111;
      box-shadow:0 0 0 5px ${OR},0 0 90px rgba(255,89,42,.65);transform:translateY(${(1 - oB(k, 2.2)) * -260}px) scale(${0.8 + 0.2 * oB(k, 2.2)});opacity:${cl(k * 4)}">
      <div class="ic" style="background:${OR};width:110px;height:110px;border-radius:28px"><img src="logo_black.png" style="width:92px"></div>
      <div class="tx"><div class="hd" style="font-size:36px"><span>Gadka studio</span><span>teraz</span></div>
      <div class="bd" style="font-weight:700;font-size:54px">Rezerwacja potwierdzona ✅</div>
      <div class="bd" style="font-size:46px;opacity:.75">Jutro, 18:00 · 2 h · 300 zł · sprzęt w cenie</div></div></div>`;
    const k2 = (t - D.GADKA - 0.25) / 0.3;
    if (k2 > 0) h += `<div class="stk" style="top:1150px;opacity:${cl(k2 * 3)};transform:translateY(${(1 - oC(k2)) * 40}px)"><span style="font-family:IDB;font-size:64px;color:${CR}">…i nagle cisza.</span></div>`;
  } else {
    h += `<div class="abs" style="left:0;top:0;width:1080px;height:1920px;background:rgba(0,0,0,.4)"></div>`;
  }
  return h;
}
// ---- montaż (od dropu): [typ, liczba uderzeń]
const CUTS = [['mic', 2], ['cam', 2], ['light', 2], ['w', 1, OR, BK, 'ZERO'], ['w', 1, BK, OR, 'WYMÓWEK.'], ['four', 2], ['files', 1], ['w', 1, CR, BK, '2 H = 300 ZŁ'], ['rec', 2]];
function cutAt(lt) {
  let b = 0;
  for (let i = 0; i < CUTS.length; i++) { const d = CUTS[i][1] * D.BEAT; if (lt < b + d || i === CUTS.length - 1) return [i, lt - b, d]; b += d; }
}
const full = (inner, css = '') => `<div class="abs" style="left:0;top:0;width:1080px;height:1920px;overflow:hidden;${css}">${inner}</div>`;
function photoFill(code, fx, scale, extraCss = '', tx = 0) {
  return `<img src="img/${code}.jpg" style="position:absolute;height:1920px;left:50%;top:0;transform:translateX(calc(-${fx * 100}% + ${tx}px)) scale(${scale});transform-origin:${fx * 100}% 50%;${extraCss}">`;
}
function hudCorners(col = '#fff', m = 90, L = 120, w = 7, top = 260, bot = 1560) {
  return `<svg class="abs" style="left:0;top:0" width="1080" height="1920"><g stroke="${col}" stroke-width="${w}" fill="none">
   <path d="M${m} ${top + L} V${top} H${m + L}"/><path d="M${1080 - m - L} ${top} H${1080 - m} V${top + L}"/>
   <path d="M${m} ${bot - L} V${bot} H${m + L}"/><path d="M${1080 - m - L} ${bot} H${1080 - m} V${bot - L}"/></g></svg>`;
}
function sceneMontage(t) {
  const lt = t - D.DROP; const [k, ct, dur] = cutAt(lt); const c = CUTS[k]; const p = ct / dur;
  let h = '';
  const sx = (hash(k, Math.floor(t * 60)) - .5) * 24 * (1 - cl(ct / .14));
  stage.style.transform = `translate(${sx}px,0)`;
  const bt = D.BEAT;
  if (c[0] === 'mic') {
    // zbliżenie produktowe: powolny najazd, reflektor, przejście światła, licznik ×1..×4
    h += full(photoFill('059', .6, 1.28 - 0.12 * oC(p), 'filter:contrast(1.15) saturate(1.1) brightness(1.05)', -50 * p));
    h += full('', `background:radial-gradient(ellipse 70% 45% at 52% 48%, rgba(0,0,0,0) 0%, rgba(0,0,0,.55) 70%, rgba(0,0,0,.85) 100%)`);
    const sw = cl((ct - 0.15) / 0.6);
    if (sw > 0 && sw < 1) h += full('', `background:linear-gradient(110deg,transparent ${sw * 180 - 60}%,rgba(255,220,190,.35) ${sw * 180 - 45}%,transparent ${sw * 180 - 30}%);mix-blend-mode:screen`);
    const n = Math.min(4, 1 + Math.floor(ct / (bt / 2)));
    const pop = oB((ct % (bt / 2)) / 0.18, 2.4);
    h += `<div class="abs" style="left:80px;top:1250px;font-family:PopB;font-size:40px;letter-spacing:10px;color:${OR};opacity:${cl(ct / .15)}">MIKROFONY</div>`;
    h += `<div class="abs" style="left:76px;top:1310px;font-family:IDB;font-size:150px;color:${CR};line-height:1;transform:translateX(${(1 - oC(ct / .3)) * -80}px);opacity:${cl(ct / .12)}">Shure SM7B</div>`;
    h += `<div class="abs" style="left:76px;top:1480px;font-family:IDB;font-size:210px;line-height:1;color:transparent;-webkit-text-stroke:5px ${OR};transform:scale(${0.6 + 0.4 * pop});transform-origin:0 50%">×${n}</div>`;
    h += `<div class="abs" style="left:80px;top:1720px;font-family:PopM;font-size:40px;color:${CR};opacity:${cl((ct - .4) / .2)}">po jednym dla każdego</div>`;
    // linia wskazująca
    const L = 520 * oC((ct - .2) / .35);
    h += `<svg class="abs" style="left:0;top:0" width="1080" height="1920"><path d="M640 1240 L640 ${1240 - L}" stroke="${CR}" stroke-width="4"/><circle cx="640" cy="${1240 - L}" r="${L > 5 ? 14 : 0}" fill="${OR}"/></svg>`;
  } else if (c[0] === 'cam') {
    // widok przez wizjer kamery: ostrzenie, blokada AF, REC, parametry
    const focus = cl(ct / 0.45);
    h += full(photoFill('101', .3, 1.12 - 0.05 * p, `filter:blur(${(1 - oC(focus)) * 14}px) contrast(1.1) saturate(1.1)`));
    h += full('', 'background:linear-gradient(rgba(0,0,0,.35),rgba(0,0,0,0) 25%,rgba(0,0,0,0) 70%,rgba(0,0,0,.6))');
    // siatka trójpodziału
    h += `<svg class="abs" style="left:0;top:0;opacity:.35" width="1080" height="1920"><g stroke="#fff" stroke-width="2"><path d="M360 0V1920M720 0V1920M0 640H1080M0 1280H1080"/></g></svg>`;
    h += hudCorners('#fff');
    // ramka AF
    const afs = 420 - 180 * oC(focus), locked = focus >= 1, col = locked ? '#3CFF7A' : '#fff';
    h += `<div class="abs" style="left:${560 - afs / 2}px;top:${900 - afs / 2}px;width:${afs}px;height:${afs}px;border:5px solid ${col};opacity:${locked && Math.floor(ct * 12) % 2 && ct < .7 ? .4 : 1}"></div>`;
    const recOn = Math.floor(ct * 3) % 2 === 0;
    h += `<div class="abs" style="left:110px;top:290px;display:flex;align-items:center;gap:16px;font:700 44px Inter;color:#fff"><span style="width:34px;height:34px;border-radius:17px;background:${recOn ? '#FF2A2A' : 'transparent'};box-shadow:0 0 30px #f22"></span>REC</div>`;
    h += `<div class="abs" style="right:110px;top:292px;font:700 42px Inter;color:#fff;text-align:right">4K · 30p</div>`;
    h += `<div class="abs" style="left:0;width:1080px;top:1470px;display:flex;justify-content:center;gap:56px;font:600 36px Inter;color:#fff;opacity:.9"><span>ISO 800</span><span>1/60</span><span>f/2.8</span><span>WB 3200K</span></div>`;
    const k2 = oB((ct - 0.45) / 0.3, 2.2);
    if (ct > 0.45) h += `<div class="stk" style="top:1150px;transform:scale(${0.6 + 0.4 * k2}) rotate(-3deg)"><span class="mk" style="font-size:112px;box-shadow:10px 10px 0 #000">2× SONY 4K</span></div>`;
  } else if (c[0] === 'light') {
    // to samo ujęcie, kolor światła zmienia się w rytm
    const step = Math.floor(ct / (bt / 2)); const hues = [0, 150, 230, 300][step % 4];
    const flashk = 1 - cl((ct % (bt / 2)) / 0.1);
    h += full(photoFill('104', .5, 1.1 - 0.05 * p, `filter:hue-rotate(${hues}deg) saturate(1.5) contrast(1.1) brightness(${1 + 0.25 * flashk})`));
    h += full('', 'background:linear-gradient(rgba(0,0,0,.4),rgba(0,0,0,0) 30%,rgba(0,0,0,0) 60%,rgba(0,0,0,.75))');
    const sw = ['#53FF6A', '#2AD8FF', '#7A5CFF', '#FF4FD8'];
    h += `<div class="abs" style="left:0;width:1080px;top:1260px;text-align:center;font-family:PopB;font-size:40px;letter-spacing:10px;color:${CR}">PROFESJONALNE</div>`;
    h += `<div class="stk" style="top:1320px;font-family:IDB;font-size:170px;color:${CR};line-height:1;transform:scale(${1 + 0.06 * flashk})">ŚWIATŁO</div>`;
    h += `<div class="abs" style="left:0;width:1080px;top:1530px;display:flex;justify-content:center;gap:30px">` +
      sw.map((s, i) => `<span style="width:${i === step % 4 ? 84 : 56}px;height:${i === step % 4 ? 84 : 56}px;border-radius:50%;background:${s};box-shadow:0 0 ${i === step % 4 ? 50 : 0}px ${s};border:5px solid ${i === step % 4 ? '#fff' : 'transparent'}"></span>`).join('') + `</div>`;
  } else if (c[0] === 'w') {
    const s = 1 + 0.9 * (1 - oE(ct / 0.2));
    h += full('', `background:${c[2]}`);
    const fs = c[4].length > 5 ? 150 : 300;
    h += `<div class="stk" style="top:${960 - fs * 0.55}px;font-family:IDB;font-size:${fs}px;color:${c[3]};transform:scale(${s});letter-spacing:-4px">${c[4]}</div>`;
  } else if (c[0] === 'four') {
    // 2x2 miejsca, numery wskakują po kolei
    const tiles = [['028', .55], ['010', .5], ['019', .3], ['001', .5]];
    const g = 10, tw = (1080 - g) / 2, th = (1920 - g) / 2;
    tiles.forEach(([code, fx], i) => {
      const ti = i * (bt / 2) * 0.9; const q = (ct - ti) / 0.22;
      if (q < 0) return;
      const x = (i % 2) * (tw + g), y = Math.floor(i / 2) * (th + g);
      h += `<div class="abs" style="left:${x}px;top:${y}px;width:${tw}px;height:${th}px;overflow:hidden;opacity:${cl(q * 3)}">
        <img src="img/${code}.jpg" style="position:absolute;height:${th}px;left:50%;transform:translateX(-${fx * 100}%) scale(${1.25 - 0.2 * oC(q)});transform-origin:${fx * 100}% 50%;filter:contrast(1.1) saturate(1.1)"></div>`;
      h += `<div class="abs" style="left:${x + tw / 2 - 70}px;top:${y + th / 2 - 70}px;width:140px;height:140px;border-radius:70px;background:${OR};color:#000;font:900 88px IDB;display:flex;align-items:center;justify-content:center;transform:scale(${oB(q, 2.6)});box-shadow:0 10px 40px rgba(0,0,0,.4)">${i + 1}</div>`;
    });
  } else if (c[0] === 'files') {
    h += full(photoFill('050', .42, 1.16 - 0.16 * oE(ct / 0.22), 'filter:contrast(1.12) saturate(1.2)'));
    h += full('', 'background:linear-gradient(transparent 50%,rgba(0,0,0,.6))');
    const s = oB(ct / 0.2, 2.4);
    h += `<div class="stk" style="top:1060px;transform:rotate(-4deg) scale(${0.5 + 0.5 * s})"><span class="mk" style="font-size:118px;background:${CR};box-shadow:10px 10px 0 #000">PLIKI OD RĘKI</span></div>`;
  } else if (c[0] === 'rec') {
    // ekran nagrywania: REC, licznik, poziomy audio, przebieg
    h += full(photoFill('053', .42, 1.15 - 0.08 * p, 'filter:contrast(1.15) saturate(1.1) brightness(.85)'));
    h += full('', 'background:radial-gradient(ellipse 80% 60% at 50% 45%,rgba(0,0,0,0),rgba(0,0,0,.7))');
    h += hudCorners('#fff');
    const pulse = 0.5 + 0.5 * Math.sin(ct * 10);
    h += `<div class="abs" style="left:110px;top:290px;display:flex;align-items:center;gap:18px;font:800 52px Inter;color:#fff"><span style="width:44px;height:44px;border-radius:22px;background:#FF2A2A;box-shadow:0 0 ${20 + 40 * pulse}px #f22"></span>REC</div>`;
    const sec = ct, ss = Math.floor(sec), ff = Math.floor((sec % 1) * 30);
    h += `<div class="abs" style="right:110px;top:294px;font:700 48px Inter;color:#fff">00:00:0${ss}:${String(ff).padStart(2, '0')}</div>`;
    // poziomy audio (4 kanały)
    for (let ch = 0; ch < 4; ch++) {
      const lv = 0.35 + 0.6 * Math.abs(Math.sin(ct * 13 + ch * 1.7)) * (0.6 + 0.4 * (1 - cl((ct % bt) / bt)));
      for (let s2 = 0; s2 < 16; s2++) {
        const on = s2 / 16 < lv, col = s2 > 12 ? '#FF2A2A' : (s2 > 9 ? '#FFC23A' : '#3CFF7A');
        h += `<div class="abs" style="left:${930 + ch * 26}px;top:${1500 - s2 * 26}px;width:18px;height:22px;background:${on ? col : 'rgba(255,255,255,.15)'}"></div>`;
      }
    }
    h += `<div class="abs" style="left:925px;top:1530px;font:600 24px Inter;color:#fff;opacity:.8">CH 1–4</div>`;
    // przebieg
    let path = 'M80 1700';
    for (let x = 0; x <= 920; x += 8) { const a = Math.sin(x * 0.045 + ct * 18) * Math.sin(x * 0.011 + ct * 3) * 70 * (0.5 + 0.5 * Math.abs(Math.sin(x * 0.02 + ct * 5))); path += ` L${80 + x} ${1700 + a}`; }
    h += `<svg class="abs" style="left:0;top:0" width="1080" height="1920"><path d="${path}" stroke="${OR}" stroke-width="6" fill="none"/></svg>`;
    const q = oB(ct / 0.25, 2.2);
    h += `<div class="stk" style="top:880px;font-family:IDB;font-size:128px;color:${CR};transform:scale(${0.6 + 0.4 * q});text-shadow:0 8px 40px rgba(0,0,0,.6)">NAGRYWASZ.</div>`;
  }
  // logo
  const darkTile = c[0] === 'w' && c[2] !== BK;
  if (c[0] !== 'four') h += `<img class="abs" src="${darkTile ? 'logo_black.png' : 'logo.png'}" style="left:440px;top:150px;width:200px">`;
  if (ct < 0.07) h += full('', `background:#fff;opacity:${0.7 * (1 - ct / .07)}`);
  return h;
}

const ROWS = [['PODCAST · ODCINEK 1', ''], ['Studio 2 h', '300 zł'], ['2 kamery 4K', '0 zł'], ['4× Shure SM7B', '0 zł'], ['Światło i tła', '0 zł'], ['Wymówki', '0 zł'], ['Stres', '0 zł']];
function sceneReceipt(t) {
  stage.style.transform = '';
  const lt = t - D.RECEIPT;
  let h = `<div class="abs" style="left:0;top:0;width:1080px;height:1920px;background:${CR}"></div>`;
  h += `<div class="stk" style="top:250px;opacity:${cl(lt / .2)}"><span style="font-family:IDB;font-size:96px;color:#000;line-height:1.05">Słuchaj,<br><span style="color:${OR}">nagrywam jutro!</span></span></div>`;
  const nShown = ROWS.filter((r, i) => lt >= D.ROWT[i] - D.RECEIPT).length;
  const hRow = 86, H0 = 200 + nShown * hRow + (lt >= D.TOT - D.RECEIPT ? 170 : 0);
  const y0 = 560 + (1 - oC(lt / 0.35)) * 900;
  let rows = '';
  ROWS.forEach((r, i) => {
    if (lt < D.ROWT[i] - D.RECEIPT) return;
    const z = r[1] === '0 zł';
    rows += `<div style="display:flex;justify-content:space-between;font-size:52px;height:${hRow}px;align-items:center;${i === 0 ? 'font-weight:700;border-bottom:4px dashed #999;margin-bottom:10px' : ''}"><span>${r[0]}</span><span style="color:${z ? OR : '#111'};font-weight:700">${r[1]}</span></div>`;
  });
  if (lt >= D.TOT - D.RECEIPT) rows += `<div style="border-top:4px dashed #999;margin-top:14px;padding-top:24px;display:flex;justify-content:space-between;font-family:IDB;font-size:84px"><span>RAZEM</span><span style="color:${OR}">300 zł</span></div>`;
  // ząbki paragonu (góra i dół)
  const zw = 40, zh = 22, nz = 960 / zw; let zp = [];
  for (let i = 0; i <= nz; i++) zp.push(`${i * zw}px ${i % 2 ? 0 : zh}px`);
  for (let i = nz; i >= 0; i--) zp.push(`${i * zw}px calc(100% - ${i % 2 ? 0 : zh}px)`);
  h += `<div class="abs" style="left:60px;top:${y0}px;width:960px;transform:rotate(-2deg);filter:drop-shadow(0 30px 40px rgba(0,0,0,.22))">
     <div class="rc" style="background:#fff;padding:${60 + zh}px 60px ${70 + zh}px;clip-path:polygon(${zp.join(',')})">
     <div style="text-align:center;margin-bottom:26px"><img src="logo_black.png" style="width:330px"></div>${rows}</div></div>`;
  if (t >= D.STAMP) {
    const k = (t - D.STAMP) / 0.22;
    h += `<div class="stk" style="top:1130px;transform:rotate(-12deg) scale(${3.2 - 2.2 * oE(k)});opacity:${cl(k * 3)}"><span style="display:inline-block;border:12px solid ${OR};color:${OR};font-family:IDB;font-size:130px;padding:10px 40px;border-radius:24px;background:rgba(255,255,255,.6)">NAGRANE ✓</span></div>`;
    const sh = (1 - cl((t - D.STAMP) / 0.25)) * 26;
    stage.style.transform = `translate(${(hash(Math.floor(t * 60), 4) - .5) * sh}px,${(hash(Math.floor(t * 60), 5) - .5) * sh}px)`;
  }
  return h;
}
function sceneEnd(t) {
  stage.style.transform = '';
  const lt = t - D.END;
  let h = `<div class="abs" style="left:0;top:0;width:1080px;height:1920px;background:${OR}"></div>`;
  for (let k = 0; k < 6; k++) { const p = cl(oC(lt / 0.45) * 1.5 - k * 0.08); h += `<div class="abs" style="left:${1080 * p}px;top:${k * 320}px;width:1080px;height:321px;background:${CR}"></div>`; }
  const s = 0.4 + 0.6 * oB((lt - 0.2) / 0.4, 2.2);
  if (lt > 0.2) h += `<div class="stk" style="top:520px;transform:scale(${s})"><img src="logo_black.png" style="width:760px"></div>`;
  if (lt > 0.45) h += `<div class="stk" style="top:900px;transform:scale(${0.6 + 0.4 * oB((lt - 0.45) / 0.3)}) rotate(-2deg)"><span style="display:inline-block;background:#000;color:${CR};font-family:IDB;font-size:88px;padding:30px 56px;border-radius:100px">gadkastudio.pl</span></div>`;
  if (lt > 0.75) h += `<div class="stk" style="top:1120px;opacity:${cl((lt - .75) / .25)};font-family:PopB;font-size:50px;color:#000">Warszawa · 2 h od 300 zł · sprzęt w cenie</div>`;
  if (lt > 1.0) h += `<div class="stk" style="top:1290px;opacity:${cl((lt - 1.0) / .25)};transform:translateY(${(1 - oC((lt - 1) / .3)) * 30}px)"><span class="mk" style="font-size:62px;transform:rotate(-3deg);white-space:normal;width:880px;line-height:1.15">Wyślij to temu, kto zaczyna „od następnego poniedziałku”</span></div>`;
  return h;
}

window.renderAt = function (t) {
  stage.style.transform = ''; stage.style.filter = '';
  let h;
  if (t < D.FREEZE) h = sceneNotifs(t);
  else if (t < D.DROP) h = sceneFreeze(t);
  else if (t < D.RECEIPT) h = sceneMontage(t);
  else if (t < D.END) h = sceneReceipt(t);
  else h = sceneEnd(t);
  // ziarno
  h += `<div class="abs" style="left:0;top:0;width:1080px;height:1920px;pointer-events:none;opacity:.07;mix-blend-mode:overlay;background-image:url(img/noise.png);background-position:${(hash(Math.floor(t * 30), 9) * 400) | 0}px ${(hash(Math.floor(t * 30), 8) * 400) | 0}px"></div>`;
  stage.innerHTML = h;
  return true;
};
Promise.all([document.fonts.ready]).then(() => {
  Promise.all([...document.images].map(i => i.decode().catch(() => 0))).then(() => setTimeout(() => window.READY = true, 400));
});
