# TagTuner — Projektnotizen

TagTuner ist ein NFC-Tag-Musikplayer für Home Assistant / Music Assistant, gebaut mit ESPHome
(M5Stack Atom Echo + Grove NFC-Reader + Dial/Button). Gehäuse und Zubehör liegen als STL/SCAD-lose
3D-Modelle unter `3d models/`. Firmware-Konfiguration liegt als ESPHome-YAML im Repo-Root,
Blueprints unter `blueprints/`.

## Repo / Fork-Setup

- `origin` → `https://github.com/ralshut/TagTuner.git` (eigener Fork, Push-Ziel)
- `upstream` → `https://github.com/luka6000/TagTuner.git` (Original von luka6000, nur lesend)
- Workflow: Änderungen auf `origin` pushen; `upstream` per `git fetch upstream` /
  `git merge upstream/main` synchron halten, falls das Original weiterentwickelt wird.

## Personalisierte Grove-Plates (gravierte Namen)

`3d models/TagTunerAtomEchoGrovePlate.stl` ist die Original-Montageplatte. Für drei Kinder wurden
namensgravierte Varianten erzeugt:

- `3d models/TagTunerAtomEchoGrovePlate_Levin.stl`
- `3d models/TagTunerAtomEchoGrovePlate_Joris.stl`
- `3d models/TagTunerAtomEchoGrovePlate_Tilian.stl`

Erzeugt mit [`_engrave_names.py`](._engrave_names.py) (Python, benötigt `trimesh`, `manifold3d`,
`shapely`, `matplotlib`, `rtree`, `numpy-stl`). Skript neu ausführen und die Namensliste am Ende
anpassen, um weitere Varianten zu erzeugen.

Geometrie-Fakten der Platte (per Ray-Casting ermittelt, da kein OpenSCAD-Quellfile vorliegt):

- Runder/"hourglass"-förmiger Plattenkörper, Bounding-Box ca. 135×135×17,2mm.
- Langer dünner Schlitz bei x ∈ [-27.8, 27.8], y ∈ [-9.9, -8.95] — **nicht** der Button/Encoder,
  hat eine 0,4mm dünne Fase ringsum → ungeeignet für Gravur (Sackgasse, siehe unten).
- Rundes Loch des Dreh-Encoders/Buttons: Zentrum (42.44, -42.43), Radius ~3.92mm, linke Kante
  bei x=38.3. Rundherum ebenfalls eine kleine Fase (Wandstärke fällt dort von 4mm auf ~2mm,
  ca. 2mm rund um die Lochkante), sonst 4mm Wandstärke, Top-Z=27.0, Boden-Z=23.0.
- Aktuelle Gravur: Text endet rechts bei x=34.3 (4mm sichtbarer Abstand zur Lochkante bei x=38.3;
  eine erste Version mit nur 0,2mm Abstand "klebte" optisch am Loch und wurde deshalb korrigiert),
  vertikal zentriert auf die Loch-Mitte (y=-42.43), 6mm Kappenhöhe (DejaVu Sans Bold), rechtsbündig
  ausgerichtet (Name wächst nach links, `TEXT_RIGHT_X` in `_engrave_names.py`). Gravurtiefe 0,6mm →
  Wandstärke bleibt ≥3,4mm, nur direkt an der Lochfase sinkt sie auf minimal 1,4mm (unbedenklich
  für FDM-Druck).
- Textinhalt (final): "Levins TagTuner" / "Joris' TagTuner" / "Tilians TagTuner" — nur Joris
  bekommt einen Apostroph (endet schon auf "s", daher Possessiv-Apostroph danach: "Joris'"), Levin
  und Tilian bleiben ohne Apostroph ("Levins", "Tilians"). Eine Zwischenversion mit "Levin's" /
  "Jori's" / "Tilian's" (und Dateisuffix "Jori" statt "Joris") wurde wieder verworfen.
- Boolean-Differenz via `trimesh.boolean.difference(..., engine="manifold")`.
- Frühere Version (verworfen): Text zentriert unter dem Schlitz bei y≈-18 — wurde ersetzt, weil
  der Nutzer die Position an den Encoder/Button statt an den Schlitz gebunden haben wollte.

**Druckbarkeits-Check-Methode** (kein Slicer lokal installiert, daher Mesh-Validierung):
watertight, `is_winding_consistent`, Einzelkörper (`mesh.split()` liefert 1 Body), 0 broken/duplicate/
degenerate Faces, Euler-Zahl unverändert ggü. Original, Bounding-Box unverändert, minimale
Wandstärke im Gravurbereich per Ray-Cast-Scan verifiziert (siehe Konversationshistorie für Details).
Alle drei Varianten haben diese Checks bestanden.

