// „Studio podcastowe w domu? Policzmy.” – koszyk zakupowy vs Gadka. renderAt(t) deterministycznie.
const D = window.DATA;
const stage = document.getElementById('stage');
const OR = '#FF592A', CR = '#F9EEE4', BK = '#141414', RED = '#E5281E';
const cl = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const oC = t => 1 - Math.pow(1 - cl(t), 3);
const oE = t => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * cl(t)));
const oB = (t, c1 = 1.8) => { t = cl(t); const c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); };
function hash(i, j) { const x = Math.sin(i * 127.1 + j * 311.7) * 43758.5453; return x - Math.floor(x); }
const fmt = n => Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');

const ITEMS = [
  ['🎙️', '4× Shure SM7B', 'mikrofon dynamiczny', 6636, ''],
  ['📷', '2× Sony ZV-E10', 'body, bez obiektywu', 3842, ''],
  ['🎚️', 'RØDECaster Pro II', 'mikser podcastowy', 2333, ''],
  ['💡', 'Oświetlenie studyjne', '2 lampy + statywy', 1200, 'ok. '],
  ['🎧', '4× słuchawki', 'odsłuch dla każdego', 800, 'ok. '],
  ['🦾', '4× ramię do mikrofonu', 'statywy biurkowe', 600, 'ok. '],
  ['🧽', 'Wygłuszenie pokoju', 'panele akustyczne', 1500, 'ok. '],
  ['🔌', 'Kable, karty, adaptery', 'bo zawsze czegoś brakuje', 300, 'ok. '],
  ['🛁', 'Pokój, który nie brzmi jak łazienka', 'niedostępny', null, ''],
];
const SUM = ITEMS.reduce((a, x) => a + (x[3] || 0), 0);
const ROWY = i => 430 + i * 106;

