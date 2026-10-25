"""3D linear tetrahedra (Tet4) from scratch: element stiffness, a uniform-tension patch test, convergence on a steel cantilever, and an L-shaped bracket with von Mises stress; sparse COO/CSR assembly with Jacobi-CG; mesh written as legacy VTK text (what meshio would read or write)."""
import math
import numpy as np


def D3(E, nu):
    l = E * nu / ((1 + nu) * (1 - 2 * nu)); m = E / (2 * (1 + nu))
    D = np.zeros((6, 6)); D[:3, :3] = l; D[np.arange(3), np.arange(3)] += 2 * m; D[np.arange(3, 6), np.arange(3, 6)] = m
    return D


def tet_B(X):
    """Strain order [ex, ey, ez, gxy, gyz, gzx]; returns B (6 x 12) and the volume."""
    M = np.hstack([np.ones((4, 1)), X]); V = np.linalg.det(M) / 6
    G = np.linalg.inv(M)[1:]            # rows: d/dx, d/dy, d/dz of the 4 barycentric shape functions
    B = np.zeros((6, 12))
    for a in range(4):
        bx, by, bz = G[:, a]
        B[:, 3 * a:3 * a + 3] = [[bx, 0, 0], [0, by, 0], [0, 0, bz], [by, bx, 0], [0, bz, by], [bz, 0, bx]]
    return B, V


KUHN = [(0, 1, 2, 6), (0, 2, 3, 6), (0, 3, 7, 6), (0, 7, 4, 6), (0, 4, 5, 6), (0, 5, 1, 6)]   # conforming 6-tet split of a hex


def box_mesh(cells, h):
    """cells: set of (i, j, k) unit cubes of size h. Returns nodes and positively oriented tets."""
    ids = {}; nodes = []; tets = []
    corner = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]
    for (i, j, k) in sorted(cells):
        c = []
        for (a, b, d) in corner:
            key = (i + a, j + b, k + d)
            if key not in ids: ids[key] = len(nodes); nodes.append([h * key[0], h * key[1], h * key[2]])
            c.append(ids[key])
        for t in KUHN:
            tt = [c[q] for q in t]
            tets.append(tt)
    nodes = np.array(nodes, float); tets = np.array(tets)
    for n_, t in enumerate(tets):
        if tet_B(nodes[t])[1] < 0: tets[n_] = t[[0, 2, 1, 3]]
    return nodes, tets


def assemble(nodes, tets, D):
    r, c, v = [], [], []
    for t in tets:
        B, V = tet_B(nodes[t]); k = B.T @ D @ B * V
        d = np.ravel([[3 * a, 3 * a + 1, 3 * a + 2] for a in t])
        r.append(np.repeat(d, 12)); c.append(np.tile(d, 12)); v.append(k.ravel())
    return np.concatenate(r), np.concatenate(c), np.concatenate(v)


def solve_sparse(r, c, v, F, fixed, tol=1e-10):
    n = len(F); free = np.ones(n, bool); free[fixed] = False
    new = -np.ones(n, int); new[free] = np.arange(free.sum())
    keep = free[r] & free[c]; rr, cc, vv = new[r[keep]], new[c[keep]], v[keep]
    order = np.lexsort((cc, rr)); rr, cc, vv = rr[order], cc[order], vv[order]
    first = np.ones(len(rr), bool); first[1:] = (rr[1:] != rr[:-1]) | (cc[1:] != cc[:-1]); s = np.flatnonzero(first)
    data, rows, cols = np.add.reduceat(vv, s), rr[s], cc[s]
    m = free.sum(); b = F[free]; diag = np.bincount(rows, weights=data * (rows == cols), minlength=m)
    mv = lambda x: np.bincount(rows, weights=data * x[cols], minlength=m)
    x = np.zeros(m); res = b.copy(); z = res / diag; p = z.copy(); rz = res @ z
    for it in range(20000):
        Ap = mv(p); a = rz / (p @ Ap); x += a * p; res -= a * Ap
        if np.linalg.norm(res) < tol * np.linalg.norm(b): break
        z = res / diag; rz2 = res @ z; p = z + rz2 / rz * p; rz = rz2
    u = np.zeros(n); u[free] = x; return u, it + 1


