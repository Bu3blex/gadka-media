import os, sys
sys.argv = ["x"]
exec(open("kierunki.py").read().split("out = os.path.join")[0])
O, Cr, B = ORANGE, CREAM, BLACK
COV = [
 ("01_koszyk", ["STUDIO", "W DOMU?", "POLICZMY."], O, B, 2, Cr, "ROLKA · KOSZYK"),
 ("02_match", ["SZYBKI", "ZAROBEK?", "SWIPE", "W LEWO."], Cr, B, (2, 3), O, "ROLKA · MATCH"),
 ("03_rpg", ["NAGRYWASZ", "TELEFONEM?", "GAME OVER."], B, Cr, 2, O, "ROLKA · 8-BIT"),
 ("04_zwiastun", ["ZWIASTUN.", "PREMIERA:", "JUŻ JUTRO."], O, B, 2, Cr, "ROLKA · ZWIASTUN"),
 ("05_pogoda", ["PROGNOZA:", "NAGRYWASZ."], Cr, B, 1, O, "ROLKA · POGODA"),
 ("06_okup", ["MAMY", "TWÓJ", "PODCAST."], B, Cr, 2, O, "ROLKA · OKUP"),
 ("07_instrukcja", ["INSTRUKCJA", "NAGRANIA", "PODCASTU."], O, B, 2, Cr, "ROLKA · INSTRUKCJA"),
 ("08_muzeum", ["MUZEUM", "DOBRYCH", "CHĘCI."], Cr, B, 2, O, "ROLKA · MUZEUM"),
]
def A2(lines, bg, fg, acc_idx, acc, tag):
    # bezpieczna strefa: środkowy kwadrat 1080x1080 (y 420-1500) z marginesem 90 px
    im = Image.new("RGB", (1080, 1920), bg); d = ImageDraw.Draw(im)
    L, R, T, Bt = 100, 980, 480, 1440
    f, s = fitlines(lines, "Black", R - L, 230)
    while len(lines) * int(s * 0.98) > 640: s -= 4; f = font("Black", s)
    lh = int(s * 0.98); y0 = 960 - lh * len(lines) // 2 + lh // 2
    ai = acc_idx if isinstance(acc_idx, tuple) else (acc_idx,)
    for i, l in enumerate(lines): d.text((L, y0 + i * lh), l, font=f, fill=acc if i in ai else fg, anchor="lm")
    d.text((L, T + 20), tag, font=font("Bold", 38), fill=fg, anchor="lm")
    logo(im, R - 190, T - 10, 190, bg != BLACK)
    d.text((L, Bt - 20), "▶  gadkastudio.pl", font=font("Bold", 38), fill=fg, anchor="lm")
    return im
os.makedirs("final", exist_ok=True)
sheet = Image.new("RGB", (3 * 364, 3 * 484), "white")
for i, (n, *a) in enumerate(COV):
    im = A2(*a); im.save(f"final/okladka_{n}.jpg", quality=95)
    sheet.paste(im.crop((0, 240, 1080, 1680)).resize((360, 480), Image.LANCZOS), ((i % 3) * 364, (i // 3) * 484))
sheet.save("final/_siatka.jpg", quality=90)
# podgląd stref na jednej okładce
im = Image.open("final/okladka_01_koszyk.jpg").convert("RGB"); d = ImageDraw.Draw(im)
d.rectangle((0, 240, 1079, 1680), outline=(0, 120, 255), width=8)
d.rectangle((0, 420, 1079, 1500), outline=(0, 200, 90), width=8)
d.rectangle((0, 1500, 1079, 1919), fill=None, outline=(200, 0, 0), width=8)
d.text((20, 250), "siatka IG 3:4", font=font("Bold", 34), fill=(0, 120, 255))
d.text((20, 430), "kwadrat 1:1 – widoczny wszędzie", font=font("Bold", 34), fill=(0, 160, 70))
d.text((20, 1700), "tu przyciski / opis w aplikacjach", font=font("Bold", 34), fill=(200, 0, 0))
im.resize((540, 960)).save("final/_strefy.jpg", quality=90)
