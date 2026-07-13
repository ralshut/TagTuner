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
- `3d models/TagTunerAtomEchoGrovePlate_Jori.stl` (Kind heißt Jori, nicht Joris — Dateiname korrigiert)
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
- Textinhalt (mit Possessiv-Apostroph): "Levin's TagTuner" / "Jori's TagTuner" / "Tilian's TagTuner"
  (Dateisuffix Levin/Jori/Tilian, siehe `names`-Dict in `_engrave_names.py`). Vorherige Version ohne
  Apostroph ("Levins"/"Joris"/"Tilians") wurde ersetzt.
- Boolean-Differenz via `trimesh.boolean.difference(..., engine="manifold")`.
- Frühere Version (verworfen): Text zentriert unter dem Schlitz bei y≈-18 — wurde ersetzt, weil
  der Nutzer die Position an den Encoder/Button statt an den Schlitz gebunden haben wollte.

**Druckbarkeits-Check-Methode** (kein Slicer lokal installiert, daher Mesh-Validierung):
watertight, `is_winding_consistent`, Einzelkörper (`mesh.split()` liefert 1 Body), 0 broken/duplicate/
degenerate Faces, Euler-Zahl unverändert ggü. Original, Bounding-Box unverändert, minimale
Wandstärke im Gravurbereich per Ray-Cast-Scan verifiziert (siehe Konversationshistorie für Details).
Alle drei Varianten haben diese Checks bestanden.

## Sonstiges

- Kein Build-/Testsystem im Repo (reine YAML/STL/MD-Sammlung), daher keine CI-Befehle nötig.
