"""Rolka „koszyk”: dźwięk syntetyczny + render przeglądarki."""
import os, sys, json, time, wave, subprocess
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

WD = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WD, "..", "ai", "rolka_match_v2.mp4")
FPS, SR = 30, 44100
NOPE = [1.45, 2.55, 3.5, 4.35]
YES = 6.6
MATCH = YES + 0.4
CHAT = MATCH + 2.4
MSG = [CHAT + 0.4, CHAT + 1.9, CHAT + 3.5]
END = MSG[-1] + 1.7
TOTAL = END + 2.7
DATA = dict(NOPE=NOPE, YES=YES, MATCH=MATCH, CHAT=CHAT, MSG=MSG, END=END, TOTAL=TOTAL)
open(os.path.join(WD, "data.js"), "w").write("window.DATA=" + json.dumps(DATA) + ";")
rng = np.random.default_rng(5)
L = int(TOTAL * SR) + SR
mix = np.zeros(L)
def tt(d): return np.arange(int(d * SR)) / SR
def add(sig, at, g=1.0):
    i = int(at * SR); j = min(L, i + len(sig))
    if 0 <= i < L: mix[i:j] += sig[:j - i] * g
def env(d, a=0.003, dec=0.1):
    t = tt(d); return np.minimum(1, t / a) * np.exp(-t / dec)
def hp(x, k=8): return x - np.convolve(x, np.ones(k) / k, "same")
def lpf(x, k=20): return np.convolve(x, np.ones(k) / k, "same")
def bell(f, d=0.9, g=1.0, parts=((1, .5, .5), (2.01, .25, .3), (3.0, .12, .2), (4.2, .07, .12))):
    t = tt(d); return sum(a * np.sin(2 * np.pi * f * p * t) * np.exp(-t / dc) for p, a, dc in parts) * np.minimum(1, t / .002) * g
def kick(g=1.0):
    t = tt(0.35); f = 50 + 110 * np.exp(-t / 0.03)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(0.35, 0.001, 0.14) * 2) * g
def hat(d=0.04, g=1.0): t = tt(d); return hp(rng.normal(0, 1, len(t)), 3) * env(d, 0.0005, d / 3) * g
def clap(g=1.0):
    out = np.zeros(int(0.22 * SR))
    for o in (0, 0.011, 0.022):
        s = hp(rng.normal(0, 1, int(0.18 * SR)), 4) * env(0.18, 0.001, 0.04 if o < .02 else 0.08); i = int(o * SR); out[i:i + len(s)] += s
    return out * 0.45 * g
def pluck(f, d=0.25, g=1.0):
    t = tt(d); return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * env(d, 0.002, 0.07) * g
def bass(f, d=0.2, g=1.0):
    t = tt(d); return np.tanh(np.sin(2 * np.pi * f * t) * 2) * env(d, 0.003, 0.09) * g
def whoosh(d=0.14, g=1.0):
    n = int(d * SR); return hp(rng.normal(0, 1, n), 4) * np.linspace(0, 1, n) ** 2 * g


def rhodes(f, d=1.2, g=1.0):
    t = tt(d)
    s = (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.4) + 0.18 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t / 0.08))
    return s * np.minimum(1, t / 0.004) * np.exp(-t / 0.9) * (1 + 0.15 * np.sin(2 * np.pi * 5 * t)) * g
