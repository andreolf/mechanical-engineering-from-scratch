"""2D heat conduction FEM with Q4 elements: conductivity, capacity and convection matrices; steady and backward-Euler transient solves. Checked against the 1D slab (steady with generation, and the transient series), then applied to an aluminium heatsink with an energy balance."""
import math
import numpy as np

G2 = [(-1 / math.sqrt(3), -1 / math.sqrt(3)), (1 / math.sqrt(3), -1 / math.sqrt(3)), (1 / math.sqrt(3), 1 / math.sqrt(3)), (-1 / math.sqrt(3), 1 / math.sqrt(3))]


def q4_mats(X, k, rc, q):
    """Conductivity Ke, consistent capacity Me (rho c), generation load fe for one Q4."""
    Ke = np.zeros((4, 4)); Me = np.zeros((4, 4)); fe = np.zeros(4)
    for a, b in G2:
        N = 0.25 * np.array([(1 - a) * (1 - b), (1 + a) * (1 - b), (1 + a) * (1 + b), (1 - a) * (1 + b)])
        dN = 0.25 * np.array([[-(1 - b), (1 - b), (1 + b), -(1 + b)], [-(1 - a), -(1 + a), (1 + a), (1 - a)]])
        J = dN @ X; dNx = np.linalg.solve(J, dN); w = np.linalg.det(J)
        Ke += k * dNx.T @ dNx * w; Me += rc * np.outer(N, N) * w; fe += q * N * w
    return Ke, Me, fe


def grid_mesh(cells, h):
    ids = {}; nodes = []; quads = []
    for (i, j) in sorted(cells):
        c = []
        for key in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)):
            if key not in ids: ids[key] = len(nodes); nodes.append([key[0] * h, key[1] * h])
            c.append(ids[key])
        quads.append(c)
    return np.array(nodes), np.array(quads), ids


def boundary_edges(cells):
    """Edges of the cell union that belong to one cell only, as ((i0, j0), (i1, j1)) grid points."""
    cnt = {}
    for (i, j) in cells:
        for e in (((i, j), (i + 1, j)), ((i + 1, j), (i + 1, j + 1)), ((i, j + 1), (i + 1, j + 1)), ((i, j), (i, j + 1))):
            cnt[e] = cnt.get(e, 0) + 1
    return [e for e, c in cnt.items() if c == 1]


def assemble(nodes, quads, k, rc, q=0.0):
    n = len(nodes); K = np.zeros((n, n)); M = np.zeros((n, n)); F = np.zeros(n)
    for e in quads:
        Ke, Me, fe = q4_mats(nodes[e], k, rc, q)
        K[np.ix_(e, e)] += Ke; M[np.ix_(e, e)] += Me; F[e] += fe
    return K, M, F


def solve_fixed(K, F, fixed, vals):
    n = len(F); T = np.zeros(n); T[fixed] = vals; free = np.setdiff1d(np.arange(n), fixed)
    T[free] = np.linalg.solve(K[np.ix_(free, free)], F[free] - K[np.ix_(free, fixed)] @ T[fixed])
    return T


def slab_series(x, t, L, alpha, terms=200):
    """Slab 0 < x < L at 1, both faces dropped to 0 at t = 0."""
    s = 0.0
    for m in range(terms):
        lam = (2 * m + 1) * math.pi / L
        s += 4 / ((2 * m + 1) * math.pi) * math.sin(lam * x) * math.exp(-lam * lam * alpha * t)
    return s


