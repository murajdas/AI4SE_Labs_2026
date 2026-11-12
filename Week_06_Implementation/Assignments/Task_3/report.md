# Report k úlohe 3

## Rozhodnutia pri návrhu

Embedding chunku vzniká zo štandardnej knižnice Pythonu, bez sťahovania
modelu, a pri každom spustení dá rovnaký výsledok. Skript
[`embedding_repository.py`](./embedding_repository.py) používa **hashovaný
TF-IDF** s **hashing trickom**:

1. **Tokenizácia identifikátorov.** Identifikátor sa rozdelí na slová
   (`BulkDiscountPricing` → `bulk`, `discount`, `pricing`; `add_item` → `add`,
   `item`) a ponechá sa aj celý identifikátor. Bez toho by dotaz "bulk
   discount pricing" nenašiel chunk s triedou `BulkDiscountPricing`.
2. **Čo sa embeduje:** cesta k súboru + zoznam symbolov + kód chunku. Cesta a
   symboly (napr. `orders.py`, `Order.add_item`) nesú význam, ktorý v samotnom
   kóde často chýba.
3. **Váženie TF-IDF.** Časté tokeny (`self`, `def`, `return`) majú nízku
   váhu, zriedkavé a výstižné vysokú. IDF sa počíta z chunkov a ukladá sa do
   úložiska, takže dotaz sa embedduje rovnako ako chunky.
4. **Hashing trick** (SHA-256): každý token sa priradí do jedného z **512
   rozmerov** a podľa hashu dostane znamienko, takže netreba ukladať slovník
   indexov. Vektor sa normalizuje na jednotkovú dĺžku, takže cosine
   similarity je obyčajný skalárny súčin.

Počet rozmerov som vybral podľa kolízií. Na 12 ručne zvolených dotazoch (v
top 5 má byť očakávaný chunk) som porovnal:

| Verzia | Zásahy v top 5 | MRR |
| --- | --- | --- |
| pôvodný hashing trick (256, bez IDF, len kód) | 4/12 | 0,23 |
| nová (256 rozmerov) | 8/12 | 0,52 |
| nová (**512 rozmerov**) | 9/12 | 0,71 |
| nová (1024 rozmerov) | 11/12 | 0,74 |
| nová (512), len kód bez cesty a symbolov | 9/12 | 0,63 |

Zvolil som 512 (zadanie hovorí o "niekoľkých stovkách čísel"); 1024 dáva
mierne lepšie výsledky, ale dvojnásobnú veľkosť úložiska. Posledný riadok
podporuje rozhodnutie embedovať aj cestu a symboly. Test je malý, takže ide
o orientačné porovnanie, nie o presné meranie.

## Ukladanie a vyhľadávanie

Úložisko [`embeddings.json`](./embeddings.json) obsahuje metódu, počet
rozmerov, tabuľku IDF a zoznam dvojíc `chunk`–`embedding` (211 dvojíc, ~1,7
MB). Chunk je uložený spolu s vektorom, takže výsledok vyhľadávania
obsahuje rovno cestu, rozsah riadkov a kód.

Vyhľadávanie vytvorí embedding dotazu rovnakou funkciou a vypočíta
podobnosť so všetkými vektormi (lineárne prehľadávanie). Pri 211 chunkoch je
to zlomok sekundy, takže ani vektorová databáza, ani aproximatívny index sa
nevyplatia. Pri desaťtisícoch chunkov by to už stálo za zváženie. Úložisko
netreba pri každom dotaze stavať odznova:

```text
python embedding_repository.py ..\Task_2\chunks.json embeddings.json
python embedding_repository.py ..\Task_2\chunks.json embeddings.json --search-only --query "order state transition"
```

Príklad: dotaz "order state transition" vráti ako 2. výsledok
`orders.py:14-40` (`OrderStateMachine`), pôvodná verzia vrátila na 1. mieste
nesúvisiaci `OrderBuilder.__len__`.

## Obmedzenia

- Embedding je lexikálny: nerozumie synonymám ani zmyslu vety. Dotaz "how is
  the total price of an order calculated" nájde `Order` len vďaka slovám
  "order" a "price", a nie preto, že by rozumel "total".
- Testy často predbehnú zdrojový kód, lebo v nich sa názvy opakujú viac
  (napr. pri "inventory stock" sú prvé `test_inventory.py`). RAG agent by mal
  pri riešení úloh vedieť s tým pracovať.
- Hashing trick spôsobuje kolízie rôznych tokenov v tom istom rozmere; menej
  rozmerov znamená viac kolízií (pozri tabuľku).
- Dotaz sa embedduje len z tokenov, ktoré sú v IDF tabuľke; úplne neznáme
  slová sa ignorujú.
