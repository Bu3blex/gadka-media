"""Rolka „zwiastun kinowy”: dźwięk syntetyczny + render przeglądarki."""
import os, sys, json, time, wave, subprocess
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

WD = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WD, "..", "ai", "rolka_zwiastun.mp4")
FPS, SR = 30, 44100
CARD, T1, T2, J1, J2, ONE, SH = 2.8, 3.2, 4.9, 7.0, 8.9, 10.9, 12.3
B = 0.5  # 120 BPM
SHOTS = [
    [SH, "101", 0.2, 0.8, 1.0, 1.0, ""],
    [SH + 1.5, "056", 0.55, 0.55, 1.0, 1.1, "MIKROFONY SHURE."],
    [SH + 3.0, "037", 0.45, 0.6, 1.05, 1.12, "DWIE KAMERY 4K."],
    [SH + 4.5, "104", 0.5, 0.5, 1.0, 1.08, "ŚWIATŁO|JAK NA PLANIE."],
    [SH + 6.0, "050", 0.35, 0.6, 1.05, 1.05, "PLIKI OD RĘKI."],
]
MON = SH + 7.5
for i, k in enumerate(["031", "019", "010", "105", "034", "102", "001", "022"]):
    SHOTS.append([MON + i * 0.25, k, 0.5, 0.5, 1.1, 1.2, ""])
BLK = MON + 2.0
ILE = BLK + 0.6
PRICE = ILE + 1.2
LOGO = PRICE + 2.3
BILL, SOON = LOGO + 0.5, LOGO + 1.1
STRIKE, TOMO = SOON + 1.1, SOON + 1.4
TOTAL = TOMO + 3.2
DATA = dict(CARD=CARD, T1=T1, T2=T2, J1=J1, J2=J2, ONE=ONE, SH=SH, SHOTS=SHOTS, MON=MON, BLK=BLK, ILE=ILE, PRICE=PRICE,
            LOGO=LOGO, BILL=BILL, SOON=SOON, STRIKE=STRIKE, TOMO=TOMO, TOTAL=TOTAL)
open(os.path.join(WD, "data.js"), "w").write("window.DATA=" + json.dumps(DATA) + ";")

rng = np.random.default_rng(11)
L = int(TOTAL * SR) + 3 * SR
mix = np.zeros(L)
def tt(d): return np.arange(int(d * SR)) / SR
def add(sig, at, g=1.0):
    i = int(at * SR); j = min(L, i + len(sig))
    if 0 <= i < L: mix[i:j] += sig[:j - i] * g
def env(d, a=0.003, dec=0.1):
    t = tt(d); return np.minimum(1, t / a) * np.exp(-t / dec)
def hp(x, k=8): return x - np.convolve(x, np.ones(k) / k, "same")
def lpf(x, k=20): return np.convolve(x, np.ones(k) / k, "same")
def saw(f, t): return 2 * ((f * t) % 1) - 1
def bell(f, d=0.9, g=1.0):
    t = tt(d); parts = ((1, .5, .5), (2.01, .25, .3), (3.0, .12, .2), (4.2, .07, .12))
    return sum(a * np.sin(2 * np.pi * f * p * t) * np.exp(-t / dc) for p, a, dc in parts) * np.minimum(1, t / .002) * g

def braam(f=55, d=3.2, g=1.0, bright=1.0):
    t = tt(d)
    s = sum(saw(f * m, t) * a for m, a in ((1, 1), (1.006, .8), (0.994, .8), (2.003, .5), (1.498, .35), (0.5, .7)))
    s = np.tanh(s * 0.9)
    k1 = int(6 + 40 / bright)
    s = lpf(lpf(s, k1), k1)
    e = np.minimum(1, t / 0.05) * np.exp(-t / (d * 0.38))
    sub = np.sin(2 * np.pi * f * 0.5 * t) * np.exp(-t / 1.4)
    hit = np.sin(2 * np.pi * np.cumsum(38 + 120 * np.exp(-t / 0.04)) / SR) * np.exp(-t / 0.5)
    return (s * e * 0.55 + sub * 0.5 + hit * 0.7) * g