if __name__ == "__main__":
    # 1) steady slab with uniform generation: 20 mm wall, k = 1.5, q = 1e5 W/m^3, faces at 20 C
    L, h, k, q = 0.02, 0.002, 1.5, 1e5
    cells = {(i, j) for i in range(10) for j in range(3)}
    nodes, quads, ids = grid_mesh(cells, h)
    K, M, F = assemble(nodes, quads, k, 1.0, q)
    faces = [i for i, (x, y) in enumerate(nodes) if x < 1e-12 or abs(x - L) < 1e-12]
    T = solve_fixed(K, F, faces, 20.0)
    ex = 20 + q * nodes[:, 0] * (L - nodes[:, 0]) / (2 * k)
    print(f"steady slab: centre {T[np.argmax(T)]:.6f} C, analytic {20 + q*L*L/(8*k):.6f} C; max nodal error {np.abs(T-ex).max():.1e}")
    assert np.abs(T - ex).max() < 1e-9
    # 2) transient slab: concrete-like alpha, sudden cooling of both faces, backward Euler
    rc, kk = 2.0e6, 1.6; alpha = kk / rc; L = 0.2; nx = 40; hh = L / nx
    nodes, quads, ids = grid_mesh({(i, 0) for i in range(nx)}, hh)
    K, M, _ = assemble(nodes, quads, kk, rc)
    faces = [i for i, (x, y) in enumerate(nodes) if x < 1e-12 or abs(x - L) < 1e-12]
    free = np.setdiff1d(np.arange(len(nodes)), faces)
    T = np.ones(len(nodes)); T[faces] = 0.0
    dt, tend = 60.0, 3 * 3600.0
    A = (M + dt * K)[np.ix_(free, free)]
    for _ in range(int(tend / dt)):
        T[free] = np.linalg.solve(A, M[np.ix_(free, free)] @ T[free])
    c = [i for i, (x, y) in enumerate(nodes) if abs(x - L / 2) < 1e-12]
    fe, se = T[c].mean(), slab_series(L / 2, tend, L, alpha)
    print(f"transient slab after 3 h: centre {fe:.5f} (FEM, dt = 60 s) vs series {se:.5f}")
    assert abs(fe - se) < 2e-3
    # 3) heatsink: 48 x 5 mm aluminium base, six 2 x 25 mm fins, 10 W chip under the middle 16 mm, 50 mm deep
    h = 0.001; base = {(i, j) for i in range(48) for j in range(5)}
    fins = {(i, j) for f in range(6) for i in (3 + 8 * f, 4 + 8 * f) for j in range(5, 30)}
    cells = base | fins
    nodes, quads, ids = grid_mesh(cells, h)
    kal, rcal, hconv, Tinf, depth, P = 200.0, 2.4e6, 25.0, 25.0, 0.05, 10.0
    K, M, F = assemble(nodes, quads, kal, rcal)
    flux = P / (0.016 * depth)          # W/m^2 into the chip footprint
    conv_len = 0.0
    for (a, b) in boundary_edges(cells):
        ia, ib = ids[a], ids[b]; le = h
        if a[1] == 0 and b[1] == 0:
            xm = (a[0] + b[0]) / 2 * h
            if 0.016 <= xm <= 0.032: F[[ia, ib]] += flux * le / 2
            continue                    # rest of the bottom is insulated
        K[np.ix_([ia, ib], [ia, ib])] += hconv * le / 6 * np.array([[2, 1], [1, 2]]); F[[ia, ib]] += hconv * Tinf * le / 2
        conv_len += le
    T = np.linalg.solve(K, F)
    # energy balance: convection out equals chip power in (per metre depth)
    out = 0.0
    for (a, b) in boundary_edges(cells):
        if a[1] == 0 and b[1] == 0: continue
        out += hconv * h * ((T[ids[a]] + T[ids[b]]) / 2 - Tinf)
    print(f"heatsink: {len(quads)} elements, wetted perimeter {conv_len*1000:.0f} mm; max {T.max():.2f} C, fin tips {min(T[ids[(3+8*f, 30)]] for f in range(6)):.2f} to {max(T[ids[(3+8*f, 30)]] for f in range(6)):.2f} C")
    print(f"energy balance: in {P/depth:.4f} W/m, out by convection {out:.4f} W/m")
    assert abs(out - P / depth) < 1e-8 * P / depth
    # lumped check: a perfectly conducting sink would sit at Tinf + P/(h A)
    print(f"lumped (infinitely conductive) estimate: {Tinf + P/(hconv*conv_len*depth):.2f} C")
    assert abs(T.mean() - (Tinf + P / (hconv * conv_len * depth))) < 1.0
