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

### Bekanntes Problem: NFC-Leser hängt, Encoder geht noch (Stand 2026-11-04)

**Symptom:** Aufgelegte Tags werden nicht gelesen, Encoder, Taste, WLAN und ESPHome-API laufen normal.
Zuletzt vom 2026-10-09 bis 2026-10-21 (zwölf Tage unbemerkt).

**Befund (per Config-Dump verifiziert, siehe unten):** I2C-Bus blockiert, `Recovery: failed, SCL is held
low on the bus`, danach `pn532 is marked FAILED`. Der PN532 hatte dabei Strom (seine LED leuchtete).
Es hängt also der **PN532-Chip selbst** und hält SCL fest.

**Abhilfe:** Netzteil ziehen, **warten bis alle LEDs aus sind**, wieder einstecken (danach
`Recovery: bus successfully recovered`, Tags werden gelesen). **Nicht** wirksam:
- Software-Neustart (`button.tagtuner_9fdef0_restart`, auch elf nächtliche Neustarts in Folge): Der
  PN532 hängt am 5-V-USB-Strom (VBUS) und wird dabei nicht stromlos.
- Kurzes Aus- und Einstecken: Die Kondensatoren halten den PN532 im Hänger.

**Auslöser: offen.** Zwei begründete Verdächtige:
1. `powerdown()`: Der PN532-Treiber (`components/pn532/pn532.h`, `on_powerdown()`) legt den PN532 bei
   **jedem Software-Neustart** schlafen; gedacht für Akkugeräte mit Deep-Sleep, beim TagTuner nutzlos.
   Beim nächsten Boot muss er per I2C geweckt werden, ohne dass er je stromlos war. Der letzte
   funktionierende Scan vor dem Oktober-Ausfall war am Abend vor einem 03:00-Neustart.
   Gegenindiz: Hänger gab es auch schon vor Einführung des 03:00-Neustarts (August).
2. **5-V-Pegel auf I2C:** Laut README wird das Elechouse-PN532-Board (rot, V3) aus VBUS gespeist; sein
   Pegelwandler zieht SDA/SCL dann auf 5 V. Der ESP32-C6 ist laut Datenblatt nicht 5-V-tolerant
   (VIH max = VDD + 0,3 V). Abhilfe wäre: PN532-VCC auf 3V3 statt VBUS umlöten (laut Handbuch
   3,3–5 V zulässig). **Nicht umgesetzt.**

**Status quo:**
- 03:00-Vorsorge-Neustart in HA seit 2026-11-04 abgeschaltet (`initial_state: false`), da wirkungslos
  und unter Verdacht 1.
- Stündlicher Health-Check auf dem Homeserver prüft den PN532 und schickt bei Ausfall ntfy
  (`homeassistant/docs/homeserver.md` → „Stündlicher Gesundheits-Check“, Skript
  `homeassistant/server/health-check/pn532_status.py`). Langzeit-Log: `/data/health-check/health-check.log`.
- Kommt der Hänger trotz abgeschaltetem 03:00-Neustart wieder, ist Verdacht 1 entlastet → Umlöten auf 3V3.

**Lessons learned zur Diagnose:**
- **Zustand des PN532 remote lesbar, ohne Flashen und ohne Tag:** `aioesphomeapi` (im HA-Container
  vorhanden, TagTuner-API unverschlüsselt `192.168.10.157:6053`) mit
  `subscribe_logs(..., dump_config=True)` lässt das Gerät seinen Config-Dump jederzeit neu ausgeben,
  inklusive I2C-Recovery-Ergebnis vom Boot und `marked FAILED`. Leerlauf-Logs allein sagen nichts.
- **Neustart in der HA-Historie:** `Ready` nach `unavailable` in `sensor.tagtuner_9fdef0_status` =
  Neustart. Die Länge der Lücke sagt nichts (Hardreset ≈ 0,15 s, Software-Neustart ≈ 10 s).
- **„Tag aufgelegt, keine Musik“ ist oft nicht der TagTuner:** Wenn die Historie `Tag <uid>` /
  `Plain UID tag` zeigt, liest das Gerät. Dann Automation-Traces und `media_player.sonos_amp` prüfen
  (`homeassistant/docs/tagtuner.md`, Diagnose-Reihenfolge). Am 2026-11-04 war z. B. Music Assistant mit
  falscher IP gestartet.
- HA-Verlauf reicht seit 2026-11-04 60 Tage zurück (vorher 10, deshalb war der Oktober-Auslöser weg).

## Verbindung zur Phoniebox (gleiche NFC-Tags)

Die Phoniebox-Karten (Pi 3B, `phoniebox.local`) spielen auch am TagTuner. Karten-ID der Phoniebox = UID
des Tags als Dezimalzahl; HA-Tag-ID = dieselbe UID hexadezimal mit Bindestrichen (z. B. `1157393924` =
`0x44FC6E04` → `44-FC-6E-04`, 7-Byte-UIDs analog: `23477622569893889` → `53-68-C5-F9-73-00-01`).

**So wurde abgeglichen (2026-08-22, Phoniebox → TagTuner, einmalig, kein Skript):** Alle 28
Spotify-Karten aus `shared/shortcuts/` der Phoniebox ausgelesen, Karten-ID in Hex-UID umgerechnet und in
HA je ein **Tag-Eintrag mit dieser UID angelegt, Name = MA-URI** (`spotify--dEY87Fdt://album|playlist/<ID>`),
per HA-MCP (`ha_config_set_helper`, Typ `tag`). Ohne Auflegen und ohne Beschreiben der Karten. Gemacht in
einer Claude-Sitzung im HA-Projekt (Protokoll `~/.claude/projects/c--Software-Checkout-homeassistant/218326e2-….jsonl`).
Ein Sync-Skript wurde damals gewünscht, aber **nie als Datei angelegt**.

**Warum das funktioniert:** Trägt eine Karte keine TagTuner-eigene NDEF-URI (leer oder nicht
beschreibbar, z. B. Mifare Classic), ruft die Firmware `homeassistant.tag_scanned` mit der rohen UID auf
(Status `Plain UID tag`), und die Blueprint-Automation spielt den **Namen** des HA-Tag-Eintrags ab.
**Falle:** Trägt die Karte schon eine TagTuner-URI (Status `Tag <uid>`), hat diese Vorrang, der Name im
Tag-Register wird ignoriert. Dann Karteninhalt mit `button.tagtuner_9fdef0_erase_tag` löschen.

**Rückrichtung (TagTuner-Karten auf der Phoniebox):** nie umgesetzt. Phoniebox-Seite: Kartenliste,
nach dem Neuaufbau 2026-11-01 fehlende Karten und Aufbau eines Karteneintrags in
`C:\Software_Checkout\Phoniebox\docs\tagtuner-karten.md`.

## Sonstiges

- Kein Build-/Testsystem im Repo (reine YAML/STL/MD-Sammlung), daher keine CI-Befehle nötig.
