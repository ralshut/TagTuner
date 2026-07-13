import trimesh
import numpy as np
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
import shapely.geometry as sg

SRC = r"3d models/TagTunerAtomEchoGrovePlate.stl"

# Geometry facts established via ray-cast inspection of the plate:
#   - long slot ("Schlitz"): x in [-27.81, 27.81], y in [-9.91, -8.95]
#   - flat top surface z = 27.0, flat bottom z = 23.0 (4mm thick) in the
#     area below the slot (checked at multiple points, y in [-25,-15])
TOP_Z = 27.0
ENGRAVE_DEPTH = 0.6          # mm, well within the 4mm local wall thickness
CAP_HEIGHT = 6.0             # mm, target capital-letter height
TEXT_CENTER_Y = -18.0        # mm, centered below the slot (slot bottom edge is y=-9.91)
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


def make_stamp_mesh(name):
    # size=10 as a reference scale, then rescale so cap height matches CAP_HEIGHT
    poly = text_to_polygon(name, size=10.0)
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
    cx = (minx + maxx) / 2.0
    cy = (miny + maxy) / 2.0
    # center horizontally at x=0, vertically at TEXT_CENTER_Y, sit the stamp
    # so it spans [TOP_Z - ENGRAVE_DEPTH, TOP_Z + GAP_ABOVE_STAMP]
    mesh.apply_translation([-cx, TEXT_CENTER_Y - cy, TOP_Z - ENGRAVE_DEPTH])
    return mesh


def main():
    plate = trimesh.load(SRC)
    assert plate.is_watertight, "source plate must be watertight for a clean boolean op"

    for name in ["Levin", "Joris", "Tilian"]:
        stamp = make_stamp_mesh(name)
        engraved = trimesh.boolean.difference([plate, stamp], engine="manifold")
        engraved.remove_unreferenced_vertices()
        ok = engraved.is_watertight
        out_path = f"3d models/TagTunerAtomEchoGrovePlate_{name}.stl"
        engraved.export(out_path)
        print(f"{name}: watertight={ok} volume={engraved.volume:.2f} (plate volume={plate.volume:.2f}) -> {out_path}")


if __name__ == "__main__":
    main()
