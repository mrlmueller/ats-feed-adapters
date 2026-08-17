# ats-feed-adapters

Erkennt, welches Bewerbermanagementsystem hinter einer Karriereseite steckt,
liest dessen öffentlichen Stellen-Feed und liefert die Anzeigen als
einheitliche, deduplizierte Liste.

## Warum

Wer Stellenanzeigen programmatisch sammeln will, landet schnell bei den
ATS-Systemen: Die meisten Firmen hängen ihre Karriereseite an eines davon, und
fast alle bieten einen öffentlichen Feed an. Nur sieht jeder anders aus, XML
hier, JSON dort, unterschiedliche Feldnamen, unterschiedliche Datumsformate,
HTML mitten in den Beschreibungstexten. Diese Bibliothek kapselt genau diesen
Teil.

## Erkennung

`detect_company(url)` lädt die Seite und prüft HTML und finale URL gegen
bekannte Signatur-Domains. Findet sich nichts, folgt sie den Karriere-Links
der Seite (`karriere`, `jobs`, `career`, `stellen`) und sucht dort erneut,
denn viele Firmen verlinken das ATS erst eine Ebene tiefer.

Acht Systeme werden erkannt: **Personio, Greenhouse, Lever, Ashby, Recruitee,
SmartRecruiters, Workday und Teamtailor.** Für sieben davon baut
`feed_url_for` aus dem erkannten Typ und dem Slug (der Kennung der Firma beim
ATS, meist die Subdomain des Feeds) die Feed-URL. Teamtailor wird erkannt,
hat aber keinen offenen Feed. Der Aufruf gibt in dem Fall einen leeren String
zurück statt eine Ausnahme zu werfen, weil die aufrufende Schleife bei einer
Firma ohne Feed weiterlaufen soll, nicht abbrechen.

```python
from ats_adapters import detect_company, feed_url_for

found = detect_company("https://beispielfirma.de/karriere")
if found:
    ats_type, slug = found
    url = feed_url_for(ats_type, slug)
```

`detect_company` gibt `None` zurück, wenn nichts gefunden wurde oder die
Seite nicht erreichbar war. Der Rückgabewert muss geprüft werden, bevor er
entpackt wird.

## Vom Feed zur Stellenliste

Das Einlesen übernehmen die Adapter: `ats_cleanjson.fetch_company` für die
sechs JSON-Systeme, `ats_personio.fetch_company` für Personio-XML, jeweils
mit `fetch_many` für ganze Firmenlisten. Jede Stelle kommt als Dictionary mit
denselben Feldern zurück, egal aus welchem System sie stammt: `job_id`,
`title`, `location`, `url`, `posted_at` als ISO-Datum, `description` als
reiner Text ohne HTML, dazu `company` und die Quelle in `_source`. Ehrlich
zu den Grenzen: SmartRecruiters und Workday liefern im Feed keinen
Beschreibungstext, dort bleibt das Feld leer, und Workday nennt gar kein
Veröffentlichungsdatum.

```python
from ats_adapters.ats_cleanjson import fetch_company
from ats_adapters import dedup_all

jobs = fetch_company("greenhouse", "beispielfirma", "Beispielfirma GmbH")
jobs = dedup_all(jobs)
```

Ein Feed, der nicht erreichbar ist, ergibt eine leere Liste und eine Zeile
auf stderr, nicht einen Abbruch des ganzen Laufs.

Von der Kommandozeile, eine oder mehrere URLs, mit Pause zwischen den
Abfragen:

```bash
python -m ats_adapters https://beispielfirma.de/karriere
{"url": "https://beispielfirma.de/karriere", "ats_type": "personio", "ats_slug": "beispielfirma", "feed_url": "https://beispielfirma.jobs.personio.de/xml"}
```

## Vier Dinge, die nicht offensichtlich sind

**Personio liefert XML, und fremdes XML wird nicht mit der Standardbibliothek
geparst.** `ats_personio.py` benutzt `defusedxml`, denn Pythons eingebauter
Parser ist offen für XXE und Entity-Bomben, und ein Feed ist per Definition
fremde Eingabe. Antwortet der Feed mit einer 307-Umleitung, ist die Firma
auf personio.com migriert, und der Adapter meldet genau das, statt still zu
scheitern, damit der Eintrag neu geprüft werden kann.

