# Dinge einfach wiederfinden

## Das Problem

Bei unseren Beratungsdokumenten wissen wir aktuell nicht:
- **welche Controls in welchen Dokumenten stehen und wo** — wer sucht, blättert die Dokumente durch
- **aus welcher Norm ein Satz stammt** — Herkunft ist nicht nachvollziehbar
- **wie viel unserer Dokumente über das Minimum hinausgeht** — unsere Dokumente sind umfangreicher als die 62443, diese ist umfangreicher als das, was Kunden für den CRA tatsächlich brauchen

Und das Ganze wiederholt sich: Mit 4-2, 2-4 und 3-3 stehen bereits die nächsten Normrevisionen an. Ohne System durchsuchen wir dann wieder alle Dokumente von Hand — in zwei Monaten dasselbe Problem wie heute.

## Die Lösung

Jede relevante Textstelle bekommt eine **Word-Textmarke**, die eindeutig auf ein **Control in einem zentralen Register** verweist — z. B. `ISO62443_3_3_SR3_3__P2_S1` für Absatz 2, Satz 1 von SR 3.3. Damit ist für jede Stelle sofort klar: welches Control, aus welcher Norm, an welcher genauen Position.

Aus den Tags kann programmatisch eine Matrix erstellt werden, die die Dokumente den Controls zuweist.
Das Register wird zur Suchbasis: Statt 30 Dokumente zu durchsuchen, filtert man das Register nach Norm oder Control und sieht sofort alle betroffenen Stellen — auch bei der nächsten Normrevision.

## Das Tool

Damit niemand sich die Syntax merken muss, gibt es dafür ein eigenes Werkzeug:

- **Text → ID bauen:** Norm auswählen, Control aus durchsuchbarer Liste wählen (Klartext-Titel inklusive), optional Absatz/Satz/Buchstabe/Nummer angeben — fertig ist eine gültige Textmarke zum Kopieren.
- **ID → Text entschlüsseln:** Eine bestehende Textmarke eingeben, das Tool übersetzt sie zurück in Klartext — z. B. „IEC 62443-3-3, SR 3.3 – Security functionality verification, Absatz 2, Satz 1".
- Funktioniert auch für Fälle ohne formales Control (Kapitel-Referenz) oder ganz ohne Normbezug.

Das Register für IEC 62443-3-3, -4-1 und -4-2 ist bereits im Tool hinterlegt — Tippfehler bei Control-IDs sind damit praktisch ausgeschlossen.

## Nutzen

- Vollständigkeitsprüfung wird ein Filter statt eine Suche
- Kundenabgleich wird nachvollziehbar: welche Stelle deckt was ab
- Normrevisionen treffen uns nicht mehr unvorbereitet — betroffene Stellen sind sofort sichtbar
