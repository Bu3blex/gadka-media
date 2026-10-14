// Retro RPG 8-bit: „NAGRYWASZ PODCAST TELEFONEM?” – canvas 270x480 skalowany 4x pikselowo. renderAt(t)
const D = window.DATA;
const cv = document.getElementById('c'), g = cv.getContext('2d');
g.imageSmoothingEnabled = false;
const W = 270, H = 480;
const C = { bg: '#14112B', bg2: '#1E1A44', panel: '#231F52', edge: '#6F68D9', text: '#F9EEE4', dim: '#8D86C9', or: '#FF592A', red: '#FF4D5A', green: '#5BE37D', gold: '#FFC83D', epic: '#B57BFF', rare: '#4FB3FF', black: '#0A0918', white: '#FFFFFF' };
const cl = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
function hash(i, j) { const x = Math.sin(i * 127.1 + j * 311.7) * 43758.5453; return x - Math.floor(x); }

// ---------------- pikselowa czcionka 5x7 z polskimi znakami
const F = {
  A: '.###.#...##...#######...##...##...#', B: '####.#...##...#####.#...##...#####.', C: '.###.#...##....#....#....#...#.###.',
  D: '####.#...##...##...##...##...#####.', E: '######....#....####.#....#....#####', F: '######....#....####.#....#....#....',
  G: '.###.#...##....#.####...##...#.####', H: '#...##...##...#######...##...##...#', I: '.###...#....#....#....#....#...###.',
  J: '..###...#....#....#....#.#..#..##..', K: '#...##..#.#.#..##...#.#..#..#.#...#', L: '#....#....#....#....#....#....#####',
  M: '#...###.###.#.##.#.##...##...##...#', N: '#...##...###..##.#.##..###...##...#', O: '.###.#...##...##...##...##...#.###.',
  P: '####.#...##...#####.#....#....#....', Q: '.###.#...##...##...##.#.##..#..##.#', R: '####.#...##...#####.#.#..#..#.#...#',
  S: '.#####....#.....###.....#....#####.', T: '#####..#....#....#....#....#....#..', U: '#...##...##...##...##...##...#.###.',
  V: '#...##...##...##...##...#.#.#...#..', W: '#...##...##...##.#.##.#.##.#.#.#.#.', X: '#...##...#.#.#...#...#.#.#...##...#',
  Y: '#...##...#.#.#...#....#....#....#..', Z: '#####....#...#...#...#...#....#####',
  '0': '.###.#...##..###.#.###..##...#.###.', '1': '..#...##....#....#....#....#...###.', '2': '.###.#...#....#...#...#...#...#####',
  '3': '####.....#....#.###.....#....#####.', '4': '...#...##..#.#.#..#.#####...#....#.', '5': '######....####.....#....##...#.###.',
  '6': '.###.#....#....####.#...##...#.###.', '7': '#####....#...#...#...#....#....#...', '8': '.###.#...##...#.###.#...##...#.###.',
  '9': '.###.#...##...#.####....#....#.###.', ' ': '...................................',
  '.': '..........................##...##..', ',': '.....................##...#...#....', ':': '.....##...##.........##...##.......',
  '!': '..#....#....#....#....#.........#..', '?': '.###.#...#...#...#....#.........#..', '-': '................###................',
  '+': '.......#....#..#####..#....#.......', '/': '....#...#....#...#...#....#...#....', '×': '.....#...#.#.#...#...#.#.#...#.....',
  '(': '...#...#...#....#....#.....#.....#.', ')': '.#.....#.....#....#....#...#...#...', '[': '.###..#....#....#....#....#....###.',
  ']': '.###....#....#....#....#....#..###.', '%': '##..###.#....#...#...#....#.###..##', '>': '.#.....#.....#.....#...#...#...#...',
  "'": '..#....#...........................', '=': '..........#####.....#####..........', '▶': '#....##...###..####.###..##...#....',
  '♥': '......#.#.##########.###...#.......', 'Ł': '.#....#....#.#..##..##....#....####',
  '„': '..........................#.#.#.#..', '”': '.#.#..#.#.#.#......................',
};
const ACC = { 'Ą': ['A', 'og'], 'Ć': ['C', 'ac'], 'Ę': ['E', 'og'], 'Ń': ['N', 'ac'], 'Ó': ['O', 'ac'], 'Ś': ['S', 'ac'], 'Ź': ['Z', 'ac'], 'Ż': ['Z', 'dot'] };
function glyph(ch, x, y, s, col) {
  let k = ch, acc = null;
  if (ACC[ch]) { [k, acc] = ACC[ch]; }
  const p = F[k] || F['?'];
  g.fillStyle = col;
  for (let r = 0; r < 7; r++) for (let c = 0; c < 5; c++) if (p[r * 5 + c] === '#') g.fillRect(x + c * s, y + r * s, s, s);
  if (acc === 'ac') { g.fillRect(x + 3 * s, y - 2 * s, s, s); g.fillRect(x + 2 * s, y - 1 * s, s, s); }
  if (acc === 'dot') { g.fillRect(x + 2 * s, y - 2 * s, s, s); }
  if (acc === 'og') { g.fillRect(x + 3 * s, y + 7 * s, s, s); g.fillRect(x + 4 * s, y + 8 * s, s, s); }
}
function tw(str, s = 1) { return str.length * 6 * s - s; }
function T(str, x, y, s = 1, col = C.text, align = 'l', shadow = true) {
  str = str.toUpperCase();
  if (align === 'c') x = Math.round(x - tw(str, s) / 2);
  if (align === 'r') x = Math.round(x - tw(str, s));
  [...str].forEach((ch, i) => {
    if (shadow) glyph(ch, x + i * 6 * s + s, y + s, s, C.black);
    glyph(ch, x + i * 6 * s, y, s, col);
  });
}
function rect(x, y, w, h, col) { g.fillStyle = col; g.fillRect(Math.round(x), Math.round(y), Math.round(w), Math.round(h)); }
function frame(x, y, w, h, fill = C.panel, edge = C.edge) {
  rect(x, y, w, h, edge); rect(x + 2, y + 2, w - 4, h - 4, C.black); rect(x + 3, y + 3, w - 6, h - 6, fill);
}

