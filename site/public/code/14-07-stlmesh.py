"""Triangle meshes and STL: build a closed gear-blank mesh, write and re-read ASCII and binary STL from scratch, and check watertightness, orientation and volume."""
import math
import os
import struct
import tempfile
from collections import Counter
import numpy as np


def cylinder_mesh(r, h, n):
    """Closed, outward-oriented triangle mesh of a cylinder approximated by an n-gon prism. Returns vertices and faces."""
    ang = 2 * np.pi * np.arange(n) / n
    bot = np.c_[r * np.cos(ang), r * np.sin(ang), np.zeros(n)]
    top = bot + [0, 0, h]
    V = np.vstack([bot, top, [[0, 0, 0], [0, 0, h]]])
    cb, ct = 2 * n, 2 * n + 1
    F = []
    for i in range(n):
        j = (i + 1) % n
        F += [(i, j, n + j), (i, n + j, n + i)]        # side quad as two triangles, counterclockwise seen from outside
        F += [(cb, j, i), (ct, n + i, n + j)]           # bottom fan (normal -z) and top fan (normal +z)
    return V, np.array(F)


def write_ascii_stl(path, V, F, name="part"):
    with open(path, "w") as fh:
        fh.write(f"solid {name}\n")
        for a, b, c in F:
            nrm = np.cross(V[b] - V[a], V[c] - V[a]); nrm /= np.linalg.norm(nrm)
            fh.write(f"  facet normal {nrm[0]:.9e} {nrm[1]:.9e} {nrm[2]:.9e}\n    outer loop\n")
            for k in (a, b, c):
                fh.write(f"      vertex {V[k][0]:.9e} {V[k][1]:.9e} {V[k][2]:.9e}\n")
            fh.write("    endloop\n  endfacet\n")
        fh.write(f"endsolid {name}\n")


def write_binary_stl(path, V, F):
    with open(path, "wb") as fh:
        fh.write(b"binary STL written from scratch".ljust(80, b" "))
        fh.write(struct.pack("<I", len(F)))
        for a, b, c in F:
            nrm = np.cross(V[b] - V[a], V[c] - V[a]); nrm /= np.linalg.norm(nrm)
            fh.write(struct.pack("<12fH", *nrm, *V[a], *V[b], *V[c], 0))


def read_stl(path):
    """Returns an array of triangles (k, 3, 3). Detects ASCII by the 'solid' keyword AND a matching size check."""
    raw = open(path, "rb").read()
    if len(raw) >= 84 and 84 + 50 * struct.unpack("<I", raw[80:84])[0] == len(raw):
        k = struct.unpack("<I", raw[80:84])[0]
        T = [struct.unpack("<12fH", raw[84 + 50 * i: 134 + 50 * i])[3:12] for i in range(k)]
        return np.array(T, float).reshape(-1, 3, 3)
    pts = [list(map(float, ln.split()[1:4])) for ln in raw.decode().splitlines() if ln.strip().startswith("vertex")]
    return np.array(pts).reshape(-1, 3, 3)


def weld(T, tol=1e-6):
    """STL stores loose triangles; merge equal vertices to recover the connectivity."""
    key = {}; F = []
    for tri in T:
        f = []
        for p in tri:
            k = tuple(np.round(p / tol).astype(np.int64))
            f.append(key.setdefault(k, len(key)))
        F.append(tuple(f))
    V = np.zeros((len(key), 3))
    for tri, f in zip(T, F):
        V[list(f)] = tri
    return V, np.array(F)


def check(F):
    """Watertight: every undirected edge used by exactly 2 faces. Consistently oriented: every directed edge used once."""
    und = Counter(tuple(sorted((f[i], f[(i + 1) % 3]))) for f in F for i in range(3))
    dirc = Counter((f[i], f[(i + 1) % 3]) for f in F for i in range(3))
    open_edges = [e for e, c in und.items() if c == 1]
    nonmanifold = [e for e, c in und.items() if c > 2]
    oriented = all(c == 1 for c in dirc.values())
    return open_edges, nonmanifold, oriented, len(und)


def volume(V, F):
    return np.einsum("ij,ij->i", V[F[:, 0]], np.cross(V[F[:, 1]], V[F[:, 2]])).sum() / 6


if __name__ == "__main__":
    # a watch-gear blank: radius 6 mm, 1.2 mm thick, as a 64-sided prism
    r, h, n = 6.0, 1.2, 64
    V, F = cylinder_mesh(r, h, n)
    op, nm, ori, E = check(F)
    print(f"blank: V = {len(V)}, E = {E}, F = {len(F)}, Euler V - E + F = {len(V) - E + len(F)}; open edges {len(op)}, oriented {ori}")
    assert not op and not nm and ori and len(V) - E + len(F) == 2
    vol = volume(V, F); exact_prism = 0.5 * n * r * r * math.sin(2 * math.pi / n) * h
    print(f"volume {vol:.6f} mm^3 = n-gon prism {exact_prism:.6f}; true cylinder {math.pi*r*r*h:.6f} ({100*(1-vol/(math.pi*r*r*h)):.3f}% short)")
    assert abs(vol - exact_prism) < 1e-9
    with tempfile.TemporaryDirectory() as tmp:
        for kind, writer in (("ascii", write_ascii_stl), ("binary", write_binary_stl)):
            path = os.path.join(tmp, f"blank_{kind}.stl")
            writer(path, V, F)
            V2, F2 = weld(read_stl(path))
            op2, _, ori2, _ = check(F2)
            print(f"{kind} STL: {os.path.getsize(path)} bytes, re-read {len(F2)} faces, {len(V2)} welded vertices, watertight {not op2}, volume {volume(V2, F2):.6f}")
            assert not op2 and ori2 and abs(volume(V2, F2) - vol) < 1e-5
        assert os.path.getsize(os.path.join(tmp, "blank_binary.stl")) == 84 + 50 * len(F)
    # break it: delete one side triangle -> 3 open edges and an undefined volume
    op3, _, _, _ = check(np.delete(F, 0, axis=0))
    print(f"one triangle deleted: {len(op3)} open edges {sorted((int(a), int(b)) for a, b in op3)}")
    assert len(op3) == 3
    # flip one triangle -> still closed, but orientation check fails
    Fb = F.copy(); Fb[5] = Fb[5][::-1]
    assert check(Fb)[0] == [] and check(Fb)[2] is False
