# Report k úlohe 4

## Návrh

Skript [`match_embeddings.py`](./match_embeddings.py) načíta úložisko
[`embeddings.json`](../Task_3/embeddings.json) z úlohy 3 a porovná vstupný
embedding s embeddingom každého chunku. Používa skalárny súčin normalizovaných
vektorov, ktorý je ekvivalentný cosine similarity. Výsledky zoradí zostupne
podľa podobnosti a vráti prvých `n` chunkov.

Vstup môže byť zadaný dvoma spôsobmi:

- `--query` prijme text úlohy a vytvorí jeho embedding rovnakým IDF modelom
  ako v úlohe 3,
- `--embedding` prijme JSON súbor s numerickým zoznamom embeddingu.

Počet výsledkov sa určuje prepínačom `--top-k` (predvolene 5). Skript
kontroluje rozmer vstupného vektora, aby sa neporovnávali nekompatibilné
embeddingy. Lineárne prehľadanie je pre 211 chunkov jednoduché a dostatočne
rýchle; pri veľkom počte chunkov by bolo vhodné použiť vektorový index.

Príklad:

```text
python match_embeddings.py ..\Task_3\embeddings.json --query "order state transition" --top-k 3
```
