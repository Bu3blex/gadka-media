import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from design import *

W, H = 1080, 1350
M = 80
OUT = os.path.join(os.environ.get("GADKA_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")), "karuzele")


def footer(d, i, n, dark=True):
    wordmark(d, M + 22, H - 96, 30, bg=NAVY)
    f = font("semi", 30)
    t = f"{i}/{n}"
    d.text((W - M - d.textlength(t, font=f), H - 92), t, font=f, fill=CREAM)


def s_cover(code, kicker, head, head2, i, n):
    im = cover(code, W, H)
    im = gradient(im, 380, 1000, bottom_alpha=235)
    d = ImageDraw.Draw(im)
    fh = font("black", 112)
    l1 = len(wrap(d, head, fh, W - 2 * M)); l2 = len(wrap(d, head2, fh, W - 2 * M)) if head2 else 0
    y = 1080 - round(112 * 1.02) * (l1 + l2)
    pill(d, M, y - 100, kicker, font("bold", 30))
    y = text_block(d, M, y, head, fh, WHITE, W - 2 * M, lh=1.02)
    if head2:
        text_block(d, M, y, head2, fh, ORANGE, W - 2 * M, lh=1.02)
    swipe = "Przesuń  →"
    f = font("semi", 32)
    footer(d, i, n)
    return im


def s_photo(code, num, title, sub, i, n):
    im = cover(code, W, H)
    im = gradient(im, 560, 1080, bottom_alpha=235)
    d = ImageDraw.Draw(im)
    ft, fs = font("black", 84), font("med", 40)
    tl = len(wrap(d, title, ft, W - 2 * M)); sl = len(wrap(d, sub, fs, W - 2 * M))
    y = 1150 - round(84 * 1.05) * tl - 20 - round(40 * 1.3) * sl
    if num:
        pill(d, M, y - 96, num, font("bold", 30))
    y = text_block(d, M, y, title, ft, WHITE, W - 2 * M, lh=1.05)
    text_block(d, M, y + 20, sub, fs, CREAM, W - 2 * M, lh=1.3)
    footer(d, i, n)
    return im


def s_list(title, items, i, n, numbered=False, code=None):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    if code:  # thin photo band at top
        band = cover(code, W, 300)
        band = gradient(band, 80, 300, bottom_alpha=255)
        im.paste(band, (0, 0))
        d = ImageDraw.Draw(im)
    ft, fi = font("black", 84), font("semi", 48)
    y = 330 if code else 150
    y = text_block(d, M, y, title, ft, WHITE, W - 2 * M, lh=1.05) + 40
    step = 118 if len(items) <= 5 else 104
    for k, it in enumerate(items):
        if numbered:
            r = 34
            d.ellipse((M, y + 4, M + 2 * r, y + 4 + 2 * r), fill=ORANGE)
            t = str(k + 1)
            fn_ = font("black", 38)
            d.text((M + r - d.textlength(t, font=fn_) / 2, y + 13), t, font=fn_, fill=WHITE)
        else:
            d.rounded_rectangle((M, y + 26, M + 26, y + 52), radius=6, fill=ORANGE)
        d.text((M + (100 if numbered else 56), y + 8), nbsp(it), font=fi, fill=CREAM)
        y += step
    footer(d, i, n)
    return im


def s_cta(code, i, n, head="Zarezerwuj termin", sub="2 godziny od 300 zł netto"):
    im = Image.new("RGB", (W, H), NAVY)
    band = cover(code, W, 560)
    band = gradient(band, 200, 560, bottom_alpha=255)
    im.paste(band, (0, 0))
    d = ImageDraw.Draw(im)
    y = text_block(d, M, 600, head, font("black", 104), WHITE, W - 2 * M, lh=1.02)
    y = text_block(d, M, y + 10, sub, font("black", 64), ORANGE, W - 2 * M, lh=1.1)
    fs = font("med", 40)
    for ln in ["Rezerwacja i płatność online", "ul. Chełmżyńska 10E, Warszawa", "Bezpłatny parking pod wejściem"]:
        d.rounded_rectangle((M, y + 52, M + 14, y + 66), radius=4, fill=ORANGE)
        d.text((M + 36, y + 36), ln, font=fs, fill=CREAM)
        y += 64
    pill(d, M, y + 70, "Link w bio  →", font("bold", 40), bg=ORANGE)
    footer(d, i, n)
    return im


