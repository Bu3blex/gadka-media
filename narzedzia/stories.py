import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from design import *

OUT = os.path.join(os.environ.get("GADKA_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")), "relacje")
os.makedirs(OUT, exist_ok=True)

# date, photo, kicker, headline, highlight, sub, cta
S = [
    ("2026-10-07", "041", "NOWA NAZWA", "Studio B to teraz Gadka studio", "Gadka studio", "To samo miejsce, ten sam sprzęt. Nowa energia.", "Zobacz nowy post"),
    ("2026-10-09", "019", "ARANŻACJA #1", "Biała cegła i skórzane fotele", "skórzane fotele", "Jedna z ponad 15 aranżacji w cenie wynajmu.", "Link w bio"),
    ("2026-10-12", "059", "SPRZĘT", "4× Shure SM7B w cenie", "4× Shure SM7B", "Kultowy mikrofon podcasterów. Na każdego rozmówcę osobny.", "Link w bio"),
    ("2026-10-14", "028", "300 ZŁ NETTO", "2 godziny w pełnym studiu", "2 godziny", "2 kamery 4K, mikrofony, światło i pliki od ręki.", "Sprawdź, co jest w cenie"),
    ("2026-10-16", "010", "PIERWSZY RAZ?", "Pokażemy Ci wszystko w 15 minut", "15 minut", "Szkolenie na start nie wlicza się w czas wynajmu.", "Link w bio"),
    ("2026-10-19", "031", "PODCAST W 4 OSOBY", "Okrągły stół i 4 mikrofony", "4 mikrofony", "Rozmowa, panel ekspertów albo wywiad z gośćmi.", "Link w bio"),
    ("2026-10-21", "037", "ROLKI", "Cztery klimaty w jednej sesji", "Cztery klimaty", "Przestawiasz krzesło i nagrywasz kolejną rolkę.", "Zobacz nowy post"),
    ("2026-10-23", "053", "BEZ CZEKANIA", "Pliki od ręki na Twój pendrive", "od ręki", "Nie masz nośnika? Wyślemy je w 1 dzień roboczy.", "Link w bio"),
    ("2026-10-26", "001", "DOJAZD", "Bezpłatny parking pod samym wejściem", "Bezpłatny parking", "ul. Chełmżyńska 10E, Warszawa. Wejście od ulicy.", "Link w bio"),
    ("2026-10-28", "034", "LISTOPAD", "Zarezerwuj termin, zanim zrobi to ktoś inny", "Zarezerwuj termin", "Wybierasz termin w kalendarzu i płacisz online.", "Rezerwuj: link w bio"),
    ("2026-10-30", "056", "GADKA STUDIO", "Masz głos. My mamy studio.", "My mamy studio.", "2 godziny od 300 zł netto. Warszawa.", "Link w bio"),
]


def story(date, code, kicker, head, hl, sub, cta):
    W, H = 1080, 1920
    im = cover(code, W, H)
    _d = ImageDraw.Draw(im)
    _hb = round(104 * 1.04) * len(wrap(_d, head, font("black", 104), W - 160))
    _sb = round(42 * 1.25) * len(wrap(_d, sub, font("med", 42), W - 160))
    _y0 = 1650 - 76 - 40 - _sb - 24 - _hb
    im = gradient(im, _y0 - 520, _y0 + 40, top_alpha=0, bottom_alpha=240)
    # soft top shade for the wordmark
    top = Image.new("L", (1, 420), 0)
    for y in range(420):
        top.putpixel((0, y), round(150 * (1 - y / 420) ** 2))
    im.paste(Image.new("RGB", (W, 420), NAVY), (0, 0), top.resize((W, 420)))
    d = ImageDraw.Draw(im)
    wordmark(d, 80, 230, 40)
    x, maxw = 80, W - 160
    fh = font("black", 104)
    fs = font("med", 42)
    hb = round(104 * 1.04) * len(wrap(d, head, fh, maxw))
    sb = round(42 * 1.25) * len(wrap(d, sub, fs, maxw))
    y0 = 1650 - 76 - 40 - sb - 24 - hb
    pill(d, x, y0 - 100, kicker, font("bold", 30), bg=ORANGE)
    y = text_block(d, x, y0, head, fh, WHITE, maxw, lh=1.04, hl=hl)
    y = text_block(d, x, y + 24, sub, fs, CREAM, maxw, lh=1.25)
    pill(d, x, y + 40, cta + "  →", font("semi", 34), bg=WHITE, fg=NAVY)
    fn = os.path.join(OUT, f"{date}_relacja.jpg")
    im.save(fn, quality=90)
    return fn


if __name__ == "__main__":
    for s in S:
        print(story(*s))
