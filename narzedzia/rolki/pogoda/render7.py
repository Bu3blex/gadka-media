"""Rolka „prognoza pogody dla twórców”: dźwięk syntetyczny + render przeglądarki."""
import os, sys, json, time, wave, subprocess
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

WD = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WD, "..", "ai", "rolka_pogoda.mp4")
PORT = 8771
FPS, SR = 30, 44100
INTRO, MAP = 2.8, 3.0
ROOM = [4.6, 7.0, 9.4, 11.8]; RDUR = 2.4
LIVE = 15.4; FCST = LIVE + 4.6; END = FCST + 4.4; TOTAL = END + 3.6
DATA = dict(INTRO=INTRO, MAP=MAP, ROOM=ROOM, RDUR=RDUR, LIVE=LIVE, FCST=FCST, END=END, TOTAL=TOTAL)
open(os.path.join(WD, "data.js"), "w").write("window.DATA=" + json.dumps(DATA) + ";")

rng = np.random.default_rng(21)
L = int(TOTAL * SR) + 3 * SR
mix = np.zeros(L); mus = np.zeros(L)
def tt(d): return np.arange(int(d * SR)) / SR
def add(sig, at, g=1.0, buf=None):
    b = mix if buf is None else buf
    i = int(at * SR); j = min(L, i + len(sig))
    if 0 <= i < L: b[i:j] += sig[:j - i] * g
def env(d, a=0.003, dec=0.1):
    t = tt(d); return np.minimum(1, t / a) * np.exp(-t / dec)
def hp(x, k=8): return x - np.convolve(x, np.ones(k) / k, "same")
def lpf(x, k=20): return np.convolve(x, np.ones(k) / k, "same")
def saw(f, t): return 2 * ((f * t) % 1) - 1
def bell(f, d=0.9, g=1.0):
    t = tt(d); parts = ((1, .5, .5), (2.01, .25, .3), (3.0, .12, .2), (4.2, .07, .12))
    return sum(a * np.sin(2 * np.pi * f * p * t) * np.exp(-t / dc) for p, a, dc in parts) * np.minimum(1, t / .002) * g
def kick(g=1.0):
    t = tt(0.3); f = 48 + 120 * np.exp(-t / 0.025)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(0.3, 0.001, 0.12) * 2.2) * g
def snare(g=1.0):
    t = tt(0.2); return (hp(rng.normal(0, 1, len(t)), 3) * env(0.2, 0.001, 0.06) * 0.6 + np.sin(2 * np.pi * 190 * t) * env(0.2, 0.001, 0.04) * 0.5) * g
def hat(d=0.04, g=1.0): t = tt(d); return hp(rng.normal(0, 1, len(t)), 2) * env(d, 0.0005, d / 3) * g
def rhodes(f, d=1.0, g=1.0):
    t = tt(d)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.3) + 0.2 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t / 0.06)
    return s * np.minimum(1, t / 0.004) * np.exp(-t / 0.7) * (1 + 0.2 * np.sin(2 * np.pi * 5.5 * t)) * g
def slap(f, d=0.22, g=1.0):
    t = tt(d); s = np.tanh((saw(f, t) * 0.6 + np.sin(2 * np.pi * f * t)) * 2.5 * np.exp(-t / 0.05) + np.sin(2 * np.pi * f * t) * 0.6)
    return lpf(s, 6) * env(d, 0.002, 0.12) * g
def brass(fs, d=0.35, g=1.0):
    t = tt(d); s = sum(saw(f, t) + saw(f * 1.005, t) for f in fs) / len(fs)
    e = np.minimum(1, t / 0.02) * np.exp(-t / (d * 0.6))
    return lpf(s, 5) * e * g
def whoosh(d=0.3, g=1.0):
    n = int(d * SR); return hp(rng.normal(0, 1, n), 4) * np.sin(np.linspace(0, np.pi, n)) ** 2 * g

# --- funk 104 BPM
B = 60 / 104
CH = [[261.63, 329.63, 392.0, 493.88, 587.33], [220.0, 261.63, 329.63, 392.0, 493.88],
      [293.66, 349.23, 440.0, 523.25, 659.25], [196.0, 246.94, 349.23, 440.0, 659.25]]
