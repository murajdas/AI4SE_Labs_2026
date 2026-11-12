# Report k úlohe 1

Repozitár bol naklonovaný do priečinka `Task_1/AI4SE_Playground` pomocou
kódovacieho asistenta, ktorý má k dispozícii nástroj na vykonávanie
príkazov v termináli (tool use).

## Mechanizmus

Jazykový model vykonal klonovanie prostredníctvom terminálového nástroja,
ktorý mu poskytol prístup k lokálnemu shellu a Git klientovi. Na základe
zadania vygeneroval volanie nástroja s príkazom:

```
git clone https://github.com/Neltharion59/AI4SE_Playground.git Task_1/AI4SE_Playground
```

Tento príkaz následne vykonal lokálny Git klient na mojom počítači (cez
shell, ku ktorému má agent prístup) a výstup príkazu sa vrátil agentovi ako
výsledok nástroja. Git stiahol objekty repozitára a spravil checkout
sledovaných súborov do cieľového priečinka.

## Čistenie

Agent následne odstránil adresár `.git`, aby sa obsah repozitára dal čisto
zahrnúť do tohto odovzdávaného repozitára. Súbory pracovného stromu sa tým
nezmenili.