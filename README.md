# KinoGenius

# Sadržaj
* [Opis](opis)
* [Ovisnosti](#ovisnosti)
* [Korisničke upute](#korisni%C4%8Dke-upute)
* [Instalacija](#instalacija)
* [Kod je otvorenog izvora](#kod-je-otvorenog-izvora)
* [Budući planovi](#budu%C4%87i-planovi)

# Opis
KinoGenius je sveobuhvatna filmska baza podataka koja obuhvaća razdoblje od 2000. do 2023. godine, no njegova ključna snaga leži u kompleksnim algoritmima za predlaganje filmova. Nakon što se korisnici prijave, mogu odabrati filmove koji ih posebno zanimaju, a naš napredni algoritam prilagođava personalizirane preporuke prema njihovim preferencijama. Umjesto klasičnog pregledavanja nepreglednih popisa, KinoGenius vam pruža jedinstveno iskustvo stvaranja personalizirane filmske liste, temeljene na preporukama koje će zadovoljiti vaš ukus. Uživajte u optimalnom filmskom iskustvu prilagođenom samo vama, uz pomoć KinoGenius umjetne inteligencije.

![vintage-cinema-black-png-reel-5693185](https://github.com/S1lentAFK/KinoGenius/assets/86916610/59ddb554-c7ed-4df4-bca2-0a193d627e59)


# Ovisnosti
* customtkinter: Prilagođena biblioteka temeljena na Tkinteru, koristi se za izradu grafičkih korisničkih sučelja (GUI).
* requests: Biblioteka za izvršavanje HTTP zahtjeva prema određenim URL-ovima, npr. za prijavu, registraciju i preporuke filmova.
* json: Ugrađena Python biblioteka za rad s JSON podacima - čitanje i pisanje JSON datoteka te pretvaranje Python objekata u JSON format.
* PIL (Python Imaging Library): Koristi se za obradu slika, uključujući dohvaćanje slika sa URL-ova, promjenu veličine i prikazivanje slika.
* threading: Biblioteka za izvršavanje više niti kako bi se poboljšala paralelnost u određenim zadacima.
* fuzzywuzzy: Biblioteka za fuzzy usporedbu nizova, koristi se prilikom pretrage filmova.
* filedialog: Modul iz Tkinter biblioteke koji se koristi za otvaranje dijaloga za odabir datoteka, primjerice prilikom odabira JSON datoteka.
* io: Modul za rad s "in-memory" podacima, posebno koristan za čitanje slika iz bajtova.
* ImageSequence: Dio PIL-a koji omogućuje rad s sekvencama slika, koristan za animirane GIF slike.
* time: Modul koji omogućuje rad s vremenom u Pythonu, uključujući mjerenje vremena i upravljanje vremenskim odgodama.
* datetime: Modul za rad s datumima i vremenima u Pythonu. Omogućuje stvaranje, manipulaciju i formatiranje datuma i vremena.
* googletrans: Ovaj modul pruža Python sučelje za Google Translator API, što omogućuje prevođenje teksta između različitih jezika.
* ImageDraw: Dio PIL-a koji omogućuje crtanje na slikama, što je korisno za dodavanje oznaka, okvira i drugih grafičkih elemenata.
* openai: Modul koji omogućuje integraciju s OpenAI platformom za umjetnu inteligenciju i obradu prirodnog jezika.
* pymongo: Biblioteka za rad s MongoDB bazama podataka iz Pythona. Omogućuje izvršavanje upita, unos i izmjenu podataka.


# Korisničke upute

## Biranje profila

Nakon pokretanja KinoGenius-a potrebno je odabrati profil ili dodati novi, bilo to prijavom već postojećeg profila ili registracijom novog profila.

https://github.com/S1lentAFK/KinoGenius/assets/86916610/be5f95fa-61b2-485f-896c-85b2d5fbfcf1

### Registracija/prijava

https://github.com/S1lentAFK/KinoGenius/assets/86916610/db1e4065-6f8f-4c33-89db-586d17b8fa8c

#### Postavljanje profila | u slučaju registracije

Ukoliko korisnik registrira novi račun, od njega se zahtjeva postavljanje žanrova koje voli.

https://github.com/S1lentAFK/KinoGenius/assets/86916610/746ee0b0-3676-49df-9ee3-16a341030729

## Prijedlozi filmova

Nakon što se korisnik prijavi, registrira ili odabere račun, dobiti će svoje prijedloge za filmove.
Prijedlozi filmova su bazirani na:
* Žanrovima
* Redateljima
* Kreatorima
* Glumcima

![Prijedolzi](https://github.com/S1lentAFK/KinoGenius/assets/86916610/eee81956-823a-4629-af00-f435e6d1e549)

Prijedlozi su prikazani u ovom formatu:
* Poster filma
* Redatelj/Redatelji
* Žanrovi
* Ocjena / 100%
* Pogledaj više

https://github.com/S1lentAFK/KinoGenius/assets/86916610/c7b8e969-57e8-49a5-a022-ba99ea2fd226

### Detaljan pregled filmskog prijedloška

Klikom na tipku "Pogledaj više" za svaki filmski prijedložak, daje sve važne detalje. Detalji su:
* Naslov filma
* Poster filma
* Redatelji
* Kreatori
* Glumci
* Ocjena / 100%
* Trajanje filma
* Datum izdanja filma
* Ocjena za primjerenu dob
* Još 5 novih prijedloga

https://github.com/S1lentAFK/KinoGenius/assets/86916610/f8fee058-f8a0-498f-8c32-acb4300f860c

## Pretraživanje baze podataka filmova

Sveukupnu bazu podataka filmova moguće je pretražiti u drugom tab-u tkz. "Pretraživanje". Pretraživanjem filma moguće je naći, rezlutate poredane od najbolje ocjenjenog do najgore ocjenjenog i također je rečeno koji su redatelji u pitanju. Klikom na svaki rezultat se prikazuje isti prozor kao i za klik na "Pogledaj više" za svaki prijedlog filma.

https://github.com/S1lentAFK/KinoGenius/assets/86916610/f3f71fbe-1152-4b5f-87d5-fe2b02ee402b

## Treći tab | "Popularni žanrovi"

U ovom tab-u, se nalaze neke popularne franšize:
* SCI-FI
  * Marvel (MCU)
  * Star Wars
* Akcija
  * The Fast and The Furious
  * James Bond
  * Mission: Impossible
* Drama
  * Lord of the Rings
  * Harry Potter
* Romance
  * Fifty shades
* Horror
  * The Conjuring

https://github.com/S1lentAFK/KinoGenius/assets/86916610/dc86511c-535e-4b73-8cb1-329fcdf1b210

## Postavke i profil

Na ovaj naćim je moguće urediti i prilagoditi korisniku izgled KinoGenius-a. Moguće je promjeniti izgled boja i temu.\
Opcije za temu:
* Tamna
* Svijetla
* Tema sistema
Opicje za prikaz boje:
* Tamno plava
* Plava
* Zelena

https://github.com/S1lentAFK/KinoGenius/assets/86916610/cce978de-12db-4aae-8fb7-804c4f98c6eb

Nakon ponovnog pokretanja:

https://github.com/S1lentAFK/KinoGenius/assets/86916610/518dd028-bb68-4079-a7a4-e1c259c4013e

# Instalacija

Nakon preuzimanja ZIP datoteka sa GitHub-a, potrebno ju je otvoriti u IDE-u vašega izbora.\
I učitni sljedeće:
```
$ pip install -r requirements.txt
$ python KinoGenius.py
```

# Kod je otvorenog izvora

Slobodno doprinesite ovom projektu otvaranjem novih problema (issues) ili slanjem zahtjeva za povlačenje (pull requests). Za OpenAI api key se javite S1lentAFK-u.

# Budući planovi

Budući planovi za KinoGenius:
* Proširenje baze podataka sve do 1970-ih godina.
* Poboljšanje AI modela za program. Program se trenutno koristi "Machine  learning-om" za davanje prijedloga filmova
* Poboljšati personalizaciju KinoGenius-a. Omogućiti lakši pristup korisnicima svih godišta i nacionalsnoti.
* Izrađivanje Web aplikacije KinoGenius-a
* Izrađivanje Mobilne aplikacije KinoGenius-a
