"""SZABLON renderu rolki: oś czasu -> data.js, dźwięk (numpy) -> _mix.wav, klatki (Playwright) -> MP4.

Użycie (w folderze rolki):
  PREV=1.0,4.5,9.0 python3 render.py        # podgląd wybranych klatek -> prev.jpg
  SAFE=1 PREV=... python3 render.py         # podgląd z ramką strefy bezpiecznej
  COVER=1 python3 render.py                 # okładka -> okladka.jpg (renderCover)
  python3 render.py                         # pełny render -> rolka.mp4 + rolka_ig.mp4 (<30 MB)
"""
import os, sys, json, time, wave, subprocess
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

WD = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WD, "rolka.mp4")
PORT = int(os.environ.get("PORT", "8799"))
FPS, SR = 30, 44100

# ---------------- OŚ CZASU
BPM = 100; B = 60 / BPM
E = dict(UI=2.0, Q1=2.3, Q2=6.4, Q3=10.6, TWIST=14.2, RES=16.6, TAP=19.4, FIN=20.0)
SC = [0.0]
TOTAL = 24.0
DATA = dict(SC=SC, TOTAL=TOTAL, PHOTOS=["101", "104"], E=E)
open(os.path.join(WD, "data.js"), "w").write("window.DATA=" + json.dumps(DATA, ensure_ascii=False) + ";")

# ---------------- BIBLIOTEKA DŹWIĘKÓW
rng = np.random.default_rng(1)
L = int(TOTAL * SR) + 3 * SR
mix = np.zeros(L); mus = np.zeros(L); wet = np.zeros(L)
def tt(d): return np.arange(int(d * SR)) / SR
def add(sig, at, g=1.0, buf=None):
    b = mix if buf is None else buf
    i = int(at * SR); j = min(L, i + len(sig))
    if 0 <= i < L: b[i:j] += sig[:j - i] * g
def env(d, a=0.003, dec=0.1): t = tt(d); return np.minimum(1, t / a) * np.exp(-t / dec)
def hp(x, k=8): return x - np.convolve(x, np.ones(k) / k, "same")
def lpf(x, k=20): return np.convolve(x, np.ones(k) / k, "same")
def noise(d): return rng.normal(0, 1, int(d * SR))
def saw(f, t): return 2 * ((f * t) % 1) - 1
def kick(g=1.0): t = tt(0.3); return np.tanh(np.sin(2 * np.pi * np.cumsum(46 + 130 * np.exp(-t / 0.025)) / SR) * env(0.3, 0.001, 0.13) * 2.5) * g
def clap(g=1.0):
    out = np.zeros(int(0.25 * SR))
    for o in (0, 0.009, 0.018): s = hp(noise(0.2), 4) * env(0.2, 0.001, 0.045); i = int(o * SR); out[i:i + len(s)] += s
    return out * 0.45 * g
def hat(d=0.04, g=1.0): return hp(noise(d), 2) * env(d, 0.0005, d / 3) * g
def bass(f, d, g=1.0): t = tt(d); return np.tanh((np.sin(2 * np.pi * f * t) + 0.4 * saw(f, t)) * 1.6) * np.minimum(1, t / 0.005) * np.minimum(1, (d - t) / 0.01) * g
def pluck(f, d=0.25, g=1.0): t = tt(d); return lpf(saw(f, t) + saw(f * 1.005, t), 4) * env(d, 0.002, 0.08) * g
def pad(fs, d, g=1.0, cut=8): t = tt(d); s = sum(saw(f * k, t) for f in fs for k in (0.993, 1, 1.007)) / (3 * len(fs)); return lpf(s, cut) * np.minimum(1, t / 0.05) * g
def rhodes(f, d=1.2, g=1.0):
    t = tt(d); s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.4) + 0.18 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t / 0.08)
    return s * np.minimum(1, t / 0.004) * np.exp(-t / 0.9) * g
def bell(f, d=1.2, g=1.0):
    t = tt(d); return sum(a * np.sin(2 * np.pi * f * p * t) * np.exp(-t / dc) for p, a, dc in ((1, .5, .6), (2.76, .25, .3), (5.4, .1, .15))) * np.minimum(1, t / .002) * g
