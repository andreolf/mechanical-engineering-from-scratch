"""Scripting CAD: generate an involute spur gear outline from parameters, extrude it to a closed mesh, export binary STL and re-open it with the same volume."""
import math
import os
import struct
import tempfile
import numpy as np


def inv(a):
    return math.tan(a) - a


def gear_outline(m, z, alpha_deg=20.0, n_flank=24, n_arc=6):
    """Closed counterclockwise polygon of a standard involute spur gear (addendum m, dedendum 1.25 m)."""
    a = math.radians(alpha_deg)
    r = m * z / 2; rb = r * math.cos(a); ra = r + m; rf = r - 1.25 * m
    half = math.pi / (2 * z) + inv(a)                      # polar half-angle of the tooth at the base circle
    r0 = max(rb, rf)
    rs = np.linspace(r0, ra, n_flank)
    phi = np.array([half - inv(math.acos(min(rb / q, 1.0))) for q in rs])   # right-flank polar angle (measured from the tooth axis)
    pts = []
    for k in range(z):
        c = 2 * math.pi * k / z
        # root arc from the previous gap centre to this tooth's right flank foot
        g0, g1 = c - math.pi / z, c - phi[0]
        for t in np.linspace(g0, g1, n_arc, endpoint=False):
            pts.append((rf * math.cos(t), rf * math.sin(t)))
        if rf < rb:
            pts.append((rf * math.cos(c - phi[0]), rf * math.sin(c - phi[0])))   # radial line from the root to the base circle
        for q, f in zip(rs, phi):                                              # right flank, going outwards (angle increasing towards the axis)
            pts.append((q * math.cos(c - f), q * math.sin(c - f)))
        for t in np.linspace(c - phi[-1], c + phi[-1], n_arc)[1:-1]:          # tip arc
            pts.append((ra * math.cos(t), ra * math.sin(t)))
        for q, f in zip(rs[::-1], phi[::-1]):                                  # left flank, coming back in
            pts.append((q * math.cos(c + f), q * math.sin(c + f)))
        if rf < rb:
            pts.append((rf * math.cos(c + phi[0]), rf * math.sin(c + phi[0])))
        for t in np.linspace(c + phi[0], c + math.pi / z, n_arc, endpoint=False)[1:]:
            pts.append((rf * math.cos(t), rf * math.sin(t)))
    return np.array(pts), dict(r=r, rb=rb, ra=ra, rf=rf)


def shoelace(P):
    x, y = P[:, 0], P[:, 1]
    return 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)


def extrude(P, h):
    """Closed mesh: fan caps from the centre (the outline is star-shaped about it) and quad sides."""
    n = len(P)
    V = np.vstack([np.c_[P, np.zeros(n)], np.c_[P, np.full(n, h)], [[0, 0, 0], [0, 0, h]]])
    F = []
    for i in range(n):
        j = (i + 1) % n
        F += [(i, j, n + j), (i, n + j, n + i), (2 * n, j, i), (2 * n + 1, n + i, n + j)]
    return V, np.array(F)


def write_stl(path, V, F):
    with open(path, "wb") as fh:
        fh.write(b"gear".ljust(80, b" ")); fh.write(struct.pack("<I", len(F)))
        for a, b, c in F:
            nr = np.cross(V[b] - V[a], V[c] - V[a]); nr /= np.linalg.norm(nr)
            fh.write(struct.pack("<12fH", *nr, *V[a], *V[b], *V[c], 0))


def read_stl(path):
    raw = open(path, "rb").read(); k = struct.unpack("<I", raw[80:84])[0]
    return np.array([struct.unpack("<12fH", raw[84 + 50 * i:134 + 50 * i])[3:12] for i in range(k)], float).reshape(-1, 3, 3)


def tri_volume(T):
    return np.einsum("ij,ij->i", T[:, 0], np.cross(T[:, 1], T[:, 2])).sum() / 6


if __name__ == "__main__":
    # a Swiss-style watch wheel: module 0.15 mm, 60 teeth, 20 deg pressure angle, 0.25 mm thick (dimensions in mm)
    m, z, h = 0.15, 60, 0.25
    P, g = gear_outline(m, z)
    print(f"pitch diameter {2*g['r']:.4f} mm = m z; base {2*g['rb']:.4f}, tip {2*g['ra']:.4f}, root {2*g['rf']:.4f} mm; {len(P)} outline points")
    assert abs(2 * g["r"] - m * z) < 1e-12
    # tooth thickness on the pitch circle: find where the outline crosses r = m z / 2 around tooth 0
    rr = np.hypot(P[:, 0], P[:, 1]); ang = np.arctan2(P[:, 1], P[:, 0])
    cross = []
    for i in range(len(P)):
        j = (i + 1) % len(P)
        if (rr[i] - g["r"]) * (rr[j] - g["r"]) < 0 and abs(ang[i]) < math.pi / z:
            t = (g["r"] - rr[i]) / (rr[j] - rr[i]); cross.append(ang[i] + t * (ang[j] - ang[i]))
    s = g["r"] * (max(cross) - min(cross))
    print(f"tooth thickness on the pitch circle {s:.6f} mm; pi m / 2 = {math.pi*m/2:.6f} mm")
    assert abs(s - math.pi * m / 2) < 2e-4
    A = shoelace(P)
    assert A > 0
    V, F = extrude(P, h)
    # star-shaped check: every cap triangle is counterclockwise
    assert all(P[i, 0] * P[(i + 1) % len(P), 1] - P[(i + 1) % len(P), 0] * P[i, 1] > 0 for i in range(len(P)))
    vol = tri_volume(V[F])
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "watch_wheel.stl")
        write_stl(path, V, F)
        vol2 = tri_volume(read_stl(path))
    print(f"outline area {A:.6f} mm^2; mesh volume {vol:.6f} mm^3 = area x thickness {A*h:.6f}; re-opened STL {vol2:.6f} mm^3 ({len(F)} triangles)")
    assert abs(vol - A * h) < 1e-12 and abs(vol2 - vol) < 1e-6 * vol
    # rebuild for a sweep of tooth counts: always closed, always star-shaped, area between root and tip discs
    for zz in (12, 18, 30, 60, 100):
        Pz, gz = gear_outline(1.0, zz)
        Az = shoelace(Pz)
        assert math.pi * gz["rf"] ** 2 < Az < math.pi * gz["ra"] ** 2
    print("sweep z = 12 ... 100: every outline closes with area between the root and tip discs")
