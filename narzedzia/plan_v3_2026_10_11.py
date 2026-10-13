"""Plan v3 (13.10–30.11.2026): każdy post w innym formacie. Szablony: kreatywne.py (grafiki), kinetyczne.py (rolki).
Uruchom: python3 narzedzia/plan_v3_2026_10_11.py [s|c|r|caps|all] [data]   -> ../<RRRR-MM>/v3/..."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kreatywne import *
import kinetyczne as K

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
HASH = "#gadkastudio #studiopodcastowe #studionagraniowe #podcastwarszawa #warszawa"
CTA_TXT = "📅 Rezerwacja online: gadkastudio.pl (link w bio)"
NOWY = "NOWY POST"


def mpath(date, kind, name=None):
    m = date[:7]
    if kind == "relacja":
        return os.path.join(ROOT, m, "v3", "relacje", f"{date}_relacja.jpg")
    if kind == "karuzela":
        return os.path.join(ROOT, m, "v3", "karuzele", date)
    return os.path.join(ROOT, m, "v3", "rolki", f"{date}_rolka_{name}.mp4")


# ================================================================ RELACJE
STORIES = {
    "2026-10-14": lambda: t_receipt(["Ile naprawdę", "kosztuje podcast?"], [("Studio 2 h", "300 zł"), ("2 kamery 4K", "0 zł"), ("4× Shure SM7B", "0 zł"), ("RØDECaster Pro", "0 zł"), ("Światło studyjne", "0 zł"), ("Aranżacje", "0 zł"), ("Kawa i parking", "0 zł")], "300 zł", stick=NOWY, sub="Ceny brutto. Sprzęt zawsze w cenie."),
    "2026-10-16": lambda: t_chat([("l", "Stary, nagrajmy w końcu ten podcast"), ("r", "Nie mamy sprzętu 😅"), ("l", "Jest studio z 4K i Shure SM7B. 300 zł za 2 h"), ("r", "…dobra. Kiedy? 🎙️")], title=["Ta rozmowa", "w końcu się", "wydarzy"], footer_t="Wyślij to swojemu współprowadzącemu 👇"),
    "2026-10-19": lambda: t_bignum("059", "4×", ["Shure SM7B"], sub="Każdy rozmówca ma swój mikrofon. W cenie.", stick="KULTOWY"),
    "2026-10-21": lambda: t_split(("102",), ("104",), "Fotel i lamele", "Cegła i zielone światło", "TO CZY TO?", sub="Odpisz A albo B"),
    "2026-10-23": lambda: t_poster(["NIE", "MASZ", "DYSKU?"], sub="Spokojnie. Przynieś SSD i zgraj pliki od ręki albo wyślemy je w 1 dzień roboczy.", band_t="pliki od ręki"),
    "2026-10-26": lambda: t_meme([("Nikt:", ""), ("Parking w Warszawie:", "płatny co do minuty"), ("Gadka studio:", "bezpłatny, pod samym wejściem")], "105", punch="0 ZŁ ZA PARKING"),
    "2026-10-28": lambda: t_check(["Pierwszy raz", "w studiu?"], [("Pomysł na odcinek", True), ("Dysk SSD na pliki", True), ("Gość albo dwóch", True), ("Stres", False)], sub="Resztę ogarniemy na miejscu. Wprowadzenie trwa 10–15 minut.", stick=NOWY),
    "2026-10-30": lambda: t_photo("104", ["Zielone światło", "dla Twojego", "podcastu"], sub="Lampa RGB zmienia kolor ściany jednym kliknięciem.", emo="💚"),
    "2026-11-02": lambda: t_poster([("GRUDZIEŃ", "o", BLACK), "SIĘ", "ZAPEŁNIA"], bg=ORANGE, sub="Życzenia, podsumowanie roku, kurs na styczeń? Zarezerwuj termin, póki jest w czym wybierać.", emo="🗓️"),
    "2026-11-04": lambda: t_strike(["Do nagrania szkolenia", "nie potrzebujesz:"], ["Ekipy filmowej", "Wynajmu kamer", "Lamp i statywów"], ["Wystarczy", "Gadka studio"], sub="8 godzin w studiu za 1000 zł. Zobacz nowy post.", code="037"),
    "2026-11-06": lambda: t_poster(["CHODŹ.", "MÓW.", ("BRZMI.", CREAM)], bg=ORANGE, sub="Sennheiser Profile Wireless: prowadzący może się ruszać, a dźwięk zostaje czysty.", band_t="mikrofon bezprzewodowy w cenie", it=True),
    "2026-11-09": lambda: t_photo("103", ["Tryb:", "wieczorny wywiad"], sub="Fotel, regał i ciepłe światło. Kadr do rozmów jeden na jeden.", duo=False, emo="🕯️", stick="ARANŻACJA"),
    "2026-11-11": lambda: t_vs("PRZY BIURKU", ["Echo z pustego pokoju", "Okno za plecami", "Kamera z laptopa"], "102", "W GADCE", ["2 kamery 4K", "Shure SM7B", "Wygłuszona sala"]),
    "2026-11-13": lambda: t_polaroids(["Ekipa z 4 osób?", "Siadajcie."], [("028", "okrągły stół"), ("034", "4 mikrofony"), ("031", "1 mikser")], sub="Panel, wywiad albo podcast we czwórkę."),
    "2026-11-16": lambda: t_poster(["BLIK.", "KARTA.", "APPLE PAY.", "GOOGLE PAY."], bg=CREAM, fg=INK, sub="Płacisz online w minutę. Termin trzymamy dla Ciebie 30 minut.", stick="PŁATNOŚCI", accent=ORANGE),
    "2026-11-18": lambda: t_poll(["Ile godzin", "bierzesz?"], [("2 h", "300 zł"), ("4 h", "500 zł"), ("6 h", "750 zł"), ("8 h", "1000 zł")], hint="Ceny brutto. Odpisz, a podpowiemy, co się zmieści 👇", hl=1),
    "2026-11-20": lambda: t_bignum("037", "4K", ["2 kamery naraz"], sub="Plan ogólny i zbliżenie. Montaż od razu wygląda dynamicznie.", fx=.62),
    "2026-11-23": lambda: t_check(["Na miejscu", "czeka"], [("Kuchnia i ekspres", True), ("Własna toaleta", True), ("Klimatyzacja", True), ("Bezpłatny parking", True), ("Realizator za plecami", False)], bg=BLACK, emo="☕"),
    "2026-11-25": lambda: t_chat([("l", "Nagramy w tym roku życzenia dla klientów?"), ("r", "Telefonem przy biurku? 🙃"), ("l", "No…"), ("r", "Rezerwuję Gadkę. 4 h, 500 zł 🎄")], title=["Grudzień", "w każdej firmie"], name="Szef", bg=BLACK, stick=NOWY),
    "2026-11-27": lambda: t_photo("034", ["Ten mikser", "robi robotę", "za realizatora"], sub="RØDECaster Pro: 4 wejścia XLR i mix-minus dla gościa zdalnego.", stick="W CENIE"),
    "2026-11-30": lambda: t_poster(["GRUDZIEŃ", "RUSZA", ("JUTRO.", CREAM)], bg=ORANGE, sub="Nagrania przed świętami? Wybierz pakiet, dzień i godzinę online.", band_t="gadkastudio.pl", emo="🎄"),
}

# ================================================================ KARUZELE
CAROUSELS = {
    "2026-10-14": ([
        slide(t_poster, ["300 ZŁ.", ("CO W TYM", "o", CREAM), "JEST?"], sub="Rozpisaliśmy, za co płacisz w Gadka studio.", stick="ZAPISZ"),
        slide(t_receipt, ["Paragon z sesji"], [("Studio 2 h", "300 zł"), ("2 kamery 4K", "0 zł"), ("4× Shure SM7B", "0 zł"), ("RØDECaster Pro", "0 zł"), ("Światło", "0 zł"), ("Kawa i parking", "0 zł")], "300 zł"),
        slide(t_bignum, "056", "4×", ["Shure SM7B"], sub="Kultowy mikrofon podcasterów. Każdy ma swój."),
        slide(t_bignum, "037", "2×", ["Kamery 4K"], sub="Plan ogólny i zbliżenie naraz.", fx=.62),
        slide(t_strike, ["Gdzie haczyk?"], ["Dopłaty za sprzęt", "Dopłaty za aranżacje"], ["Montaż robisz sam"], sub="Albo oddajesz swojemu montażyście."),
        slide(t_cta, ["2 godziny", "za 300 zł"], sub="Ceny brutto. Pliki od ręki na Twój dysk SSD.", code="106"),
    ], "Za 300 zł nie kupisz dobrych butów. A możesz zacząć swój podcast 👀\n\nCo dostajesz w Gadka studio za 2 godziny:\n\n🎥 2 kamery 4K Sony ZV-E10\n🎧 4 mikrofony Shure SM7B i mikser RØDECaster Pro\n💡 Ciche, studyjne oświetlenie\n🪑 Meble, tła i zasłony, które przestawiasz, jak chcesz\n💾 Pliki audio i wideo od ręki na Twój dysk SSD\n☕ Kuchnia, ekspres do kawy, toaleta i bezpłatny parking\n\nGdzie haczyk? Montaż robisz sam albo oddajesz swojemu montażyście. To wszystko.\n\nCeny brutto, bez dopłat za sprzęt.\n\n" + CTA_TXT + "\n\n" + HASH + " #shuresm7b #podcast"),
    "2026-10-21": ([
        slide(t_grid, ["102", "104", "028", "101"], ["1 studio.", "Który klimat", "jest Twój?"], labels=["1", "2", "3", "4"]),
        slide(t_photo, "102", ["1. Fotel", "przy lamelach"], sub="Ciepłe światło lampy i drewno w tle.", msize=88),
        slide(t_photo, "104", ["2. Cegła", "i kolorowe światło"], sub="Lampa RGB zmienia klimat jednym kliknięciem.", msize=88, mbg=CREAM),
        slide(t_photo, "028", ["3. Okrągły stół"], sub="Rozmowa nawet w 4 osoby. Każdy ma swój mikrofon.", msize=88),
        slide(t_photo, "101", ["4. Dwa fotele", "i zasłona"], sub="Klasyczny wywiad twarzą w twarz.", msize=88, mbg=CREAM),
        slide(t_poll, ["Który", "wybierasz?"], [("1", "Fotel i lamele"), ("2", "Cegła i światło"), ("3", "Okrągły stół"), ("4", "Fotele i zasłona")], hint="Napisz numer w komentarzu 👇", bg=ORANGE),
    ], "Jedno studio, a za każdym razem inny kadr 👀\n\nPrzesuń i wybierz swój klimat 👉\n\n1️⃣ Skórzany fotel przy lamelach: ciepło i kameralnie\n2️⃣ Biała cegła i kolorowe światło: jasno i świeżo\n3️⃣ Okrągły stół: rozmowa nawet w 4 osoby\n4️⃣ Dwa fotele przy granatowej zasłonie: klasyczny wywiad\n\nMeble, tła i zasłony przestawiasz sam, więc w jednej sesji nagrasz kilka rolek w różnych klimatach. Bez dopłat za zmianę scenografii.\n\nKtóry numer jest Twój? Napisz w komentarzu 👇\n\n" + CTA_TXT + "\n\n" + HASH + " #rolki #contentcreator"),
    "2026-10-28": ([
        slide(t_chat, [("l", "Boję się, że nie ogarnę sprzętu 😬"), ("r", "Spokojnie. W 15 minut pokażemy Ci wszystko"), ("l", "Serio?"), ("r", "Serio. Przesuń 👉")], title=["Pierwszy raz", "w studiu?"]),
        slide(t_poster, ["01", "REZERWUJESZ", "ONLINE"], bg=BLACK, fg=CREAM, sub="Pakiet, dzień i godzina. BLIK, karta, Apple Pay albo Google Pay.", maxsize=170),
        slide(t_poster, ["02", "PARKUJESZ", "ZA DARMO"], bg=ORANGE, sub="Wejście od ul. Chełmżyńskiej 10E, obok Żabki.", maxsize=170),
        slide(t_poster, ["03", "15 MINUT", "WPROWADZENIA"], bg=CREAM, fg=INK, sub="Kamery, światło, mikrofony. To część wynajmu, więc za pierwszym razem weź dłuższy pakiet.", maxsize=170),
        slide(t_check, ["04 Nagrywasz", "i wychodzisz"], [("Nagrywasz po swojemu", True), ("Zgrywasz pliki na SSD", True), ("Realizator za plecami", False)], bg=BLACK),
        slide(t_cta, ["Twój pierwszy", "odcinek?"], sub="Zarezerwuj termin w kilka minut.", bg=CREAM),
    ], "Pierwszy raz w studiu i stresujesz się, że zostaniesz sam ze sprzętem? Spokojnie 😌\n\nTak wygląda sesja w Gadka studio:\n\n1️⃣ Rezerwujesz online: pakiet, dzień i godzina, płatność od razu\n2️⃣ Przyjeżdżasz: bezpłatny parking, wejście od ul. Chełmżyńskiej obok Żabki\n3️⃣ Przez 10–15 minut pokazujemy Ci kamery, światło i mikrofony\n4️⃣ Nagrywasz po swojemu, bez realizatora za plecami\n5️⃣ Zgrywasz pliki na swój dysk SSD i wychodzisz z gotowym materiałem\n\nWskazówka: wprowadzenie jest częścią wynajmu, więc przy pierwszej wizycie wybierz dłuższy pakiet.\n\nOznacz kogoś, kto od miesięcy mówi, że zacznie podcast 👇\n\n" + CTA_TXT + "\n\n" + HASH + " #pierwszypodcast #podcast"),
    "2026-11-04": ([
        slide(t_photo, "037", ["Szkolenie", "nagrane RAZ.", ("Nie co kwartał.", CREAM, BLACK)], msize=100, duo=True, pos="low"),
        slide(t_strike, ["Nie potrzebujecie:"], ["Ekipy filmowej", "Wynajmu kamer", "Lamp i statywów"], ["Wystarczy Gadka"]),
        slide(t_vs, "BIURO", ["Echo z open space", "Telefon na statywie"], "031", "STUDIO", ["2 kamery 4K", "Panel do 4 osób"]),
        slide(t_poster, ["CHODŹ.", "MÓW.", ("BRZMI.", CREAM)], bg=ORANGE, sub="Sennheiser Profile Wireless: trener może chodzić i pokazywać.", it=True),
        slide(t_ticket, "8 h", "1000 zł", "Cały dzień: kilka modułów szkolenia i zapowiedzi na social media"),
        slide(t_cta, ["Nagrajcie", "to porządnie"], sub="Pliki od ręki na dysk SSD, montaż może ruszyć od razu.", bg=ORANGE),
    ], "Szkolenie dla nowych pracowników nagrywacie co kwartał na nowo? Zróbcie to raz, porządnie 🎥\n\nW Gadka studio firma nagra szkolenia, onboarding czy filmy produktowe bez wynajmowania ekipy filmowej.\n\n👉 2 kamery 4K: plan ogólny i zbliżenie na prowadzącego\n👉 Sennheiser Profile Wireless: trener może chodzić i pokazywać\n👉 Ciche, studyjne światło niezależnie od pogody\n👉 Do 4 osób w kadrze, np. panel ekspertów\n\nCały dzień w studiu (8 h) to 1000 zł brutto. Pliki zgrywacie od ręki na dysk SSD, więc montaż może ruszyć od razu.\n\n" + CTA_TXT + "\n\n" + HASH + " #filmfirmowy #szkoleniaonline"),
    "2026-11-11": ([
        slide(t_meme, [("Kursant, minuta 1:", "czemu tu jest takie echo?"), ("Kursant, minuta 2:", "zwrot pieniędzy")], "104", punch="NIE RÓB TEGO SOBIE"),
        slide(t_check, ["Plan", "na kurs"], [("Lekcje w krótkich modułach", True), ("4 h albo 6 h w studiu", True), ("Lekcje w jednym klimacie", True), ("Promo w drugim", True), ("Echo i zmywarka w tle", False)]),
        slide(t_polaroids, ["Lekcje i promo", "z jednej sesji"], [("103", "lekcje"), ("104", "promo")]),
        slide(t_ticket, "4 h", "500 zł", "Kilka lekcji i materiały promocyjne z jednej sesji"),
        slide(t_cta, ["Twój kurs", "zasługuje na więcej"], sub="2 kamery 4K, Shure SM7B i RØDECaster Pro na miejscu.", bg=BLACK),
    ], "Kurs online, który wygląda jak nagrany w kuchni? Kursanci widzą to od pierwszej minuty 😅\n\nDo profesjonalnego kursu albo webinaru nie potrzebujesz własnego studia. Wystarczy kilka godzin w naszym.\n\n1️⃣ Podziel lekcje na krótkie moduły\n2️⃣ Zarezerwuj 4 h (500 zł) albo 6 h (750 zł)\n3️⃣ Lekcje nagraj w spokojnej aranżacji, a promo w innym klimacie\n4️⃣ Zgraj pliki na swój dysk SSD i oddaj do montażu tego samego dnia\n\nNa miejscu masz 2 kamery 4K, mikrofony Shure SM7B i mikser RØDECaster Pro. Na start 10–15 minut wprowadzenia do sprzętu. Ceny brutto.\n\n" + CTA_TXT + "\n\n" + HASH + " #kursonline #webinar"),
    "2026-11-18": ([
        slide(t_poll, ["Ile godzin", "potrzebujesz?"], [("2 h", "300 zł"), ("4 h", "500 zł"), ("6 h", "750 zł"), ("8 h", "1000 zł")], hint="Przesuń, podpowiemy 👉", bg=ORANGE),
        slide(t_ticket, "2 h", "300 zł", "Rolki, shortsy albo krótka rozmowa"),
        slide(t_ticket, "4 h", "500 zł", "Pełny odcinek podcastu z gościem", bg=ORANGE),
        slide(t_ticket, "6 h", "750 zł", "Kilka odcinków albo lekcje kursu", bg=CREAM),
        slide(t_ticket, "8 h", "1000 zł", "Cały dzień: szkolenie dla firmy"),
        slide(t_cta, ["Ta sama sala.", "Ten sam sprzęt."], sub="W każdym pakiecie. Pierwszy raz? Weź dłuższy, bo wprowadzenie jest częścią wynajmu.", bg=CREAM),
    ], "2, 4, 6 czy 8 godzin? Podpowiadamy, który pakiet wybrać ⏱️\n\n🟠 2 h, 300 zł: rolki, shortsy albo krótka rozmowa\n🟠 4 h, 500 zł: pełny odcinek podcastu\n🟠 6 h, 750 zł: kilka odcinków albo lekcje kursu\n🟠 8 h, 1000 zł: cały dzień w studiu, np. szkolenie dla firmy\n\nCeny brutto. W każdym pakiecie ta sama sala, te same kamery 4K i mikrofony Shure SM7B. Pierwszy raz? Weź dłuższy pakiet, bo 10–15 minut wprowadzenia jest częścią wynajmu.\n\nZapisz, żeby mieć pod ręką 📌\n\n" + CTA_TXT + "\n\n" + HASH + " #nagrywaniepodcastu #rolki"),
    "2026-11-25": ([
        slide(t_poster, ["ŻYCZENIA", "OD PREZESA", ("NAGRANE", "o", BLACK), ("TELEFONEM?", "o", BLACK)], bg=ORANGE, sub="W tym roku możecie lepiej.", emo="📱"),
        slide(t_chat, [("l", "Nagramy w tym roku życzenia dla klientów?"), ("r", "Telefonem przy biurku? 🙃"), ("l", "No…"), ("r", "Rezerwuję Gadkę 🎄")], title=["Grudzień", "w każdej firmie"], name="Szef", bg=BLACK),
        slide(t_check, ["W jedno", "popołudnie"], [("Podsumowanie roku", True), ("Życzenia dla klientów", True), ("Pionowe wersje", True), ("Film dla zespołu", True)]),
        slide(t_polaroids, ["Dwa klimaty,", "jedna sesja"], [("031", "podsumowanie"), ("104", "życzenia")]),
        slide(t_cta, ["4 godziny", "za 500 zł"], sub="Pliki od ręki na SSD, film trafi do klientów przed świętami.", stick="🎄 GRUDZIEŃ".replace("🎄 ", "")),
    ], "Życzenia świąteczne od prezesa nagrane telefonem przy biurku? W tym roku możecie lepiej 🎄\n\nW Gadka studio nagracie w jedno popołudnie:\n👉 Podsumowanie roku w formie rozmowy przy okrągłym stole\n👉 Życzenia dla klientów na jasnym tle z kolorowym światłem\n👉 Pionowe wersje na LinkedIn i Instagram z tej samej sesji\n👉 Krótki film dla zespołu\n\n4 h w studiu to 500 zł brutto. Pliki zgrywacie od ręki na dysk SSD, więc film trafi do klientów jeszcze przed świętami.\n\nIm bliżej świąt, tym trudniej o dogodny termin.\n\n" + CTA_TXT + "\n\n" + HASH + " #zyczeniaswiateczne #filmfirmowy"),
}

# ================================================================ ROLKI
REELS = {
    "2026-10-13": ("300-zl", lambda: [
        K.k_words([("300 ZŁ", ORANGE), "I MASZ", "STUDIO?"], 1.6),
        K.k_photo("106", 1.0, ["2 godziny", "w studiu"]),
        K.k_photo("037", 1.0, ["2 kamery 4K"], stick="W CENIE", fx=.62),
        K.k_photo("056", 1.0, ["4× Shure SM7B"], stick="W CENIE"),
        K.k_photo("050", 1.0, ["RØDECaster Pro"], stick="W CENIE"),
        K.k_photo("104", 1.0, ["Światło RGB"], emo="💡"),
        K.k_counter(0, 2.0, label="dopłat za sprzęt", frm=999, top="A ile", sub="Wszystko w cenie. Ceny brutto.", bg=BLACK, fg=ORANGE),
        K.k_cta(["2 h w studiu", "za 300 zł"], 2.0, sub="Pliki od ręki na Twój dysk SSD."),
    ], "300 zł i masz studio na 2 godziny. Co w tym jest? 👀\n\n🎙️ 2 godziny w wygłuszonej sali\n🎥 2 kamery 4K\n🎧 4 mikrofony Shure SM7B\n🎚️ Mikser RØDECaster Pro\n💡 Światło studyjne i lampa RGB\n💾 Pliki od ręki na Twój dysk SSD\n\nDopłaty za sprzęt? 0 zł. Ceny brutto.\n\n" + CTA_TXT + "\n\n" + HASH + " #shuresm7b #podcast"),
    "2026-10-20": ("pierwszy-raz", lambda: [
        K.k_words(["POV:", "PIERWSZY RAZ", ("W STUDIU", ORANGE)], 1.6),
        K.k_photo("031", 1.0, ["Tyle sprzętu?!"], emo="😳"),
        K.k_photo("050", 1.0, ["Co to robi?"], emo="🤔", zoom_in=False),
        K.k_chat([("l", "Od czego mam zacząć? 😬"), ("r", "Spokojnie. 15 minut i wszystko ogarniesz"), ("l", "Serio?"), ("r", "Serio. Potem nagrywasz po swojemu 🎙️")], 3.5, title=["Wiadomość", "do Gadki"]),
        K.k_photo("102", 1.5, ["Nagrywasz", "bez stresu"], stick="BEZ REALIZATORA"),
        K.k_cta(["Twój pierwszy", "odcinek?"], 2.0, sub="Przy pierwszej wizycie weź dłuższy pakiet."),
    ], "POV: pierwszy raz w studiu podcastowym i tyle sprzętu, że nie wiesz, od czego zacząć 😅\n\nSpokojnie. Przez pierwsze 10–15 minut pokazujemy Ci kamery, światło i mikrofony. Potem nagrywasz po swojemu, bez realizatora za plecami.\n\nWprowadzenie jest częścią wynajmu, więc za pierwszym razem weź dłuższy pakiet.\n\nOznacz kogoś, kto od miesięcy mówi, że zacznie podcast 👇\n\n" + CTA_TXT + "\n\n" + HASH + " #pierwszypodcast #podcast"),
    "2026-10-27": ("gdzie-haczyk", lambda: [
        K.k_words([("300 ZŁ", ORANGE), "ZA 2 H", "Z 4K?"], 1.5),
        K.k_words(["GDZIE", ("HACZYK?", "o", ORANGE)], 1.0, bg=ORANGE, fg=BLACK),
        K.k_photo("059", 1.0, ["Mikrofony?"], stick="W CENIE"),
        K.k_photo("104", 1.0, ["Światło i tła?"], stick="W CENIE"),
        K.k_photo("053", 1.0, ["Pliki od ręki?"], stick="TAK"),
        K.k_strike(["Dopłaty:"], ["Za sprzęt", "Za aranżacje"], ["0 zł"], 2.5),
        K.k_words(["HACZYK:", "MONTUJESZ", ("SAM.", ORANGE)], 1.5),
        K.k_cta(["Reszta", "jest w cenie"], 2.0, sub="Ceny brutto."),
    ], "300 zł za 2 godziny w studiu z kamerami 4K? Gdzie haczyk? 🤔\n\nMikrofony w cenie? Tak.\nŚwiatło i tła w cenie? Tak.\nPliki od ręki na Twój dysk SSD? Tak.\n\nJedyny haczyk: montaż robisz sam albo oddajesz swojemu montażyście. Reszta jest w cenie. Ceny brutto.\n\n" + CTA_TXT + "\n\n" + HASH + " #podcast #rolki"),
    "2026-11-03": ("szkolenia", lambda: [
        K.k_words(["SZKOLENIE", "NAGRANE", ("RAZ.", ORANGE)], 1.6),
        K.k_strike(["Nie potrzebujecie:"], ["Ekipy filmowej", "Wynajmu kamer", "Lamp"], ["Wystarczy Gadka"], 3.0),
        K.k_photo("037", 1.0, ["2 kamery 4K"], fx=.62),
        K.k_photo("031", 1.0, ["Panel do 4 osób"]),
        K.k_photo("102", 1.0, ["Mikrofon", "bezprzewodowy"], stick="TRENER CHODZI"),
        K.k_counter(1000, 2.0, label="za cały dzień", top="8 godzin", bg=ORANGE, fg=BLACK),
        K.k_cta(["Nagrajcie", "to porządnie"], 2.0, sub="Pliki od ręki na dysk SSD.", bg=BLACK),
    ], "Nagrywacie szkolenia dla zespołu? Zróbcie to raz, a porządnie 🎥\n\n👉 Mikrofon bezprzewodowy: trener chodzi, a dźwięk zostaje czysty\n👉 Panel ekspertów do 4 osób przy okrągłym stole\n👉 Spokojne tło, które nie odciąga uwagi\n👉 Pliki od ręki na dysk SSD, więc montaż rusza tego samego dnia\n\nCały dzień w studiu (8 h) to 1000 zł brutto.\n\n" + CTA_TXT + "\n\n" + HASH + " #filmfirmowy #szkoleniaonline"),
    "2026-11-10": ("kurs-online", lambda: [
        K.k_words(["POV:", "KURS NAGRANY", ("PRZY BIURKU", ORANGE)], 1.6),
        K.k_words(["A MOGŁEŚ", ("TUTAJ 👇".replace(" 👇", ""), ORANGE)], 1.0, bg=ORANGE, fg=BLACK),
        K.k_photo("102", 0.5, ["tutaj"]),
        K.k_photo("104", 0.5, ["albo tutaj"]),
        K.k_photo("101", 0.5, ["albo tutaj"]),
        K.k_photo("028", 0.5, ["albo tutaj"]),
        K.k_photo("019", 0.5, ["albo tutaj"]),
        K.k_photo("010", 1.0, ["Lekcje i promo", "z jednej sesji"]),
        K.k_counter(500, 2.0, label="za 4 godziny", top="Cały kurs", bg=BLACK, fg=ORANGE),
        K.k_cta(["Twój kurs", "w studiu"], 2.0, sub="2 kamery 4K i Shure SM7B na miejscu."),
    ], "POV: nagrywasz kurs online przy biurku, a mogłeś tutaj 👀\n\nFotel przy lamelach, biała cegła z kolorowym światłem albo granatowa zasłona: lekcje nagrasz w jednym klimacie, a materiały promocyjne w drugim. Wszystko z jednej sesji.\n\n4 godziny w studiu to 500 zł brutto. Na miejscu 2 kamery 4K, mikrofony Shure SM7B i ciche światło studyjne.\n\n" + CTA_TXT + "\n\n" + HASH + " #kursonline #webinar"),
    "2026-11-17": ("cennik", lambda: [
        K.k_words(["ILE KOSZTUJE", ("STUDIO?", ORANGE)], 1.5),
        K.k_counter(300, 1.5, top="2 godziny", label="rolki i shorty", bg=ORANGE, fg=BLACK),
        K.k_counter(500, 1.5, top="4 godziny", label="pełny odcinek", code="101"),
        K.k_counter(750, 1.5, top="6 godzin", label="kilka odcinków", bg=CREAM, fg=INK),
        K.k_counter(1000, 1.5, top="8 godzin", label="cały dzień", bg=BLACK, fg=ORANGE),
        K.k_receipt(["Dopłaty za sprzęt?"], [("Kamery 4K", "0 zł"), ("Shure SM7B", "0 zł"), ("Światło", "0 zł"), ("Aranżacje", "0 zł")], "0 zł", 2.0, stamp="CENY BRUTTO", ),
        K.k_cta(["Zapisz", "na później"], 2.0, sub="BLIK, karta, Apple Pay, Google Pay."),
    ], "Ile kosztuje wynajem studia nagraniowego w Warszawie? U nas bez dopłat za sprzęt 👇\n\n2 h: 300 zł\n4 h: 500 zł\n6 h: 750 zł\n8 h: 1000 zł\n\nCeny brutto. W cenie kamery 4K, mikrofony Shure SM7B, światło, meble i tła. Płacisz online: BLIK, Przelewy24, Apple Pay, Google Pay albo kartą.\n\nZapisz, żeby mieć pod ręką 📌\n\n" + CTA_TXT + "\n\n" + HASH + " #podcast #contentcreator"),
    "2026-11-24": ("zyczenia", lambda: [
        K.k_words(["ŻYCZENIA", "OD PREZESA", ("TELEFONEM?", ORANGE)], 1.6),
        K.k_chat([("l", "Nagramy w tym roku życzenia?"), ("r", "Telefonem przy biurku? 🙃"), ("l", "No…"), ("r", "Rezerwuję Gadkę 🎄")], 3.5, title=["Grudzień", "w każdej firmie"], name="Szef", bg=BLACK),
        K.k_words(["W TYM ROKU", ("LEPIEJ.", "o", BLACK)], 1.0, bg=ORANGE, fg=BLACK),
        K.k_photo("031", 1.0, ["Podsumowanie", "roku"]),
        K.k_photo("104", 1.0, ["Życzenia", "dla klientów"], emo="🎄"),
        K.k_photo("102", 1.0, ["Film", "dla zespołu"]),
        K.k_cta(["4 godziny", "za 500 zł"], 2.0, sub="Zarezerwujcie grudzień z wyprzedzeniem."),
    ], "Życzenia od prezesa nagrane telefonem przy biurku? W tym roku zróbcie to lepiej 🎄\n\nPodsumowanie roku przy jednym stole, życzenia dla klientów na jasnym tle i pionowe wersje na social media. Wszystko w jedno popołudnie.\n\n4 godziny w Gadka studio to 500 zł brutto.\n\nWyślij to osobie, która w Twojej firmie ogarnia grudzień 👇\n\n" + CTA_TXT + "\n\n" + HASH + " #zyczeniaswiateczne #filmfirmowy"),
}

if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    only = sys.argv[2] if len(sys.argv) > 2 else None
    if what in ("s", "all"):
        for d, fn in STORIES.items():
            if only and d != only: continue
            p = mpath(d, "relacja"); os.makedirs(os.path.dirname(p), exist_ok=True)
            fn().convert("RGB").save(p, quality=92); print(p, flush=True)
    if what in ("c", "all"):
        for d, (slides, cap) in CAROUSELS.items():
            if only and d != only: continue
            render_carousel(slides, mpath(d, "karuzela")); print(d, flush=True)
    if what in ("r", "all"):
        for d, (name, shots, cap) in REELS.items():
            if only and d != only: continue
            p = mpath(d, "rolka", name); K.render(shots(), p); print(p, flush=True)
    if what in ("caps", "all"):
        opisy = {d + " karuzela": c for d, (_, c) in CAROUSELS.items()}
        opisy.update({d + " rolka": c for d, (_, _, c) in REELS.items()})
        json.dump(opisy, open(os.path.join(ROOT, "opisy_v3_2026_10_11.json"), "w"), ensure_ascii=False, indent=1)
