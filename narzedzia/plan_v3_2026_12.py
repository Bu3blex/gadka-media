"""Plan v3 (grudzień 2026): każdy post w innym formacie. Szablony: kreatywne.py (grafiki), kinetyczne.py (rolki).
Uruchom: python3 narzedzia/plan_v3_2026_12.py [s|c|r|caps|all] [data]   -> ../<RRRR-MM>/v3/..."""
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
    "2026-12-02": lambda: t_poll(["Odcinek", "na koniec roku?"], [("A", "Podsumowanie 2026"), ("B", "Plany na 2027"), ("C", "Jedno i drugie"), ("D", "Jeszcze nie wiem")], hint="Zaznacz w ankiecie albo odpisz literą 👇", hl=2),
    "2026-12-04": lambda: t_receipt(["Grudniowy", "paragon"], [("Studio 6 h", "750 zł"), ("Odcinki na styczeń", "3 szt."), ("Kawa z ekspresu", "0 zł"), ("Parking", "0 zł"), ("Stres w styczniu", "0 zł")], "750 zł", bg=ORANGE, stick="ZAPAS"),
    "2026-12-07": lambda: t_meme([("Nikt:", ""), ("Ja w grudniu:", "nagrywam 3 odcinki na zapas"), ("Ja w styczniu:", "publikuję i piję kawę")], "028", punch="ZAPAS NA STYCZEŃ"),
    "2026-12-09": lambda: t_photo("102", ["Dziadek ma", "lepsze historie", "niż pół internetu"], sub="Nagrajcie z nim rozmowę w studiu. Prezent, który zostaje na lata.", emo="🎁"),
    "2026-12-11": lambda: t_bignum("050", "30", ["minut na płatność"], sub="Tyle trzymamy Twój termin. BLIK, Przelewy24, Apple Pay, Google Pay albo karta.", stick="BEZ STRESU"),
    "2026-12-14": lambda: t_chat([("l", "Co chcesz pod choinkę? 🎄"), ("r", "Shure SM7B 🎙️"), ("l", "Jeden?"), ("r", "Cztery. I studio na 2 h 😇")], title=["List do", "Mikołaja"], name="Mikołaj", footer_t="Wyślij to komuś, kto kupuje Ci prezent 🎁"),
    "2026-12-16": lambda: t_split(("101",), ("028",), "We dwoje w fotelach", "W czwórkę przy stole", "ŚWIĄTECZNY ODCINEK?", sub="Odpisz A albo B"),
    "2026-12-18": lambda: t_strike(["Przed świętami", "nie zdążysz z:"], ["Zakupem kamer", "Wygłuszaniem pokoju", "Nauką miksera"], ["Zdążysz", "z Gadką"], sub="Wprowadzenie do sprzętu trwa 10–15 minut."),
    "2026-12-21": lambda: t_ticket("2 h", "300 zł", "Ostatni odcinek w tym roku: krótko, konkretnie, z plikami od ręki na SSD", bg=CREAM, size=STORY),
    "2026-12-23": lambda: t_polaroids(["Świąteczny klimat", "bez dekorowania"], [("103", "lampion i ciepłe światło")], sub="Ciepłe światło ustawisz sam."),
    "2026-12-25": lambda: t_poster(["WESOŁYCH", ("ŚWIĄT", CREAM), "I DOBREJ", ("GADKI", "o", BLACK)], bg=ORANGE, sub="Dziękujemy za wszystkie rozmowy nagrane u nas w 2026 roku.", emo="🎄"),
    "2026-12-28": lambda: t_vs("SIŁOWNIA", ["Karnet na cały rok", "Byłeś 3 razy"], "031", "PODCAST", ["2 h za 300 zł", "Pliki od ręki na SSD"]),
    "2026-12-30": lambda: t_cta(["Pierwszy odcinek", "w 2027?"], sub="Wybierz styczniowy termin online. Płatność BLIK albo kartą.", code="106", stick="NOWY ROK"),
}

