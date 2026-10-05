"""Pionowe plansze 1080x1920 do relacji i wyróżnionych relacji Gadka studio (kolory z logo)."""
import os, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design import cover, gradient

W, H = 1080, 1920
M = 84
BLACK = (0, 0, 0)
CARD = (22, 22, 22)
CARD2 = (34, 34, 34)
CREAM = (249, 238, 228)
MUTED = (178, 170, 162)
ORANGE = (255, 89, 42)
GF = "/usr/share/fonts/truetype/google-fonts/"
LOGO_SRC = os.environ.get("GADKA_LOGO", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "marka", "logo_gadka.png"))
OUT = os.environ.get("GADKA_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "wyroznione"))


def F(w, s):
    return ImageFont.truetype(GF + {"b": "Poppins-Bold.ttf", "m": "Poppins-Medium.ttf", "r": "Poppins-Regular.ttf", "l": "Poppins-Light.ttf"}[w], s)


# ---------- logo (czarne tło -> przezroczystość, ostre skalowanie) ----------
_logo = None


def logo_rgba():
    global _logo
    if _logo is None:
        src = Image.open(LOGO_SRC).convert("RGB")
        g = src.convert("L").point(lambda v: 255 if v > 40 else 0)
        src = src.crop(g.getbbox())
        big = src.resize((src.width * 3, src.height * 3), Image.LANCZOS)
        pal = Image.new("P", (1, 1)); pal.putpalette([0, 0, 0, *CREAM, *ORANGE] + [0] * 759)
        q = big.quantize(palette=pal, dither=Image.Dither.NONE)
        rgb = q.convert("RGB")
        alpha = rgb.convert("L").point(lambda v: 0 if v < 20 else 255)
        rgb.putalpha(alpha)
        _logo = rgb
    return _logo


def paste_logo(img, cx, y, width):
    lg = logo_rgba()
    h = round(lg.height * width / lg.width)
    lg = lg.resize((width, h), Image.LANCZOS)
    img.paste(lg, (round(cx - width / 2), y), lg)
    return y + h


# ---------- tekst ----------
def nb(t):
    import re
    return re.sub(r"(?<![\w ])(\w|\d+[×x]?) ", lambda m: m.group(1) + " ", t)


def wrap(d, t, f, mw):
    out = []
    for para in nb(t).split("\n"):
        cur = ""
        for w in para.split(" "):
            c = (cur + " " + w).strip()
            if d.textlength(c, font=f) <= mw:
                cur = c
            else:
                if cur: out.append(cur)
                cur = w
        out.append(cur)
    return out


def text(d, x, y, t, f, fill, mw, lh=1.2, center=False):
    for ln in wrap(d, t, f, mw):
        xx = x + (mw - d.textlength(ln, font=f)) / 2 if center else x
        d.text((xx, y), ln, font=f, fill=fill)
        y += round(f.size * lh)
    return y


def pill(d, x, y, t, f, bg=ORANGE, fg=BLACK, px=30, py=14, center_w=None):
    w = d.textlength(t, font=f); asc, desc = f.getmetrics(); h = asc + desc + py * 2 - 8
    if center_w is not None:
        x = x + (center_w - (w + 2 * px)) / 2
    d.rounded_rectangle((x, y, x + w + 2 * px, y + h), radius=h // 2, fill=bg)
    d.text((x + px, y + py - 4), t, font=f, fill=fg)
    return y + h


def base(tag=None, logo=True):
    im = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(im)
    if logo:
        paste_logo(im, W / 2, 210, 300)
    return im, d


def photo_band(im, code, y0, h, radius=36, fx=None):
    ph = cover(code, W - 2 * M, h, fx=fx)
    mask = Image.new("L", ph.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, ph.width, ph.height), radius=radius, fill=255)
    im.paste(ph, (M, y0), mask)
    return y0 + h


def card(d, y, title, body, h=None, accent=ORANGE, num=None):
    ft, fb = F("b", 46), F("r", 34)
    lines = wrap(d, body, fb, W - 2 * M - 80) if body else []
    hh = h or (52 + 60 + len(lines) * 46 + 36)
    d.rounded_rectangle((M, y, W - M, y + hh), radius=32, fill=CARD)
    d.rounded_rectangle((M, y, M + 12, y + hh), radius=6, fill=accent)
    x = M + 44
    d.text((x, y + 36), title, font=ft, fill=CREAM)
    yy = y + 36 + 66
    for ln in lines:
        d.text((x, yy), ln, font=fb, fill=MUTED); yy += 46
    return y + hh


def headline(d, y, kicker, title, sub=None, center=True):
    if kicker:
        y = pill(d, M, y, kicker, F("b", 30), center_w=W - 2 * M if center else None) + 34
    y = text(d, M, y, title, F("b", 84), CREAM, W - 2 * M, lh=1.08, center=center)
    if sub:
        y = text(d, M, y + 14, sub, F("r", 38), MUTED, W - 2 * M, lh=1.3, center=center)
    return y


def cta(d, y, t="Rezerwacja: gadkastudio.pl"):
    return pill(d, M, y, t, F("b", 38), bg=CREAM, fg=BLACK, center_w=W - 2 * M)


# ================= PLANSZE =================

def nowa_nazwa_1():
    im, d = base(logo=False)
    f = F("m", 64)
    t = "Studio B"
    tw = d.textlength(t, font=f)
    x = (W - tw) / 2; y = 560
    d.text((x, y), t, font=f, fill=MUTED)
    d.line((x - 10, y + 50, x + tw + 10, y + 50), fill=ORANGE, width=8)
    text(d, M, y + 150, "od dziś to", F("l", 56), CREAM, W - 2 * M, center=True)
    yy = paste_logo(im, W / 2, y + 290, 860)
    yy = text(d, M, yy + 90, "To samo miejsce.\nTen sam sprzęt.\nNowa nazwa.", F("b", 54), CREAM, W - 2 * M, lh=1.25, center=True)
    cta(d, yy + 90, "Zobacz: gadkastudio.pl")
    return im


def nowa_nazwa_2():
    im = cover("041", W, H)
    im = gradient(im, 700, 1500, bottom_alpha=245, color=BLACK)
    top = Image.new("L", (1, 520)); [top.putpixel((0, y), round(230 * (1 - y / 520) ** 1.5)) for y in range(520)]
    im.paste(Image.new("RGB", (W, 520), BLACK), (0, 0), top.resize((W, 520)))
    d = ImageDraw.Draw(im)
    paste_logo(im, W / 2, 190, 520)
    y = 1080
    y = text(d, M, y, "Samoobsługowe studio nagraniowe w Warszawie", F("b", 72), CREAM, W - 2 * M, lh=1.1, center=True)
    y = text(d, M, y + 24, "Podcast, rolki, webinar, kurs. Nagrywasz po swojemu, a sprzęt czeka na miejscu.", F("r", 38), MUTED, W - 2 * M, lh=1.3, center=True)
    cta(d, y + 60, "2 h od 300 zł netto")
    return im


# ---- SPRZĘT ----
def sprzet_okladka():
    im, d = base("Wyróżnione: SPRZĘT")
    y = headline(d, 470, "SPRZĘT W CENIE", "Wchodzisz, włączasz i nagrywasz", "Cały sprzęt jest na miejscu. Nic nie dopłacasz.")
    items = [("Mikrofony", "4× Shure SM7B + Sennheiser Wireless"), ("Kamery", "2× Sony ZV-E10, obraz 4K"),
             ("Światło", "Nanlite, Godox, Yongnuo"), ("Audio", "Mikser RØDECaster Pro")]
    y += 70
    for i, (a, b) in enumerate(items):
        d.rounded_rectangle((M, y, W - M, y + 150), radius=30, fill=CARD)
        d.text((M + 40, y + 26), f"0{i+1}", font=F("b", 40), fill=ORANGE)
        d.text((M + 140, y + 22), a, font=F("b", 44), fill=CREAM)
        d.text((M + 140, y + 82), b, font=F("r", 32), fill=MUTED)
        y += 172
    return im


def sprzet_mikrofony():
    im, d = base("SPRZĘT · 01 Mikrofony")
    y = photo_band(im, "059", 360, 470)
    y = headline(d, y + 50, "01 · MIKROFONY", "Brzmisz jak w radiu")
    y = card(d, y + 44, "4× Shure SM7B", "Kultowy mikrofon dynamiczny. Ciepłe, naturalne brzmienie i świetna izolacja od otoczenia.")
    y = card(d, y + 24, "Sennheiser Profile Wireless", "Bezprzewodowy system z dwoma nadajnikami. Swoboda ruchu i czysty kadr bez kabli.")
    return im


def sprzet_kamery():
    im, d = base("SPRZĘT · 02 Kamery")
    y = photo_band(im, "037", 360, 470)
    y = headline(d, y + 50, "02 · KAMERY", "2× Sony ZV-E10")
    feats = [("Obraz 4K", "Ostry, szczegółowy obraz."), ("Szybki autofokus", "Kadr jest czysty od pierwszej sekundy."),
             ("Odchylany ekran", "Widzisz siebie i ustawiasz ujęcie bez pomocy."), ("Dwa ujęcia naraz", "Plan ogólny i zbliżenie: dynamiczny montaż.")]
    y += 44
    for a, b in feats:
        d.ellipse((M + 4, y + 18, M + 30, y + 44), fill=ORANGE)
        d.text((M + 56, y), a, font=F("b", 42), fill=CREAM)
        d.text((M + 56, y + 58), b, font=F("r", 32), fill=MUTED)
        y += 132
    return im


def sprzet_swiatlo():
    im, d = base("SPRZĘT · 03 Oświetlenie")
    y = headline(d, 420, "03 · OŚWIETLENIE", "Światło, które nie szumi", "Ciche lampy, które nie zakłócają mikrofonów.")
    y = card(d, y + 50, "Nanlite FC-500", "Lampa bez wentylatora. 5600 K, CRI 96+.")
    y = card(d, y + 24, "Godox SZ200Bi", "Bi-color 200 W, 2800–6500 K. Zoom 20°–65° i tryb cichy.")
    y = card(d, y + 24, "Yongnuo YN-360 III", "Miecz świetlny LED RGB, 3200–5600 K, CRI 96+. Sterowany pilotem lub smartfonem.")
    return im


def sprzet_audio():
    im, d = base("SPRZĘT · 04 Audio")
    y = photo_band(im, "050", 360, 520)
    y = headline(d, y + 50, "04 · AUDIO", "RØDECaster Pro")
    feats = [("4 wejścia XLR", "Każdy rozmówca na swoim mikrofonie."), ("microSD albo USB", "Nagrywa na kartę lub działa jako interfejs."),
             ("Mix-minus", "Możesz połączyć się z gościem zdalnym.")]
    y += 44
    for a, b in feats:
        d.ellipse((M + 4, y + 18, M + 30, y + 44), fill=ORANGE)
        d.text((M + 56, y), a, font=F("b", 42), fill=CREAM)
        d.text((M + 56, y + 58), b, font=F("r", 32), fill=MUTED)
        y += 132
    return im


# ---- CENNIK ----
def cennik_1():
    im, d = base("Wyróżnione: CENNIK")
    y = headline(d, 440, "CENNIK", "Płacisz tylko za czas", "Ceny netto. Sprzęt i aranżacje w cenie.")
    rows = [("2 h", "300 zł", "150 zł / h", "Rolki, shortsy albo jedna rozmowa"),
            ("4 h", "500 zł", "125 zł / h", "Pełny odcinek podcastu"),
            ("6 h", "750 zł", "125 zł / h", "Kilka odcinków, różne aranżacje"),
            ("8 h", "1000 zł", "125 zł / h", "Cały dzień: seria, szkolenia")]
    y += 60
    for i, (h, p, ph, desc) in enumerate(rows):
        hl = i == 0
        d.rounded_rectangle((M, y, W - M, y + 196), radius=34, fill=CARD if not hl else CARD2, outline=ORANGE if hl else None, width=4)
        d.text((M + 44, y + 40), h, font=F("b", 76), fill=ORANGE)
        d.text((M + 250, y + 30), p, font=F("b", 64), fill=CREAM)
        pw = d.textlength(p, font=F("b", 64))
        d.text((M + 250 + pw + 18, y + 58), "netto", font=F("r", 30), fill=MUTED)
        d.text((M + 250, y + 118), desc, font=F("r", 30), fill=MUTED)
        fw = d.textlength(ph, font=F("m", 28))
        d.text((W - M - 40 - fw, y + 50), ph, font=F("m", 28), fill=MUTED)
        y += 220
    return im


def cennik_2():
    im, d = base("CENNIK · co jest w cenie")
    y = headline(d, 440, "W KAŻDYM PAKIECIE", "Wszystko w cenie")
    items = ["Wygłuszona, klimatyzowana sala 27 m²", "2 kamery 4K i 4 mikrofony Shure SM7B", "Oświetlenie, statywy, meble i tła",
             "Ponad 15 aranżacji przestrzeni", "Pliki od ręki na Twój nośnik", "Bezpłatny parking, kuchnia, kawa, toaleta"]
    y += 50
    for it in items:
        d.rounded_rectangle((M, y + 14, M + 34, y + 48), radius=8, fill=ORANGE)
        y = text(d, M + 64, y, it, F("m", 40), CREAM, W - 2 * M - 64, lh=1.25) + 26
    y += 40
    d.rounded_rectangle((M, y, W - M, y + 250), radius=32, fill=CARD)
    d.text((M + 44, y + 34), "Pierwszy raz?", font=F("b", 44), fill=ORANGE)
    text(d, M + 44, y + 100, "Wybierz dłuższy termin. Szkolenie (10–15 min) nie wlicza się w czas wynajmu.", F("r", 34), CREAM, W - 2 * M - 88, lh=1.3)
    return im


# ---- JAK TO DZIAŁA ----
def krok(num, title, lines, code=None, tag=None):
    im, d = base(tag or f"JAK TO DZIAŁA · krok {num}")
    y = 380
    if code:
        y = photo_band(im, code, y, 520) + 50
    else:
        y = 640
    f = F("b", 150)
    d.text((M, y - 20), f"0{num}", font=f, fill=ORANGE)
    y = text(d, M, y + 170, title, F("b", 80), CREAM, W - 2 * M, lh=1.08) + 30
    for ln in lines:
        d.ellipse((M + 4, y + 20, M + 24, y + 40), fill=ORANGE)
        y = text(d, M + 50, y, ln, F("r", 38), CREAM, W - 2 * M - 50, lh=1.3) + 18
    return im


def jak_okladka():
    im, d = base("Wyróżnione: JAK TO DZIAŁA")
    y = headline(d, 450, "JAK TO DZIAŁA", "Od rezerwacji do gotowych plików", "5 prostych kroków. Bez ekipy i bez długich umów.")
    steps = ["Rezerwujesz online", "Przyjeżdżasz", "Krótkie szkolenie", "Nagrywasz", "Zgrywasz pliki"]
    y += 60
    for i, s in enumerate(steps):
        d.ellipse((M, y, M + 90, y + 90), fill=ORANGE)
        t = str(i + 1); fw = d.textlength(t, font=F("b", 46))
        d.text((M + 45 - fw / 2, y + 12), t, font=F("b", 46), fill=BLACK)
        d.text((M + 130, y + 14), s, font=F("b", 48), fill=CREAM)
        if i < 4:
            d.line((M + 45, y + 96, M + 45, y + 134), fill=CARD2, width=6)
        y += 140
    return im


def jak_dojazd():
    im, d = base("JAK TO DZIAŁA · dojazd")
    y = headline(d, 420, "DOJAZD", "ul. Chełmżyńska 10E, Warszawa")
    y = card(d, y + 50, "Samochodem", "Duży, bezpłatny parking przed studiem. Wjazd bramą od ul. Chełmżyńskiej, obok Żabki.")
    y = card(d, y + 24, "Autobusem", "Linie 145, 225, 143, 183, 173, 402 i 520.")
    y = card(d, y + 24, "Uwaga na mapy!", "Wejście jest od ul. Chełmżyńskiej. Część map prowadzi na tyły budynku, a tam wejścia nie ma.", accent=CREAM)
    return im


# ---- ARANŻACJE ----
def aranz_okladka():
    im = cover("037", W, H)
    im = gradient(im, 760, 1500, bottom_alpha=245, color=BLACK)
    top = Image.new("L", (1, 480)); [top.putpixel((0, y), round(220 * (1 - y / 480) ** 1.5)) for y in range(480)]
    im.paste(Image.new("RGB", (W, 480), BLACK), (0, 0), top.resize((W, 480)))
    d = ImageDraw.Draw(im)
    paste_logo(im, W / 2, 210, 300)
    y = 1120
    y = pill(d, M, y, "ARANŻACJE", F("b", 30), center_w=W - 2 * M) + 34
    y = text(d, M, y, "Jedno studio,\nwiele klimatów", F("b", 80), CREAM, W - 2 * M, lh=1.08, center=True)
    text(d, M, y + 20, "Przesuń i zobacz, jak może wyglądać Twoje nagranie", F("r", 38), MUTED, W - 2 * M, lh=1.3, center=True)
    return im


def aranz(code, num, title, sub, fx=None):
    im = cover(code, W, H, fx=fx)
    im = gradient(im, 1000, 1580, bottom_alpha=240, color=BLACK)
    top = Image.new("L", (1, 420)); [top.putpixel((0, y), round(200 * (1 - y / 420) ** 1.6)) for y in range(420)]
    im.paste(Image.new("RGB", (W, 420), BLACK), (0, 0), top.resize((W, 420)))
    d = ImageDraw.Draw(im)
    paste_logo(im, W / 2, 210, 260)
    y = 1290
    y = pill(d, M, y, f"ARANŻACJA {num}", F("b", 30)) + 30
    y = text(d, M, y, title, F("b", 80), CREAM, W - 2 * M, lh=1.08)
    text(d, M, y + 14, sub, F("r", 38), CREAM, W - 2 * M, lh=1.3)
    return im


def aranz_final():
    im, d = base("ARANŻACJE · na koniec")
    y = photo_band(im, "031", 360, 560)
    y = headline(d, y + 60, "TWOJE STUDIO, TWOJE ZASADY", "Przestawiasz, jak chcesz", "Meble, tła i zasłony zmieniasz sam. W jednej sesji nagrasz kilka rolek w różnych klimatach.")
    cta(d, y + 70)
    return im


def okladka_wyroznionej(label):
    im = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(im)
    r = 330
    cx, cy = W // 2, H // 2
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=ORANGE)
    f = F("b", 96 if len(label) <= 8 else 74)
    lines = label.split("\n")
    lh = round(f.size * 1.05)
    y = cy - lh * len(lines) / 2 - 8
    for ln in lines:
        tw = d.textlength(ln, font=f)
        d.text((cx - tw / 2, y), ln, font=f, fill=BLACK)
        y += lh
    return im


