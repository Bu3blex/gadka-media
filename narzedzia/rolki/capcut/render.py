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

# ---------------- OŚ CZASU (drill 140 BPM)
BPM = 140; B = 60 / BPM
DROP = 15 * B
SHOTS = [[0, "bath"], [13 * B, "black"], [DROP, "101"], [DROP + 5 * B, "056", 0.6, 0.55], [DROP + 9 * B, "037"], [DROP + 13 * B, "104"],
         [DROP + 17 * B, "034"], [DROP + 21 * B, "orange"], [DROP + 26 * B, "019"]]
END = DROP + 30 * B
CAP = [
    [0.1, 2.0, "ZIOMEK NAGRYWA PODCAST", None, 112],
    [2.0, 3.6, "W ŁAZIENCE 💀", "all", 128],
    [3.6, 13 * B, "ECHO JAK W KATEDRZE", None, 96],
    [13 * B, DROP, "A MÓGŁ…", "all", 140],
    [DROP + 0.05, DROP + 5 * B, "WBIĆ DO STUDIA 🎙️", [2], 112],
    [DROP + 5 * B, DROP + 9 * B, "MIKROFONY SHURE", [1], 112],
    [DROP + 9 * B, DROP + 13 * B, "2 KAMERY 4K", [1, 2], 120],
    [DROP + 13 * B, DROP + 17 * B, "ŚWIATŁO JAK NA PLANIE ✨", [0], 100],
    [DROP + 17 * B, DROP + 21 * B, "PLIKI OD RĘKI", [2], 120],
    [DROP + 26 * B, END, "TO CO, NAGRYWAMY?", "all", 104],
]
TOTAL = END + 2.6
DATA = dict(SC=[0.0], TOTAL=TOTAL, PHOTOS=["101", "056", "037", "104", "034", "019"], B=B, DROP=DROP, END=END, SHOTS=SHOTS, CAP=CAP, ECHO=[3.6, 13 * B])
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

# ---------------- MUZYKA: drill (ślizgające się 808, triole hi-hatów, snare na 3), przed dropem stłumiony „z łazienki”
def b808s(f0, f1, d, g=1.0):
    t = tt(d); fr = f0 + (f1 - f0) * np.clip((t - d * 0.55) / (d * 0.3), 0, 1)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(fr * (1 + 0.5 * np.exp(-t / 0.02))) / SR) * 2.4) * np.minimum(1, t / 0.003) * np.exp(-t / (d * 0.9)) * g
def snare(g=1.0): t = tt(0.25); return (hp(noise(0.25), 3) * env(0.25, 0.001, 0.07) * 0.7 + np.sin(2 * np.pi * 200 * t) * env(0.25, 0.001, 0.04) * 0.5) * g
def bellk(f, d=0.6, g=1.0): t = tt(d); return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.4 * t) * np.exp(-t / 0.1)) * env(d, 0.002, 0.25) * g
pre = np.zeros(L); post = np.zeros(L)
mel = [311.13, 0, 369.99, 311.13, 0, 277.18, 293.66, 0]   # mroczne dzwonki (Eb-moll)
roots = [(38.89, 38.89), (38.89, 46.25), (34.65, 34.65), (41.2, 36.71)]
nb = int(TOTAL / B) + 1
for b in range(nb):
    x = b * B; buf = pre if x < DROP else post
    if 13 * B <= x < DROP: continue          # pauza przed dropem
    bar = (b // 4) % 4
    if b % 4 == 0: add(kick(0.9), x, 1, buf); add(b808s(roots[bar][0], roots[bar][1], 4 * B * 0.95, 0.55), x, 1, buf)
    if b % 4 == 2: add(snare(0.8), x, 1, buf); add(clap(0.5), x, 1, buf)
    if b % 8 == 3: add(kick(0.6), x + B / 2, 1, buf)
    # hi-haty: ósemki z triolowymi przyspieszeniami
    if b % 4 == 3:
        for k in range(6): add(hat(0.02, 0.10), x + k * B / 6, 1, buf)
    else:
        add(hat(0.03, 0.12), x, 1, buf); add(hat(0.025, 0.08), x + B / 2, 1, buf)
    m = mel[b % 8]
    if m: add(bellk(m * 2, 0.5, 0.08), x, 1, buf)
    if b % 8 == 0: add(pad([155.56, 185.0, 233.08], 8 * B, 0.035, 14), x, 1, buf)
# „łazienka”: stłumienie + pogłos
pre_f = lpf(lpf(pre, 25), 25)
n = int(1.2 * SR); ir = rng.normal(0, 1, n) * np.exp(-np.arange(n) / SR / 0.25); ir = lpf(ir, 4); ir /= np.sqrt((ir ** 2).sum()) * 2.5
mus += pre_f * 0.9 + np.convolve(pre_f, ir)[:L] * 0.8 + post
# ---------------- EFEKTY
add(hp(noise(0.03), 2) * env(0.03, 0.0005, 0.005) * 0.4, 0.05)         # klik nagrywania
for k in range(4): add(lpf(snare(0.5), 6) * (0.55 ** k), 2.0 + k * 0.28)   # „bum” echa przy łazience
t_ = tt(0.35); add(np.sin(2 * np.pi * np.cumsum(900 - 700 * t_ / 0.35) / SR) * env(0.35, 0.002, 0.15) * 0.25, 13 * B)  # zgrzyt / zatrzymanie
add(riser(DROP - 13 * B, 0.7), 13 * B)
add(braam(41.2, 2.0, 1.0), DROP); add(kick(1.0), DROP)
for s in SHOTS[3:]: add(whoosh(0.2, 0.35), s[0] - 0.18)
for k, f in enumerate([622.25, 739.99, 932.33]): add(bell(f, 1.4, 0.12), SHOTS[7][0] + k * 0.05, 1, wet)   # „ka-ching” przy cenie
add(pop(1200, 0.4), END + 0.5)

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