// ---------------- sprite'y (rysowane prostokątami)
const SPR = {
  phone(x, y) { rect(x + 8, y + 3, 12, 22, C.black); rect(x + 9, y + 4, 10, 18, '#3A7BD5'); rect(x + 13, y + 23, 2, 1, '#888'); },
  laptop(x, y) { rect(x + 4, y + 6, 20, 13, '#9AA0B4'); rect(x + 6, y + 8, 16, 9, '#2C3550'); rect(x + 2, y + 19, 24, 3, '#C8CCD8'); },
  lamp(x, y) { rect(x + 6, y + 23, 14, 2, '#666'); rect(x + 12, y + 12, 2, 11, '#888'); rect(x + 8, y + 6, 12, 7, '#E8C547'); rect(x + 10, y + 13, 8, 2, '#FFF3A0'); },
  pan(x, y) { rect(x + 4, y + 10, 16, 8, '#555B66'); rect(x + 5, y + 11, 14, 6, '#3C414A'); rect(x + 20, y + 12, 7, 3, '#8A5A2B'); rect(x + 9, y + 4, 2, 4, '#DDD'); rect(x + 13, y + 2, 2, 5, '#DDD'); },
  mic(x, y) {
    rect(x + 9, y + 2, 10, 15, '#2B2B33'); rect(x + 10, y + 3, 8, 13, '#3F3F4A');
    for (let k = 0; k < 6; k++) rect(x + 10, y + 4 + k * 2, 8, 1, '#5A5A68');
    rect(x + 7, y + 8, 2, 10, '#777'); rect(x + 19, y + 8, 2, 10, '#777'); rect(x + 7, y + 17, 14, 2, '#777'); rect(x + 13, y + 19, 2, 6, '#999');
  },
  cam(x, y) {
    rect(x + 3, y + 8, 20, 13, '#22222A'); rect(x + 5, y + 6, 7, 3, '#22222A'); rect(x + 10, y + 10, 10, 10, '#555'); rect(x + 12, y + 12, 6, 6, '#1B6FD1'); rect(x + 13, y + 13, 2, 2, '#9FD0FF');
    rect(x + 20, y + 9, 2, 2, C.or); rect(x + 4, y + 22, 2, 4, '#888'); rect(x + 20, y + 22, 2, 4, '#888');
  },
  softbox(x, y) { rect(x + 4, y + 3, 20, 14, '#FFFFFF'); rect(x + 6, y + 5, 16, 10, '#FFF6D6'); rect(x + 13, y + 17, 2, 8, '#999'); rect(x + 8, y + 24, 12, 2, '#777'); },
  studio(x, y) {
    rect(x + 3, y + 3, 22, 22, C.or);
    const hts = [4, 8, 12, 16, 10, 6, 12, 8];
    hts.forEach((h, i) => rect(x + 5 + i * 2.5, y + 14 - h / 2, 2, h, C.black));
  },
};
function slot(x, y, sprite, label, item, bonus, colBonus, glow = 0, rarityCol = null) {
  frame(x, y, 32, 32, C.bg2, rarityCol || C.edge);
  if (glow > 0) { g.globalAlpha = glow; rect(x - 3, y - 3, 38, 38, rarityCol); g.globalAlpha = 1; frame(x, y, 32, 32, C.bg2, rarityCol); }
  SPR[sprite](x + 2, y + 3);
  T(label, x + 40, y - 1, 1, C.dim);
  T(item, x + 40, y + 9, 2, C.text);
  if (bonus) T(bonus, x + 40, y + 26, 1, colBonus);
}
function bar(x, y, label, val, col, max = 100) {
  T(label, x, y, 1, C.text);
  const bx = x + 52, n = 22;
  for (let i = 0; i < n; i++) rect(bx + i * 7, y - 2, 6, 11, i < Math.round(val / max * n) ? col : '#2E2A5A');
  T(String(Math.round(val)), bx + n * 7 + 4, y - 3, 2, col);
}
function stars() {
  for (let i = 0; i < 60; i++) { const x = (hash(i, 1) * W) | 0, y = (hash(i, 2) * H) | 0; rect(x, y, 1, 1, hash(i, 3) > .5 ? '#3B3580' : '#2A2560'); }
}
function scanlines() { g.globalAlpha = 0.12; for (let y = 0; y < H; y += 2) rect(0, y, W, 1, '#000'); g.globalAlpha = 1; }