# ================================================================ KARUZELE
CAROUSELS = {
    "2026-12-02": ([
        slide(t_poster, ["5 PYTAŃ", "NA KONIEC", ("ROKU", "o", BLACK)], bg=ORANGE, sub="Gotowy scenariusz na odcinek-podsumowanie 2026.", stick="ZAPISZ"),
        slide(t_bignum, "059", "01", ["Co było hitem?"], sub="Najlepszy odcinek, gość albo moment roku."),
        slide(t_photo, "101", ["02 Co nie", "wyszło?"], sub="Słuchacze lubią szczerość. Jedna wpadka i czego Cię nauczyła.", msize=88),
        slide(t_chat, [("l", "Skąd wziąć pytania od słuchaczy?"), ("r", "Zbierz je w relacji tydzień wcześniej 📩"), ("l", "A jak nikt nie napisze?"), ("r", "Napiszą. Każdy chce być w odcinku 😉")], title=["03 Głos", "słuchaczy"], bg=BLACK),
        slide(t_check, ["04 i 05"], [("Czego chcę w 2027?", True), ("Kogo zaproszę?", True), ("Godzina lania wody", False)]),
        slide(t_cta, ["Nagraj to", "w studiu"], sub="4 h za 500 zł: odcinek i rolki z jednej sesji. Ceny brutto."),
    ], "Odcinek-podsumowanie roku bez scenariusza? Zapisz te 5 pytań 📌\n\n1️⃣ Co było Twoim hitem: odcinek, gość, moment?\n2️⃣ Co nie wyszło i czego Cię to nauczyło?\n3️⃣ Pytania od słuchaczy (zbierz je w relacji tydzień wcześniej)\n4️⃣ Czego chcesz w 2027?\n5️⃣ Kogo zaprosisz do studia w nowym roku?\n\nTaki odcinek nagrasz w 4 godziny, a z tej samej sesji wytniesz rolki na cały styczeń. Na miejscu 2 kamery 4K, 4 mikrofony Shure SM7B i RØDECaster Pro. 4 h to 500 zł brutto.\n\nOznacz współprowadzącego, z którym nagrywasz podsumowanie 👇\n\n" + CTA_TXT + "\n\n" + HASH + " #podsumowanieroku #podcast"),
    "2026-12-09": ([
        slide(t_photo, "102", ["Prezent", "na święta?", ("Rozmowa z dziadkiem.", CREAM, BLACK)], msize=88),
        slide(t_strike, ["Pod choinką", "co roku:"], ["Skarpetki", "Kolejny kubek", "Bon do drogerii"], ["Jego historia"]),
        slide(t_check, ["Pytania,", "które działają"], [("Jak poznałeś babcię?", True), ("Twoja pierwsza praca?", True), ("Najlepsze wakacje?", True), ("Pytania na tak/nie", False)]),
        slide(t_polaroids, ["Dwa fotele.", "Dwie kamery."], [("101", "plan ogólny"), ("103", "zbliżenie")], sub="Ciche światło i nic, co rozprasza."),
        slide(t_ticket, "2 h", "300 zł", "Spokojna rozmowa i pliki od ręki na Twój dysk SSD"),
        slide(t_cta, ["Rodzinna historia", "w 4K"], sub="Do 4 osób przy stole: zabierzcie też babcię.", bg=CREAM),
    ], "Kolejne skarpetki pod choinkę? W tym roku podaruj dziadkowi coś, co zostanie na lata 🎁\n\nNagrajcie rozmowę o jego życiu w studiu:\n\n👉 Jak poznał babcię?\n👉 Jaka była jego pierwsza praca?\n👉 Najlepsze wakacje, najśmieszniejsza wpadka, najważniejsza rada\n\nPytaj otwarcie, nie na tak/nie. Resztę zrobią dobre fotele i spokojne światło.\n\nW Gadka studio: 2 kamery 4K, mikrofony Shure SM7B, do 4 osób przy stole. 2 godziny to 300 zł brutto, a pliki zgrywasz od ręki na swój dysk SSD.\n\nWyślij to rodzeństwu i zróbcie to razem 👇\n\n" + CTA_TXT + "\n\n" + HASH + " #prezentnaswieta #historiarodzinna"),
    "2026-12-16": ([
        slide(t_meme, [("Ty, 2 stycznia:", "nie mam odcinka"), ("Ty, który nagrał w grudniu:", "mam trzy")], "028", punch="NAGRAJ ZAPAS"),
        slide(t_bignum, "031", "6 h", ["3 odcinki"], sub="750 zł brutto. Spokojnie, z przerwą na kawę."),
        slide(t_receipt, ["Plan dnia"], [("0:00 wprowadzenie", "15 min"), ("Odcinek 1", "90 min"), ("Kawa", "30 min"), ("Odcinek 2", "90 min"), ("Odcinek 3", "90 min"), ("Rolki + SSD", "45 min")], "3 odc.", total_label="WYNIK"),
        slide(t_poster, ["ZMIEŃ", "KLIMAT", ("CO ODCINEK", "o", ORANGE)], bg=CREAM, fg=INK, sub="Przestaw meble i zmień kolor lampy RGB między nagraniami."),
        slide(t_vs, "BEZ ZAPASU", ["Nagrywanie na ostatnią chwilę", "Dziura w publikacjach"], "106", "Z ZAPASEM", ["3 odcinki gotowe", "Spokojny styczeń"]),
        slide(t_cta, ["Zapas", "na styczeń"], sub="6 h za 750 zł. Pliki od ręki na Twój dysk SSD."),
    ], "2 stycznia, a Ty nie masz ani jednego odcinka? Nagraj zapas jeszcze w grudniu 🗓️\n\nTak zmieścisz 3 odcinki w 6 godzin:\n\n⏱️ 15 min: wprowadzenie do sprzętu (jest częścią wynajmu)\n🎙️ 90 min: odcinek 1\n☕ 30 min: kawa z ekspresu i zmiana scenografii\n🎙️ 90 min: odcinek 2\n🎙️ 90 min: odcinek 3\n💾 Na koniec: rolki i zgranie plików na Twój dysk SSD\n\nMiędzy odcinkami przestaw meble i zmień kolor lampy RGB, żeby każdy wyglądał inaczej.\n\n6 godzin w studiu to 750 zł brutto.\n\nZapisz plan na później 📌\n\n" + CTA_TXT + "\n\n" + HASH + " #nagrywaniepodcastu #contentplan"),
    "2026-12-23": ([
        slide(t_poster, ["PODCASTER", "PRZY", ("WIGILII", "o", ORANGE)], bg=BLACK, fg=CREAM, sub="Przesuń, jeśli znasz to z autopsji.", emo="🎄"),
        slide(t_chat, [("l", "A z czego Ty żyjesz z tym podcastem?"), ("r", "Ciociu, to pasja 🙂"), ("l", "Pasja… a ilu ma słuchaczy?"), ("r", "Podasz barszcz? 🥣")], title=["Ciocia", "przy barszczu"], name="Ciocia"),
        slide(t_poll, ["Co gorsze?"], [("A", "„Kiedy ślub?”"), ("B", "„Kto tego słucha?”"), ("C", "„Pokaż, jak gadasz”")], hint="Napisz literę w komentarzu 👇", bg=CREAM),
        slide(t_meme, [("Rodzina:", "czym Ty się właściwie zajmujesz?"), ("Ty:", "puszczasz odcinek nagrany w 4K")], "037", punch="I CISZA PRZY STOLE"),
        slide(t_check, ["Jak przetrwać", "Wigilię"], [("Odpowiadaj z uśmiechem", True), ("Pokaż najlepszy odcinek", True), ("Dokładka pierogów", True), ("Kłótnia przy stole", False)], bg=BLACK),
        slide(t_cta, ["Wesołych Świąt", "od Gadki"], sub="A po świętach nowy sezon. Termin zarezerwujesz online."),
    ], "Podcaster przy wigilijnym stole: znasz to? 😅\n\n„A z czego Ty żyjesz z tym podcastem?”\n„Ilu ma słuchaczy?”\n„Pokaż, jak tam gadasz”\n\nNasza rada: odpowiadaj z uśmiechem, pokaż najlepszy odcinek i weź dokładkę pierogów 🥟\n\nKtóre pytanie słyszysz co roku? A, B czy C? Napisz w komentarzu 👇\n\nWesołych Świąt od całej Gadki! 🎄\n\n" + CTA_TXT + "\n\n" + HASH + " #wigilia #podcaster"),
    "2026-12-30": ([
        slide(t_strike, ["Postanowienia", "na 2027:"], ["Siłownia od jutra", "Angielski w aplikacji"], ["Podcast. Serio."], code="106"),
        slide(t_check, ["Zanim", "wejdziesz"], [("Nazwa i temat", True), ("Solo czy z gościem?", True), ("10 tematów na start", True), ("Perfekcyjne logo", False)]),
        slide(t_bignum, "053", "3", ["odcinki na start"], sub="Publikujesz pierwszy, dwa masz w zapasie. Łatwiej utrzymać rytm."),
        slide(t_photo, "034", ["Sprzęt", "już czeka"], sub="2 kamery 4K, 4× Shure SM7B, RØDECaster Pro i światło. W cenie.", msize=88),
        slide(t_ticket, "4 h", "500 zł", "Pierwsza wizyta: wprowadzenie, odcinek i zapas", bg=CREAM),
        slide(t_cta, ["Pierwszy odcinek", "w styczniu"], sub="Wybierz termin online. Ceny brutto.", bg=BLACK),
    ], "Siłownia od poniedziałku i angielski w aplikacji? W 2027 postaw na postanowienie, które naprawdę dowieziesz: podcast 🎙️\n\nChecklista na start:\n\n✅ Nazwa i temat\n✅ Format: solo czy z gościem\n✅ 10 tematów w notatkach\n✅ 3 odcinki nagrane na start: publikujesz pierwszy, dwa masz w zapasie\n❌ Perfekcyjne logo (może poczekać)\n\nSprzęt już czeka: 2 kamery 4K, 4 mikrofony Shure SM7B, mikser RØDECaster Pro i ciche światło studyjne.\n\nPierwszy raz w studiu? Weź 4 h (500 zł brutto), bo 10–15 minut wprowadzenia jest częścią wynajmu.\n\nOznacz osobę, z którą zaczynasz w styczniu 👇\n\n" + CTA_TXT + "\n\n" + HASH + " #postanowienia2027 #nowypodcast"),
}

