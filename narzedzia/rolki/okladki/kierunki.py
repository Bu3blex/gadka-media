from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import os
F = "/usr/share/fonts/opentype/inter/InterDisplay-%s.otf"
def font(w, s): return ImageFont.truetype(F % w, s)
BLACK, CREAM, ORANGE = (17, 17, 17), (249, 238, 228), (255, 89, 42)
S = os.path.dirname(os.path.abspath(__file__)); IMG = os.path.join(S, "..", "wow6", "img")
LOGO = Image.open(os.path.join(S, "..", "wow6", "logo.png")).convert("RGBA")
LOGOB = Image.open(os.path.join(S, "..", "wow6", "logo_black.png")).convert("RGBA")
def logo(im, x, y, w, dark):
    lg = (LOGOB if dark else LOGO); lg = lg.resize((w, int(w * lg.height / lg.width))); im.paste(lg, (x, y), lg)
def fitlines(lines, wname, maxw, start):
    s = start
    while s > 40:
        f = font(wname, s)
        if all(f.getlength(l) <= maxw for l in lines): return f, s
        s -= 4
    return font(wname, s), s

# A: wielka typografia
def A(lines, bg, fg, acc_idx, acc, tag):
    im = Image.new("RGB", (1080, 1920), bg); d = ImageDraw.Draw(im)
    f, s = fitlines(lines, "Black", 960, 260)
    lh = int(s * 0.98); y0 = 960 - lh * len(lines) // 2 + lh // 2
    for i, l in enumerate(lines):
        d.text((60, y0 + i * lh), l, font=f, fill=acc if i == acc_idx else fg, anchor="lm")
    d.text((60, 330), tag, font=font("Bold", 42), fill=fg, anchor="lm")
    logo(im, 1080 - 60 - 210, 300, 210, bg != BLACK)
    d.text((60, 1600), "▶  gadkastudio.pl", font=font("Bold", 40), fill=fg, anchor="lm")
    return im
# B: zdjęcie w duotonie + naklejka
def duo(path, dark, light):
    g = ImageOps.grayscale(Image.open(path)); g = ImageOps.autocontrast(g, 2)
    return ImageOps.colorize(g, dark, light)
def B(photo, fx, l1, l2, dark, light, stick_bg, stick_fg, rot):
    p = duo(os.path.join(IMG, photo), dark, light)
    s = 1920 / p.height; p = p.resize((int(p.width * s), 1920), Image.LANCZOS)
    x0 = int(max(0, min(p.width - 1080, p.width * fx - 540))); im = p.crop((x0, 0, x0 + 1080, 1920)).filter(ImageFilter.GaussianBlur(3))
    d = ImageDraw.Draw(im)
    for (txt, bgc, fgc, y, r) in ((l1, stick_bg, stick_fg, 820, rot), (l2, stick_fg, stick_bg, 1010, -rot)):
        f, sz = fitlines([txt], "Black", 900, 150)
        w = int(f.getlength(txt)) + 80; h = int(sz * 1.25)
        st = Image.new("RGBA", (w, h), bgc + (255,)); ImageDraw.Draw(st).text((w // 2, h // 2), txt, font=f, fill=fgc, anchor="mm")
        st = st.rotate(r, expand=True, resample=Image.BICUBIC)
        im.paste(st, (540 - st.width // 2, y - st.height // 2), st)
    logo(im, 540 - 130, 1450, 260, False)
    return im
# C: seria – numer odcinka
def C(num, title, sub):
    im = Image.new("RGB", (1080, 1920), BLACK); d = ImageDraw.Draw(im)
    d.text((70, 330), "GADKA STUDIO PRZEDSTAWIA", font=font("Bold", 36), fill=ORANGE, anchor="lm")
    big = font("Black", 560)
    d.text((40, 760), num, font=big, fill=BLACK, stroke_width=5, stroke_fill=ORANGE, anchor="lm")
    f, s = fitlines(title, "Black", 940, 130)
    for i, l in enumerate(title): d.text((70, 1150 + i * int(s * 1.0)), l, font=f, fill=CREAM, anchor="lm")
    yb = 1150 + len(title) * int(s * 1.0) + 10
    d.rectangle((70, yb, 330, yb + 14), fill=ORANGE)
    d.text((70, yb + 80), sub, font=font("SemiBold", 44), fill=(180, 170, 160), anchor="lm")
    logo(im, 70, 1560, 200, False)
    return im

out = os.path.join(S, "kierunki"); os.makedirs(out, exist_ok=True)
sets = {
 "A": [A(["STUDIO", "W DOMU?", "POLICZMY."], ORANGE, BLACK, 2, CREAM, "ROLKA · KOSZYK"),
       A(["MAMY", "TWÓJ", "PODCAST."], CREAM, BLACK, 2, ORANGE, "ROLKA · OKUP"),
       A(["PROGNOZA:", "NAGRYWASZ."], BLACK, CREAM, 1, ORANGE, "ROLKA · POGODA")],
 "B": [B("053.jpg", .5, "Studio w domu?", "Policzmy.", (40, 12, 0), ORANGE, CREAM, BLACK, -3),
       B("101.jpg", .5, "Mamy Twój", "podcast.", BLACK, CREAM, ORANGE, BLACK, 3),
       B("104.jpg", .5, "Prognoza:", "nagrywasz.", (20, 30, 70), (150, 200, 255), CREAM, BLACK, -3)],
 "C": [C("01", ["Studio w domu?", "Policzmy."], "ile kosztuje sprzęt vs 300 zł"),
       C("06", ["Mamy Twój", "podcast."], "list z żądaniem okupu"),
       C("05", ["Prognoza dla", "twórców"], "ostrzeżenie: echo w kuchni")],
}
sheet = Image.new("RGB", (3 * 364 + 60, 3 * 484 + 40), "white"); d = ImageDraw.Draw(sheet)
for r, (k, ims) in enumerate(sets.items()):
    d.text((10, r * 494 + 250), k, font=font("Black", 60), fill=BLACK, anchor="lm")
    for c, im in enumerate(ims):
        im.save(f"{out}/{k}{c+1}.jpg", quality=93)
        sheet.paste(im.crop((0, 240, 1080, 1680)).resize((360, 480), Image.LANCZOS), (60 + c * 364, r * 494 + 10))
sheet.save(f"{out}/_kierunki.jpg", quality=90)
