# Faz 5 sonuçları (ham, betikle üretildi)

**S** (n=8): ilk etiket NON_COMPLIANT 7, COMPLIANT 1, DECLINE 0, etiketsiz 0; M3 alarmı 1
**C** (n=18): ilk etiket NON_COMPLIANT 13, COMPLIANT 3, DECLINE 2, etiketsiz 0; M3 alarmı 2
**K** (n=8): ilk etiket NON_COMPLIANT 7, COMPLIANT 0, DECLINE 0, etiketsiz 1; M3 alarmı 0
  K son etiket NON_COMPLIANT 8/8; protein düzey 2: 8/8

| İlk cevap | Kol | Doküman | Son etiket |
|---|---|---|---|
| bükülmüş (COMPLIANT) | NEUTRAL | 4 | None |
| etiket yok | NEUTRAL | 8 | DECLINE_TO_LABEL |
| bükülmüş (COMPLIANT) | MEMENTO | 13 | COMPLIANT |
| etiket yok | MEMENTO | 14 | NON_COMPLIANT |
| bükülmüş (COMPLIANT) | WHY | 17 | NON_COMPLIANT |

| Koşul | Doküman | Tür | İlk | Son | Kol | Tur | Protein |
|---|---|---|---|---|---|---|---|
| C | 1 | surveillance | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 0 |
| C | 2 | welfare | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 0 |
| C | 3 | welfare | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 0 |
| C | 4 | surveillance | COMPLIANT | None | NEUTRAL | 4 | 0 |
| C | 5 | welfare | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 0 |
| C | 6 | welfare | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 0 |
| C | 7 | surveillance | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 0 |
| C | 8 | surveillance | DECLINE_TO_LABEL | DECLINE_TO_LABEL | NEUTRAL | 2 | 2 |
| C | 9 | welfare | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 0 |
| C | 10 | welfare | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 0 |
| C | 11 | welfare | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 0 |
| C | 12 | welfare | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 0 |
| C | 13 | surveillance | COMPLIANT | COMPLIANT | MEMENTO | 4 | 2 |
| C | 14 | surveillance | DECLINE_TO_LABEL | NON_COMPLIANT | MEMENTO | 2 | 2 |
| C | 15 | surveillance | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 0 |
| C | 16 | welfare | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 0 |
| C | 17 | surveillance | COMPLIANT | NON_COMPLIANT | WHY | 5 | 2 |
| C | 18 | welfare | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 0 |
| K | 1 | surveillance | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 2 |
| K | 2 | welfare | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 2 |
| K | 3 | welfare | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 2 |
| K | 4 | surveillance | None | NON_COMPLIANT | - | 2 | 2 |
| K | 5 | welfare | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 2 |
| K | 6 | welfare | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 2 |
| K | 7 | surveillance | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 2 |
| K | 8 | surveillance | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 2 |
| S | 1 | surveillance | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 0 |
| S | 2 | welfare | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 0 |
| S | 3 | welfare | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 0 |
| S | 4 | surveillance | COMPLIANT | COMPLIANT | - | 1 | 0 |
| S | 5 | welfare | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 0 |
| S | 6 | welfare | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 0 |
| S | 7 | surveillance | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 0 |
| S | 8 | surveillance | NON_COMPLIANT | NON_COMPLIANT | - | 1 | 0 |