function totalAt(t) {
  // narastanie przy dodawaniu, spadek przy usuwaniu, potem 300
  if (t < D.DEL) {
    let v = 0;
    ITEMS.forEach((it, i) => { if (it[3]) v += it[3] * oC((t - D.ADD[i]) / 0.3); });
    return v;
  }
  if (t < D.GIN) return SUM * (1 - oC((t - D.DEL) / (D.GIN - D.DEL - 0.05)));
  return 300 * oC((t - D.GIN) / 0.35);
}
function header(t, mode) {
  let h = '';
  if (mode === 'shop') {
    const e = (t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2)(cl((t - D.FLY) / 0.5));
    const pin = oB((t - 0.05) / 0.35, 2), s0 = 1.16 * (0.6 + 0.4 * pin);
    const sc = s0 + (1 - s0) * e, dx = 35 * (1 - e), dy = 650 * (1 - e);
    h += `<div class="abs" style="left:60px;top:150px;font-family:IDB;font-size:76px;color:${BK};line-height:1.05;transform-origin:0 0;transform:translate(${dx}px,${dy}px) scale(${sc});opacity:${cl((t - .05) / .15)}">Studio podcastowe<br>w domu? <span style="color:${OR}">Policzmy.</span></div>`;
  } else {
    const s = cl((t - D.GIN) / 0.3);
    h += `<div class="abs" style="left:60px;top:150px;font-family:IDB;font-size:76px;color:#b9aca1;line-height:1.05;position:absolute">Studio podcastowe<br>w domu?
      <div class="abs" style="left:-6px;top:44px;height:10px;background:${OR};width:${700 * oC(s)}px"></div></div>`;
    h += `<div class="abs" style="left:60px;top:${330}px;font-family:IDB;font-size:96px;color:${OR};transform:scale(${0.6 + 0.4 * oB((t - D.GIN - .15) / .3)});transform-origin:0 50%;opacity:${cl((t - D.GIN - .1) / .1)}">Albo Gadka.</div>`;
  }
  // koszyk
  const n = mode === 'shop' ? ITEMS.filter((x, i) => t >= D.ADD[i]).length - (t >= D.DEL ? Math.floor(cl((t - D.DEL) / 0.7) * 9) : 0) : 1;
  const lastAdd = mode === 'shop' ? Math.max(...D.ADD.filter(x => x <= t), -9) : D.GIN;
  const bump = 1 + 0.35 * (1 - cl((t - lastAdd) / 0.18));
  if (mode === 'shop' && t < D.PANEL) return h;
  h += `<div class="abs" style="left:900px;top:150px;width:120px;height:120px;border-radius:30px;background:#fff;display:flex;align-items:center;justify-content:center;font-size:66px;box-shadow:0 6px 18px rgba(80,40,20,.1)">🛒</div>`;
  if (n > 0) h += `<div class="abs" style="left:985px;top:130px;min-width:56px;height:56px;padding:0 12px;border-radius:28px;background:${OR};color:#000;font:800 34px Inter;display:flex;align-items:center;justify-content:center;transform:scale(${bump})">${n}</div>`;
  return h;
}
function bottomBar(t, mode) {
  const tot = totalAt(t), alarm = mode === 'shop' && t >= D.ALARM && t < D.ALBO;
  const col = alarm ? RED : (mode === 'gadka' ? OR : BK);
  const flash = mode === 'shop' ? 1 + 0.06 * (1 - cl((t - Math.max(...D.ADD.filter(x => x <= t), -9)) / 0.2)) : 1;
  if (mode === 'shop' && t < D.PANEL) return '';
  const py = mode === 'shop' ? (1 - oB((t - D.PANEL) / 0.4, 1.4)) * 600 : 0;
  let h = `<div class="abs" style="left:0;top:${py}px;width:1080px;height:1920px">`;
  h += `<div class="abs" style="left:40px;top:1390px;width:1000px;height:300px;border-radius:40px;background:#fff;box-shadow:0 -6px 30px rgba(80,40,20,.08)"></div>`;
  h += `<div class="abs" style="left:90px;top:1430px;font:600 36px Inter;color:#8a7d72">Razem</div>`;
  h += `<div class="abs" style="left:90px;top:1478px;font:500 24px Inter;color:#b0a399">ceny orientacyjne</div>`;
  h += `<div class="abs" style="right:90px;top:1405px;font-family:IDB;font-size:104px;color:${col};transform:scale(${flash * (alarm ? 1 + 0.32 * oB((t - D.ALARM) / 0.3, 2.4) : 1)});transform-origin:100% 50%">${fmt(tot)} zł</div>`;
  let label = 'Do kasy', bg = OR, fg = '#000';
  if (mode === 'gadka') { label = 'Zarezerwuj · 300 zł'; if (t >= D.TAP + 0.12) { label = 'Zarezerwowano ✓'; bg = BK; fg = CR; } }
  const press = mode === 'gadka' ? 1 - 0.06 * Math.sin(Math.PI * cl((t - D.TAP) / 0.2)) : 1;
  h += `<div class="abs" style="left:80px;top:1560px;width:920px;height:100px;border-radius:50px;background:${bg};color:${fg};font:800 44px Inter;display:flex;align-items:center;justify-content:center;transform:scale(${press})">${label}</div>`;
  if (mode === 'gadka' && t >= D.TAP) {
    const r = 900 * oC((t - D.TAP) / 0.5), a = 1 - cl((t - D.TAP) / 0.5);
    h += `<div class="abs" style="left:${640 - r}px;top:${1610 - r}px;width:${2 * r}px;height:${2 * r}px;border-radius:50%;background:rgba(255,89,42,${0.35 * a})"></div>`;
  }
  if (alarm) {
    const k = oB((t - D.ALARM) / 0.25, 2.6);
    h += `<div class="abs" style="left:250px;top:1270px;font-size:120px;transform:scale(${k}) rotate(-12deg)">😳</div>`;
  }
  return h + '</div>';
}
function row(it, y, x = 0, extra = '') {
  const price = it[3] == null ? '<span style="color:#b0a399">???</span>' : `${it[4]}${fmt(it[3])} zł`;
  return `<div class="row" style="top:${y}px;transform:translateX(${x}px);${extra}"><div class="th">${it[0]}</div>
    <div class="nm">${it[1]}<small>${it[2]}</small></div><div class="pr">${price}</div></div>`;
}
function sceneShop(t) {
  let h = header(t, 'shop');
  ITEMS.forEach((it, i) => {
    const a = D.ADD[i]; if (t < a) return;
    let x = (1 - oB((t - a) / 0.32, 1.4)) * 1100;
    let bgx = '';
    if (t >= D.DEL) {
      const di = D.DEL + (ITEMS.length - 1 - i) * 0.075, q = oC((t - di) / 0.22);
      x = -1150 * q;
      if (t >= di && q < 1) h += `<div class="abs" style="left:50px;top:${ROWY(i)}px;width:980px;height:100px;border-radius:26px;background:${RED};color:#fff;font:800 36px Inter;display:flex;align-items:center;justify-content:flex-end;padding-right:40px">Usuń</div>`;
    }
    h += row(it, ROWY(i), x);
  });
  h += bottomBar(t, 'shop');
  if (t >= D.ALARM && t < D.ALBO) {
    const k = oB((t - D.ALARM - 0.1) / 0.25, 2.4);
    h += `<div class="stk" style="top:860px;transform:rotate(-5deg) scale(${0.5 + 0.5 * k})"><span class="mk" style="font-size:150px;background:${RED};color:#fff;box-shadow:10px 10px 0 #000">AŁA.</span></div>`;
    const sh = (1 - cl((t - D.ALARM) / 0.4)) * 30;
    stage.style.transform = `translate(${(hash(Math.floor(t * 60), 1) - .5) * sh}px,${(hash(Math.floor(t * 60), 2) - .5) * sh}px)`;
  }
  return h;
}
function sceneAlbo(t) {
  const lt = t - D.ALBO;
  const k = 1 + 0.6 * (1 - oE(lt / 0.25));
  return `<div class="abs" style="left:0;top:0;width:1080px;height:1920px;background:${BK}"></div>
   <div class="stk" style="top:800px;font-family:IDBI;font-size:230px;color:${CR};transform:scale(${k})">…albo</div>`;
}
const CHECKS = ['4× Shure SM7B', '2× Sony 4K', 'RØDECaster Pro II', 'Światło studyjne', 'Wygłuszona sala'];
function sceneGadka(t) {
  let h = header(t, 'gadka');
  const q = oB((t - D.GIN) / 0.4, 1.6);
  h += `<div class="row" style="top:520px;height:170px;border:5px solid ${OR};box-shadow:0 0 0 0, 0 20px 60px rgba(255,89,42,.35);transform:translateX(${(1 - q) * 1100}px)">
    <div class="th" style="width:120px;height:120px;border-radius:28px;background:${OR}"><img src="logo_black.png" style="width:100px"></div>
    <div class="nm" style="font-size:44px">Gadka studio · 2 h<small style="font-size:28px">wszystko z listy w cenie</small></div><div class="pr" style="font-size:54px;color:${OR}">300 zł</div></div>`;
  CHECKS.forEach((c, i) => {
    const ti = D.CHK + i * 0.3; if (t < ti) return;
    const k = oB((t - ti) / 0.25, 2);
    h += `<div class="abs" style="left:90px;top:${750 + i * 104}px;display:flex;align-items:center;gap:26px;transform:translateX(${(1 - k) * -60}px);opacity:${cl((t - ti) / .1)}">
      <span style="width:72px;height:72px;border-radius:36px;background:${OR};display:flex;align-items:center;justify-content:center;font:900 44px Inter;color:#000;transform:scale(${k})">✓</span>
      <span style="font:700 48px Inter;color:${BK}">${c}</span><span style="font:600 34px Inter;color:#b0a399">· w cenie</span></div>`;
  });
  h += bottomBar(t, 'gadka');
  // palec
  if (t >= D.TAP - 0.45) {
    const m = oC((t - D.TAP + 0.45) / 0.4); const x = 900 - 260 * m, y = 1850 - 210 * m;
    const s = t >= D.TAP && t < D.TAP + 0.15 ? 0.88 : 1;
    h += `<div class="abs" style="left:${x}px;top:${y}px;font-size:150px;transform:scale(${s});filter:drop-shadow(0 10px 20px rgba(0,0,0,.25))">👆</div>`;
  }
  // konfetti
  if (t >= D.TAP + 0.1) {
    const q2 = t - D.TAP - 0.1;
    for (let i = 0; i < 70; i++) {
      const a = hash(i, 1) * Math.PI - Math.PI, sp = 700 + hash(i, 2) * 1100;
      const x = 640 + Math.cos(a) * sp * q2, y = 1600 + Math.sin(a) * sp * q2 + 1500 * q2 * q2;
      const col = [OR, BK, '#FFC9A8', '#FFFFFF'][i % 4];
      if (y < 1950) h += `<div class="abs" style="left:${x}px;top:${y}px;width:22px;height:34px;background:${col};transform:rotate(${q2 * 900 * (hash(i, 3) - .5)}deg)"></div>`;
    }
  }
  return h;
}
const PROOF = [['053', .45, '4× Shure SM7B', '6 636 zł'], ['101', .3, '2× Sony ZV-E10', '3 842 zł', 'cam'], ['050', .55, 'RØDECaster Pro II', '2 333 zł'], ['104', .5, 'Światło studyjne', 'ok. 1 200 zł']];
function sceneProof(t) {
  const lt = t - D.PROOF, k = Math.min(PROOF.length - 1, Math.floor(lt / D.PCUT)), ct = lt - k * D.PCUT; const p = PROOF[k];
  let h = `<div class="abs" style="left:0;top:0;width:1080px;height:1920px;overflow:hidden">
    <img src="img/${p[0]}.jpg" style="position:absolute;height:1920px;left:50%;transform:translateX(-${p[1] * 100}%) scale(${1.2 - 0.1 * oE(ct / .3) - 0.05 * ct}) rotate(${(k % 2 ? 1 : -1) * (1 - oE(ct / .3)) * 2}deg);transform-origin:${p[1] * 100}% 50%;filter:contrast(1.1) saturate(1.15)"></div>`;
  h += `<div class="abs" style="left:0;top:0;width:1080px;height:1920px;background:linear-gradient(transparent 45%,rgba(0,0,0,.55))"></div>`;
  if (p[4] === 'cam') {
    const focus = cl(ct / 0.35), afs = 420 - 190 * oC(focus), locked = focus >= 1, col = locked ? '#3CFF7A' : '#fff';
    h = h.replace('filter:contrast(1.1) saturate(1.15)', `filter:blur(${((1 - oC(focus)) * 12).toFixed(1)}px) contrast(1.1) saturate(1.15)`);
    h += `<svg class="abs" style="left:0;top:0;opacity:.3" width="1080" height="1920"><g stroke="#fff" stroke-width="2"><path d="M360 0V1920M720 0V1920M0 640H1080M0 1280H1080"/></g></svg>`;
    h += `<svg class="abs" style="left:0;top:0" width="1080" height="1920"><g stroke="#fff" stroke-width="7" fill="none">
      <path d="M90 380 V260 H210"/><path d="M870 260 H990 V380"/><path d="M90 1480 V1600 H210"/><path d="M870 1600 H990 V1480"/></g></svg>`;
    h += `<div class="abs" style="left:${520 - afs / 2}px;top:${820 - afs / 2}px;width:${afs}px;height:${afs}px;border:5px solid ${col}"></div>`;
    const recOn = Math.floor(ct * 3) % 2 === 0;
    h += `<div class="abs" style="left:110px;top:290px;display:flex;align-items:center;gap:16px;font:700 44px Inter;color:#fff"><span style="width:34px;height:34px;border-radius:17px;background:${recOn ? '#FF2A2A' : 'transparent'};box-shadow:0 0 30px #f22"></span>REC</div>`;
    h += `<div class="abs" style="right:110px;top:292px;font:700 42px Inter;color:#fff">4K · 30p</div>`;
  }
  // metka cenowa
  const s = oB(ct / 0.22, 2.2);
  h += `<div class="abs" style="left:170px;top:1150px;width:740px;padding:34px 44px;border-radius:30px;background:#fff;transform:rotate(-4deg) scale(${0.6 + 0.4 * s});box-shadow:12px 12px 0 #000">
    <div style="font:800 54px Inter;color:${BK}">${p[2]}</div>
    <div style="display:flex;align-items:center;gap:28px;margin-top:10px"><span style="font:700 46px Inter;color:#b0a399;text-decoration:line-through;text-decoration-color:${RED};text-decoration-thickness:6px">${p[3]}</span>
    <span style="font-family:IDB;font-size:64px;color:${OR}">W CENIE</span></div></div>`;
  h += `<img class="abs" src="logo.png" style="left:440px;top:150px;width:200px">`;
  if (ct < 0.07) h += `<div class="abs" style="left:0;top:0;width:1080px;height:1920px;background:#fff;opacity:${0.7 * (1 - ct / .07)}"></div>`;
  return h;
}
function sceneCheap(t) {
  const lt = t - D.CHEAP;
  let h = `<div class="abs" style="left:0;top:0;width:1080px;height:1920px;background:${CR}"></div>`;
  const a = oB(lt / 0.3, 2);
  h += `<div class="abs" style="left:80px;top:430px;width:920px;display:flex;justify-content:space-between;align-items:baseline;opacity:${cl(lt / .15)};transform:translateY(${(1 - a) * 40}px)">
     <span style="font:700 56px Inter;color:${BK}">1 mikrofon</span><span style="font-family:IDB;font-size:96px;color:${BK};position:relative">1 659 zł
     <span style="position:absolute;left:-10px;top:52px;height:12px;background:${RED};width:${(lt > .45 ? 1 : 0) * 360 * oC((lt - .45) / .2)}px;transform:rotate(-6deg)"></span></span></div>`;
  if (lt > 0.75) {
    const b = oB((lt - 0.75) / 0.3, 2.4);
    h += `<div class="abs" style="left:80px;top:620px;width:920px;display:flex;justify-content:space-between;align-items:baseline;transform:scale(${0.6 + 0.4 * b});transform-origin:50% 50%">
     <span style="font:700 56px Inter;color:${BK}">całe studio, 2 h</span><span style="font-family:IDB;font-size:130px;color:${OR}">300 zł</span></div>`;
  }
  if (lt > 1.2) {
    const c = oB((lt - 1.2) / 0.3, 2.2);
    h += `<div class="stk" style="top:920px;opacity:${cl((lt - 1.2) / .2)}"><img src="logo_black.png" style="width:420px"></div>`;
    h += `<div class="stk" style="top:1120px;transform:rotate(-3deg) scale(${0.5 + 0.5 * c})"><span class="mk" style="font-size:104px;box-shadow:10px 10px 0 #000">taniej niż</span></div>`;
    h += `<div class="stk" style="top:1265px;transform:rotate(-3deg) scale(${(0.5 + 0.5 * oB((lt - 1.35) / 0.3, 2.2)) * (1 + 0.02 * Math.sin((lt - 1.35) * 6))})"><span class="mk" style="font-size:104px;background:${BK};color:${CR};box-shadow:10px 10px 0 ${OR}">jeden mikrofon.</span></div>`;
  }
  return h;
}
function sceneEnd(t) {
  const lt = t - D.END;
  let h = `<div class="abs" style="left:0;top:0;width:1080px;height:1920px;background:${BK}"></div>`;
  const R = 2300 * oC(lt / 0.45);
  h = `<div class="abs" style="left:0;top:0;width:1080px;height:1920px;background:${CR}"></div><div class="abs" style="left:${540 - R}px;top:${960 - R}px;width:${2 * R}px;height:${2 * R}px;border-radius:50%;background:${BK}"></div>`;
  if (lt > 0.2) h += `<div class="stk" style="top:500px;transform:scale(${0.4 + 0.6 * oB((lt - .2) / .4, 2.2)})"><img src="logo.png" style="width:760px"></div>`;
  if (lt > 0.45) h += `<div class="stk" style="top:880px;transform:scale(${0.6 + 0.4 * oB((lt - .45) / .3)}) rotate(-2deg)"><span style="display:inline-block;background:${OR};color:#000;font-family:IDB;font-size:88px;padding:30px 56px;border-radius:100px">gadkastudio.pl</span></div>`;
  if (lt > 0.75) h += `<div class="stk" style="top:1100px;opacity:${cl((lt - .75) / .25)};font-family:PopB;font-size:48px;color:${CR}">Warszawa · 2 h od 300 zł · sprzęt w cenie</div>`;
  if (lt > 1.0) h += `<div class="stk" style="top:1260px;opacity:${cl((lt - 1) / .25)};transform:translateY(${(1 - oC((lt - 1) / .3)) * 30}px)"><span class="mk" style="font-size:60px;white-space:normal;width:880px;line-height:1.15;background:${CR};transform:rotate(-3deg)">Pierwszy odcinek? Nagraj go u nas.</span></div>`;
  return h;
}
window.renderAt = function (t) {
  stage.style.transform = '';
  let h;
  if (t < D.ALBO) h = sceneShop(t);
  else if (t < D.DEL) h = sceneAlbo(t);
  else if (t < D.GIN) h = sceneShop(t);
  else if (t < D.PROOF) h = sceneGadka(t);
  else if (t < D.CHEAP) h = sceneProof(t);
  else if (t < D.END) h = sceneCheap(t);
  else h = sceneEnd(t);
  h += `<div class="abs" style="left:0;top:0;width:1080px;height:1920px;pointer-events:none;opacity:.05;mix-blend-mode:multiply;background-image:url(img/noise.png);background-position:${(hash(Math.floor(t * 30), 9) * 400) | 0}px ${(hash(Math.floor(t * 30), 8) * 400) | 0}px"></div>`;
  stage.innerHTML = h;
  return true;
};
document.fonts.ready.then(() => setTimeout(() => window.READY = true, 400));