def von_mises(s):
    sx, sy, sz, txy, tyz, tzx = s
    return math.sqrt(0.5 * ((sx - sy)**2 + (sy - sz)**2 + (sz - sx)**2) + 3 * (txy**2 + tyz**2 + tzx**2))


def to_vtk(nodes, tets, cell_values):
    lines = ["# vtk DataFile Version 3.0", "tet mesh", "ASCII", "DATASET UNSTRUCTURED_GRID", f"POINTS {len(nodes)} double"]
    lines += [" ".join(f"{q:.6g}" for q in p) for p in nodes]
    lines += [f"CELLS {len(tets)} {5*len(tets)}"] + [f"4 {' '.join(map(str, t))}" for t in tets]
    lines += [f"CELL_TYPES {len(tets)}"] + ["10"] * len(tets)
    lines += [f"CELL_DATA {len(tets)}", "SCALARS von_mises double 1", "LOOKUP_TABLE default"] + [f"{q:.6g}" for q in cell_values]
    return "\n".join(lines)


E, NU = 210e3, 0.3          # MPa, so lengths in mm and forces in N


if __name__ == "__main__":
    D = D3(E, NU)
    B, V = tet_B(np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1.0]]))
    k = B.T @ D @ B * V
    w = np.linalg.eigvalsh(k)
    print(f"unit tet: volume {V:.6f}, zero-energy modes {np.sum(w < 1e-9*w.max())} (6 rigid-body motions in 3D)")
    assert abs(V - 1 / 6) < 1e-15 and np.sum(w < 1e-9 * w.max()) == 6
    # patch test: a 3 x 2 x 2 block, uniform tension 50 MPa on x = max, minimal supports
    nodes, tets = box_mesh({(i, j, k) for i in range(3) for j in range(2) for k in range(2)}, 10.0)
    n = len(nodes); F = np.zeros(3 * n); S = 50.0
    for t in tets:      # consistent traction: each boundary triangle on x = 30 gives a third of its force to each node
        for face in ([0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]):
            f = t[face]
            if np.all(abs(nodes[f, 0] - 30) < 1e-9):
                a = 0.5 * np.linalg.norm(np.cross(nodes[f[1]] - nodes[f[0]], nodes[f[2]] - nodes[f[0]]))
                F[3 * f] += S * a / 3
    x0 = np.flatnonzero(abs(nodes[:, 0]) < 1e-9)
    fixed = list(3 * x0)                                           # u = 0 on x = 0
    o = int(np.flatnonzero((abs(nodes) < 1e-9).all(1))[0]); fixed += [3 * o + 1, 3 * o + 2]
    yz = int(np.flatnonzero((abs(nodes[:, 0]) < 1e-9) & (abs(nodes[:, 1] - 20) < 1e-9) & (abs(nodes[:, 2]) < 1e-9))[0]); fixed += [3 * yz + 2]
    u, it = solve_sparse(*assemble(nodes, tets, D), F, fixed, tol=1e-14)
    St = np.array([D @ tet_B(nodes[t])[0] @ u[np.ravel([[3 * a, 3 * a + 1, 3 * a + 2] for a in t])] for t in tets])
    print(f"patch test, {len(tets)} tets: sigma_x from {St[:,0].min():.10f} to {St[:,0].max():.10f} MPa, other components below {np.abs(St[:,1:]).max():.1e}")
    assert np.allclose(St[:, 0], S, atol=1e-8) and np.abs(St[:, 1:]).max() < 1e-8
    assert abs(u[3 * int(np.argmax(nodes[:, 0]))] - S / E * 30) < 1e-12
    # convergence: 100 x 20 x 20 mm steel cantilever, 1 kN tip load spread over the end face
    P, L, b = 1000.0, 100.0, 20.0; I = b**4 / 12; G = E / (2 * (1 + NU))
    timo = P * L**3 / (3 * E * I) + P * L / (5 / 6 * G * b * b)
    print(f"beam theory tip deflection {timo*1000:.3f} um")
    prev = 0
    for h in (10.0, 5.0, 2.5):
        m = int(round(20 / h)); nodes, tets = box_mesh({(i, j, k) for i in range(int(L / h)) for j in range(m) for k in range(m)}, h)
        n = len(nodes); F = np.zeros(3 * n); tip = np.flatnonzero(abs(nodes[:, 0] - L) < 1e-9); F[3 * tip + 2] = -P / len(tip)
        fixed = np.ravel([[3 * a, 3 * a + 1, 3 * a + 2] for a in np.flatnonzero(abs(nodes[:, 0]) < 1e-9)])
        u, it = solve_sparse(*assemble(nodes, tets, D), F, fixed)
        d = -u[3 * tip + 2].mean()
        print(f"h = {h:4.1f} mm: {len(tets):5d} tets, {3*n:5d} dofs, CG {it:4d} iterations; tip {d*1000:.3f} um = {d/timo*100:.1f} % of beam theory")
        assert d > prev; prev = d
    assert 0.85 < prev / timo < 1.02
    # L bracket: arm 80 x 20 x 20 on a 20 x 20 x 60 leg, the back face (x = 0) bolted, 1 kN down at the arm tip
    I = 20.0**4 / 12; nominal = P * 60 * 10 / I    # beam bending stress in the arm at x = 20, where it leaves the leg
    prev = (0, 0)
    for h in (10.0, 5.0, 2.5):
        m = int(20 / h)
        cells = {(i, j, k) for i in range(int(80 / h)) for j in range(m) for k in range(int(40 / h), int(60 / h))} | {(i, j, k) for i in range(m) for j in range(m) for k in range(int(60 / h))}
        nodes, tets = box_mesh(cells, h); n = len(nodes)
        F = np.zeros(3 * n); tip = np.flatnonzero(abs(nodes[:, 0] - 80) < 1e-9); F[3 * tip + 2] = -P / len(tip)
        fixed = np.ravel([[3 * a, 3 * a + 1, 3 * a + 2] for a in np.flatnonzero(abs(nodes[:, 0]) < 1e-9)])
        u, it = solve_sparse(*assemble(nodes, tets, D), F, fixed)
        vm = np.array([von_mises(D @ tet_B(nodes[t])[0] @ u[np.ravel([[3 * a, 3 * a + 1, 3 * a + 2] for a in t])]) for t in tets])
        cen = nodes[tets].mean(1); worst = cen[np.argmax(vm)]; d = -u[3 * tip + 2].mean()
        print(f"bracket h = {h:4.1f}: {len(tets):5d} tets, tip {d*1000:.2f} um; max von Mises {vm.max():.2f} MPa at ({worst[0]:.1f}, {worst[1]:.1f}, {worst[2]:.1f}) mm")
        assert 15 < worst[0] < 26 and 34 < worst[2] < 46     # at the re-entrant corner (x = 20, z = 40)
        assert d > prev[0] and vm.max() > prev[1]; prev = (d, vm.max())
    print(f"beam-theory bending stress where the arm leaves the leg: {nominal:.2f} MPa; the corner peak keeps rising (a sharp corner is a singularity)")
    vtk = to_vtk(nodes, tets, vm)
    print(f"VTK text: {len(vtk.splitlines())} lines; first: {vtk.splitlines()[0]!r}")
    ls = vtk.splitlines(); k = ls.index(f"CELL_TYPES {len(tets)}")
    assert all(q == "10" for q in ls[k + 1:k + 1 + len(tets)]) and len(ls) == 5 + n + 1 + 2 * len(tets) + 1 + 3 + len(tets)