ROOTS = [65.41, 55.0, 73.42, 49.0]
BASSPAT = [(0, 1), (0.75, 1), (1.5, 2), (2, 1), (2.5, 1.5), (3.25, 2), (3.5, 1)]
def funk(t0, t1, g=1.0, full=True):
    x = t0; bar = 0
    while x < t1 - 0.1:
        c = CH[bar % 4]; r = ROOTS[bar % 4]
        for b in range(4):
            bt = x + b * B
            if bt >= t1: break
            add(kick(0.8), bt, g, mus) if b in (0, 2) else add(snare(0.55), bt, g, mus)
            if full and b == 2: add(kick(0.5), bt + B * 0.75, g, mus)
            for s in range(4):
                sw = 0.03 if s % 2 else 0
                add(hat(0.03, 0.12 if s % 2 else 0.18), bt + s * B / 4 + sw, g, mus)
        for (o, m) in BASSPAT:
            if x + o * B < t1: add(slap(r * m, 0.22, 0.42), x + o * B, g, mus)
        for k, f in enumerate(c): add(rhodes(f, 1.2, 0.07), x + k * 0.008, g, mus)
        for k, f in enumerate(c[1:4]): add(rhodes(f, 0.4, 0.05), x + 2.5 * B + k * 0.008, g, mus)
        if full and bar % 2 == 1: add(brass([f * 2 for f in c[:3]], 0.25, 0.12), x + 3.5 * B, g, mus)
        x += 4 * B; bar += 1
funk(INTRO, LIVE - 0.1, 0.75, full=False)
funk(LIVE, END + 2.6, 1.0, full=True)

# --- 0. alarm
for k in range(3):
    x = 0.05 + k * 0.9
    for j in range(2):
        t = tt(0.35); f = 880 if j == 0 else 1108
        add(np.sign(np.sin(2 * np.pi * f * t)) * 0.5 * env(0.35, 0.005, 0.5) * np.minimum(1, (0.35 - t) / 0.02) * 0.22, x + j * 0.38)
t = tt(INTRO); add(lpf(rng.normal(0, 1, len(t)), 40) * 0.5 * np.minimum(1, t / 0.5), 0)
add(kick(0.9), 0.02)
# --- intro jingle
add(whoosh(0.4, 0.5), INTRO - 0.3)
for k, f in enumerate([523.25, 659.25, 783.99, 1046.5]): add(brass([f, f * 1.26], 0.3, 0.22), INTRO + k * 0.09)
add(hat(0.8, 0.25), INTRO)
for k in range(5): add(bell(1200 + 200 * k, 0.3, 0.05), MAP + k * 0.18)  # rysowanie planu
# --- pokoje
def dingdong(x):
    add(bell(784, 0.9, 0.22), x); add(bell(622, 1.2, 0.22), x + 0.28)
for x in ROOM: add(whoosh(0.35, 0.35), x - 0.3); dingdong(x)
# kuchnia: lodówka
t = tt(1.6); hum = (np.sin(2 * np.pi * 50 * t) + 0.6 * np.sin(2 * np.pi * 100 * t) + lpf(rng.normal(0, 1, len(t)), 30) * 0.5) * np.minimum(1, t / 0.1) * np.minimum(1, (1.6 - t) / 0.2)
add(hum * 0.28, ROOM[0] + 0.3)
# łazienka: echo
for k in range(6): add(bell(1318, 0.5, 0.18 * 0.6 ** k), ROOM[1] + 0.4 + k * 0.28)
# salon: grzmot + wiertarka
t = tt(1.4); add(lpf(rng.normal(0, 1, len(t)), 60) * np.exp(-t / 0.5) * np.minimum(1, t / 0.05) * 1.6, ROOM[2] + 0.25)
t = tt(0.9); dr = np.sign(np.sin(2 * np.pi * (180 + 30 * np.sin(2 * np.pi * 7 * t)) * t)) * 0.5 + hp(rng.normal(0, 1, len(t)), 3) * 0.3
add(lpf(dr, 3) * np.minimum(1, t / 0.05) * np.minimum(1, (0.9 - t) / 0.05) * 0.18, ROOM[2] + 1.1)
# sypialnia: syrena mgłowa
t = tt(1.4); fh = (saw(73, t) + saw(73.6, t) + 0.5 * saw(110, t)) * np.minimum(1, t / 0.15) * np.minimum(1, (1.4 - t) / 0.3)
add(lpf(fh, 25) * 0.35, ROOM[3] + 0.35)
# --- kamera na żywo
add(whoosh(0.6, 0.6), LIVE - 0.6)
for k, f in enumerate([523.25, 659.25, 783.99, 1046.5, 1318.5]): add(bell(f, 1.2, 0.15), LIVE + k * 0.06)
for k in range(10):  # ptaki
    x = LIVE + 0.6 + rng.uniform(0, 3.6); t = tt(0.09)
    f0 = rng.uniform(2800, 4200)
    add(np.sin(2 * np.pi * np.cumsum(f0 + 900 * np.sin(np.pi * t / 0.09)) / SR) * np.sin(np.pi * t / 0.09) * 0.05, x)