## XIAO-auf-Atom-Echo-Adapter

`3d models/TagTunerAtomEchoGroveBase.stl` (die Basis, nicht die Plate) hat eine Aufnahme für das
**M5Stack Atom-Echo-Modul** (24×24mm), die für den kleineren **Seeed XIAO ESP32-C6** (21×17,5mm)
zu groß ist — es entsteht sichtbarer Leerraum um die Platine. `3d models/TagTunerXiaoEchoAdapter.stl`
gleicht das aus.

Geometrie-Fakten der Base (per Mesh-Analyse ermittelt, nicht per Bild/Ray-Cast-Schätzung — direkt
über Face-Normalen/-Höhen aus dem Mesh gelesen, da Bild-basierte Schätzung mehrfach zu falschen
Ergebnissen führte):

- 3 alte Atom-Echo-Halteplattformen ("A", "B", "D") haben je **zwei** flache Ebenen:
  - untere Ebene bei **z=5,70mm** (vermutlich die alte Klemm-/Schnapp-Ebene für das Echo-Modul)
  - obere Ebene bei **z=11,00mm** — das ist die Ebene, auf der der XIAO tatsächlich aufliegen muss
    (vom Nutzer per Handauflegen mit Kabeltest bestätigt: bei z=11 passt das USB-C-Kabel exakt).
  - Plattform-Zentren (obere Ebene, Flächen-Schwerpunkt): A≈(32,39), B≈(52,39), D≈(32,58,5).
- Zentraler Schraubdom bei (42,43, 48,93): konische Seiten, flache Kappe bei z=5,70, kein
  Durchgangsloch gefunden (kein Support für den XIAO, da zu niedrig).
- Kleiner flacher Schacht (Boden z=0,4mm) bei x≈49-62, y≈47-58, direkt vor dem USB-C-Durchbruch
  im Gehäuse — nur die Buchse des XIAO reicht dort hinein, der Rest der Platine liegt auf A/B/D.

