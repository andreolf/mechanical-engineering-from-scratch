"""A minimal slicer: cut a triangle mesh of a sphere into layers, join the cut segments into contours, and compare layer areas, volume and print time with the exact shape."""
import math
import numpy as np


def sphere_mesh(R, nlat=60, nlon=120):
    """Latitude-longitude triangulation of a sphere of radius R centred at (0, 0, R)."""
    tris = []
    for i in range(nlat):
        t0, t1 = math.pi * i / nlat, math.pi * (i + 1) / nlat
        for j in range(nlon):
            p0, p1 = 2 * math.pi * j / nlon, 2 * math.pi * (j + 1) / nlon
            P = lambda t, p: (R * math.sin(t) * math.cos(p), R * math.sin(t) * math.sin(p), R + R * math.cos(t))
            a, b, c, d = P(t0, p0), P(t0, p1), P(t1, p0), P(t1, p1)
            if i > 0: tris.append((a, b, d))
            if i < nlat - 1: tris.append((a, d, c))
    return tris


def slice_layer(tris, z):
    """Segments where the plane at height z cuts the mesh."""
    segs = []
    for tri in tris:
        pts = []
        for k in range(3):
            p, q = tri[k], tri[(k + 1) % 3]
            if (p[2] - z) * (q[2] - z) < 0:
                s = (z - p[2]) / (q[2] - p[2]); pts.append((p[0] + s * (q[0] - p[0]), p[1] + s * (q[1] - p[1])))
        if len(pts) == 2: segs.append(tuple(pts))
    return segs


def contour_area(segs):
    """Chain the segments into loops by matching endpoints, then take the shoelace area."""
    key = lambda pt: (round(pt[0], 9), round(pt[1], 9))
    nxt = {}
    for a, b in segs:
        nxt.setdefault(key(a), []).append(b); nxt.setdefault(key(b), []).append(a)
    start = segs[0][0]; loop = [start]; prev = None; cur = start
    while True:
        cands = [p for p in nxt[key(cur)] if prev is None or key(p) != key(prev)]
        prev, cur = cur, cands[0]
        if key(cur) == key(start): break
        loop.append(cur)
    A = 0.5 * abs(sum(loop[i][0] * loop[i - 1][1] - loop[i - 1][0] * loop[i][1] for i in range(len(loop))))
    return A, len(loop), len(segs)


if __name__ == "__main__":
    R, h = 20.0, 0.2      # mm sphere, layer height
    tris = sphere_mesh(R)
    zs = np.arange(h / 2, 2 * R, h)
    areas = []
    for z in zs:
        A, n, ns = contour_area(slice_layer(tris, z))
        areas.append(A)
        assert n == ns          # every segment used exactly once: a closed contour
    areas = np.array(areas)
    exact = math.pi * (R**2 - (zs - R) ** 2)
    print(f"{len(tris)} triangles, {len(zs)} layers of {h} mm")
    print(f"mid layer area {areas[len(zs)//2]:.2f} mm^2 (exact {exact[len(zs)//2]:.2f}); worst layer error {np.max(abs(areas/exact-1))*100:.2f} %")
    V = areas.sum() * h; Vex = 4 / 3 * math.pi * R**3
    print(f"sliced volume {V:.0f} mm^3, sphere {Vex:.0f} mm^3 ({(V/Vex-1)*100:+.2f} %)")
    assert abs(V / Vex - 1) < 0.01
    # time: perimeters at 40 mm/s with 0.4 mm lines, 20 % infill
    per = 2 * np.sqrt(math.pi * areas)
    line_len = (2 * per.sum() + 0.2 * areas.sum() / 0.4)
    print(f"two perimeters + 20 % infill: {line_len/1000:.1f} m of extrusion, about {line_len/40/60:.0f} min at 40 mm/s")
    # staircase (cusp) error is about h |n_z|: zero on vertical walls, worst on nearly flat tops
    for zf in (0.5, 0.9, 0.99):
        nz = abs(zf)   # |cos| of normal from vertical at height z = R(1+zf)
        print(f"  surface normal at {math.degrees(math.acos(nz)):.0f} deg from vertical: cusp height {h*nz:.3f} mm")