C = {
    "2026-10-07": [
        ("cover", "041", "NOWA NAZWA", "Studio B to teraz", "Gadka studio"),
        ("photo", "001", "", "Samoobsługowe studio nagraniowe", "Podcasty, rolki, webinary i kursy online. Nagrywasz po swojemu."),
        ("list", "Co masz na miejscu", ["2 kamery 4K Sony ZV-E10", "4× mikrofon Shure SM7B", "Mikser RØDECaster Pro", "Studyjne światło bez szumu", "Ponad 15 aranżacji"], False, "031"),
        ("photo", "022", "", "2 godziny od 300 zł netto", "Bez ekipy, bez długich umów i bez dopłat za sprzęt."),
        ("cta", "037"),
    ],
    "2026-10-14": [
        ("cover", "056", "300 ZŁ NETTO", "Za 300 zł nie kupisz dobrych butów.", "A możesz zacząć podcast."),
        ("list", "Co jest w cenie", ["2 h w wygłuszonej sali", "2 kamery 4K", "4 mikrofony Shure SM7B", "Światło, meble i tła", "Pliki od ręki na pendrive", "Kuchnia, kawa i toaleta"], False, "028"),
        ("photo", "050", "", "Mikser RØDECaster Pro", "4 wejścia XLR i nagrywanie na kartę microSD."),
        ("photo", "034", "", "Gdzie haczyk?", "Montaż robisz sam albo oddajesz swojemu montażyście. To wszystko."),
        ("cta", "041"),
    ],
    "2026-10-21": [
        ("cover", "037", "ROLKI I PODCASTY", "Jedno studio,", "cztery klimaty"),
        ("photo", "044", "01", "Lamele i ciemna ściana", "Elegancko. Idealne do rozmów biznesowych."),
        ("photo", "010", "02", "Granatowa zasłona", "Klasyczny podcastowy look."),
        ("photo", "019", "03", "Biała cegła", "Jasno, ciepło i lifestyle'owo."),
        ("photo", "028", "04", "Okrągły stół", "Rozmowa nawet w 4 osoby."),
        ("cta", "041", "Wszystkie w jednej sesji", "2 godziny od 300 zł netto"),
    ],
    "2026-10-28": [
        ("cover", "016", "PIERWSZY RAZ W STUDIU?", "Spokojnie.", "Nie zostawimy Cię z tym samego."),
        ("list", "Tak wygląda sesja", ["Rezerwujesz termin online", "Parkujesz pod samym wejściem", "15 minut szkolenia ze sprzętu", "Nagrywasz po swojemu", "Wychodzisz z gotowymi plikami"], True, "034"),
        ("photo", "047", "", "Szkolenie nie zjada Ci czasu", "10–15 minut na start nie wlicza się w czas wynajmu."),
        ("photo", "053", "", "Wychodzisz z plikami", "Na swoim pendrivie albo online w 1 dzień roboczy."),
        ("cta", "001", "Pierwszy odcinek?", "Wybierz dłuższy termin"),
    ],
}

if __name__ == "__main__":
    for date, slides in C.items():
        od = os.path.join(OUT, date)
        os.makedirs(od, exist_ok=True)
        n = len(slides)
        for i, s in enumerate(slides, 1):
            k = s[0]
            if k == "cover":
                im = s_cover(*s[1:], i, n)
            elif k == "photo":
                im = s_photo(*s[1:], i, n)
            elif k == "list":
                im = s_list(s[1], s[2], i, n, numbered=s[3], code=s[4])
            else:
                im = s_cta(s[1], i, n, *s[2:])
            im.save(os.path.join(od, f"{i:02d}.jpg"), quality=90)
        print(date, n)
