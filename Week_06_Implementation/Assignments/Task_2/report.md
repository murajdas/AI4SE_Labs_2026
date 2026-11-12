# Report k úlohe 2

## Rozhodnutia pri návrhu

Repozitár z úlohy 1 rozdeľuje skript
[`chunk_repository.py`](./chunk_repository.py) na bloky s dĺžkou najviac
**1 500 znakov** (~375 tokenov, približne 35–40 riadkov kódu). Typická metóda
v repozitári má 10–20 riadkov (300–800 znakov), takže sa vojde do jedného
bloku. Blok je zároveň dosť malý na to, aby sa týkal jednej témy a aby sa do
kontextu RAG agenta nedostávalo veľa nepodstatného kódu. Celý repozitár má
~160 KB (~40 000 tokenov), kým priemerný blok má 754,6 znakov (~190 tokenov),
takže päť vyhľadaných blokov je približne 2,5 % repozitára.

Python súbory sa delia podľa syntaktického stromu (`ast`), nie po pevnom počte
riadkov. Hranice blokov sú hranice tried, metód a funkcií, takže sa metóda
takmer nikdy nerozreže uprostred. Skúšal som aj čisto riadkové delenie (80
riadkov, prekryv 10): dalo 73 blokov s mediánom ~2 700 znakov, ktoré zvyčajne
obsahovali niekoľko nesúvisiacich metód a mohli rozdeliť funkciu na dve
polovice. Menšie bloky podľa tried a metód by mali byť pri vyhľadávaní
presnejšie.

Ďalšie pravidlá:

- **Spájanie malých častí:** importy, docstring, krátke metódy a konštanty sa
  spájajú, kým blok nemá aspoň **600 znakov** (a súčet nepresiahne 1 500),
  aby nevznikali bloky s jedným riadkom.
- **Veľké časti:** trieda, ktorá sa nezmestí, sa rozdelí na hlavičku a
  jednotlivé metódy. Funkcia dlhšia ako limit sa rozdelí po riadkoch s
  **prekryvom 3 riadkov**, aby sa nestratila súvislosť. V tomto repozitári sa
  to stalo len raz (`Simulation.step`, 2 časti).
- **Ostatné textové súbory** a súbory, ktoré sa nepodarí spracovať, sa delia po
  riadkoch s rovnakým limitom a prekryvom.
- **Vynechané:** binárne súbory, technické adresáre (`.git`, `__pycache__`,
  `.pytest_cache`) a `.gitignore` (šablóna, ktorá by len zašumila
  vyhľadávanie).

## Dátová štruktúra

Výsledok je uložený v [`chunks.json`](./chunks.json). Obsahuje nastavenia
delenia (`max_chars`, `min_chars`, `overlap`) a zoznam blokov. Každý blok má
cestu k pôvodnému súboru (`path`), číslo prvého a posledného riadku
(`start_line`, `end_line`), zoznam symbolov v bloku (`symbols`, napr.
`Order.add_item`) a samotný text (`content`).

## Výsledok a obmedzenia

- 26 neprázdnych súborov, **211 blokov**; prázdny `__init__.py` nevytvára
  chunk. Dĺžka: min 46, medián 719, priemer 754,6, max 1 467 znakov.
- Pri každom behu som overil, že každý neprázdny riadok každého súboru je v
  aspoň jednom bloku (0 nepokrytých riadkov).
- Obmedzenie: syntaktické delenie je len pre Python. Ostatné súbory sa delia po
  riadkoch, v tomto repozitári však žiadne iné (okrem `.gitignore`) nie sú. Po
  zmene repozitára treba skript spustiť znova.