def pop(f=900, g=1.0): t = tt(0.09); return np.sin(2 * np.pi * np.cumsum(f + 1100 * np.exp(-t / 0.012)) / SR) * env(0.09, 0.001, 0.03) * g
def whoosh(d=0.35, g=1.0): n = int(d * SR); return hp(noise(d), 4) * np.linspace(0, 1, n) ** 2 * g
def riser(d, g=1.0): t = tt(d); return (hp(noise(d), 3)[:len(t)] * (t / d) ** 2.5 * 0.3 + np.sin(2 * np.pi * np.cumsum(200 + 1200 * (t / d) ** 2) / SR) * (t / d) ** 2 * 0.1) * g
def braam(f=55, d=3.0, g=1.0):
    t = tt(d); s = np.tanh(sum(saw(f * m, t) * a for m, a in ((1, 1), (1.006, .8), (0.994, .8), (2.003, .5), (0.5, .7))) * 0.9)
    return (lpf(lpf(s, 30), 30) * np.minimum(1, t / 0.05) * np.exp(-t / (d * 0.38)) * 0.55 + np.sin(2 * np.pi * f * 0.5 * t) * np.exp(-t / 1.4) * 0.5) * g
def wav_in(path):  # dźwięk z własnego nagrania (klip.sh) -> numpy
    with wave.open(path) as w: a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
    return a

