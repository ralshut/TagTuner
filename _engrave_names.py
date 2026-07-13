import trimesh
import numpy as np
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
import shapely.geometry as sg

SRC = r"3d models/TagTunerAtomEchoGrovePlate.stl"

# Geometry facts established via ray-cast inspection of the plate:
#   - rotary-encoder / button hole: round, center (42.44, -42.43), radius ~3.92mm,
#     left edge at x=38.3. Flat, 4mm-thick material continues uninterrupted from
#     there all the way to the plate's outer edge (~x=-67 at this y), so there is
#     ample room for the text to the left of the hole with no thin chamfer nearby
#     (unlike the long slot near y=-9.4, which has a 0.4mm-thick bevel around it
#     and was ruled out as a placement site for this reason).
TOP_Z = 27.0
ENGRAVE_DEPTH = 0.6          # mm, well within the 4mm local wall thickness
CAP_HEIGHT = 6.0             # mm, target capital-letter height
TEXT_RIGHT_X = 38.1          # mm, flush with the encoder hole's left edge (38.3), tiny 0.2mm clearance
TEXT_CENTER_Y = -42.43       # mm, same y-coordinate as the encoder hole's center
GAP_ABOVE_STAMP = 0.6        # mm the stamp pokes above the top surface, for a clean boolean cut


def text_to_polygon(text, size=10.0, font="DejaVu Sans", weight="bold"):
    fp = FontProperties(family=font, weight=weight)
    tp = TextPath((0, 0), text, size=size, prop=fp)
    polys = [p for p in tp.to_polygons() if len(p) >= 3]
    shapely_polys = [sg.Polygon(p) for p in polys]
    shapely_polys.sort(key=lambda p: p.area, reverse=True)
    result = None
    for poly in shapely_polys:
        if not poly.is_valid:
            poly = poly.buffer(0)
        if result is None:
            result = poly
        elif result.contains(poly):
            result = result.difference(poly)
        else:
            result = result.union(poly)
    return result


def make_stamp_mesh(text):
    # size=10 as a reference scale, then rescale so cap height matches CAP_HEIGHT
    poly = text_to_polygon(text, size=10.0)
    minx, miny, maxx, maxy = poly.bounds
    # cap height reference: DejaVu Sans capital letters at size=10 are ~7.17 units tall
    ref_cap_height = 7.17
    scale = CAP_HEIGHT / ref_cap_height

    stamp_height = ENGRAVE_DEPTH + GAP_ABOVE_STAMP
    polys = poly.geoms if isinstance(poly, sg.MultiPolygon) else [poly]
    letter_meshes = [trimesh.creation.extrude_polygon(p, height=stamp_height) for p in polys]
    mesh = trimesh.util.concatenate(letter_meshes)
    mesh.apply_scale([scale, scale, 1.0])

    minx, miny, maxx, maxy = (np.array(poly.bounds) * scale)
    cy = (miny + maxy) / 2.0
    # right-align the text so it ends flush at TEXT_RIGHT_X, vertically center at
    # TEXT_CENTER_Y, sit the stamp so it spans [TOP_Z - ENGRAVE_DEPTH, TOP_Z + GAP_ABOVE_STAMP]
    mesh.apply_translation([TEXT_RIGHT_X - maxx, TEXT_CENTER_Y - cy, TOP_Z - ENGRAVE_DEPTH])
    return mesh


def main():
    plate = trimesh.load(SRC)
    assert plate.is_watertight, "source plate must be watertight for a clean boolean op"

    # file-suffix name -> full engraved text
    names = {
        "Levin": "Levins TagTuner",
        "Joris": "Joris TagTuner",
        "Tilian": "Tilians TagTuner",
    }

    for suffix, text in names.items():
        stamp = make_stamp_mesh(text)
        engraved = trimesh.boolean.difference([plate, stamp], engine="manifold")
        engraved.remove_unreferenced_vertices()
        ok = engraved.is_watertight
        out_path = f"3d models/TagTunerAtomEchoGrovePlate_{suffix}.stl"
        engraved.export(out_path)
        print(f"{text!r}: watertight={ok} volume={engraved.volume:.2f} (plate volume={plate.volume:.2f}) -> {out_path}")


if __name__ == "__main__":
    main()