**Workday ist der Sonderfall.** Der Slug ist dreiteilig aus Mandant,
Rechenzentrum und Site (`firma.wd5/karriereseite`), und der Feed will keinen
GET-Aufruf, sondern einen POST mit JSON-Körper samt Seitengröße. Wer das wie
bei den anderen sechs Systemen behandelt, bekommt keine einzige Stelle.

**Dieselbe Stelle taucht mehrfach auf**, in unterschiedlicher Schreibweise
und mit Tracking-Parametern in der URL. `dedup_all` entfernt zuerst die
Tracking-Parameter aus der URL und normalisiert dann kräftig, bevor
verglichen wird: Rechtsformen wie „GmbH & Co. KG" fliegen aus dem
Firmennamen, Gender-Schreibweisen wie „(m/w/d)" oder „*in" aus dem Titel,
Postleitzahlen aus dem Ort. Exakte Duplikate erwischt ein Fingerabdruck aus
den drei normalisierten Feldern, den Rest ein unscharfer Vergleich über
`rapidfuzz` (Titel ab 88, Firma ab 90 von 100 Punkten). So sind
„Werkstudent*in Softwareentwicklung" bei der „Acme Solutions GmbH" und
„Werkstudent Softwareentwicklung" bei „Acme Solutions" dieselbe Stelle.

**Die Beschreibungen kommen voller HTML.** Ein kleiner Helfer
(`html_text.py`) macht daraus reinen Text, damit nachgelagerte Werkzeuge
nicht an Tags und Entities hängen bleiben.

## Tests

```bash
python -m pytest
```

29 Tests: 10 für die Erkennung, 7 für die JSON-Adapter, 4 für Personio, 8
für die Deduplizierung. Keine Netzwerkaufrufe, alle Feeds liegen als
Fixtures bei.

## Installation

Python 3.10 oder neuer.

```bash
pip install -r requirements.txt   # httpx, defusedxml, rapidfuzz, pytest
```

## Herkunft und Einsatz

Herausgelöst aus einem größeren Werkzeug, das ich für meine eigene
Stellensuche gebaut habe: einem Claude-Code-Skill, bei dem ein Coding-Agent
die Suche orchestriert. Der Skill sammelt Stellen aus mehreren Quellen,
neben offiziellen Schnittstellen wie der API der Bundesagentur für Arbeit
und großen Jobportalen eben auch direkt von den Karriereseiten der Firmen,
die mich interessieren. Diese Bibliothek ist der Karriereseiten-Weg: In
einer Firmenliste stehen Namen und Websites, `detect_company` findet zu
jeder Firma das Bewerbermanagementsystem, die Adapter holen die Feeds und
bringen jede Anzeige in dasselbe Format wie die übrigen Quellen. Danach
laufen die Anzeigen aller Quellen gemeinsam durch die Deduplizierung dieser
Bibliothek, denn dieselbe Stelle steht gern dreimal im Netz: im Portal, in
der Behörden-API und auf der Karriereseite. Alle sieben Feeds sind dabei
die offiziellen, öffentlichen Schnittstellen der Systeme, gedacht genau für
diesen Zweck, und zwischen den Abrufen liegt eine Pause.

Die Arbeitsteilung im Skill ist bewusst gewählt. Alles, was deterministisch
sein kann, liegt in Python-Bausteinen wie diesem, denn Feeds erkennen,
abrufen, normalisieren und deduplizieren soll bei jedem Lauf gleich
funktionieren, testbar sein und nichts kosten. Was die Bibliothek bewusst
nicht macht, ist bewerten. Das grobe Vorsortieren übernimmt der Skill in
Python, und das eigentliche Urteil, welche der gesammelten Stellen zu mir
passen, trifft der Agent beim Lesen der Ergebnisse, also erst dort, wo
tatsächlich Urteil gebraucht wird. Das Werkzeug ist im echten Einsatz, die
Anzeige für meine erste Bewerbung stammt aus seinen Ergebnissen.

Dieser Teil ist allgemein nützlich, deshalb liegt er hier einzeln, ohne
meine Suchkriterien, ohne meine Firmenliste, ohne meine Ergebnisse. Gebaut
habe ich es mit Coding-Agenten. Der Entwurf und die Entscheidungen sind
meine, den Code hat die KI geschrieben.

## Lizenz

MIT
