"""Rolka „Instrukcja nagrania podcastu”: rysunek kreskowy + dźwięk syntetyczny."""
import os, sys, json, time, wave, subprocess
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

WD = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WD, "..", "ai", "rolka_instrukcja.mp4")
PORT = 8773
FPS, SR = 30, 44100
P = [0.0, 3.4, 7.4, 11.4, 15.6, 19.8]
TOTAL = 25.2
open(os.path.join(WD, "data.js"), "w").write("window.DATA=" + json.dumps(dict(P=P, TOTAL=TOTAL)) + ";")
rng = np.random.default_rng(41)
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
def noise(d): return rng.normal(0, 1, int(d * SR))
def glock(f, d=0.8, g=1.0):
    t = tt(d); return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.08) + 0.15 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.03)) * env(d, 0.001, 0.35) * g
def pluck(f, d=0.3, g=1.0):
    t = tt(d); return np.tanh((np.sin(2 * np.pi * f * t) + 0.5 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.04)) * 1.5) * env(d, 0.002, 0.11) * g
def kick(g=1.0):
    t = tt(0.25); return np.sin(2 * np.pi * np.cumsum(50 + 90 * np.exp(-t / 0.02)) / SR) * env(0.25, 0.001, 0.09) * g
def clap(g=1.0):
    out = np.zeros(int(0.2 * SR))
    for o in (0, 0.01, 0.02):
        s = hp(noise(0.15), 4) * env(0.15, 0.001, 0.035); i = int(o * SR); out[i:i + len(s)] += s
    return out * 0.4 * g
def shaker(g=1.0): return hp(noise(0.05), 2) * np.sin(np.linspace(0, np.pi, int(0.05 * SR))) * g
def pop(f=900, g=1.0):
    t = tt(0.08); return np.sin(2 * np.pi * np.cumsum(f + 900 * np.exp(-t / 0.01)) / SR) * env(0.08, 0.001, 0.025) * g
def pencil(d, g=1.0):
    t = tt(d); n = lpf(hp(noise(d), 5), 2); am = 0.4 + 0.6 * np.abs(np.sin(2 * np.pi * 9 * t))
    return n[:len(t)] * am * np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.03) * 0.25 * g
def flip(g=1.0):
    d = 0.35; n = lpf(hp(noise(d), 6), 3); t = tt(d)
    return n[:len(t)] * np.sin(np.pi * t / d) ** 2 * (0.6 + 0.4 * np.sin(2 * np.pi * 30 * t)) * 0.7 * g

# muzyka: pogodna, 120 BPM, C-dur
B = 0.5
prog = [(130.81, [523.25, 659.25, 783.99]), (110.0, [523.25, 659.25, 880.0]), (174.61, [523.25, 698.46, 880.0]), (196.0, [587.33, 783.99, 987.77])]
mel = [784, 0, 880, 784, 659, 0, 523, 0, 587, 659, 0, 587, 523, 0, 0, 0,
       659, 0, 784, 880, 1047, 0, 880, 0, 784, 659, 0, 587, 659, 0, 0, 0]
x = 0.0; b = 0
while x < TOTAL - 0.5:
    bar = (b // 4) % 4; r, ch = prog[bar]
    final = x >= P[5] + 0.6
    add(kick(0.55), x, 1, mus) if b % 2 == 0 else add(clap(0.6), x, 1, mus)
    add(shaker(0.12), x + B / 2, 1, mus); add(shaker(0.07), x + B / 4, 1, mus); add(shaker(0.07), x + 3 * B / 4, 1, mus)
    add(pluck(r, 0.3, 0.5), x, 1, mus); add(pluck(r * 2, 0.2, 0.25), x + B / 2, 1, mus)
    if b % 4 == 0:
        for k, f in enumerate(ch): add(glock(f / 2, 0.9, 0.05), x + k * 0.01, 1, mus)
    if b >= 4:
        for h in range(2):
            f = mel[((b - 4) * 2 + h) % 32]
            if f: add(glock(f, 0.6, 0.12 if not final else 0.16), x + h * B / 2, 1, mus)
    x += B; b += 1

# efekty
for p in P[1:]: add(flip(1.0), p - 0.05)
def pg(i, t): return P[i] + t
add(pencil(0.8), pg(0, 0.25)); add(pop(1200, 0.3), pg(0, 1.0))
add(pencil(0.6), pg(1, 0.15))
t = tt(0.4); add(np.sign(np.sin(2 * np.pi * 110 * t)) * env(0.4, 0.005, 0.2) * 0.25, pg(1, 0.8))  # brzęczyk
t = tt(1.2); add((np.sin(2 * np.pi * 50 * t) + lpf(noise(1.2), 20)[:len(t)] * 0.4) * np.minimum(1, t / 0.05) * np.minimum(1, (1.2 - t) / 0.1) * 0.12, pg(1, 0.3))
add(pencil(0.6), pg(1, 1.6))
for k, f in enumerate([1047, 1319, 1568]): add(glock(f, 0.7, 0.18), pg(1, 2.3) + k * 0.07)
for i in range(6): add(pop(700 + 120 * i, 0.4), pg(2, 0.2 + i * 0.4))
add(glock(1568, 0.8, 0.15), pg(2, 2.8))
add(pencil(0.4), pg(3, 0.3)); add(pop(1000, 0.4), pg(3, 0.1))
t = tt(0.05); add(hp(noise(0.05), 2) * env(0.05, 0.0005, 0.006) * 0.6, pg(3, 1.45))  # klik
add(glock(1319, 0.6, 0.18), pg(3, 1.5)); add(pop(900, 0.4), pg(3, 1.9))
for k in range(7): add(lpf(noise(0.06), 8) * env(0.06, 0.001, 0.015) * 0.7, pg(3, 2.45 + k * 1 / 6))  # kroki
t = tt(0.3); add(np.sin(2 * np.pi * 330 * t) * env(0.3, 0.005, 0.2) * 0.15, pg(3, 3.6)); add(np.sin(2 * np.pi * 262 * t) * env(0.3, 0.005, 0.2) * 0.15, pg(3, 3.85))  # dzwonek do drzwi
add(pop(1000, 0.4), pg(4, 0.1)); add(pencil(0.5), pg(4, 0.3))
for x0 in (0.9, 1.5):  # „bla bla”
    for k in range(5):
        t = tt(0.07); f = rng.uniform(300, 500)
        add(np.sign(np.sin(2 * np.pi * f * t)) * env(0.07, 0.003, 0.03) * 0.08, pg(4, x0 + k * 0.08))
t = tt(0.06); add(np.sin(2 * np.pi * 1800 * t) * env(0.06, 0.001, 0.02) * 0.2, pg(4, 0.9))
add(pop(1000, 0.4), pg(4, 2.2))
n = int(0.5 * SR); add(hp(noise(0.5), 3) * np.sin(np.linspace(0, np.pi, n)) ** 2 * 0.25, pg(4, 2.6))
add(glock(1568, 0.6, 0.18), pg(4, 3.2))
for k, f in enumerate([523, 659, 784, 1047, 1319]): add(glock(f, 1.4, 0.2), pg(5, 0.6) + k * 0.06)
add(kick(0.8), pg(5, 0.6))
mix[:] += mus * 0.6
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
