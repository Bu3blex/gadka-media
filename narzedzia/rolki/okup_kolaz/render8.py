"""Rolka „Mamy Twój podcast”: kolaż poklatkowy + dźwięk syntetyczny."""
import os, sys, json, time, wave, subprocess
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

WD = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WD, "..", "ai", "rolka_okup.mp4")
PORT = 8772
FPS, SR = 30, 44100
S = [0.0, 4.4, 8.9, 14.8, 19.4, 24.4]
TOTAL = 30.0
DATA = dict(S=S, TOTAL=TOTAL)
open(os.path.join(WD, "data.js"), "w").write("window.DATA=" + json.dumps(DATA) + ";")
q = lambda x: np.ceil(x * 12) / 12  # poklatkowo

# zdarzenia: (scena, t0, liczba liter, krok)
RANSOM = [(0, 0.0, 4, .07), (0, .4, 4, .07), (0, .8, 8, .07),
          (1, .15, 5, .06), (1, .5, 11, .05), (1, 1.15, 8, .06),
          (2, .1, 7, .06), (2, .55, 11, .05),
          (3, .1, 4, .06), (3, .45, 9, .06),
          (4, .1, 5, .08), (4, .75, 5, .12),
          (5, .1, 6, .06), (5, .55, 7, .07)]
HAND = [(0, 2.1, .5), (0, 2.6, .8), (2, 4.2, .8), (3, 3.0, .6), (4, 2.3, .7), (4, 2.9, .6), (5, 1.5, .7), (5, 2.1, .6), (5, 2.6, .5), (1, 2.6, .4), (4, 1.9, .4)]
POLA = [(1, 1.9), (3, 1.2), (3, 1.8), (3, 2.4)]
STRIP = [(2, 1.3 + i * .55) for i in range(5)] + [(4, 3.6), (5, 3.8)]
STICK = [(5, 3.2)]

rng = np.random.default_rng(31)
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
def bp(x, lo, hi): return lpf(hp(x, hi), lo)
def noise(d): return rng.normal(0, 1, int(d * SR))

def slap(g=1.0):  # naklejenie wycinka
    d = 0.09; n = noise(d)
    return (lpf(n, 6) * env(d, 0.001, 0.012) * 0.9 + hp(n, 3) * env(d, 0.001, 0.02) * 0.35 + np.sin(2 * np.pi * 140 * tt(d)) * env(d, 0.001, 0.02) * 0.5) * g
def snip(g=1.0):
    out = np.zeros(int(0.25 * SR))
    for o in (0, 0.11):
        s = hp(noise(0.05), 2) * env(0.05, 0.0005, 0.008) + np.sin(2 * np.pi * 3200 * tt(0.05)) * env(0.05, 0.0005, 0.006) * 0.4
        i = int(o * SR); out[i:i + len(s)] += s
    return out * 0.5 * g
def tape_rip(g=1.0):
    d = 0.35; n = hp(noise(d), 3); am = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 70 * tt(d) + rng.normal(0, .8, len(n))))
    return n * am * np.sin(np.linspace(0, np.pi, len(n))) * 0.35 * g
def type_clack(g=1.0):
    s = hp(noise(0.04), 3) * env(0.04, 0.0005, 0.006) + np.sin(2 * np.pi * 900 * tt(0.04)) * env(0.04, 0.0005, 0.01) * 0.3
    return s * g
def pen(d, g=1.0):
    n = bp(noise(d), 4, 10); t = tt(d)
    am = 0.4 + 0.6 * np.abs(np.sin(2 * np.pi * 7 * t + 3 * np.sin(2 * np.pi * 1.7 * t)))
    return n[:len(t)] * am * np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.03) * 0.22 * g
def paper_slide(g=1.0):
    d = 0.4; n = bp(noise(d), 5, 30); return n * np.sin(np.linspace(0, np.pi, len(n))) ** 2 * 0.6 * g
def bell(f, d=0.9, g=1.0):
    t = tt(d); parts = ((1, .5, .5), (2.01, .25, .3), (3.0, .12, .2), (4.2, .07, .12))
    return sum(a * np.sin(2 * np.pi * f * p * t) * np.exp(-t / dc) for p, a, dc in parts) * np.minimum(1, t / .002) * g
