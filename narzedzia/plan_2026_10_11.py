"""Odświeżony plan 13.10–30.11.2026 w stylu wyróżnionych relacji (narzedzia/styl.py).
Uruchom:  python3 narzedzia/plan_2026_10_11.py [s|c|r|all]   (wyniki w ../2026-10 i ../2026-11, folder v2)"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from styl import *

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
HASH = "#gadkastudio #studiopodcastowe #studionagraniowe #podcastwarszawa #warszawa"
CTA_TXT = "📅 Rezerwacja online: gadkastudio.pl (link w bio)"


def mpath(date, kind, name=None):
    m = date[:7]
    if kind == "relacja":
        return os.path.join(ROOT, m, "v2", "relacje", f"{date}_relacja.jpg")
    if kind == "karuzela":
        return os.path.join(ROOT, m, "v2", "karuzele", date)
    return os.path.join(ROOT, m, "v2", "rolki", f"{date}_rolka_{name}.mp4")


# ---------------- RELACJE ----------------
STORIES = {
    "2026-10-14": lambda: story_card("028", "300 ZŁ / 2 H", "2 godziny w pełnym studiu", sub="2 kamery 4K, 4 mikrofony, światło i aranżacje w cenie.", cta="Zobacz nowy post"),
    "2026-10-16": lambda: story_full("102", "PIERWSZY RAZ?", "Pokażemy Ci wszystko na start", sub="10–15 minut wprowadzenia: kamery, światło i mikrofony."),
    "2026-10-19": lambda: story_card("105", "SPRZĘT", "4× Shure SM7B w cenie", sub="Kultowy mikrofon podcasterów. Każdy rozmówca ma swój."),
    "2026-10-21": lambda: story_full("101", "ARANŻACJE", "Skórzane fotele i granatowa zasłona", sub="Zobacz nowy post z aranżacjami.", cta="Zobacz nowy post"),
    "2026-10-23": lambda: story_text("BEZ CZEKANIA", "Wychodzisz", title2="z gotowymi plikami", sub="Zgrywasz je od ręki na swój dysk SSD. Bez dysku? Wyślemy je w 1 dzień roboczy."),
    "2026-10-26": lambda: story_card("001", "DOJAZD", "Bezpłatny parking pod samym wejściem", sub="ul. Chełmżyńska 10E. Wejście od ulicy, obok Żabki."),
    "2026-10-28": lambda: story_text("JAK TO DZIAŁA", "Od rezerwacji", title2="do gotowych plików", card_items=[("Rezerwujesz online", "Pakiet, dzień i godzina. Płacisz od razu."), ("Wprowadzenie", "10–15 minut: sprzęt, światło i kadry."), ("Nagrywasz sam", "Zmieniasz aranżację, jak chcesz."), ("Zgrywasz pliki", "Na swój dysk SSD.")], cta="Zobacz nowy post"),
    "2026-10-30": lambda: story_full("104", "BIAŁA CEGŁA", "Kolorowe światło na ścianie", sub="Lampa RGB zmienia klimat kadru jednym kliknięciem."),
    "2026-11-02": lambda: story_card("106", "LISTOPAD", "Planujesz nagrania na grudzień?", sub="Zarezerwuj termin z wyprzedzeniem.", cta="Rezerwacja: gadkastudio.pl"),
    "2026-11-04": lambda: story_full("037", "DLA FIRM", "Szkolenia nagrasz w jeden dzień", sub="8 godzin w studiu za 1000 zł.", cta="Zobacz nowy post"),
    "2026-11-06": lambda: story_card("047", "SPRZĘT", "Sennheiser Profile Wireless", sub="Prowadzący może chodzić, a dźwięk zostaje czysty."),
    "2026-11-09": lambda: story_full("103", "ARANŻACJA", "Fotel, regał i ciepłe światło", sub="Kameralny kadr do rozmów jeden na jeden."),
    "2026-11-11": lambda: story_text("KURSY ONLINE", "Kurs, który nie wygląda", title2="jak z kuchni", sub="4 godziny w studiu za 500 zł.", cta="Zobacz nowy post"),
    "2026-11-13": lambda: story_card("031", "PODCAST W 4 OSOBY", "Okrągły stół i 4 mikrofony", sub="Rozmowa, panel ekspertów albo wywiad z gośćmi."),
    "2026-11-16": lambda: story_text("PŁATNOŚĆ", "Płacisz tak,", title2="jak lubisz", items=["BLIK", "Przelewy24", "Apple Pay i Google Pay", "Karta płatnicza"], cta="Termin czeka na Ciebie 30 minut"),
    "2026-11-18": lambda: story_card("028", "PAKIETY", "2, 4, 6 czy 8 godzin?", sub="Podpowiadamy, który pakiet wybrać.", cta="Zobacz nowy post"),
    "2026-11-20": lambda: story_full("105", "DWIE KAMERY", "Plan ogólny i zbliżenie naraz", sub="2× Sony ZV-E10 w 4K. Montaż od razu wygląda dynamicznie."),
    "2026-11-23": lambda: story_text("KOMFORT", "Wygłuszona", title2="i klimatyzowana sala", items=["Kuchnia i ekspres do kawy", "Własna toaleta", "Sala na parterze", "Bezpłatny parking"]),
    "2026-11-25": lambda: story_full("019", "GRUDZIEŃ W FIRMIE", "Życzenia od firmy? Nagrajcie je u nas", sub="Zobacz, jak zrobić to w jedno popołudnie.", cta="Zobacz nowy post"),
    "2026-11-27": lambda: story_card("050", "AUDIO", "RØDECaster Pro", sub="4 wejścia XLR i mix-minus dla gościa zdalnego."),
    "2026-11-30": lambda: story_full("106", "GRUDZIEŃ", "Zaplanuj nagrania na grudzień", sub="Wybierasz pakiet, dzień i godzinę.", cta="Rezerwacja: gadkastudio.pl"),
}

# ---------------- KARUZELE (+ opisy) ----------------
CAROUSELS = {
    "2026-10-14": ([
        c_cover("028", "CENNIK", "Co dostajesz", title2="za 300 zł?"),
        c_cards("W CENIE", "2 godziny w pełnym studiu", [("2 kamery 4K", "Sony ZV-E10: plan ogólny i zbliżenie."), ("4× Shure SM7B", "Plus Sennheiser Profile Wireless."), ("Ciche światło studyjne", "Nanlite, Godox i Yongnuo RGB."), ("Meble, tła i zasłony", "Przestawiasz je, jak chcesz.")]),
        c_photo("050", "AUDIO", "Mikser RØDECaster Pro", "4 wejścia XLR, nagrywanie na microSD albo przez USB."),
        c_photo("105", "GDZIE HACZYK?", "Montaż robisz sam", "Albo oddajesz swojemu montażyście. Reszta jest w cenie."),
        c_cta(code="106"),
    ], "Za 300 zł nie kupisz dobrych butów. A możesz zacząć swój podcast 👀\n\nCo dostajesz w Gadka studio za 2 godziny:\n\n🎥 2 kamery 4K Sony ZV-E10\n🎧 4 mikrofony Shure SM7B i mikser RØDECaster Pro\n💡 Ciche, studyjne oświetlenie\n🪑 Meble, tła i zasłony, które przestawiasz, jak chcesz\n💾 Pliki audio i wideo od ręki na Twój dysk SSD\n☕ Kuchnia, ekspres do kawy, toaleta i bezpłatny parking\n\nGdzie haczyk? Montaż robisz sam albo oddajesz swojemu montażyście. To wszystko.\n\n" + CTA_TXT + "\n\n" + HASH + " #shuresm7b #podcast"),
    "2026-10-21": ([
        c_cover("101", "ARANŻACJE", "Jedno studio,", title2="wiele klimatów"),
        c_photo("102", "01 · LAMELE", "Skórzany fotel przy lamelach", "Ciepłe światło lampy i drewno w tle."),
        c_photo("104", "02 · BIAŁA CEGŁA", "Jasno i kolorowo", "Lampa RGB zmienia klimat jednym kliknięciem."),
        c_photo("028", "03 · OKRĄGŁY STÓŁ", "Rozmowa nawet w 4 osoby", "Mikrofony na ramionach, każdy ma swój."),
        c_photo("101", "04 · ZASŁONA", "Dwa fotele, jedna rozmowa", "Klasyczny wywiad twarzą w twarz."),
        c_cta(title="Przestawiasz, jak chcesz", sub="Meble, tła i zasłony zmieniasz sam. Bez dopłat.", code="106"),
    ], "Jedno studio, a za każdym razem inny kadr 👀\n\nPrzesuń i zobacz, jak może wyglądać Twoje nagranie 👉\n\n1️⃣ Skórzany fotel przy lamelach: ciepło i kameralnie\n2️⃣ Biała cegła i kolorowe światło: jasno i świeżo\n3️⃣ Okrągły stół: rozmowa nawet w 4 osoby\n4️⃣ Dwa fotele przy granatowej zasłonie: klasyczny wywiad\n\nMeble, tła i zasłony przestawiasz sam, więc w jednej sesji nagrasz kilka rolek w różnych klimatach. Bez dopłat za zmianę scenografii.\n\nKtóra aranżacja jest Twoja: 1, 2, 3 czy 4? Daj znać w komentarzu 👇\n\n" + CTA_TXT + "\n\n" + HASH + " #rolki #contentcreator"),
    "2026-10-28": ([
        c_cover("102", "PIERWSZY RAZ W STUDIU?", "Spokojnie.", title2="Pokażemy Ci wszystko."),
        c_cards("JAK TO DZIAŁA", "Tak wygląda sesja", [("Rezerwujesz online", "Pakiet, dzień i godzina. Płacisz BLIK-iem, kartą albo Apple/Google Pay."), ("Przyjeżdżasz", "Bezpłatny parking, wejście od ul. Chełmżyńskiej."), ("Wprowadzenie", "10–15 minut: kamery, światło i mikrofony."), ("Nagrywasz i zgrywasz", "Pliki od ręki na Twój dysk SSD.")], num=True),
        c_photo("047", "WPROWADZENIE", "15 minut i wiesz, co gdzie jest", "Wprowadzenie jest częścią wynajmu, więc przy pierwszej wizycie weź dłuższy pakiet."),
        c_photo("053", "PLIKI", "Wychodzisz z gotowym materiałem", "Bez dysku? Wyślemy pliki WeTransferem w 1 dzień roboczy."),
        c_cta(code="101"),
    ], "Pierwszy raz w studiu i stresujesz się, że zostaniesz sam ze sprzętem? Spokojnie 😌\n\nTak wygląda sesja w Gadka studio:\n\n1️⃣ Rezerwujesz online: pakiet, dzień i godzina, płatność od razu\n2️⃣ Przyjeżdżasz: bezpłatny parking, wejście od ul. Chełmżyńskiej obok Żabki\n3️⃣ Przez 10–15 minut pokazujemy Ci kamery, światło i mikrofony\n4️⃣ Nagrywasz po swojemu, bez realizatora za plecami\n5️⃣ Zgrywasz pliki na swój dysk SSD i wychodzisz z gotowym materiałem\n\nWskazówka: wprowadzenie jest częścią wynajmu, więc przy pierwszej wizycie wybierz dłuższy pakiet.\n\n" + CTA_TXT + "\n\n" + HASH + " #pierwszypodcast #podcast"),
    "2026-11-04": ([
        c_cover("037", "SZKOLENIA DLA FIRM", "Nagrane raz,", title2="a nie co kwartał"),
        c_cards("CO DOSTAJE FIRMA", "Studio na cały dzień", [("2 kamery 4K", "Plan ogólny i zbliżenie na prowadzącego."), ("Mikrofon bezprzewodowy", "Trener chodzi, a dźwięk zostaje czysty."), ("Do 4 osób w kadrze", "Panel ekspertów przy okrągłym stole.")]),
        c_photo("031", "PANEL", "Okrągły stół i 4 mikrofony", "Każdy ekspert ma swój Shure SM7B."),
        c_photo("106", "CAŁY DZIEŃ", "8 godzin za 1000 zł", "Kilka modułów szkolenia i jeszcze zapowiedzi na social media."),
        c_cta(code="103"),
    ], "Szkolenie dla nowych pracowników nagrywacie co kwartał na nowo? Zróbcie to raz, porządnie 🎥\n\nW Gadka studio firma nagra szkolenia, onboarding czy filmy produktowe bez wynajmowania ekipy filmowej.\n\n👉 2 kamery 4K: plan ogólny i zbliżenie na prowadzącego\n👉 Sennheiser Profile Wireless: trener może chodzić i pokazywać\n👉 Ciche, studyjne światło niezależnie od pogody\n👉 Do 4 osób w kadrze, np. panel ekspertów\n\nCały dzień w studiu (8 h) to 1000 zł. Pliki zgrywacie od ręki na dysk SSD, więc montaż może ruszyć od razu.\n\n" + CTA_TXT + "\n\n" + HASH + " #filmfirmowy #szkoleniaonline"),
    "2026-11-11": ([
        c_cover("044", "KURSY I WEBINARY", "Kurs online,", title2="który wygląda profesjonalnie"),
        c_cards("PLAN", "Jak to zaplanować", [("Podziel lekcje na moduły", ""), ("Zarezerwuj 4 lub 6 godzin", ""), ("Lekcje w jednej aranżacji", ""), ("Promo w drugiej", ""), ("Pliki zgraj na SSD", "")], num=True),
        c_photo("103", "LEKCJE", "Spokojny kadr, który nie rozprasza", "Fotel, regał i ciepłe światło."),
        c_photo("104", "PROMO", "Inny klimat na zapowiedzi", "Biała cegła i kolorowe światło."),
        c_cta(title="4 godziny w studiu", sub="500 zł za lekcje i promo z jednej sesji.", code="102"),
    ], "Kurs online, który wygląda jak nagrany w kuchni? Kursanci widzą to od pierwszej minuty 😅\n\nDo profesjonalnego kursu albo webinaru nie potrzebujesz własnego studia. Wystarczy kilka godzin w naszym.\n\n1️⃣ Podziel lekcje na krótkie moduły\n2️⃣ Zarezerwuj 4 h (500 zł) albo 6 h (750 zł)\n3️⃣ Lekcje nagraj w spokojnej aranżacji, a promo w innym klimacie\n4️⃣ Zgraj pliki na swój dysk SSD i oddaj do montażu tego samego dnia\n\nNa miejscu masz 2 kamery 4K, mikrofony Shure SM7B i mikser RØDECaster Pro. Na start 10–15 minut wprowadzenia do sprzętu.\n\n" + CTA_TXT + "\n\n" + HASH + " #kursonline #webinar"),
    "2026-11-18": ([
        c_cover("028", "PAKIETY", "2, 4, 6 czy 8 godzin?", title2="Podpowiadamy."),
        c_prices(),
        c_cards("KTÓRY DLA CIEBIE?", "Dobierz pakiet do nagrania", [("2 h", "Rolki, shortsy albo krótka rozmowa."), ("4 h", "Pełny odcinek podcastu z gościem."), ("6 h", "Kilka odcinków albo lekcje kursu."), ("8 h", "Cały dzień: szkolenie dla firmy.")]),
        c_photo("101", "W KAŻDYM PAKIECIE", "Ten sam sprzęt i ta sama sala", "Kamery 4K, mikrofony Shure SM7B, światło i aranżacje."),
        c_cta(code="106"),
    ], "2, 4, 6 czy 8 godzin? Podpowiadamy, który pakiet wybrać ⏱️\n\n🟠 2 h, 300 zł: rolki, shortsy albo krótka rozmowa\n🟠 4 h, 500 zł: pełny odcinek podcastu\n🟠 6 h, 750 zł: kilka odcinków albo lekcje kursu\n🟠 8 h, 1000 zł: cały dzień w studiu, np. szkolenie dla firmy\n\nW każdym pakiecie ta sama sala, te same kamery 4K i mikrofony Shure SM7B. Pierwszy raz? Weź dłuższy pakiet, bo 10–15 minut wprowadzenia jest częścią wynajmu.\n\nZapisz, żeby mieć pod ręką 📌\n\n" + CTA_TXT + "\n\n" + HASH + " #nagrywaniepodcastu #rolki"),
    "2026-11-25": ([
        c_cover("019", "GRUDZIEŃ W FIRMIE", "Życzenia nagrane telefonem?", title2="W tym roku lepiej."),
        c_bullets("W JEDNO POPOŁUDNIE", "Co nagracie", ["Podsumowanie roku przy stole", "Życzenia dla klientów", "Pionowe wersje na social media", "Film dla zespołu"]),
        c_photo("104", "ŻYCZENIA", "Jasne tło i kolorowe światło", "Świąteczny klimat bez dekorowania biura."),
        c_photo("031", "PODSUMOWANIE ROKU", "Rozmowa do 4 osób", "Okrągły stół i mikrofon dla każdego."),
        c_cta(title="4 godziny w studiu", sub="500 zł. Zarezerwujcie grudzień z wyprzedzeniem.", code="101"),
    ], "Życzenia świąteczne od prezesa nagrane telefonem przy biurku? W tym roku możecie lepiej 🎄\n\nW Gadka studio nagracie w jedno popołudnie:\n👉 Podsumowanie roku w formie rozmowy przy okrągłym stole\n👉 Życzenia dla klientów na jasnym tle z kolorowym światłem\n👉 Pionowe wersje na LinkedIn i Instagram z tej samej sesji\n👉 Krótki film dla zespołu\n\n4 h w studiu to 500 zł. Pliki zgrywacie od ręki na dysk SSD, więc film trafi do klientów jeszcze przed świętami.\n\nIm bliżej świąt, tym trudniej o dogodny termin.\n\n" + CTA_TXT + "\n\n" + HASH + " #zyczeniaswiateczne #filmfirmowy"),
}

# ---------------- ROLKI (+ opisy) ----------------
END = lambda title, title2=None, sub=None: r_scene(None, 2.8, None, title, title2=title2, sub=sub, cta="gadkastudio.pl")
REELS = {
    "2026-10-13": ("300-zl", [
        r_scene("105", 2.2, "GADKA STUDIO", "Co dostajesz", title2="za 300 zł?"),
        r_scene("106", 1.5, None, "2 godziny", title2="w studiu"),
        r_scene("037", 1.5, None, "2 kamery 4K"),
        r_scene("059", 1.5, None, "4× Shure SM7B"),
        r_scene("050", 1.5, None, "Mikser", title2="RØDECaster Pro"),
        r_scene("102", 1.5, None, "Różne", title2="aranżacje"),
        END("Wszystko", "w cenie", "Bez dopłat za sprzęt i scenografię."),
    ], "Co dostajesz w studiu za 300 zł? Sprawdź, zanim kupisz kolejny mikrofon do domu 👀\n\n🎙️ 2 godziny w wygłuszonej sali\n🎥 2 kamery 4K\n🎧 4 mikrofony Shure SM7B\n🎚️ Mikser RØDECaster Pro\n🪑 Różne aranżacje do wyboru\n💾 Pliki od ręki na Twój dysk SSD\n\nWszystko w cenie, bez dopłat za sprzęt i scenografię.\n\n" + CTA_TXT + "\n\n" + HASH + " #shuresm7b #podcast"),
    "2026-10-20": ("pierwszy-raz", [
        r_scene("034", 2.4, "POV", "Pierwszy raz", title2="w studiu podcastowym"),
        r_scene("031", 1.8, None, "Tyle sprzętu…", title2="od czego zacząć?"),
        r_scene("047", 2.0, None, "15 minut", title2="wprowadzenia", sub="Kamery, światło i mikrofony."),
        r_scene("101", 1.8, None, "I nagrywasz", title2="bez stresu"),
        END("Twój pierwszy", "odcinek?", "Przy pierwszej wizycie weź dłuższy pakiet."),
    ], "POV: pierwszy raz w studiu podcastowym i tyle sprzętu, że nie wiesz, od czego zacząć 😅\n\nSpokojnie. Przez pierwsze 10–15 minut pokazujemy Ci kamery, światło i mikrofony. Potem nagrywasz po swojemu, bez realizatora za plecami.\n\nWprowadzenie jest częścią wynajmu, więc za pierwszym razem weź dłuższy pakiet.\n\nOznacz kogoś, kto od miesięcy mówi, że zacznie podcast 👇\n\n" + CTA_TXT + "\n\n" + HASH + " #pierwszypodcast #podcast"),
    "2026-10-27": ("gdzie-haczyk", [
        r_scene("028", 2.4, None, "300 zł za 2 h", title2="w studiu z 4K?"),
        r_scene("044", 1.6, None, "Gdzie", title2="haczyk?"),
        r_scene("059", 1.6, None, "Mikrofony w cenie?", title2="Tak."),
        r_scene("104", 1.6, None, "Światło i tła?", title2="Tak."),
        r_scene("053", 1.6, None, "Pliki od ręki?", title2="Tak."),
        r_scene("102", 2.0, "HACZYK", "Montujesz", title2="sam."),
        END("Reszta", "jest w cenie"),
    ], "300 zł za 2 godziny w studiu z kamerami 4K? Gdzie haczyk? 🤔\n\nMikrofony w cenie? Tak.\nŚwiatło i tła w cenie? Tak.\nPliki od ręki na Twój dysk SSD? Tak.\n\nJedyny haczyk: montaż robisz sam albo oddajesz swojemu montażyście. Reszta jest w cenie.\n\n" + CTA_TXT + "\n\n" + HASH + " #podcast #rolki"),
    "2026-11-03": ("szkolenia", [
        r_scene("037", 2.4, "DLA FIRM", "Nagrywacie", title2="szkolenia?"),
        r_scene("047", 1.8, None, "Mikrofon", title2="bezprzewodowy", sub="Trener chodzi, dźwięk zostaje czysty."),
        r_scene("031", 1.6, None, "Panel", title2="do 4 osób"),
        r_scene("103", 1.6, None, "Spokojne", title2="tło"),
        END("Cały dzień", "w studiu", "8 godzin za 1000 zł."),
    ], "Nagrywacie szkolenia dla zespołu? Zróbcie to raz, a porządnie 🎥\n\n👉 Mikrofon bezprzewodowy: trener chodzi, a dźwięk zostaje czysty\n👉 Panel ekspertów do 4 osób przy okrągłym stole\n👉 Spokojne tło, które nie odciąga uwagi\n👉 Pliki od ręki na dysk SSD, więc montaż rusza tego samego dnia\n\nCały dzień w studiu (8 h) to 1000 zł.\n\n" + CTA_TXT + "\n\n" + HASH + " #filmfirmowy #szkoleniaonline"),
    "2026-11-10": ("kurs-online", [
        r_scene("007", 2.4, "POV", "Nagrywasz kurs", title2="przy biurku?"),
        r_scene("102", 1.5, None, "A mogłeś", title2="tutaj"),
        r_scene("104", 1.3, None, "Albo", title2="tutaj"),
        r_scene("101", 1.3, None, "Albo", title2="tutaj"),
        END("4 godziny", "za 500 zł", "Lekcje i promo z jednej sesji."),
    ], "POV: nagrywasz kurs online przy biurku, a mogłeś tutaj 👀\n\nFotel przy lamelach, biała cegła z kolorowym światłem albo granatowa zasłona: lekcje nagrasz w jednym klimacie, a materiały promocyjne w drugim. Wszystko z jednej sesji.\n\n4 godziny w studiu to 500 zł. Na miejscu 2 kamery 4K, mikrofony Shure SM7B i ciche światło studyjne.\n\n" + CTA_TXT + "\n\n" + HASH + " #kursonline #webinar"),
    "2026-11-17": ("cennik", [
        r_scene("059", 2.2, "CENNIK", "Ile kosztuje", title2="studio?"),
        r_scene("106", 1.5, None, "2 h", title2="300 zł"),
        r_scene("101", 1.5, None, "4 h", title2="500 zł"),
        r_scene("028", 1.5, None, "6 h", title2="750 zł"),
        r_scene("104", 1.5, None, "8 h", title2="1000 zł"),
        END("Sprzęt", "w cenie", "Kamery 4K, mikrofony, światło i aranżacje."),
    ], "Ile kosztuje wynajem studia nagraniowego w Warszawie? U nas bez dopłat za sprzęt 👇\n\n2 h: 300 zł\n4 h: 500 zł\n6 h: 750 zł\n8 h: 1000 zł\n\nW cenie kamery 4K, mikrofony Shure SM7B, światło, meble i tła. Płacisz online: BLIK, Przelewy24, Apple Pay, Google Pay albo kartą.\n\nZapisz, żeby mieć pod ręką 📌\n\n" + CTA_TXT + "\n\n" + HASH + " #podcast #contentcreator"),
    "2026-11-24": ("zyczenia", [
        r_scene("019", 2.4, "GRUDZIEŃ", "Życzenia od prezesa", title2="nagrane telefonem?"),
        r_scene("101", 1.6, None, "W tym roku", title2="zróbcie to lepiej"),
        r_scene("031", 1.6, None, "Podsumowanie roku", title2="przy jednym stole"),
        r_scene("104", 1.6, None, "Życzenia", title2="na jasnym tle"),
        END("Grudzień", "w Gadka studio", "4 godziny za 500 zł."),
    ], "Życzenia od prezesa nagrane telefonem przy biurku? W tym roku zróbcie to lepiej 🎄\n\nPodsumowanie roku przy jednym stole, życzenia dla klientów na jasnym tle i pionowe wersje na social media. Wszystko w jedno popołudnie.\n\n4 godziny w Gadka studio to 500 zł.\n\nWyślij to osobie, która w Twojej firmie ogarnia grudzień 👇\n\n" + CTA_TXT + "\n\n" + HASH + " #zyczeniaswiateczne #filmfirmowy"),
}

if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    opisy = {}
    if what in ("s", "all"):
        for d, fn in STORIES.items():
            p = mpath(d, "relacja"); os.makedirs(os.path.dirname(p), exist_ok=True)
            fn().save(p, quality=92)
    if what in ("c", "all"):
        for d, (slides, cap) in CAROUSELS.items():
            render_carousel(slides, mpath(d, "karuzela"))
            opisy[d + " karuzela"] = cap
    if what in ("r", "all"):
        for d, (name, scenes, cap) in REELS.items():
            p = mpath(d, "rolka", name); os.makedirs(os.path.dirname(p), exist_ok=True)
            render_reel(scenes, p); print(p, flush=True)
            opisy[d + " rolka"] = cap
    if what in ("caps",):
        for d, (_, cap) in CAROUSELS.items(): opisy[d + " karuzela"] = cap
        for d, (_, _, cap) in REELS.items(): opisy[d + " rolka"] = cap
        json.dump(opisy, open(os.path.join(ROOT, "opisy_2026_10_11.json"), "w"), ensure_ascii=False, indent=1)
