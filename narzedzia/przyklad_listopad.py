import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from design import *
import stories, carousels, reels
from carousels import s_cover, s_photo, s_list, s_cta, footer, W as CW, H as CH, M as CM
from reels import overlay, render

S = [
    ("2026-11-02", "013", "LISTOPAD", "Planujesz nagrania na grudzień?", "na grudzień?", "Zarezerwuj termin z wyprzedzeniem.", "Link w bio"),
    ("2026-11-04", "037", "DLA FIRM", "Szkolenia nagrasz w jeden dzień", "w jeden dzień", "8 godzin w studiu za 1000 zł netto.", "Zobacz nowy post"),
    ("2026-11-06", "047", "SPRZĘT", "Sennheiser Profile Wireless", "Wireless", "Prowadzący może chodzić, a dźwięk zostaje czysty.", "Link w bio"),
    ("2026-11-09", "004", "ARANŻACJA", "Ciemne fotele i lamele", "lamele", "Elegancki kadr do rozmów biznesowych.", "Link w bio"),
    ("2026-11-11", "007", "KURSY ONLINE", "Kurs, który nie wygląda jak z kuchni", "nie wygląda", "4 godziny w studiu za 500 zł netto.", "Zobacz nowy post"),
    ("2026-11-13", "025", "PIERWSZY RAZ?", "Kliknąć „nagrywaj” możemy za Ciebie", "za Ciebie", "Na start pokazujemy, jak działa cały sprzęt.", "Link w bio"),
    ("2026-11-16", "031", "PODCAST W 4 OSOBY", "Wywiad z gośćmi przy jednym stole", "przy jednym stole", "4 mikrofony Shure SM7B i mikser RØDECaster Pro.", "Link w bio"),
    ("2026-11-18", "028", "PAKIETY", "2, 4, 6 czy 8 godzin?", "8 godzin?", "Podpowiadamy, który pakiet wybrać.", "Zobacz nowy post"),
    ("2026-11-20", "059", "TANIEJ ZA GODZINĘ", "Od 125 zł za godzinę", "125 zł", "Przy pakiecie 8 h za 1000 zł netto.", "Link w bio"),
    ("2026-11-23", "010", "KOMFORT", "Wygłuszona i klimatyzowana sala", "klimatyzowana", "Nagrywasz w ciszy, o każdej porze roku.", "Link w bio"),
    ("2026-11-25", "019", "GRUDZIEŃ W FIRMIE", "Życzenia od firmy? Nagrajcie je u nas", "Nagrajcie je u nas", "Zobacz, jak zrobić to w jedno popołudnie.", "Zobacz nowy post"),
    ("2026-11-27", "050", "BEZ CZEKANIA", "Montujesz tego samego dnia", "tego samego dnia", "Pliki zgrywasz od ręki na swój pendrive.", "Link w bio"),
    ("2026-11-30", "041", "GRUDZIEŃ", "Zaplanuj nagrania na grudzień", "na grudzień", "Wybierasz termin w kalendarzu i płacisz online.", "Rezerwuj: link w bio"),
]


def s_prices(i, n):
    im = Image.new("RGB", (CW, CH), NAVY)
    band = cover("028", CW, 300)
    band = gradient(band, 80, 300, bottom_alpha=255)
    im.paste(band, (0, 0))
    d = ImageDraw.Draw(im)
    y = text_block(d, CM, 330, "Który pakiet wybrać?", font("black", 80), WHITE, CW - 2 * CM, lh=1.05) + 30
    rows = [("2 h", "300 zł", "Odcinek podcastu albo seria rolek"),
            ("4 h", "500 zł", "Dwa odcinki z gośćmi albo kurs"),
            ("6 h", "750 zł", "Lekcje kursu, webinar, kilka osób"),
            ("8 h", "1000 zł", "Cały dzień zdjęciowy dla firmy")]
    for h, price, desc in rows:
        d.rounded_rectangle((CM, y, CW - CM, y + 150), radius=24, fill=(22, 42, 66))
        d.text((CM + 32, y + 30), h, font=font("black", 64), fill=ORANGE)
        d.text((CM + 200, y + 26), price + " netto", font=font("black", 46), fill=WHITE)
        d.text((CM + 200, y + 88), nbsp(desc), font=font("med", 34), fill=CREAM)
        y += 172
    footer(d, i, n)
    return im