for i in range(3): add(bell(1568, 0.4, 0.1), LIVE + 1.0 + i * 0.35)
for k in range(1, 4): add(hp(rng.normal(0, 1, int(0.03 * SR)), 2) * 0.15, LIVE + k * 1.15)  # migawka przy zmianie ujęcia
# --- prognoza dni
for i in range(4):
    x = FCST + 0.35 + i * 0.75
    if i < 3: add(whoosh(0.2, 0.3), x - 0.1); add(bell(523.25 * (1.12 ** i), 0.4, 0.15), x)
    else:
        add(brass([523.25, 659.25, 783.99], 0.6, 0.35), x); add(brass([1046.5], 0.6, 0.15), x); add(kick(0.8), x)
for i in range(3):
    add(hp(rng.normal(0, 1, int(0.15 * SR)), 2) * np.sin(np.linspace(0, np.pi, int(0.15 * SR))) * 0.18, FCST + 3.0 + i * 0.12)
# --- koniec
add(whoosh(0.5, 0.5), END - 0.4)
for k, f in enumerate([392.0, 523.25, 659.25, 783.99]): add(brass([f], 0.5, 0.2), END + 0.6 + k * 0.08)
add(brass([523.25, 659.25, 783.99, 1046.5], 1.4, 0.35), END + 2.6); add(kick(1.0), END + 2.6)
for k, f in enumerate([1046.5, 1318.5, 1568.0, 2093.0]): add(bell(f, 1.6, 0.14), END + 2.6 + k * 0.05)
mix[:] += mus * 0.75
m = mix[:int(TOTAL * SR)]
fo = int(0.8 * SR); m[-fo:] *= np.linspace(1, 0, fo)
m = np.tanh(m * 1.1); m = m / np.abs(m).max() * 0.93
wav = os.path.join(WD, "_mix.wav")
with wave.open(wav, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    a = (m * 32767).astype(np.int16); w.writeframes(np.repeat(a[:, None], 2, 1).tobytes())
print("audio ok", round(TOTAL, 2))
# ---------------- obraz
srv = subprocess.Popen(["python3", "-m", "http.server", str(PORT)], cwd=WD, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
prev = os.environ.get("PREV")
try:
    with sync_playwright() as p:
        br = p.chromium.launch(args=["--force-device-scale-factor=1", "--no-proxy-server"])
        pg = br.new_page(viewport={"width": 1080, "height": 1920})
        pg.on("pageerror", lambda e: print("pageerror:", e))
        pg.goto(f"http://127.0.0.1:{PORT}/index.html")
        pg.wait_for_function("window.READY===true", timeout=20000)
        def shot(t):
            pg.evaluate(f"renderAt({t})")
            return pg.screenshot(type="jpeg", quality=93)
        if prev:
            ims = []
            for t in [float(x) for x in prev.split(",")]:
                open(WD + "/_f.jpg", "wb").write(shot(t)); ims.append(Image.open(WD + "/_f.jpg").resize((270, 480)))
            sh = Image.new("RGB", (280 * len(ims), 480), "white")
            for i, im in enumerate(ims): sh.paste(im, (i * 280, 0))
            sh.save(WD + "/prev.jpg"); sys.exit()
        ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "image2pipe", "-c:v", "mjpeg", "-r", str(FPS), "-i", "-", "-i", wav,
                               "-shortest", "-c:v", "libx264", "-preset", "medium", "-b:v", "10M", "-maxrate", "12M", "-bufsize", "20M", "-pix_fmt", "yuv420p",
                               "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
        n = int(TOTAL * FPS); t0 = time.time()
        for i in range(n):
            ff.stdin.write(shot(i / FPS))
            if i % 150 == 0: print(i, n, round(time.time() - t0, 1), flush=True)
        ff.stdin.close(); ff.wait()
        print("ok", OUT)
finally:
    srv.terminate()