# ================================================================ ROLKI
REELS = {
    "2026-12-01": ("podsumowanie-roku", lambda: [
        K.k_words(["2026", "W JEDNYM", ("ODCINKU", ORANGE)], 1.5),
        K.k_photo("031", 0.9, ["Najlepsze momenty"]),
        K.k_photo("059", 0.9, ["Wpadki"], emo="🙈"),
        K.k_photo("101", 0.9, ["Plany na 2027"]),
        K.k_chat([("l", "Będzie odcinek-podsumowanie? 👀"), ("r", "Nagrywamy w grudniu w studiu 🎙️"), ("l", "Czekam!")], 3.0, title=["Słuchacz", "pisze"], bg=BLACK, name="Słuchacz"),
        K.k_counter(500, 1.6, top="4 godziny", label="odcinek + rolki", bg=ORANGE, fg=BLACK),
        K.k_cta(["Nagraj swoje", "podsumowanie"], 2.2, sub="Ceny brutto. Pliki od ręki na SSD.", bg=BLACK),
    ], "Cały 2026 w jednym odcinku. Masz już scenariusz? 🎙️\n\nNajlepsze momenty, wpadki i plany na 2027: słuchacze uwielbiają odcinki-podsumowania, a Ty z jednej sesji wytniesz rolki na cały styczeń.\n\n4 godziny w Gadka studio to 500 zł brutto. Na miejscu 2 kamery 4K, mikrofony Shure SM7B i mikser RØDECaster Pro. Pliki zgrywasz od ręki na swój dysk SSD.\n\nW środę wrzucamy 5 pytań do takiego odcinka. Obserwuj, żeby nie przegapić 👀\n\n" + CTA_TXT + "\n\n" + HASH + " #podsumowanieroku #podcast"),
    "2026-12-08": ("prezent-dziadek", lambda: [
        K.k_words(["PREZENT,", "KTÓRY NIE", ("TRAFI", ORANGE), ("DO SZAFY", ORANGE)], 1.6),
        K.k_strike(["Pod choinkę:"], ["Skarpetki", "Kubek", "Bon"], ["Historia dziadka"], 2.6),
        K.k_photo("102", 1.0, ["Dwa fotele"], emo="🎁"),
        K.k_photo("037", 1.0, ["Dwie kamery 4K"], fx=.62),
        K.k_photo("056", 1.0, ["Shure SM7B"], stick="W CENIE"),
        K.k_counter(300, 1.6, top="2 godziny", label="rozmowa na lata", bg=CREAM, fg=INK),
        K.k_cta(["Nagrajcie", "jego historię"], 2.2, sub="Do 4 osób przy stole."),
    ], "Prezent, który nie trafi do szafy: rozmowa z dziadkiem nagrana w 4K 🎁\n\nZamiast skarpetek i kolejnego kubka usiądźcie razem w studiu. Jak poznał babcię? Jaka była jego pierwsza praca? Za kilka lat będziecie wracać do tego nagrania.\n\n2 godziny w Gadka studio to 300 zł brutto: 2 kamery 4K, mikrofony Shure SM7B i ciche światło. Przy stole zmieści się do 4 osób.\n\nWyślij to rodzeństwu 👇\n\n" + CTA_TXT + "\n\n" + HASH + " #prezentnaswieta #historiarodzinna"),
    "2026-12-15": ("pliki-od-reki", lambda: [
        K.k_words(["NAGRYWASZ", "RANO.", ("MONTUJESZ", ORANGE), ("WIECZOREM.", ORANGE)], 1.6),
        K.k_photo("106", 0.8, ["Nagranie"]),
        K.k_photo("050", 0.8, ["Zgranie"]),
        K.k_words(["PENDRIVE?", ("NIE.", CREAM), "DYSK SSD."], 1.3, bg=ORANGE, fg=BLACK),
        K.k_receipt(["Ile czekasz", "na pliki?"], [("Z dyskiem SSD", "od ręki"), ("Bez dysku", "1 dzień rob."), ("Dopłata", "0 zł")], "0 min", 2.6, stamp="OD RĘKI"),
        K.k_photo("053", 1.0, ["Montaż", "jeszcze dziś"], emo="⚡"),
        K.k_cta(["Przynieś SSD", "i działaj"], 2.2, sub="Bez dysku wyślemy pliki w 1 dzień roboczy.", bg=BLACK),
    ], "Nagrywasz rano, montujesz wieczorem. Przed świętami liczy się każdy dzień ⚡\n\nPrzynieś swój dysk SSD, a pliki audio i wideo zgrasz od ręki, zaraz po nagraniu. Nie masz dysku? Wyślemy je w 1 dzień roboczy.\n\nPendrive? Lepiej nie. Materiał z 2 kamer 4K to sporo gigabajtów.\n\nMontaż robisz sam albo oddajesz swojemu montażyście, więc film czy odcinek może wyjść jeszcze przed świętami.\n\n" + CTA_TXT + "\n\n" + HASH + " #montazwideo #podcast"),
    "2026-12-22": ("zapas-na-styczen", lambda: [
        K.k_words(["POV:", "MASZ WOLNE", ("W GRUDNIU", ORANGE)], 1.5),
        K.k_words(["A W STYCZNIU", ("ZERO", "o", BLACK), "ODCINKÓW?"], 1.3, bg=ORANGE, fg=BLACK),
        K.k_photo("031", 0.7, ["Odcinek 1"]),
        K.k_photo("104", 0.7, ["Odcinek 2"]),
        K.k_photo("102", 0.7, ["Odcinek 3"]),
        K.k_counter(750, 1.7, top="6 godzin", label="3 odcinki zapasu", bg=CREAM, fg=INK),
        K.k_photo("037", 1.0, ["Styczeń", "ogarnięty"], emo="😎"),
        K.k_cta(["Nagraj zapas", "w grudniu"], 2.4, sub="Ceny brutto. Rezerwacja online."),
    ], "POV: masz wolne w grudniu, a w styczniu zero odcinków 😬\n\nNagraj zapas teraz. W 6 godzin spokojnie zmieścisz 3 odcinki, a między nimi przestawisz meble i zmienisz kolor lampy RGB, żeby każdy wyglądał inaczej.\n\n6 godzin w Gadka studio to 750 zł brutto. Pliki od ręki na Twój dysk SSD.\n\nOznacz współprowadzącego, który mówi, że „w styczniu się nagramy” 👇\n\n" + CTA_TXT + "\n\n" + HASH + " #nagrywaniepodcastu #contentplan"),
    "2026-12-29": ("postanowienie-2027", lambda: [
        K.k_words(["POSTANOWIENIA", ("2027", ORANGE)], 1.3),
        K.k_strike(["Lista:"], ["Siłownia", "Angielski", "Wstawać o 6"], ["Podcast"], 3.0),
        K.k_words(["TO JEDNO", ("DOWIEZIESZ.", "o", ORANGE)], 1.2),
        K.k_photo("028", 1.0, ["Do 4 osób"]),
        K.k_photo("034", 1.0, ["Sprzęt na miejscu"], stick="W CENIE"),
        K.k_counter(300, 1.6, top="Start od", label="za 2 godziny", bg=ORANGE, fg=BLACK),
        K.k_cta(["Pierwszy odcinek", "w styczniu"], 2.2, sub="Płacisz online: BLIK, karta, Apple Pay.", bg=BLACK),
    ], "Siłownia, angielski, wstawanie o 6… A może w 2027 postanowienie, które naprawdę dowieziesz? 🎙️\n\nPodcast nie wymaga kupowania sprzętu ani wygłuszania pokoju. W Gadka studio czekają 2 kamery 4K, 4 mikrofony Shure SM7B i mikser RØDECaster Pro, a przy stole zmieszczą się maksymalnie 4 osoby.\n\nStart od 300 zł brutto za 2 godziny. Pierwszy raz? Weź dłuższy pakiet, bo 10–15 minut wprowadzenia jest częścią wynajmu.\n\nOznacz osobę, z którą zaczynasz 👇\n\n" + CTA_TXT + "\n\n" + HASH + " #postanowienia2027 #nowypodcast"),
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
        json.dump(opisy, open(os.path.join(ROOT, "opisy_v3_2026_12.json"), "w"), ensure_ascii=False, indent=1)
