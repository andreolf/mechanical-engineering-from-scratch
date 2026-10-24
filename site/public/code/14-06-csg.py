"""Constructive solid geometry with signed distance functions: booleans as min and max, Monte Carlo volume against inclusion-exclusion, and a mesh by marching tetrahedra."""
import math
import numpy as np


def sphere(c, r):
    c = np.asarray(c, float)
    return lambda p: np.linalg.norm(p - c, axis=-1) - r


def box(c, half):
    c, h = np.asarray(c, float), np.asarray(half, float)
    def f(p):
        q = np.abs(p - c) - h
        return np.linalg.norm(np.maximum(q, 0), axis=-1) + np.minimum(q.max(axis=-1), 0)
    return f


def cylinder_z(c, r, half_h):
    c = np.asarray(c, float)
    def f(p):
        d = np.stack([np.hypot(p[..., 0] - c[0], p[..., 1] - c[1]) - r, np.abs(p[..., 2] - c[2]) - half_h], axis=-1)
        return np.linalg.norm(np.maximum(d, 0), axis=-1) + np.minimum(d.max(axis=-1), 0)
    return f


union = lambda a, b: (lambda p: np.minimum(a(p), b(p)))
intersect = lambda a, b: (lambda p: np.maximum(a(p), b(p)))
cut = lambda a, b: (lambda p: np.maximum(a(p), -b(p)))


def mc_volume(f, lo, hi, n=2_000_000, seed=3):
    rng = np.random.default_rng(seed)
    lo, hi = np.asarray(lo, float), np.asarray(hi, float)
    p = rng.uniform(lo, hi, (n, 3))
    frac = np.mean(f(p) < 0)
    V = np.prod(hi - lo)
    return frac * V, V * math.sqrt(frac * (1 - frac) / n)


# split each cube into 6 tetrahedra sharing the main diagonal 0-6
CUBE = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]])
TETS = [(0, 5, 1, 6), (0, 1, 2, 6), (0, 2, 3, 6), (0, 3, 7, 6), (0, 7, 4, 6), (0, 4, 5, 6)]


def marching_tetrahedra(f, lo, hi, n):
    """Triangles of the surface f = 0, each oriented with its normal pointing out (towards f > 0)."""
    lo, hi = np.asarray(lo, float), np.asarray(hi, float); h = (hi - lo) / n
    idx = np.stack(np.meshgrid(*[np.arange(n + 1)] * 3, indexing="ij"), -1).reshape(-1, 3)
    P = lo + idx * h
    F = f(P).reshape(n + 1, n + 1, n + 1)
    tris = []
    cells = np.stack(np.meshgrid(*[np.arange(n)] * 3, indexing="ij"), -1).reshape(-1, 3)
    corner_vals = np.stack([F[cells[:, 0] + o[0], cells[:, 1] + o[1], cells[:, 2] + o[2]] for o in CUBE], 1)
    mixed = cells[(corner_vals.min(1) < 0) & (corner_vals.max(1) >= 0)]
    for cell in mixed:
        cp = lo + (cell + CUBE) * h
        cv = F[cell[0] + CUBE[:, 0], cell[1] + CUBE[:, 1], cell[2] + CUBE[:, 2]]
        for t in TETS:
            v, x = cv[list(t)], cp[list(t)]
            ins = [i for i in range(4) if v[i] < 0]; out = [i for i in range(4) if v[i] >= 0]
            if len(ins) in (0, 4): continue
            cross = lambda i, j: x[i] + (x[j] - x[i]) * (v[i] / (v[i] - v[j]))
            if len(ins) == 1:
                polys = [[cross(ins[0], o) for o in out]]
            elif len(ins) == 3:
                polys = [[cross(i, out[0]) for i in ins]]
            else:
                a, b = ins; c, d = out
                q = [cross(a, c), cross(a, d), cross(b, d), cross(b, c)]
                polys = [[q[0], q[1], q[2]], [q[0], q[2], q[3]]]
            centre_in = x[ins].mean(0)
            for tri in polys:
                tri = np.array(tri)
                nrm = np.cross(tri[1] - tri[0], tri[2] - tri[0])
                if nrm @ (tri.mean(0) - centre_in) < 0: tri = tri[[0, 2, 1]]   # point the normal away from the inside corners
                tris.append(tri)
    return np.array(tris)


def mesh_volume(T):
    """Divergence theorem: sum of signed tetrahedra from the origin."""
    return np.einsum("ij,ij->i", T[:, 0], np.cross(T[:, 1], T[:, 2])).sum() / 6


if __name__ == "__main__":
    # two spheres of radius 20 mm, centres 24 mm apart
    r, d = 20.0, 24.0
    A, B = sphere((0, 0, 0), r), sphere((d, 0, 0), r)
    lens = math.pi * (4 * r + d) * (2 * r - d) ** 2 / 12          # intersection volume of two equal spheres
    exact = 2 * 4 / 3 * math.pi * r ** 3 - lens                   # inclusion-exclusion
    v, se = mc_volume(union(A, B), (-21, -21, -21), (45, 21, 21))
    print(f"union of spheres: Monte Carlo {v:.1f} +- {se:.1f} mm^3, inclusion-exclusion {exact:.1f} mm^3 (lens {lens:.1f})")
    assert abs(v - exact) < 4 * se
    vi, sei = mc_volume(intersect(A, B), (-21, -21, -21), (45, 21, 21))
    assert abs(vi - lens) < 4 * sei
    T = marching_tetrahedra(union(A, B), (-22, -22, -22), (46, 22, 22), 48)
    vm = mesh_volume(T)
    print(f"marching tetrahedra (48 cells across): {len(T)} triangles, mesh volume {vm:.1f} mm^3, {100*(vm/exact-1):+.2f}% from exact")
    assert abs(vm / exact - 1) < 0.01
    # a bearing housing: a 60 x 40 x 30 block, minus a 26 mm bore, plus a 40 mm boss on top
    housing = cut(union(box((0, 0, 0), (30, 20, 15)), cylinder_z((0, 0, 20), 20, 5)), cylinder_z((0, 0, 0), 13, 40))
    exact_h = 60 * 40 * 30 + math.pi * 20 ** 2 * 10 - math.pi * 13 ** 2 * 40
    vh, seh = mc_volume(housing, (-31, -21, -16), (31, 21, 26))
    Th = marching_tetrahedra(housing, (-32, -22, -17), (32, 22, 27), 64)
    print(f"bearing housing: exact {exact_h:.1f} mm^3, Monte Carlo {vh:.1f} +- {seh:.1f}, mesh {mesh_volume(Th):.1f} ({len(Th)} triangles)")
    assert abs(vh - exact_h) < 4 * seh and abs(mesh_volume(Th) / exact_h - 1) < 0.02