C = {
    "2026-11-04": [
        ("cover", "037", "DLA FIRM", "Szkolenie nagrane raz,", "a nie co kwartał"),
        ("list", "Co dostaje firma", ["2 kamery 4K: plan i zbliżenie", "Mikrofon bezprzewodowy", "Równe światło studyjne", "Do 4 osób w kadrze", "Pliki od ręki"], False, "031"),
        ("photo", "047", "", "Sennheiser Profile Wireless", "Trener może chodzić i pokazywać, a dźwięk zostaje czysty."),
        ("photo", "028", "", "Panel ekspertów", "Okrągły stół i 4 mikrofony Shure SM7B."),
        ("cta", "041", "Cały dzień w studiu", "8 godzin za 1000 zł netto"),
    ],
    "2026-11-11": [
        ("cover", "007", "KURSY I WEBINARY", "Kurs online,", "który wygląda profesjonalnie"),
        ("list", "Jak to zaplanować", ["Podziel lekcje na moduły", "Zarezerwuj 4 lub 6 godzin", "Lekcje nagraj przy lamelach", "Promo nagraj przy zasłonie", "Zgraj pliki i oddaj do montażu"], True, "044"),
        ("photo", "044", "", "Lamele i ciemna ściana", "Spokojne tło, które nie odciąga uwagi od lekcji."),
        ("photo", "016", "", "Granatowa zasłona", "Na zapowiedzi i materiały promocyjne."),
        ("cta", "053", "4 godziny w studiu", "500 zł netto"),
    ],
    "2026-11-18": [
        ("cover", "028", "PAKIETY", "2, 4, 6 czy 8 godzin?", "Podpowiadamy."),
        ("prices",),
        ("photo", "059", "", "Im dłużej, tym taniej", "Od 150 zł za godzinę przy 2 h do 125 zł przy 8 h."),
        ("photo", "013", "", "W każdym pakiecie to samo", "Ta sama sala, kamery 4K i mikrofony Shure SM7B."),
        ("cta", "041"),
    ],
    "2026-11-25": [
        ("cover", "019", "GRUDZIEŃ W FIRMIE", "Życzenia nagrane telefonem?", "W tym roku lepiej."),
        ("list", "Nagracie w jedno popołudnie", ["Podsumowanie roku przy stole", "Życzenia dla klientów", "Pionowe wersje na social media", "Film dla zespołu"], False, "034"),
        ("photo", "022", "", "Biała cegła i fotele", "Jasne, ciepłe tło na świąteczne życzenia."),
        ("photo", "031", "", "Rozmowa do 4 osób", "Podsumowanie roku w formie podcastu."),
        ("cta", "001", "4 godziny w studiu", "500 zł netto"),
    ],
}

R = {
    "2026-11-03_rolka_szkolenia": [
        ("037", 2.4, overlay("DLA FIRM", "Nagrywacie", "szkolenia?")),
        ("047", 1.8, overlay(None, "Mikrofon", "bezprzewodowy", "Trener chodzi, dźwięk zostaje czysty.")),
        ("031", 1.6, overlay(None, "Panel", "do 4 osób")),
        ("044", 1.6, overlay(None, "Spokojne", "tło")),
        ("053", 1.6, overlay(None, "Pliki", "od ręki")),
        ("041", 2.8, overlay(None, "Cały dzień", "w studiu", "8 godzin za 1000 zł netto.", "Link w bio  →")),
    ],
    "2026-11-10_rolka_kurs-online": [
        ("007", 2.4, overlay("POV", "Nagrywasz kurs", "przy biurku")),
        ("044", 1.6, overlay(None, "A mogłeś", "tutaj")),
        ("016", 1.4, overlay(None, "Albo", "tutaj")),
        ("019", 1.4, overlay(None, "Albo", "tutaj")),
        ("028", 2.8, overlay(None, "4 godziny", "za 500 zł netto", "Lekcje i promo z jednej sesji.", "Link w bio  →")),
    ],
    "2026-11-17_rolka_cennik": [
        ("059", 2.2, overlay("CENNIK", "Ile kosztuje", "studio?")),
        ("041", 1.5, overlay(None, "2 h", "300 zł")),
        ("037", 1.5, overlay(None, "4 h", "500 zł")),
        ("028", 1.5, overlay(None, "6 h", "750 zł")),
        ("001", 1.5, overlay(None, "8 h", "1000 zł")),
        ("022", 2.8, overlay(None, "Ceny netto,", "z całym sprzętem", "Kamery 4K, mikrofony i światło w cenie.", "Link w bio  →")),
    ],
    "2026-11-24_rolka_zyczenia": [
        ("019", 2.4, overlay("GRUDZIEŃ", "Życzenia od prezesa", "nagrane telefonem?")),
        ("004", 1.6, overlay(None, "W tym roku", "zróbcie to lepiej")),
        ("031", 1.6, overlay(None, "Podsumowanie roku", "przy jednym stole")),
        ("022", 1.6, overlay(None, "Życzenia", "na jasnym tle")),
        ("034", 2.8, overlay(None, "Grudzień", "w Gadka studio", "4 godziny za 500 zł netto.", "Link w bio  →")),
    ],
}

if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("all", "s"):
        pass
        for s in S:
            stories.story(*s)
    if what in ("all", "c"):
        for date, slides in C.items():
            od = os.path.join(carousels.OUT, date); os.makedirs(od, exist_ok=True)
            n = len(slides)
            for i, s in enumerate(slides, 1):
                k = s[0]
                if k == "cover": im = s_cover(*s[1:], i, n)
                elif k == "photo": im = s_photo(*s[1:], i, n)
                elif k == "list": im = s_list(s[1], s[2], i, n, numbered=s[3], code=s[4])
                elif k == "prices": im = s_prices(i, n)
                else: im = s_cta(s[1], i, n, *s[2:])
                im.save(os.path.join(od, f"{i:02d}.jpg"), quality=90)
    if what in ("all", "r"):
        for k, v in R.items():
            print(render(k, v))
