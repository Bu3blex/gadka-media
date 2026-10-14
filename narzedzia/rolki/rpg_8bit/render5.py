"""Rolka retro RPG 8-bit + chiptune (wszystko syntetyczne)."""
import os, sys, json, time, wave, subprocess
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

WD = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WD, "..", "ai", "rolka_rpg_v2.mp4")
FPS, SR = 30, 44100
K_ = 1.35
SLOTT = [x * K_ for x in [0.6, 1.1, 1.6, 2.1]]
WARN, CHEST, OPEN, LOOT = [x * K_ for x in (2.8, 4.0, 5.3, 6.0)]
LOOTT = [x * K_ for x in [6.3, 7.1, 7.9, 8.7]]
LEVEL, COST, END = [x * K_ for x in (9.8, 11.8, 14.0)]
TOTAL = END + 4.4
DATA = dict(SLOTT=SLOTT, WARN=WARN, CHEST=CHEST, OPEN=OPEN, LOOT=LOOT, LOOTT=LOOTT, LEVEL=LEVEL, COST=COST, END=END, TOTAL=TOTAL)
open(os.path.join(WD, "data.js"), "w").write("window.DATA=" + json.dumps(DATA) + ";")
rng = np.random.default_rng(8)
L = int(TOTAL * SR) + SR
mix = np.zeros(L)
def tt(d): return np.arange(int(d * SR)) / SR
def add(sig, at, g=1.0):
    i = int(at * SR); j = min(L, i + len(sig))
    if 0 <= i < L: mix[i:j] += sig[:j - i] * g
NOTES = {'C': -9, 'C#': -8, 'D': -7, 'D#': -6, 'E': -5, 'F': -4, 'F#': -3, 'G': -2, 'G#': -1, 'A': 0, 'A#': 1, 'B': 2}
def nf(n):
    name, octv = n[:-1], int(n[-1]); return 440 * 2 ** ((NOTES[name] + (octv - 4) * 12) / 12)
def adsr(d, a=0.005, rel=0.03, sus=0.8):
    n = int(d * SR); e = np.ones(n) * sus; ai = max(1, int(a * SR)); e[:ai] = np.linspace(0, 1, ai)
    ri = min(n, int(rel * SR)); e[-ri:] *= np.linspace(1, 0, ri); return e
def sq(f, d, duty=0.5, g=1.0, sweep=None):
    t = tt(d); ff = f if sweep is None else np.linspace(f, sweep, len(t))
    ph = np.cumsum(np.broadcast_to(ff, t.shape)) / SR % 1.0
    return np.where(ph < duty, 1.0, -1.0) * adsr(d) * g
def tri(f, d, g=1.0):
    t = tt(d); ph = (f * t) % 1.0; return (4 * np.abs(ph - 0.5) - 1) * adsr(d, 0.002, 0.02, 1) * g
def noise(d, g=1.0, dec=0.05):
    n = int(d * SR); x = np.sign(rng.normal(0, 1, n)); x = np.repeat(x[::4], 4)[:n]
    return x * np.exp(-np.arange(n) / SR / dec) * g
def ckick(g=1.0):
    t = tt(0.12); return np.where((np.cumsum(np.linspace(220, 40, len(t))) / SR) % 1 < .5, 1, -1) * np.exp(-t / 0.05) * g

