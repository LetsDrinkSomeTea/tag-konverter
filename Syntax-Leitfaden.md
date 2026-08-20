# Tag-Syntax für Control-Mapping

## Ziel

Jede relevante Textstelle in unseren Beratungsdokumenten wird mit einer
Word-Textmarke markiert, die eindeutig auf ein Control im zentralen Register
verweist. Damit wissen wir jederzeit, welches Control wo im Dokument steht und
aus welcher Norm es stammt.

## Vorgehen

1. Textstelle markieren (Wort, Halbsatz, Satz, Bullet-Point)
2. Einfügen → Textmarke
3. Namen nach untenstehender Syntax eintragen → Hinzufügen
4. Erfüllt derselbe Text mehrere Controls: Auswahl beibehalten, Schritt 2–3 mit
   weiterem Namen wiederholen

Word-Textmarken-Namen dürfen nur Buchstaben, Ziffern und Unterstriche enthalten
und müssen mit einem Buchstaben beginnen.

## Syntax

```
<Normkürzel>_<Normstelle>[__<Locator>][_N<n>]
```

| Baustein                    | Pflicht | Bedeutung                                                                                                         |
| --------------------------- | ------- | ----------------------------------------------------------------------------------------------------------------- |
| `<Normkürzel>_<Normstelle>` | ✅      | Welches Control aus dem Register                                                                                  |
| `__<Locator>`               | –       | Welcher Teil des Controls genau (Kapitel/Absatz/Satz/Buchstabe/Nummer)                                            |
| `_N<n>`                     | –       | Nur bei Namenskollision: wird derselbe Name ein zweites Mal vergeben, `_N2` anhängen, beim dritten Mal `_N3` usw. |

## Normkürzel

| Kürzel                                  | Norm                 |
| --------------------------------------- | -------------------- |
| `IEC62443_2_1`                          | IEC 62443-2-1        |
| `IEC62443_3_3`                          | IEC 62443-3-3        |
| `IEC62443_4_1`                          | IEC 62443-4-1        |
| `IEC62443_4_2`                          | IEC 62443-4-2        |
| `EN40000_1` / `EN40000_2` / `EN40000_3` | EN 40000-1/-2/-3     |
| `CRA`                                   | Cyber Resilience Act |
| `EN50742`                               | EN 50742             |

Normstelle danach so nah wie möglich am Normtext, Punkte/Bindestriche werden zu
`_`: `SR3.3` → `SR3_3`, `PR-1` → `PR_1`, `Art. 11.1` → `Art_11_1`.

## Kapitel statt Control

Gibt es für eine Stelle kein formales Control, steht anstelle des
Control-Kürzels einfach eine Kapitel-Angabe: `K<n>[_<n>...]`, z. B. `K5_3` für
Kapitel 5.3. Locator funktioniert danach genauso weiter.

## Anhang statt Control

Verweist die Stelle auf einen Anhang, steht `Annex_<Buchstabe>` an Stelle des
Control-Kürzels. Abschnitte im Anhang hängen als Ziffern an, so tief wie der
Anhang gegliedert ist: `Annex_D_2_1` für D.2.1. Locator funktioniert danach
genauso weiter.

| Textmarken-Name            | Bedeutung                        |
| -------------------------- | -------------------------------- |
| `IEC62443_4_1_Annex_D`     | IEC 62443-4-1, Anhang D komplett |
| `IEC62443_4_1_Annex_D_2_1` | Anhang D, Abschnitt D.2.1        |
| `CRA_Annex_I__Lita`        | CRA Anhang I, Buchstabe a        |

Mehrbuchstabige Anhänge (`Annex_ZA`, `Annex_ZZ`) und römische Nummerierungen
wie beim CRA (`Annex_VIII`) werden genauso geschrieben.

## Locator

Ebenen mit `_` verketten, Reihenfolge Absatz → Satz → Buchstabe → Nummer:

| Code     | Bedeutung   | Beispiel |
| -------- | ----------- | -------- |
| `P<n>`   | Absatz n    | `P2`     |
| `S<n>`   | Satz n      | `S1`     |
| `Lit<x>` | Buchstabe x | `Litb`   |
| `Nr<n>`  | Nummer n    | `Nr3`    |

Nur so tief referenzieren, wie nötig. Kein Locator = das ganze Control gemeint.

## Beispiele

| Textmarken-Name                | Bedeutung                                          |
| ------------------------------ | -------------------------------------------------- |
| `IEC62443_3_3_SR3_3`           | Ganzes Control SR3.3                               |
| `IEC62443_3_3_SR3_3__P2_S1`    | Nur Absatz 2, Satz 1                               |
| `IEC62443_3_3_SR3_3__P2_S1_N2` | Gleicher Teil, zweites Vorkommen (Namenskollision) |
| `CRA_Art_11_1__Litb`            | Nur Buchstabe b des CRA-Artikels                   |
| `IEC62443_4_1_Annex_D_2_1`     | IEC 62443-4-1, Anhang D, Abschnitt D.2.1           |
| `EN40000_1_K5_3`               | EN 40000-1, Kapitel 5.3, kein Control              |
| `EN40000_1_K5_3__S2`           | Dieselbe Stelle, nur Satz 2                        |

Ein Satz, der zwei Controls gleichzeitig erfüllt: zwei Textmarken auf derselben
Auswahl, z. B. `IEC62443_4_1_PR_1` **und** `CRA_Art_11_1__Litb`.

## Sonderfälle

- **Kein passendes Control vorhanden:** Textmarke `TODO_NEU` setzen, keine ID
  erfinden.
- **Unsicher, welches Control passt:** trotzdem taggen, Klärung erfolgt im
  Register.
- **Kein Control passt:** Textmarke `INTERNES_WISSEN` (ebenfalls mit \_N2, ...).
