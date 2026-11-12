# Report k úlohe 5

## Pipeline

Skript [`solve_tasks.py`](./solve_tasks.py) načíta úlohy z `missing_code.json`
a pre každú z nich:

1. zloží textové zadanie (trieda, metóda, súbor a docstring),
2. vytvorí jeho embedding rovnakým IDF modelom ako v úlohe 3 a cez matcher z
   úlohy 4 vyberie **top 5** chunkov (`retrieve_chunks`),
3. pošle zadanie a vybrané chunky v prompte do LLM (`generate_code`),
4. overí odpoveď (syntax, názov metódy, trieda) a nahradí iba príslušnú metódu
   v cieľovom súbore (`solve_task`, `replace_method`).

Skript používa OpenAI-kompatibilný Chat Completions endpoint, model je
kontrolovaný voči zoznamu povolenému zadaním. Ak odpoveď modelu neprejde
kontrolou, súbor sa nezmení, úloha sa vypíše ako `FAILED` a skript pokračuje
ďalšou úlohou. Ak model vynechá dekorátor (napr. `@property`), zachová sa
pôvodný. Prepínač `--dry-run` vypíše nájdené chunky bez volania modelu.

Spustenie (model `gpt-5-mini`, API kľúč v `OPENAI_API_KEY`):

```text
python .\Task_5\solve_tasks.py .\missing_code.json .\Task_3\embeddings.json .\Task_1\AI4SE_Playground --model gpt-5-mini
```

Pipeline sa dokončila pre všetkých 10 úloh (10-krát `Updated`, žiadne
`FAILED`). Skript som spustil dvakrát za sebou, takže výsledok testov
nižšie patrí k poslednému behu.

## Testy

Pred doplnením kódu: **429 passed, 52 failed, 65 subtests passed**.

Po doplnení kódu cez pipeline (`python -m pytest -q`):

```text
14 failed, 467 passed, 1 warning, 65 subtests passed
```

Z pôvodných 52 zlyhaní pipeline opravila 38. Zostáva 14 zlyhaní v troch
metódach, ktoré LLM implementoval chybne:

| Metóda | Zlyhania | Príčina |
| --- | --- | --- |
| `BulkDiscountPricing.price` | 10 | používa neexistujúci atribút `self.base` (správne je `_base`), `AttributeError` |
| `Warehouse.stock_report` | 3 | `sorted(skus)` triedi objekty `Product`, nie SKU reťazce, `TypeError` |
| `InventoryLedger.__contains__` | 1 | po úplnom `commit` vráti `False` namiesto `True` |

Zvyšných 7 metód z `missing_code.json` prešlo všetkými testami. Zostávajúce
chyby ukazujú limit pipeline: model dostane len 5 chunkov, a ak v nich chýba
potrebný detail (napr. názov atribútu v konštruktore alebo kontrakt
`normalize_sku`), môže si ho domyslieť nesprávne.
