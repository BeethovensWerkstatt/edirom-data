# Skripte

Hilfsskripte zur Pflege der Edition. Sie werden **nicht** ins XAR gepackt –
`build.xml` übernimmt nur den Ordner `edition/`.

Voraussetzung: Python 3 (keine zusätzlichen Pakete).

## generate_concordance.py

Erzeugt die Taktnavigation (Konkordanzen) für ein Werk und schreibt sie in
`edition/edition.xml`. Bestehende Konkordanzen dieses Werks werden dabei
**ersetzt** – manuelle Änderungen daran gehen verloren.

### Aufruf für op. 120

Aus dem Wurzelverzeichnis des Repos:

```bash
python3 scripts/generate_concordance.py --work op120_work --dir op120 \
    --source "Ausgangsdokument=Ausgangsdokument.xml" \
    --source "Originalausgabe=Originalausgabe.xml" \
    --source "Zieldokument=Zieldokument.xml"
```

| Parameter   | Bedeutung |
|-------------|-----------|
| `--work`    | `xml:id` des `<work>` in `edition.xml` |
| `--dir`     | Unterordner des Werks in `edition/` |
| `--source`  | `Anzeigename=Dateiname`, einmal pro Quelle; für jede Quelle entsteht eine Konkordanz „Taktnavigation nach: Anzeigename“ |
| `--dry-run` | Ergebnis nur ausgeben, `edition.xml` nicht ändern |

Danach das XAR neu bauen (`ant edition`) und installieren.

### Wie Takte verbunden werden

Takte verschiedener Quellen gehören zusammen, wenn sie im **gleichnamigen Satz**
(`mdiv/@label`) dasselbe **Takt-Label** (`measure/@label`, ersatzweise `@n`) haben.
Die Satznamen müssen also in allen Quellen identisch geschrieben sein
(z. B. `Var21`, nicht einmal `Var21` und einmal `Var 21`).

- `@label` ist die angezeigte Taktzahl, `@n` zählt die `measure`-Elemente.
  Ein Auftakt mit demselben Label wie der Folgetakt landet in derselben Verbindung.
- Label `x` (z. B. gestrichene Takte) wird ausgelassen.
- Kommagetrennte Labels (`12,13`) verbinden einen Takt mit beiden Taktzahlen.
- Volten werden über ihre Labels unterschieden (`32a`, `32b`).

Am Ende meldet das Skript, wie viele Takt-Labels einer Quelle gegenüber den
anderen fehlen. Das sind meist echte Fassungsunterschiede, können aber auch
Erfassungsfehler sein (falscher Satzname, Tippfehler im Label).

Quellen, die nicht nach Sätzen gegliedert sind (z. B. das Revisionsdokument
von op. 120 mit Monita als `mdiv`), lassen sich so nicht verbinden und
werden nicht als `--source` angegeben.

### Neues Werk

1. Werk- und Quelldateien in `edition/<werk>/` ablegen.
2. In `edition.xml` ein `<work>` mit Navigator anlegen und darin ein leeres
   `<concordances/>` vorsehen.
3. Skript mit den Quellen des Werks aufrufen.

### Format

Die Namen stehen sowohl in Attributen (`@name`, `@label`, für ältere
Edirom-Versionen) als auch in `<names><name xml:lang="de">` (wird von
Edirom Online ab 1.x gelesen – ohne diese Elemente bleibt der
Concordance Navigator leer).
