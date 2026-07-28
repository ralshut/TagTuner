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

Adapter-Konstruktion (`_engrave_names.py`-Stil, ad-hoc-Skript nicht im Repo committet):
Robuster Ansatz statt einzelner Füße: ein Volumenblock über der gesamten Zielfläche von z=0,3 bis
z=11,0 wird per `trimesh.boolean.difference` mit der vorhandenen Base verrechnet — das Ergebnis
füllt automatisch genau die Lücke zum vorhandenen Terrain, unabhängig von dessen tatsächlicher
Form (deutlich zuverlässiger als manuell platzierte Füße, die zweimal mit vorhandener Geometrie
kollidierten, bis dieser Ansatz verwendet wurde). 4 kleine Klemmnasen (2,2×2,2mm, 1,6mm hoch)
sitzen außerhalb der XIAO-Kontur (x=32-53, y=39-56,5) an deren 4 Ecken.

**Wichtige Lektion aus zwei Bugs in v1:** (1) eine "Donut-Loch" in der Deckfläche entstand, weil
der Fußabdruck unnötig um den Schraubdom herumgeführt wurde (der Dom ist mit 5,7mm weit niedriger
als die Deckplatte bei 9,6-11mm, keine Kollisionsgefahr); (2) die 4 Klemmnasen waren zentriert auf
den XIAO-Eckpunkten statt außerhalb davon platziert. Beide Fehler wurden per direkter
Mesh-Kollisionsprüfung (`trimesh.boolean.intersection` mit der Base, Volumen muss ~0 sein) und
Ray-Cast-Verifikation der Standfläche gefunden und behoben.

Offen/nicht verifiziert: Nur 4 Eck-Klemmnasen statt (wie im offiziellen XIAO-Custom-Design, siehe
README-Bild "XIAO will fit perfectly into the bottom part braces") vieler kleiner Noppen entlang
beider Platinen-Längskanten. Sollte in Kombination mit der aufgeschraubten Deckplatte reichen,
wurde aber nicht physisch getestet.

## Sonstiges

- Kein Build-/Testsystem im Repo (reine YAML/STL/MD-Sammlung), daher keine CI-Befehle nötig.
