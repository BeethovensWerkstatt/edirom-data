# Edirom-Daten von Beethovens Werkstatt

Daten für [Edirom Online](https://github.com/Edirom/Edirom-Online) aus dem
Projekt [Beethovens Werkstatt](https://beethovens-werkstatt.de/). Die Edition
dient der internen Arbeit an den Quellen und enthält:

- **op. 120, Diabelli-Variationen (Modul 5)**
- **op. 73, 5. Klavierkonzert** (Modul 3)
- **op. 120, Diabelli-Variationen (Modul 3)**

## Aufbau

| Ordner / Datei | Inhalt |
|---|---|
| `edition/` | Daten der Edition, wird ins XAR gepackt (`edition.xml`, `prefs.xml`, je Werk ein Unterordner mit MEI-Dateien) |
| `datenvorlagen/` | Ausgangsmaterial (Vertaktungen, Exporte), nicht Teil der Edition |
| `existPackaging/` | Paketbeschreibung für eXist-db |
| `scripts/` | Hilfsskripte, z. B. zum Erzeugen der Taktnavigation, siehe [scripts/README.md](scripts/README.md) |
| `build.xml` | baut das XAR (`ant edition`) |
| `Dockerfile` | baut ein Image mit eXist-db, Edirom Online und den Daten |

## Lokal starten

Voraussetzung: [Docker Desktop](https://www.docker.com/products/docker-desktop/).

Fertiges Image aus der GitHub Container Registry starten:

```bash
docker run --rm -p 8080:8080 ghcr.io/beethovenswerkstatt/edirom-data:latest
```

Oder das Image aus diesem Repository selbst bauen und starten:

```bash
docker build -t edirom-data .
docker run --rm -p 8080:8080 edirom-data
```

Nach etwa einer Minute ist die Edition unter <http://localhost:8080/>
erreichbar. Ist Port 8080 belegt, z. B. durch eine andere eXist-db, einfach
einen anderen Port wählen: `-p 8090:8080` und dann <http://localhost:8090/>.

Nur das XAR bauen, etwa um es in eine bestehende eXist-db zu laden:

```bash
ant edition
```

Das XAR liegt danach in `dist/`.

## Image und Versionen

Das Image wird von GitHub Actions gebaut
([.github/workflows/docker.yml](.github/workflows/docker.yml)) und unter
`ghcr.io/beethovenswerkstatt/edirom-data` abgelegt:

| Anlass | Image-Tags | Version des Daten-XAR |
|---|---|---|
| Pull Request auf `main` | wird nur gebaut und getestet | – |
| Merge auf `main` | `main` | `0.1-<Datum><Uhrzeit>` |
| Versions-Tag, z. B. `v0.3.0` | `0.3.0`, `0.3`, `latest` | `0.3.0-<Datum>` |

Enthalten sind eXist-db 6, Edirom Online Backend und Frontend (Version im
`Dockerfile`, derzeit 1.5.0) und das Daten-XAR.

### Ein Release erstellen

1. Änderungen per Pull Request nach `main` bringen.
2. Versions-Tag setzen und hochladen:
   ```bash
   git switch main && git pull
   git tag -a v0.3.0 -m "Kurze Beschreibung"
   git push origin v0.3.0
   ```
3. GitHub baut das Image mit den Tags `0.3.0`, `0.3` und `latest`.
4. Auf GitHub unter *Releases* ein Release zum Tag anlegen.

## Betrieb auf dem Server

Das Image enthält alles, was für die Edition nötig ist, und braucht keine
dauerhafte Datenablage: Alle Inhalte kommen aus dem Image.

```bash
docker pull ghcr.io/beethovenswerkstatt/edirom-data:latest
docker run -d --name edirom-online --restart unless-stopped \
    -p 8080:8080 ghcr.io/beethovenswerkstatt/edirom-data:latest
```

Die Edirom ist im Container direkt unter `/` erreichbar. Ein Reverse Proxy
leitet die Domain (z. B. `edirom-online.beethovens-werkstatt.de`) auf
Port 8080 weiter. Frontend und Backend laufen im selben Container und sprechen
sich über relative Pfade an, deshalb ist keine Anpassung an die Domain nötig.

Update auf eine neue Version:

```bash
docker pull ghcr.io/beethovenswerkstatt/edirom-data:latest
docker rm -f edirom-online
docker run -d --name edirom-online --restart unless-stopped \
    -p 8080:8080 ghcr.io/beethovenswerkstatt/edirom-data:latest
```

Statt `latest` kann auch eine feste Version wie `0.3.0` verwendet werden.

## Lizenzen

Die Faksimiles von D1 (D-B, DMS 128757/5) stammen von der Staatsbibliothek zu
Berlin – Preußischer Kulturbesitz und stehen unter
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