# --- A: smutne menu (A-moll, 110 BPM)
B = 60 / 100
melA = ['E5', None, 'C5', None, 'A4', None, 'B4', 'C5', 'D5', None, 'C5', 'B4', 'A4', None, None, None]
bassA = ['A2', 'A2', 'F2', 'F2', 'D2', 'D2', 'E2', 'E2']
for i in range(int(CHEST / (B / 2))):
    x = i * B / 2
    m = melA[i % 16]
    if m: add(sq(nf(m), B / 2 * 0.9, 0.25, 0.10), x)
    if i % 2 == 0: add(tri(nf(bassA[(i // 4) % 8]), B * 0.9, 0.25), x)
    if i % 4 == 0: add(ckick(0.25), x)
    if i % 4 == 2: add(noise(0.08, 0.10, 0.03), x)
for x in SLOTT: add(sq(300, 0.12, 0.5, 0.18, sweep=120), x)
for k in range(4): add(sq(880 if k % 2 == 0 else 660, 0.12, 0.5, 0.14), WARN + k * 0.25)
# --- skrzynia: napięcie
for k in range(14): add(noise(0.04, 0.12, 0.015), CHEST + 0.3 + k * 0.07)
for k in range(10): add(sq(nf('C4') * 2 ** (k / 12 * 1.2), 0.07, 0.25, 0.08), CHEST + 0.4 + k * 0.09)
arp = ['C5', 'E5', 'G5', 'C6', 'E6', 'G6', 'C7']
for k, n in enumerate(arp): add(sq(nf(n), 0.12, 0.25, 0.12), OPEN + k * 0.035)
add(sq(nf('C6'), 0.6, 0.5, 0.06), OPEN + 0.25); add(sq(nf('E6'), 0.6, 0.5, 0.05), OPEN + 0.25)
# --- B: wesoła pętla (C-dur, 140 BPM) od LOOT do końca
B2 = 60 / 126
arpB = [['C5', 'E5', 'G5', 'E5', 'C6', 'G5', 'E5', 'G5'], ['B4', 'D5', 'G5', 'D5', 'B5', 'G5', 'D5', 'G5'],
        ['A4', 'C5', 'E5', 'C5', 'A5', 'E5', 'C5', 'E5'], ['F4', 'A4', 'C5', 'A4', 'F5', 'C5', 'A4', 'G4']]
roots = ['C3', 'G2', 'A2', 'F2']
i = 0; x = LOOT
while x < TOTAL - 0.4:
    bar = (i // 8) % 4; n = arpB[bar][i % 8]
    soft = 0.6 if x >= END else 1.0
    add(sq(nf(n), B2 / 2 * 0.85, 0.25, 0.085 * soft), x)
    if i % 2 == 0: add(tri(nf(roots[bar]), B2 * 0.45, 0.32 * soft), x); add(tri(nf(roots[bar]) * 2, B2 * 0.4, 0.2 * soft), x + B2 / 2)
    if i % 4 == 0: add(ckick(0.35 * soft), x)
    if i % 4 == 2: add(noise(0.12, 0.16 * soft, 0.05), x)
    add(noise(0.02, 0.05 * soft, 0.006), x + B2 / 4)
    i += 1; x += B2 / 2
# zdobycze
for x in LOOTT:
    add(sq(400, 0.15, 0.5, 0.14, sweep=1600), x)
    for k in range(8): add(sq(nf('C5') * 2 ** (k / 8), 0.04, 0.25, 0.08), x + 0.15 + k * 0.06)
# level up fanfara
fan = [('C5', 0.0, .1), ('E5', .1, .1), ('G5', .2, .1), ('C6', .3, .5), ('A5', .85, .12), ('B5', .97, .12), ('C6', 1.09, .6)]
for n, st, d in fan: add(sq(nf(n), d, 0.5, 0.13), LEVEL + st); add(sq(nf(n) / 2, d, 0.25, 0.06), LEVEL + st)
# monety
for k in range(8): add(sq(nf('A5'), 0.06, 0.5, 0.11), COST + k * 0.1); add(sq(nf('E6'), 0.18, 0.5, 0.1), COST + k * 0.1 + 0.06)
# continue: odliczanie
for k in range(9): add(sq(nf('G5'), 0.05, 0.5, 0.08), END + k * 0.45)
for k, n in enumerate(['C5', 'G5', 'C6']): add(sq(nf(n), 0.18, 0.5, 0.1), END + 0.7 + k * 0.12)
m = mix[:int(TOTAL * SR)]
fo = int(0.6 * SR); m[-fo:] *= np.linspace(1, 0, fo)
m = np.convolve(m, np.ones(3) / 3, "same")
m = np.tanh(m * 1.05); m = m / np.abs(m).max() * 0.9
wav = os.path.join(WD, "_mix.wav")
with wave.open(wav, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    a = (m * 32767).astype(np.int16); w.writeframes(np.repeat(a[:, None], 2, 1).tobytes())
print("audio ok", round(TOTAL, 2))
# ---------------- obraz
srv = subprocess.Popen(["python3", "-m", "http.server", "8769"], cwd=WD, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
prev = os.environ.get("PREV")
try:
    with sync_playwright() as p:
        br = p.chromium.launch(args=["--force-device-scale-factor=1", "--no-proxy-server"])
        pg = br.new_page(viewport={"width": 1080, "height": 1920})
        pg.on("pageerror", lambda e: print("pageerror:", e))
        pg.goto("http://127.0.0.1:8769/index.html")
        pg.wait_for_function("window.READY===true", timeout=20000)
        def shot(t):
            pg.evaluate(f"(async()=>{{renderAt({t}); await Promise.all([...document.images].map(i=>i.decode().catch(()=>0)));}})()")
            return pg.screenshot(type="jpeg", quality=93)
        if prev:
            ims = []
            for t in [float(x) for x in prev.split(",")]:
                open(WD + "/_f.jpg", "wb").write(shot(t)); ims.append(Image.open(WD + "/_f.jpg").resize((270, 480)))
            sh = Image.new("RGB", (280 * len(ims), 480), "white")
            for i, m in enumerate(ims): sh.paste(m, (i * 280, 0))
            sh.save(WD + "/prev.jpg"); sys.exit()
        ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "image2pipe", "-c:v", "mjpeg", "-r", str(FPS), "-i", "-", "-i", wav,
                               "-shortest", "-c:v", "libx264", "-preset", "medium", "-b:v", "10M", "-maxrate", "12M", "-bufsize", "20M", "-pix_fmt", "yuv420p",
                               "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
        n = int(TOTAL * FPS); t0 = time.time()
        for i in range(n):
            ff.stdin.write(shot(i / FPS))
            if i % 100 == 0: print(i, n, round(time.time() - t0, 1), flush=True)
        ff.stdin.close(); ff.wait()
        print("ok", OUT)
finally:
    srv.terminate()