Adapter-Konstruktion (aktuelle v3, ad-hoc-Skript nicht im Repo committet):
**4 einzelne Stützbeine** (Zylinder, r=1-1.6mm) stehen exakt auf den 4 vorhandenen z=5,70mm-Flächen
(A, B, D **und zusätzlich der Schraubdom-Kappe**, versetzt vom Domzentrum bei (44.4, 48.93) um die
zentrale Pilotbohrung zu meiden) und reichen hoch bis z=11,0. Eine **dünne, frei schwebende
Deckplatte** (1,4mm dick, z=9,6-11,0, Fläche x=[27,57] y=[34,60]) verbindet die 4 Beinspitzen —
dazwischen ist bewusst **keine** Fläche/Material (kein Vollblock mehr, siehe unten). Beine und Deck
werden je per `trimesh.boolean.difference(fill_block, base)` erzeugt ("Volumenblock minus
vorhandene Geometrie" — füllt automatisch nur die Lücke zum Terrain, unabhängig von dessen Form)
und dann per `union` verbunden. 4 Klemmnasen (2,6×2,6mm, meist; die Ecke nahe der Gehäusewand ist
kleiner: 1,8×1,8mm) sitzen außerhalb der XIAO-Kontur (x=32-53, y=39-56,5) an deren 4 Ecken, mit
Sicherheitsabstand zur Wand geprüft.

**Wichtige Lektionen aus den Entwicklungs-Iterationen** (jeweils per direkter Mesh-Kollisionsprüfung
`trimesh.boolean.intersection` mit der Base gefunden, Volumen muss ~0 sein):
1. v1: Fußabdruck wich unnötig dem Schraubdom aus → Donut-Loch mitten in der XIAO-Auflagefläche
   (der Dom ist mit 5,7mm weit niedriger als das Deck bei 9,6-11mm, keine Kollisionsgefahr).
2. v2: Klemmnasen waren zentriert auf den XIAO-Eckpunkten statt außerhalb davon.
3. v2→v3: Nutzer wollte statt eines flächendeckenden Vollblocks (unnötig viel Material, "wirkt wie
   ein Zylinder am Dom") eine Konstruktion mit nur 4 diskreten Auflagepunkten (A/B/D/Dom) und einer
   dazwischen frei schwebenden Deckplatte — umgesetzt wie oben beschrieben. Dabei fielen erneut
   Detailfehler auf: 3 der 4 Klemmnasen ragten ohne Deck-Material darunter über den Rand hinaus
   ("hängen in der Luft"), weil die Deckfläche zu knapp bemessen war; behoben durch Vergrößerung
   der Deckfläche und Anpassung einer Nasen-Position/-Größe nahe der Gehäusewand.

Offen/nicht verifiziert: Nur 4 Eck-Klemmnasen statt (wie im offiziellen XIAO-Custom-Design, siehe
README-Bild "XIAO will fit perfectly into the bottom part braces") vieler kleiner Noppen entlang
beider Platinen-Längskanten. Sollte in Kombination mit der aufgeschraubten Deckplatte reichen,
wurde aber nicht physisch getestet.

## Deployment: Joris' TagTuner läuft live auf dem Homeserver

Von den drei geplanten Einheiten (Levin, Joris, Tilian) ist aktuell nur **Joris'** TagTuner
tatsächlich in Betrieb, per ESPHome an die Home-Assistant-Instanz auf dem Homeserver
(`192.168.10.100`, siehe `C:\Software_Checkout\homeassistant\CLAUDE.md`) angebunden:

- Device-Name intern `tagtuner_9fdef0` ("TagTuner-Joris"), Automation
  `automation.tagtuner_music_player_for_nfc_tags_automation` (id `1785780841704`) nutzt das
  Blueprint `blueprints/automation/luka6000/TagTuner4HAss.yaml` (im HA-Repo getrackt), Ziel
  ist `media_player.sonos_amp` ("6) Joris").
- Ein zweites Gerät `tagtuner_9f79bc` ("TagTuner-Xiao") existierte in HA, war aber dauerhaft
  `unavailable` (kam nie online) — vermutlich der XIAO-ESP32-C6-Aufbau (siehe oben,
  "XIAO-auf-Atom-Echo-Adapter") für Levin oder Tilian, nie fertig in Betrieb genommen.
  **Am 2026-09-01 komplett aus HA entfernt** (Config-Entry `01KYM1ZM8V7ZMDGZBY7WF151T5` +
  Gerät + alle 13 Entitäten) — reine Karteileiche ohne Nutzen. Aktuell existiert in HA nur
  noch Joris' Gerät.

### Bekanntes Problem: Gerät reagiert nicht mehr auf Tags, Lautstärke-Regler geht noch

Tritt wiederkehrend auf (mind. zweimal beobachtet, Stand 2026-08-31): Ein aufgelegter NFC-Tag
löst keine Wiedergabe aus, aber Drehen am Lautstärke-Encoder erzeugt weiterhin normale
`volumeUp`/`volumeDown`-Events in HA (`event.tagtuner_9fdef0_action`). Befund aus der
HA-Historie: Im betroffenen Zeitraum taucht **kein einziger Tag-Scan-Event** auf, nur
Lautstärke-Events — das NFC-Lesen scheint auf Geräteebene gar nicht erst auszulösen, während
der Encoder (vermutlich Interrupt-getrieben) weiterläuft. Deutet auf einen **Hänger in der
NFC-Poll-Schleife der Firmware** hin, nicht auf ein WLAN-/API- oder HA-seitiges Problem
(Sonos/Media-Player und die Automation selbst liefen unauffällig weiter).

**Sofort-Fix:** Kein Ausstecken nötig — `button.tagtuner_9fdef0_restart` (ESPHome-Restart-Entity)
aus der Ferne drücken bewirkt denselben Neustart wie Strom trennen.

**Noch offen:** Root Cause in der Firmware nicht gefunden (kein passendes Issue im
`luka6000/TagTuner`-Upstream-Repo gefunden, Stand 2026-08-31). Falls es wiederkehrt: prüfen, ob
es sich mit bestimmten Tag-Typen/-Platzierungen korreliert, oder ein Watchdog-Reset in der
ESPHome-YAML ergänzen, der bei Ausbleiben von NFC-Aktivität über einen längeren Zeitraum
automatisch neu startet. Grund, warum in `tagtuner-core-nfc.yaml` bislang kein Watchdog steckt:
der `pn532_i2c`-Custom-Component (live von `github://luka6000/TagTuner@main` gezogen, 350ms-Polling)
hat keine eingebaute Recovery-Logik — ein Fix müsste im Firmware-Fork selbst ansetzen.

**Wichtiger Gegenbefund (2026-09-01): der Fehler überlebt einen Kaltstart.** Nach Neustart *und*
komplettem Strom-Ziehen werden weiterhin keine Tags erkannt, während Encoder, WLAN und ESPHome-API
unauffällig laufen. Ein Hänger in der Poll-Schleife müsste durch einen Power-Cycle zwingend
verschwinden — tut er nicht. Damit ist die Firmware-Hänger-These für diesen Fall **entkräftet**;
wahrscheinlichste Ursache ist jetzt die Hardware: PN532-Modul defekt, Grove-Kabel/-Stecker lose oder
gebrochen, oder eine kalte Lötstelle auf der I2C-Strecke (SDA=GPIO22/D4, SCL=GPIO23/D5, 100 kHz,
`timeout: 13ms`). Nächste sinnvolle Schritte in dieser Reihenfolge: Grove-Kabel beidseitig neu
stecken → Kabel tauschen → PN532-Modul tauschen (z.B. gegen das des nie in Betrieb genommenen
zweiten Geräts `tagtuner_9f79bc`).

**Diagnose-Grenzen, damit das nicht nochmal durchprobiert wird:** Gerätelogs lassen sich ohne
ESPHome-Installation über den HA-Container abgreifen (`aioesphomeapi` ist dort vorhanden, die
TagTuner-API ist unverschlüsselt, IP `192.168.10.157:6053`) — Details im HA-Repo-CLAUDE.md. Was das
**nicht** leistet: Der Boot-Config-Dump mit der entscheidenden Zeile (`Found chip PN532 with firmware
version …` bzw. `Error communicating with PN532`) läuft ~1 s nach dem Reset, die API ist erst nach
~13 s wieder erreichbar. Und im Leerlauf schweigt bei `logger: level: DEBUG` sowohl ein gesunder als
auch ein per `mark_failed()` abgeschalteter PN532 — Leerlauf-Logs beweisen also gar nichts.
Aussagekräftig ist nur ein **aufgelegter Tag** (dann `sensor.tagtuner_9fdef0_status` → `Tag <uid>`,
`binary_sensor.tagtuner_9fdef0_tag` → `on`) oder ein serielles Log am USB-Port. Wer es endgültig
remote klären will, muss `i2c: scan: true` in `tagtuner-XIAO-custom.yaml` setzen und neu flashen.

**Von selbst wieder repariert, 2026-09-01, ~11:12 Uhr** — Befund stützt die Lose-Steckverbindung-These
weiter: Nutzer hat nach eigener Aussage nochmal Strom gezogen/wieder angeschlossen, am Encoder
rumgespielt und verschiedene Tags probiert; danach hat das Gerät wieder normal gelesen (HA-Logbook
bestätigt ab 11:12:51 saubere `Tag <uid>` → `Tag removed`-Zyklen für mehrere unterschiedliche Tags
hintereinander). **Wichtig:** Das Logbook zeigt für dieses Zeitfenster nur eine `unavailable`-Lücke
von **0,19 Sekunden** (11:12:39,025 → 11:12:39,217) — ein echter Kaltstart braucht laut eigenem Test
vom selben Tag ~13s bis die ESPHome-API wieder antwortet. Der behauptete Stromzieh-Zyklus hat sich in
HA also gar nicht als vollständiger Neustart niedergeschlagen (evtl. zu kurz/nicht vollständig
unterbrochen, oder er lag außerhalb des geloggten Fensters). Naheliegendste Erklärung bleibt daher:
**das Anfassen/Bewegen des Geräts selbst** (Encoder drehen, Tags auflegen) hat einen wackligen
Stecker/eine kalte Lötstelle wieder in Kontakt gebracht — kein Beweis, aber ein zweites Indiz für
Hardware statt Firmware. Kein Log wurde während dieses Fensters mitgeschnitten (die Live-Log-Sitzung
von 09:53 war zu dem Zeitpunkt bereits beendet), nur das HA-Logbook. **Noch nicht als erledigt
betrachten** — ohne verifizierten Kaltstart mit definierter unterbrechungsfreier Dauer bleibt offen,
ob der Fehler wiederkehrt. Bei erneutem Auftreten: gezielt Grove-Stecker/-Kabel nachdrücken, bevor
zum Werkzeug (Kabeltausch) gegriffen wird.

**Vorläufige Vorbeugung (HA-seitig, seit 2026-09-01):** Da kein Firmware-Fix vorliegt, läuft auf
dem Homeserver eine tägliche 03:00-Uhr-Automation (`automation.tagtuner_joris_taeglicher_vorsorge_neustart`,
siehe `C:\Software_Checkout\homeassistant\CLAUDE.md`), die `button.tagtuner_9fdef0_restart` drückt.
Kuriert nur das Symptom (senkt die Chance, dass Joris tagsüber ein bereits hängendes Gerät vorfindet),
behebt aber nicht die eigentliche Ursache in der Poll-Schleife.

## Sonstiges

- Kein Build-/Testsystem im Repo (reine YAML/STL/MD-Sammlung), daher keine CI-Befehle nötig.
