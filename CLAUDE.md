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
- Langer dünner Schlitz ("Lochknopf"/Button-Schlitz) bei x ∈ [-27.8, 27.8], y ∈ [-9.9, -8.95].
- Darunter liegende Fläche ist durchgehend eben, Top-Z=27.0, Boden-Z=23.0 → 4mm Wandstärke.
- Namen werden zentriert auf x=0 (Schlitzmitte), bei y≈-18, mit 6mm Kappenhöhe (DejaVu Sans Bold)
  eingraviert. Gravurtiefe 0,6mm → verbleibende Wandstärke 3,4mm.
- Boolean-Differenz via `trimesh.boolean.difference(..., engine="manifold")`.

**Druckbarkeits-Check-Methode** (kein Slicer lokal installiert, daher Mesh-Validierung):
watertight, `is_winding_consistent`, Einzelkörper (`mesh.split()` liefert 1 Body), 0 broken/duplicate/
degenerate Faces, Euler-Zahl unverändert ggü. Original, Bounding-Box unverändert, minimale
Wandstärke im Gravurbereich per Ray-Cast-Scan verifiziert (siehe Konversationshistorie für Details).
Alle drei Varianten haben diese Checks bestanden.

## Sonstiges

- Kein Build-/Testsystem im Repo (reine YAML/STL/MD-Sammlung), daher keine CI-Befehle nötig.