# ---------------- MUZYKA: nocny synthwave (Am–F–C–G), od wyniku jaśniej i pełniej
CH = [[220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [261.63, 329.63, 392.0], [196.0, 246.94, 293.66]]
RT = [55.0, 43.65, 65.41, 49.0]
for b in range(int(TOTAL / B)):
    x = b * B; bar = (b // 4) % 4; c = CH[bar]
    full = x >= E["RES"] - 0.1
    if x >= E["UI"] - 0.05 and not (E["TWIST"] <= x < E["RES"] - 0.1):
        add(kick(0.75), x, 1, mus)
        if b % 2: add(clap(0.55 if full else 0.4), x, 1, mus)
        add(hat(0.035, 0.12), x + B / 2, 1, mus)
        if full: add(hat(0.025, 0.07), x + B / 4, 1, mus); add(hat(0.025, 0.07), x + 3 * B / 4, 1, mus)
    for k in range(4):  # arpeggio ósemkowe
        add(pluck(c[(b * 4 + k) % 3] * (4 if full else 2), 0.2, 0.08), x + k * B / 4, 1, wet)
    add(bass(RT[bar] * 2, B * 0.9, 0.3), x, 1, mus)
    if b % 4 == 0: add(pad(c, 4 * B + 0.2, 0.06, 12), x, 1, mus)
# ---------------- EFEKTY
def typing(q, t0):
    for i in range(len(q)): add(hp(noise(0.02), 2) * env(0.02, 0.0005, 0.004) * 0.18, t0 + i * 0.065 + rng.uniform(0, 0.01))
add(braam(55, 1.6, 0.5), 0.35); add(pop(700, 0.4), 0.35)
for k, f in enumerate([523.25, 659.25]): add(bell(f, 0.8, 0.12), 0.9 + k * 0.08, 1, wet)
add(whoosh(0.3, 0.3), E["UI"] - 0.25)
typing("jak zacząć podcast", E["Q1"])
for i in range(3): add(pop(900 + 100 * i, 0.25), E["Q1"] + 1.35 + i * 0.28)
add(hp(noise(0.03), 2) * env(0.03, 0.0005, 0.005) * 0.4, E["Q1"] + 2.6); add(pop(1200, 0.35), E["Q1"] + 2.8)
typing("ile kosztuje sprzęt do podcastu", E["Q2"])
for i in range(4): add(pop(800, 0.25), E["Q2"] + 2.35 + i * 0.3)
t_ = tt(0.5); add(np.sin(2 * np.pi * np.cumsum(300 * np.exp(-t_ / 0.3) + 80) / SR) * env(0.5, 0.002, 0.2) * 0.4, E["Q2"] + 3.6)
add(pop(1100, 0.35), E["Q2"] + 4.1)
typing("jak wygłuszyć pokój w bloku", E["Q3"])
add(pop(900, 0.3), E["Q3"] + 1.9); add(pop(600, 0.35), E["Q3"] + 2.9)
add(riser(E["RES"] - E["TWIST"], 0.9), E["TWIST"])
typing("studio podcastowe warszawa", E["TWIST"] + 0.9)
for k, f in enumerate([523.25, 659.25, 783.99, 1046.5]): add(bell(f, 1.4, 0.14), E["RES"] + k * 0.05, 1, wet)
add(kick(0.9), E["RES"])
for i in range(5): add(pop(900 + 120 * i, 0.3), E["RES"] + 0.4 + i * 0.22)
add(hp(noise(0.03), 2) * env(0.03, 0.0005, 0.005) * 0.5, E["TAP"]); add(bell(1318.5, 1.0, 0.15), E["TAP"] + 0.05, 1, wet)
add(whoosh(0.5, 0.5), E["FIN"] - 0.2)
for k, f in enumerate([523.25, 659.25, 783.99, 1046.5, 1318.5]): add(bell(f, 1.6, 0.12), E["FIN"] + 1.6 + k * 0.05, 1, wet)

mix[:] += mus * 0.7
n = int(2.0 * SR); ir = rng.normal(0, 1, n) * np.exp(-np.arange(n) / SR / 0.5); ir = lpf(ir, 4); ir /= np.sqrt((ir ** 2).sum()) * 2
mix[:] += wet * 0.6 + np.convolve(wet, ir)[:L]
m = mix[:int(TOTAL * SR)]
fo = int(0.6 * SR); m[-fo:] *= np.linspace(1, 0, fo)
m = np.tanh(m * 1.15); m = m / max(1e-9, np.abs(m).max()) * 0.93
wav = os.path.join(WD, "_mix.wav")
with wave.open(wav, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(np.repeat((m * 32767).astype(np.int16)[:, None], 2, 1).tobytes())
print("audio ok", round(TOTAL, 2))

# ---------------- OBRAZ
srv = subprocess.Popen(["python3", "-m", "http.server", str(PORT)], cwd=WD, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
try:
    with sync_playwright() as p:
        br = p.chromium.launch(args=["--force-device-scale-factor=1", "--no-proxy-server"])
        pg = br.new_page(viewport={"width": 1080, "height": 1920})
        pg.on("pageerror", lambda e: print("pageerror:", e))
        pg.goto(f"http://127.0.0.1:{PORT}/index.html")
        pg.wait_for_function("window.READY===true", timeout=30000)
        if os.environ.get("SAFE"): pg.evaluate("window.SAFE_BOX=true")
        def shot(t):
            pg.evaluate(f"renderAt({t})")          # renderAt może być async (klatki nagrań)
            return pg.screenshot(type="jpeg", quality=93)
        if os.environ.get("COVER"):
            pg.evaluate("renderCover()"); pg.screenshot(path=os.path.join(WD, "okladka.jpg"), type="jpeg", quality=95); print("okladka.jpg"); sys.exit()
        prev = os.environ.get("PREV")
        if prev:
            ims = []
            for t in [float(x) for x in prev.split(",")]:
                open(WD + "/_f.jpg", "wb").write(shot(t)); ims.append(Image.open(WD + "/_f.jpg").resize((270, 480)))
            sh = Image.new("RGB", (280 * len(ims), 480), "white")
            for i, im in enumerate(ims): sh.paste(im, (i * 280, 0))
            sh.save(WD + "/prev.jpg"); print("prev.jpg"); sys.exit()
        ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "image2pipe", "-c:v", "mjpeg", "-r", str(FPS), "-i", "-", "-i", wav,
                               "-shortest", "-c:v", "libx264", "-preset", "medium", "-b:v", "10M", "-pix_fmt", "yuv420p",
                               "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
        n = int(TOTAL * FPS); t0 = time.time()
        for i in range(n):
            ff.stdin.write(shot(i / FPS))
            if i % 150 == 0: print(i, n, round(time.time() - t0, 1), flush=True)
        ff.stdin.close(); ff.wait()
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", OUT, "-c:v", "libx264", "-b:v", "7M", "-maxrate", "9M", "-bufsize", "14M",
                        "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", OUT.replace(".mp4", "_ig.mp4")])
        print("ok", OUT.replace(".mp4", "_ig.mp4"))
finally:
    srv.terminate()
