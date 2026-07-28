# ats-feed-adapters

Erkennt, welches Bewerbermanagementsystem hinter einer Karriereseite steckt, und
liest dessen öffentlichen Stellen-Feed in ein einheitliches Format.

## Warum

Wer Stellenanzeigen programmatisch sammeln will, landet schnell bei den
ATS-Systemen: Die meisten Firmen hängen ihre Karriereseite an eines davon, und
fast alle bieten einen öffentlichen Feed an. Nur sieht jeder anders aus — XML
hier, JSON dort, unterschiedliche Feldnamen, unterschiedliche Datumsformate,
HTML mitten in den Beschreibungstexten.

Diese Bibliothek kapselt genau diesen Teil.

## Erkennung

`detect_company(url)` lädt die Seite und prüft HTML und finale URL gegen bekannte
Signatur-Domains. Findet sich nichts, folgt sie den Karriere-Links der Seite
(`karriere`, `jobs`, `career`, `stellen`) und sucht dort erneut — viele Firmen
verlinken das ATS erst eine Ebene tiefer.

Acht Systeme werden erkannt: **Personio, Greenhouse, Lever, Ashby, Recruitee,
SmartRecruiters, Workday und Teamtailor.** Für sieben davon baut `feed_url_for`
eine Feed-URL; Teamtailor wird erkannt, hat aber keinen offenen Feed. Der Aufruf
gibt in dem Fall einen leeren String zurück statt eine Ausnahme zu werfen — die
aufrufende Schleife soll bei einer Firma ohne Feed weiterlaufen, nicht abbrechen.

```python
from ats_adapters import detect_company, feed_url_for

found = detect_company("https://beispielfirma.de/karriere")
if found:
    ats_type, slug = found
    url = feed_url_for(ats_type, slug)
```

`detect_company` gibt `None` zurück, wenn nichts gefunden wurde oder die Seite
nicht erreichbar war — der Rückgabewert muss geprüft werden, bevor er entpackt wird.

Von der Kommandozeile:

```bash
python -m ats_adapters https://beispielfirma.de/karriere
```

Eine JSON-Zeile pro URL auf stdout.

## Zwei Dinge, die nicht offensichtlich sind

**Personio liefert XML, und fremdes XML wird nicht mit der Standardbibliothek
geparst.** `ats_personio.py` benutzt `defusedxml` — Pythons eingebauter Parser
ist offen für XXE und Entity-Bomben, und ein Feed ist per Definition fremde
Eingabe.

**Dieselbe Stelle taucht mehrfach auf**, in unterschiedlicher Schreibweise und
mit Tracking-Parametern in der URL. `dedup.py` kanonisiert die URL, bildet einen
Fingerabdruck aus Firma, Titel und Ort und vergleicht den Rest unscharf über
`rapidfuzz` — „Werkstudent*in Softwareentwicklung" bei der „Acme Solutions GmbH"
und „Werkstudent Softwareentwicklung" bei „Acme Solutions" sind dieselbe Stelle.

## Tests

```bash
python -m pytest
```

29 Tests: 10 für die Erkennung, 7 für die JSON-Adapter, 4 für Personio, 8 für die
Deduplizierung. Keine Netzwerkaufrufe — alle Feeds liegen als Fixtures bei.

## Installation

```bash
pip install -r requirements.txt   # httpx, defusedxml, rapidfuzz, pytest
```

## Herkunft

Herausgelöst aus einem größeren, privaten Werkzeug, das ich für meine eigene
Stellensuche gebaut habe. Dieser Teil ist allgemein nützlich, deshalb liegt er
hier einzeln — ohne meine Suchkriterien, ohne meine Firmenliste, ohne meine
Ergebnisse.

## Lizenz

MIT