def vib(f, d=0.6, g=1.0):
    t = tt(d); return (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t / 0.05)) * env(d, 0.002, 0.35) * (1 + 0.25 * np.sin(2 * np.pi * 6 * t)) * g
def pizz(f, d=0.35, g=1.0):
    t = tt(d); s = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.05) + 0.2 * np.sin(6 * np.pi * f * t) * np.exp(-t / 0.03)
    return np.tanh(s * 1.4) * env(d, 0.003, 0.12) * g
def snap(g=1.0):
    return (hp(noise(0.06), 2) * env(0.06, 0.0005, 0.01) + np.sin(2 * np.pi * 2100 * tt(0.06)) * env(0.06, 0.0005, 0.006) * 0.5) * g
def brush(d=0.12, g=1.0): return hp(noise(d), 3) * env(d, 0.01, d / 3) * g
def kick(g=1.0):
    t = tt(0.25); return np.sin(2 * np.pi * np.cumsum(50 + 80 * np.exp(-t / 0.02)) / SR) * env(0.25, 0.001, 0.1) * g

# --- muzyka: skradający się jazz 112 BPM ze swingiem
B = 60 / 112; sw = B * 0.17
E = 82.41
walk = [0, 3, 5, 6, 7, 6, 5, 3, 0, 3, 5, 10, 12, 10, 7, 5]  # półtony od E
def note(n): return E * 2 ** (n / 12)
x = 0.15; b = 0
while x < TOTAL - 0.6:
    final = x >= S[5] + 0.4
    n = walk[b % 16]
    if final: n = [0, 4, 7, 4][b % 4]
    add(pizz(note(n), 0.4, 0.55), x, 1, mus)
    if b % 8 == 7 and not final: add(pizz(note(n + 1), 0.2, 0.35), x + B / 2 + sw, 1, mus)
    if b % 2 == 1: add(snap(0.35), x, 1, mus)
    add(brush(0.1, 0.06), x, 1, mus); add(brush(0.06, 0.05), x + B / 2 + sw, 1, mus)
    if b % 4 == 0: add(kick(0.35), x, 1, mus)
    if b % 8 == 2:  # wibrafon – tajemnicze akordy
        ch = [329.63, 392.0, 493.88, 587.33] if not final else [329.63, 415.3, 493.88, 622.25]
        for k, f in enumerate(ch): add(vib(f, 0.9, 0.06), x + B / 2 + sw + k * 0.02, 1, mus)
    if b % 16 == 14 and not final:
        add(vib(659.25, 0.3, 0.07), x, 1, mus); add(vib(622.25, 0.3, 0.07), x + B / 2 + sw, 1, mus)
    x += B; b += 1

# --- efekty
for i, s0 in enumerate(S):
    if i: add(paper_slide(0.9), s0 - 0.05)
for sc, t0, n, st in RANSOM:
    base = S[sc] + t0
    add(snip(0.6), base - 0.18)
    for k in range(n): add(slap(0.55 + 0.15 * rng.random()), q(base + k * st))
for sc, t0, d in HAND: add(pen(d), S[sc] + t0)
for sc, t0 in POLA: add(tape_rip(0.9), S[sc] + t0 - 0.05); add(slap(0.9), q(S[sc] + t0))
for sc, t0 in STRIP:
    tt0 = q(S[sc] + t0)
    for k in range(5): add(type_clack(0.25), tt0 - 0.35 + k * 0.06)
    add(slap(0.7), tt0)
add(bell(2093, 0.8, 0.2), q(S[2] + 1.3 + 4 * .55) + 0.12)  # dzwonek maszyny
for sc, t0 in STICK: add(slap(1.0), q(S[sc] + t0)); add(tape_rip(0.6), S[sc] + t0 + 0.15)
# 300 zł – akcent
add(kick(0.9), q(S[4] + 0.75)); add(vib(196.0, 1.5, 0.2), q(S[4] + 0.75))
# finał
for k, f in enumerate([659.25, 830.61, 987.77, 1318.5]): add(vib(f, 1.6, 0.1), S[5] + 3.2 + k * 0.07)

mix[:] += mus * 0.55
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