// ---------------- dane przedmiotów
const BAD = [['phone', 'MIKROFON:', 'TELEFON', '+1'], ['laptop', 'KAMERA:', 'LAPTOP 720P', '+2'], ['lamp', 'ŚWIATŁO:', 'LAMPKA Z IKEI'.replace(' Z IKEI', ' NOCNA'), '+1'], ['pan', 'POKÓJ:', 'KUCHNIA', '-10']];
const GOOD = [['mic', 'MIKROFON:', '4× SHURE SM7B', 'LEGENDARNY', C.gold], ['cam', 'KAMERA:', '2× SONY 4K', 'EPICKI', C.epic], ['softbox', 'ŚWIATŁO:', 'STUDYJNE + RGB', 'RZADKI', C.rare], ['studio', 'POKÓJ:', 'WYGŁUSZONA SALA', 'LEGENDARNY', C.gold]];
const STAT0 = [['DŹWIĘK', 12], ['OBRAZ', 18], ['ŚWIATŁO', 7], ['ECHO', 99]];
const STAT1 = [98, 96, 95, 3];

function sceneInventory(t) {
  rect(0, 0, W, H, C.bg); stars();
  // tytuł
  const blinkTitle = 1;
  if (t < D.LOOT) { T('NAGRYWASZ', W / 2, 26, 3, C.text, 'c'); T('PODCAST', W / 2, 52, 3, C.text, 'c'); T('TELEFONEM?', W / 2, 78, 3, C.or, 'c'); }
  else { T('A TERAZ', W / 2, 26, 3, C.text, 'c'); T('NAGRYWASZ', W / 2, 52, 3, C.text, 'c'); T('W GADCE!', W / 2, 78, 3, C.or, 'c'); }
  // ekwipunek
  frame(6, 106, 258, 186);
  T('EKWIPUNEK', 20, 118, 1, C.gold);
  const upgraded = t >= D.LOOT;
  for (let i = 0; i < 4; i++) {
    const y = 130 + i * 40;
    if (!upgraded || t < D.LOOTT[i]) {
      if (t >= D.SLOTT[i]) {
        const sh = t < D.SLOTT[i] + 0.12 ? ((Math.floor(t * 60) % 2) ? 1 : -1) : 0;
        slot(18 + sh, y, BAD[i][0], BAD[i][1], BAD[i][2], BAD[i][3], BAD[i][3][0] === '-' ? C.red : C.dim);
      }
    } else {
      const k = cl((t - D.LOOTT[i]) / 0.4);
      slot(18, y, GOOD[i][0], GOOD[i][1], GOOD[i][2], GOOD[i][3], GOOD[i][4], (1 - k) * 0.8, GOOD[i][4]);
    }
  }
  // statystyki
  frame(6, 298, 258, 100);
  T('STATYSTYKI', 16, 306, 1, C.gold);
  STAT0.forEach(([lab, v0], i) => {
    let v = v0 * cl((t - D.SLOTT[i]) / 0.3), col = i === 3 ? C.red : C.red;
    if (upgraded && t >= D.LOOTT[i]) { const k = cl((t - D.LOOTT[i] - 0.15) / 0.5); v = v0 + (STAT1[i] - v0) * k; col = C.green; }
    if (i === 3 && !upgraded) col = C.red;
    bar(16, 322 + i * 18, lab, v, col);
  });
  // ostrzeżenie
  if (t >= D.WARN && !upgraded && Math.floor(t * 4) % 2 === 0) { frame(20, 404, 230, 28, '#4A0F1A', C.red); T('UWAGA: ECHO 99%!', W / 2, 411, 2, C.red, 'c'); }
  return true;
}
function sceneChest(t) {
  const lt = t - D.CHEST;
  rect(0, 0, W, H, C.bg); stars();
  T('!', W / 2, 70, 5, C.gold, 'c');
  T('ZNALEZIONO', W / 2, 120, 2, C.text, 'c');
  T('SKRZYNIĘ:', W / 2, 142, 2, C.text, 'c');
  T('GADKA STUDIO', W / 2, 168, 2, C.or, 'c');
  const cx = 135, cy = 270, open = cl((t - D.OPEN) / 0.25);
  // promienie
  if (open > 0) {
    g.save(); g.translate(cx, cy - 10); g.rotate(lt * 0.8);
    for (let i = 0; i < 12; i++) { g.rotate(Math.PI / 6); g.fillStyle = i % 2 ? 'rgba(255,200,61,.35)' : 'rgba(255,89,42,.25)'; g.beginPath(); g.moveTo(0, 0); g.lineTo(200, -14); g.lineTo(200, 14); g.fill(); }
    g.restore();
    for (let i = 0; i < 30; i++) { const a = hash(i, 4) * Math.PI * 2, r = (t - D.OPEN) * (60 + 120 * hash(i, 5)); rect(cx + Math.cos(a) * r, cy - 10 + Math.sin(a) * r, 2, 2, [C.gold, C.or, C.white][i % 3]); }
  }
  const shake = open === 0 && lt > 0.3 ? ((Math.floor(t * 30) % 2) ? 3 : -3) * cl((lt - 0.3) / 0.6) : 0;
  const k2 = 2, x = cx - 30 * k2 + shake, y = cy - 10;
  const R2 = (a, b, w, h, c) => rect(x + a * k2, y + b * k2, w * k2, h * k2, c);
  R2(0, 0, 60, 34, '#6B3A1A'); R2(2, 2, 56, 30, '#8A4E24'); R2(0, 12, 60, 3, C.gold); R2(26, 8, 8, 10, C.gold); R2(28, 11, 4, 4, '#6B3A1A');
  const ly = -18 - open * 16;
  R2(0, ly, 60, 18, '#6B3A1A'); R2(2, ly + 2, 56, 14, '#9A5A2C'); R2(0, ly + 14, 60, 3, C.gold);
  if (open > 0) { g.globalAlpha = 0.9; R2(4, -4, 52, 6, '#FFF3B0'); g.globalAlpha = 1; }
  T('LOOT: X4', W / 2, 380, 2, C.dim, 'c');
  return true;
}
function sceneLevel(t) {
  const lt = t - D.LEVEL;
  rect(0, 0, W, H, C.bg); stars();
  const cols = [C.gold, C.or, C.green, C.rare, C.epic];
  const col = cols[Math.floor(lt * 10) % cols.length];
  const s = lt < 0.15 ? 6 : 5;
  T('LEVEL', W / 2, 110, s, col, 'c'); T('UP!', W / 2, 160, s, col, 'c');
  T('NOWY POZIOM:', W / 2, 226, 2, C.dim, 'c');
  T('PODCASTER PRO', W / 2, 244, 2, C.text, 'c');
  for (let i = 0; i < 50; i++) {
    const x = hash(i, 7) * W, y = ((hash(i, 8) * H + lt * (60 + 80 * hash(i, 9))) % H);
    rect(x, y, 3, 3, cols[i % 5]);
  }
  // podsumowanie statystyk
  frame(16, 280, 238, 96);
  ['DŹWIĘK 98', 'OBRAZ 96', 'ŚWIATŁO 95', 'ECHO 3'].forEach((s2, i) => T(s2, W / 2, 292 + i * 20, 2, C.green, 'c'));
  return true;
}
function sceneCost(t) {
  const lt = t - D.COST;
  rect(0, 0, W, H, C.bg); stars();
  T('KOSZT', W / 2, 90, 3, C.text, 'c'); T('ULEPSZENIA:', W / 2, 118, 3, C.text, 'c');
  const v = Math.round(300 * cl(lt / 0.8));
  T(v + ' ZŁ', W / 2, 170, 5, C.gold, 'c');
  T('ZA 2 H W STUDIU', W / 2, 220, 2, C.text, 'c');
  if (lt > 0.9) { frame(30, 248, 210, 32, '#173D24', C.green); T('SPRZĘT W CENIE', W / 2, 257, 2, C.green, 'c'); }
  // monety
  for (let i = 0; i < 8; i++) {
    const q = lt - i * 0.1; if (q < 0) continue;
    const x = 40 + i * 26, y = 330 - Math.max(0, 40 * Math.sin(Math.min(Math.PI, q * 6)));
    rect(x, y, 10, 10, C.gold); rect(x + 2, y + 2, 6, 6, '#E0A520'); rect(x + 4, y + 3, 2, 4, C.gold);
  }
  return true;
}
function sceneEnd(t) {
  const lt = t - D.END;
  rect(0, 0, W, H, C.bg); stars();
  const n = Math.max(0, 9 - Math.floor(lt / 0.45));
  T('CONTINUE?', W / 2, 60, 3, C.text, 'c');
  T(String(n), W / 2, 96, 4, C.or, 'c');
  const lg = document.getElementById('logo');
  if (lt > 0.4) { const w = 170, h = Math.round(lg.naturalHeight * w / lg.naturalWidth); g.drawImage(lg, Math.round(W / 2 - w / 2), 150, w, h); }
  if (lt > 0.7) { frame(30, 236, 210, 30, C.or, C.gold); T('GADKASTUDIO.PL', W / 2, 247, 2, C.black, 'c', false); }
  if (lt > 1.0) T('2 H OD 300 ZŁ', W / 2, 282, 2, C.text, 'c');
  if (lt > 1.3 && Math.floor(lt * 3) % 2 === 0) T('▶ REZERWUJ ONLINE', W / 2, 318, 2, C.gold, 'c');
  return true;
}
window.renderAt = function (t) {
  g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1;
  if (t < D.CHEST) sceneInventory(t);
  else if (t < D.LOOT) sceneChest(t);
  else if (t < D.LEVEL) sceneInventory(t);
  else if (t < D.COST) sceneLevel(t);
  else if (t < D.END) sceneCost(t);
  else sceneEnd(t);
  // przejście: pikselowy błysk
  const cuts = [D.CHEST, D.LOOT, D.LEVEL, D.COST, D.END];
  cuts.forEach(c => { const k = (t - c) / 0.1; if (k >= 0 && k < 1) { g.globalAlpha = 1 - k; rect(0, 0, W, H, '#FFFFFF'); g.globalAlpha = 1; } });
  scanlines();
  return true;
};
Promise.all([document.getElementById('logo').decode()]).then(() => setTimeout(() => window.READY = true, 200));