PLANSZE = {
    "01_nowosc/01_studio-b-to-gadka.jpg": nowa_nazwa_1,
    "01_nowosc/02_czym-jest-gadka.jpg": nowa_nazwa_2,
    "02_sprzet/01_okladka.jpg": sprzet_okladka,
    "02_sprzet/02_mikrofony.jpg": sprzet_mikrofony,
    "02_sprzet/03_kamery.jpg": sprzet_kamery,
    "02_sprzet/04_oswietlenie.jpg": sprzet_swiatlo,
    "02_sprzet/05_audio.jpg": sprzet_audio,
    "03_cennik/01_ceny.jpg": cennik_1,
    "03_cennik/02_w-cenie.jpg": cennik_2,
    "04_jak-to-dziala/01_okladka.jpg": jak_okladka,
    "04_jak-to-dziala/02_rezerwacja.jpg": lambda: krok(1, "Rezerwujesz online", ["Wybierasz pakiet: 2, 4, 6 lub 8 godzin", "W kalendarzu widzisz wolne terminy", "Płacisz od razu, online"]),
    "04_jak-to-dziala/03_przyjazd.jpg": lambda: krok(2, "Przyjeżdżasz", ["ul. Chełmżyńska 10E, Warszawa", "Bezpłatny parking pod wejściem", "Wejście od ulicy, obok Żabki"], code="001"),
    "04_jak-to-dziala/04_szkolenie.jpg": lambda: krok(3, "Krótkie szkolenie", ["10–15 minut: kamery, światło, mikrofony i kadry", "Ten czas nie wlicza się w wynajem", "Pytasz o wszystko, potem zostajesz sam"], code="047"),
    "04_jak-to-dziala/05_nagrywasz.jpg": lambda: krok(4, "Nagrywasz po swojemu", ["Sam ustawiasz kamery, mikrofony i światło", "Przestawiasz meble, ściany i zasłony", "Do 4 osób naraz. Własny sprzęt też możesz zabrać"], code="034"),
    "04_jak-to-dziala/06_pliki.jpg": lambda: krok(5, "Zgrywasz pliki", ["Audio i wideo od razu na Twój pendrive lub kartę", "Nie masz nośnika? Wyślemy pliki online w 1 dzień roboczy", "Wychodzisz z gotowym materiałem"], code="053"),
    "04_jak-to-dziala/07_dojazd.jpg": jak_dojazd,
    "05_aranzacje/01_okladka.jpg": aranz_okladka,
    "05_aranzacje/02_lamele.jpg": lambda: aranz("044", "01", "Lamele i ciemna ściana", "Elegancko i spokojnie. Idealne do rozmów biznesowych."),
    "05_aranzacje/03_zaslona.jpg": lambda: aranz("016", "02", "Granatowa zasłona", "Klasyczny podcastowy look z miękkimi fotelami."),
    "05_aranzacje/04_cegla.jpg": lambda: aranz("019", "03", "Biała cegła", "Jasno i ciepło. Skórzane fotele i drewniany stolik."),
    "05_aranzacje/05_okragly-stol.jpg": lambda: aranz("028", "04", "Okrągły stół", "Rozmowa nawet w 4 osoby, mikrofony na ramionach."),
    "05_aranzacje/06_fotele-przy-lamelach.jpg": lambda: aranz("004", "05", "Fotele przy lamelach", "Klasyczny wywiad przy stole, twarzą w twarz."),
    "05_aranzacje/07_przestawiasz.jpg": aranz_final,
    "00_okladki-wyroznionych/nowosc.jpg": lambda: okladka_wyroznionej("NOWOŚĆ"),
    "00_okladki-wyroznionych/sprzet.jpg": lambda: okladka_wyroznionej("SPRZĘT"),
    "00_okladki-wyroznionych/cennik.jpg": lambda: okladka_wyroznionej("CENNIK"),
    "00_okladki-wyroznionych/jak-to-dziala.jpg": lambda: okladka_wyroznionej("JAK TO\nDZIAŁA"),
    "00_okladki-wyroznionych/aranzacje.jpg": lambda: okladka_wyroznionej("ARANŻACJE"),
}

if __name__ == "__main__":
    for path, fn in PLANSZE.items():
        p = os.path.join(OUT, path)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        fn().save(p, quality=92)
        print(p)