def taiko(g=1.0, f=70):
    t = tt(0.6); body = np.sin(2 * np.pi * np.cumsum(f + 90 * np.exp(-t / 0.02)) / SR) * np.exp(-t / 0.18)
    sk = lpf(rng.normal(0, 1, len(t)), 4) * np.exp(-t / 0.02) * 0.4
    return np.tanh((body + sk) * 1.6) * g
def tick(g=1.0): t = tt(0.03); return hp(rng.normal(0, 1, len(t)), 2) * np.exp(-t / 0.004) * g

def reverb(x, dec=1.6, wet=0.35):
    n = int(dec * SR); ir = rng.normal(0, 1, n) * np.exp(-np.arange(n) / SR / (dec / 5))
    ir = lpf(ir, 6); ir /= np.abs(ir).sum() ** 0.5 * 6
    y = np.convolve(x, ir)[:len(x) + n]
    out = np.zeros(len(y)); out[:len(x)] += x * (1 - wet); return out + y * wet

# --- 1. plansza: projektor
t = tt(CARD)
proj = (lpf(rng.normal(0, 1, len(t)), 10) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 24 * t))) * 0.06
        + np.sin(2 * np.pi * 60 * t) * 0.025)
add(proj, 0.0)
add(tick(0.6), 0.0); add(tick(0.4), 0.05)
add(lpf(rng.normal(0, 1, int(0.06 * SR)), 3) * env(0.06, 0.001, 0.02) * 0.6, CARD - 0.02)

# --- 2. plansze z BRAAM
add(braam(55, 3.5, 0.75), T1)
add(braam(49, 3.0, 0.6, 0.7), T2)
t = tt(J1 - T1); drone = (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 82.4 * t) + 0.3 * np.sin(2 * np.pi * 110.3 * t))
add(drone * np.minimum(1, t / 1.5) * 0.12, T1)
add(np.linspace(0, 1, int(0.4 * SR)) ** 3 * hp(rng.normal(0, 1, int(0.4 * SR)), 3) * 0.25, J1 - 0.4)  # zasysanie przed ciszą
# żart 1: lodówka (muzyka znika)
t = tt(J2 - J1 - 0.1)
hum = (np.sin(2 * np.pi * 50 * t) + 0.6 * np.sin(2 * np.pi * 100 * t) + 0.25 * np.sign(np.sin(2 * np.pi * 150 * t)) * 0.3
       + lpf(rng.normal(0, 1, len(t)), 30) * 0.4) * np.minimum(1, t / 0.05) * np.minimum(1, (t[-1] - t) / 0.05)
add(hum * 0.16, J1 + 0.15)
add(tick(0.5), J1 + 0.12)
# żart 2: echo – klaśnięcie i odbicia
cl = np.zeros(int(0.2 * SR))
for o in (0, 0.01, 0.02):
    s = hp(rng.normal(0, 1, int(0.15 * SR)), 4) * env(0.15, 0.001, 0.03); i = int(o * SR); cl[i:i + len(s)] += s
for k in range(5): add(lpf(cl, 1 + 3 * k) * 0.5 * (0.55 ** k), J2 + 0.05 + 0.35 * k)
add(reverb(cl * 0.3, 2.0, 0.9), J2 + 0.05)
# „jedno miejsce”
add(braam(41.2, 4.0, 1.0, 1.3), ONE)
add(taiko(0.6, 60), ONE)

# --- 3. ujęcia: ostinato smyczków + taiko
roots = [73.42, 73.42, 87.31, 98.0, 110.0]
pat = [1, 1, 2, 1, 1.5, 1, 2, 1.5]
for si in range(5):
    t0 = SH + si * 1.5
    for e in range(6):  # ósemki
        f = roots[si] * pat[(si * 6 + e) % 8]
        d = 0.24; t = tt(d)
        n = (saw(f, t) + saw(f * 1.004, t)) * env(d, 0.008, 0.09)
        add(lpf(n, max(4, 24 - si * 4)) * (0.16 + 0.04 * si), t0 + e * 0.25)
        add(np.sin(2 * np.pi * f / 2 * t) * env(d, 0.005, 0.1) * 0.25, t0 + e * 0.25)
    add(taiko(0.65 + 0.07 * si, 65), t0)
    if si >= 2: add(taiko(0.35, 90), t0 + 0.75)
    if si >= 3: add(taiko(0.35, 90), t0 + 1.0); add(taiko(0.3, 95), t0 + 1.25)
    add(hp(rng.normal(0, 1, int(0.25 * SR)), 3) * np.linspace(0, 1, int(0.25 * SR)) ** 2 * 0.12, t0 - 0.25)