def lofi(t0, t1, bpm=88, g=1.0, bright=False):
    B = 60 / bpm; bar = 4 * B
    ch = [[174.61, 220.0, 261.63, 329.63, 392.0], [164.81, 196.0, 246.94, 293.66], [146.83, 174.61, 220.0, 261.63, 329.63], [130.81, 164.81, 196.0, 246.94, 293.66]]
    roots = [43.65, 41.20, 36.71, 32.70]
    x = t0; b = 0
    while x < t1 - 0.05:
        c = ch[(b // 4) % 4]; sw = B * 0.08
        if b % 4 == 0:
            for k, f in enumerate(c): add(rhodes(f, 1.6, 0.11 * g), x + k * 0.012)
        if b % 4 == 2:
            for k, f in enumerate(c[1:]): add(rhodes(f * 2 if k == 3 else f, 0.9, 0.07 * g), x + B / 2 + sw + k * 0.01)
        # perkusja
        if b % 2 == 0: add(kick(0.75 * g), x)
        if b % 4 == 1: add(kick(0.45 * g), x + B / 2 + sw)
        if b % 2 == 1:
            sn = hp(rng.normal(0, 1, int(0.15 * SR)), 5) * env(0.15, 0.001, 0.05) * 0.35 + np.sin(2 * np.pi * 220 * tt(0.15)) * env(0.15, 0.001, 0.03) * 0.3
            add(sn * g, x)
        add(hat(0.03, 0.12 * g), x); add(hat(0.03, (0.16 if bright else 0.09) * g), x + B / 2 + sw)
        if bright and b % 2 == 1: add(clap(0.5 * g), x)
        # bas
        r = roots[(b // 4) % 4]
        if b % 4 in (0, 2):
            t = tt(B * 1.6); add(np.tanh(np.sin(2 * np.pi * r * 2 * t) * 1.5) * np.minimum(1, t / .01) * np.exp(-t / 0.6) * 0.4 * g, x)
        b += 1; x += B
    # trzaski winylu
    n = int((t1 - t0) * SR); cr = np.zeros(n); idx = rng.integers(0, n, int((t1 - t0) * 9)); cr[idx] = rng.normal(0, 1, len(idx))
    add(np.convolve(cr, np.ones(6) / 6, "same") * 0.35 * g + hp(rng.normal(0, 1, n), 4) * 0.006 * g, t0)
lofi(0.0, MATCH, 88, 0.9)
lofi(MATCH, TOTAL - 0.2, 88, 1.0, bright=True)
# odrzucenia
for x in NOPE:
    add(whoosh(0.22, 0.45), x - 0.05)
    t = tt(0.25); add(np.sin(2 * np.pi * np.cumsum(np.linspace(140, 55, len(t))) / SR) * env(0.25, 0.002, 0.08) * 0.6, x + 0.1)
    add(hp(rng.normal(0, 1, int(0.015 * SR)), 2) * 0.4, x - 0.12)
# zawahanie: dwa „hmm” dzwoneczki, potem tak
for k in range(3): add(rhodes(659.25 * (1.12 ** k), 0.4, 0.12), NOPE[-1] + 0.7 + k * 0.17)
add(hp(rng.normal(0, 1, int(0.015 * SR)), 2) * 0.4, YES - 0.12)
add(whoosh(0.3, 0.5), YES - 0.05)
d = YES - (YES - 0.9); t = tt(0.9); ramp = (t / 0.9) ** 2
add((lpf(rng.normal(0, 1, len(t)), 6) * 0.5) * ramp, YES - 0.9)
# match
for k, f in enumerate([523.25, 659.25, 783.99, 1046.5, 1318.5]): add(bell(f, 1.6, 0.28), MATCH + k * 0.05)
t = tt(1.4); add(np.sin(2 * np.pi * np.cumsum(42 + 100 * np.exp(-t / 0.08)) / SR) * env(1.4, 0.001, 0.6) * 0.8, MATCH)
for k in range(8): add(pluck(1200 + 200 * (k % 4), 0.12, 0.12), MATCH + 0.4 + k * 0.11)
# czat
for i, x in enumerate(MSG):
    if i != 1:
        for k in range(6): add(hp(rng.normal(0, 1, int(0.008 * SR)), 2) * 0.08, x - 0.6 + k * 0.09)
    t = tt(0.12); add(np.sin(2 * np.pi * np.cumsum(np.linspace(500, 1300, len(t))) / SR) * env(0.12, 0.002, 0.05) * 0.35, x)
add(bell(1568, 0.8, 0.25), MSG[-1] + 0.25)
add(whoosh(0.35, 0.5), END - 0.3)
for k, f in enumerate([349.23, 440.0, 523.25, 659.25]): add(rhodes(f, 2.2, 0.15), END + 0.25 + k * 0.03)
m = mix[:int(TOTAL * SR)]
fo = int(0.8 * SR); m[-fo:] *= np.linspace(1, 0, fo)
m = np.tanh(m * 1.15); m = m / np.abs(m).max() * 0.93
wav = os.path.join(WD, "_mix.wav")
with wave.open(wav, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    a = (m * 32767).astype(np.int16); w.writeframes(np.repeat(a[:, None], 2, 1).tobytes())
print("audio ok", round(TOTAL, 2))
# ---------------- obraz
srv = subprocess.Popen(["python3", "-m", "http.server", "8768"], cwd=WD, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
prev = os.environ.get("PREV")
try:
    with sync_playwright() as p:
        br = p.chromium.launch(args=["--force-device-scale-factor=1", "--no-proxy-server"])
        pg = br.new_page(viewport={"width": 1080, "height": 1920})
        pg.on("pageerror", lambda e: print("pageerror:", e))
        pg.goto("http://127.0.0.1:8768/index.html")
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
