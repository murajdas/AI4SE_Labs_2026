# Bonus Task 1 – Ideálny pipeline

## Cieľ

Cieľom je vytvoriť repository-aware generovanie kódu, ktoré rozumie nielen
textovej podobnosti, ale aj štruktúre repozitára, závislostiam a existujúcim
testom.

## Navrhovaný pipeline

1. **Indexovanie repozitára:** načítať zdrojové súbory, AST, triedy, funkcie,
   importy, volania metód, dedičnosť a verejné API.
2. **Chunkovanie:** deliť Python podľa symbolov a udržiavať metadáta
   `file`, `class`, `function`, rozsah riadkov a závislosti. Veľké funkcie
   deliť s malým prekryvom; spolu s implementáciou ukladať aj súvisiaci
   docstring, signatúru a testy.
3. **Hybridné vyhľadávanie:** kombinovať lexikálne BM25 vyhľadávanie,
   embeddingovú podobnosť a filtráciu podľa symbolov alebo cesty. Výsledky
   následne zoradiť malým rerankerom.
4. **Dynamický kontext:** nevyberať vždy pevne päť chunkov. Vyberať chunky
   až do limitu kontextu podľa skóre a pridať susedné alebo závislé symboly,
   ak sú potrebné na pochopenie implementácie.
5. **Generovanie:** poslať LLM zadanie, relevantný kód, signatúru cieľovej
   metódy, podobné implementácie a príslušné testy. Model má vrátiť iba
   minimálnu zmenu.
6. **Validácia:** odpoveď overiť cez AST, zachovať dekorátory a signatúru,
   skontrolovať importy a zapísať zmenu až po úspešnej validácii.
7. **Iterácia podľa testov:** spustiť formatter, typovú kontrolu a dotknuté
   testy. Pri chybe poslať LLM presnú diagnostiku a obmedzený diff na jednu
   alebo niekoľko opravných iterácií.

## Je embedding matching najlepší?

Samotné embedding matching nie je ideálne. Zachytáva významovú podobnosť, ale
pri zdrojovom kóde môže prehliadnuť presné názvy symbolov, importy, typy alebo
kontrakt uložený v testoch. Lepšie je hybridné vyhľadávanie: BM25 nájde presné
identifikátory a cesty, embeddingy zachytia podobné formulácie a reranker
vyberie najvhodnejší kontext.

## Počet chunkov a chunkovanie

Pevný počet piatich chunkov je jednoduchý, ale nie vždy vhodný. Pri malej
úlohe môže stačiť jeden až tri chunky, pri úlohe meniacej viac vrstiev treba
pridať testy, volané metódy a dátové modely. Praktickejší je dynamický výber
podľa skóre, prahu relevancie a dostupného tokenového rozpočtu.

Chunkovanie podľa pevných riadkov by som nahradil AST chunkami na úrovni
tried a funkcií. Každý chunk by obsahoval symbol a jeho lokálny kontext;
samostatný graf závislostí by umožnil pridať definície volaných metód bez
načítania celého súboru. Testy by boli indexované ako samostatné chunky
prepojené s API, ktoré overujú.

## Záver

Ideálny systém by teda používal AST a graf závislostí na štruktúrované
chunkovanie, hybridný retriever s rerankingom na výber kontextu a iteratívnu
LLM slučku uzavretú syntaktickou kontrolou a testami. Embeddingy sú užitočná
časť pipeline, ale samy osebe nie sú najspoľahlivejším riešením pre
repository-aware generovanie.