# pad
t = tt(MON - SH)
pad = sum(np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 0.2 * t)) for f in (146.83, 220.0, 293.66)) / 3
add(pad * np.minimum(1, t / 1.0) * 0.08, SH)
# riser do montażu
d = BLK - (SH + 4.5); t = tt(d)
add(hp(rng.normal(0, 1, len(t)), 3) * (t / d) ** 2.5 * 0.28, SH + 4.5)
add(np.sin(2 * np.pi * np.cumsum(200 + 900 * (t / d) ** 2) / SR) * (t / d) ** 2 * 0.12, SH + 4.5)
# montaż: bębny na każde cięcie + szesnastki
for i in range(8):
    x = MON + i * 0.25
    add(taiko(0.75, 60 + 4 * i), x); add(tick(0.3), x)
    add(taiko(0.3, 110), x + 0.125)
    f = 146.83 * (2 ** (i / 12)); t = tt(0.2)
    add((saw(f, t) + saw(f * 1.005, t)) * env(0.2, 0.004, 0.07) * 0.12, x)
# --- 4. cisza, świerszcze
for k in range(3):
    x = ILE + 0.15 + k * 0.38
    for j in range(3):
        t = tt(0.035); add(np.sin(2 * np.pi * 4300 * t) * np.sin(np.pi * t / 0.035) * 0.07, x + j * 0.05)
add(braam(55, 2.6, 0.95, 1.1), PRICE)
add(tick(0.5), PRICE)
# --- 5. logo
add(braam(36.7, 5.0, 1.1, 1.6), LOGO)
add(taiko(0.9, 50), LOGO)
t = tt(TOTAL - LOGO + 0.5)
ch = [146.83, 174.61, 220.0, 293.66, 349.23]
pad = sum(np.sin(2 * np.pi * f * t) + 0.3 * saw(f * 1.002, t) for f in ch) / len(ch)
add(lpf(pad, 10) * np.minimum(1, t / 1.2) * np.exp(-t / 6) * 0.22, LOGO + 0.1)
for k, f in enumerate([587.33, 698.46, 880.0]): add(bell(f, 2.0, 0.1), LOGO + 0.6 + k * 0.4)
# skreślenie + „ding” + puenta
t = tt(0.22); add(hp(rng.normal(0, 1, len(t)), 2) * np.sin(np.pi * t / 0.22) * 0.25, STRIKE)
for k, f in enumerate([1046.5, 1318.5, 1568.0, 2093.0]): add(bell(f, 1.4, 0.25), TOMO + k * 0.06)
add(taiko(0.7, 55), TOMO)
t = tt(TOTAL - TOMO + 0.3)
ch2 = [146.83, 185.0, 220.0, 293.66, 369.99]  # D-dur – optymistyczne rozwiązanie
pad2 = sum(np.sin(2 * np.pi * f * t) for f in ch2) / len(ch2)
add(pad2 * np.minimum(1, t / 0.3) * np.exp(-t / 3) * 0.2, TOMO)

m = mix[:int(TOTAL * SR)]
fo = int(0.9 * SR); m[-fo:] *= np.linspace(1, 0, fo)
m = np.tanh(m * 1.1); m = m / np.abs(m).max() * 0.93
wav = os.path.join(WD, "_mix.wav")
with wave.open(wav, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    a = (m * 32767).astype(np.int16); w.writeframes(np.repeat(a[:, None], 2, 1).tobytes())
print("audio ok", round(TOTAL, 2))
if os.environ.get("AUDIO_ONLY"): sys.exit()
# ---------------- obraz
srv = subprocess.Popen(["python3", "-m", "http.server", "8770"], cwd=WD, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
prev = os.environ.get("PREV")
try:
    with sync_playwright() as p:
        br = p.chromium.launch(args=["--force-device-scale-factor=1", "--no-proxy-server"])
        pg = br.new_page(viewport={"width": 1080, "height": 1920})
        pg.on("pageerror", lambda e: print("pageerror:", e))
        pg.goto("http://127.0.0.1:8770/index.html")
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
