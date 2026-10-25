"""Plane stress Q4 and CST elements on a quarter plate with a circular hole under uniaxial tension: the hoop stress at the hole approaches about 3 times the applied stress as the mesh is refined."""
import math
import numpy as np


def D_matrix(E, nu, kind="stress"):
    if kind == "stress":
        return E / (1 - nu**2) * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    c = E / ((1 + nu) * (1 - 2 * nu))
    return c * np.array([[1 - nu, nu, 0], [nu, 1 - nu, 0], [0, 0, (1 - 2 * nu) / 2]])


def q4_B(X, xi, eta):
    dN = 0.25 * np.array([[-(1 - eta), (1 - eta), (1 + eta), -(1 + eta)], [-(1 - xi), -(1 + xi), (1 + xi), (1 - xi)]])
    J = dN @ X
    dNx = np.linalg.solve(J, dN)
    B = np.zeros((3, 8))
    B[0, 0::2] = dNx[0]; B[1, 1::2] = dNx[1]; B[2, 0::2] = dNx[1]; B[2, 1::2] = dNx[0]
    return B, np.linalg.det(J)


def q4_k(X, D, t=1.0):
    g = 1 / math.sqrt(3); k = np.zeros((8, 8))
    for a in (-g, g):
        for b in (-g, g):
            B, dJ = q4_B(X, a, b)
            k += B.T @ D @ B * dJ * t
    return k


def cst_B(X):
    (x1, y1), (x2, y2), (x3, y3) = X
    A2 = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
    b = np.array([y2 - y3, y3 - y1, y1 - y2]) / A2
    c = np.array([x3 - x2, x1 - x3, x2 - x1]) / A2
    B = np.zeros((3, 6)); B[0, 0::2] = b; B[1, 1::2] = c; B[2, 0::2] = c; B[2, 1::2] = b
    return B, A2 / 2


def quarter_mesh(n, a=1.0, w=10.0):
    """Mapped mesh: n rings x 2n spokes between the hole (radius a) and the square boundary (half-width w)."""
    th = np.linspace(0, math.pi / 2, 2 * n + 1)
    outer = []
    for t in th:   # point on the square boundary along angle t
        outer.append((w, w * math.tan(t)) if t <= math.pi / 4 else (w / math.tan(t) if t < math.pi / 2 else 0.0, w))
    outer = np.array(outer)
    s = np.linspace(0, 1, n + 1) ** 1.8          # grade the rings towards the hole
    nodes = []
    for r in s:
        for k, t in enumerate(th):
            inner = np.array([a * math.cos(t), a * math.sin(t)])
            nodes.append(inner + r * (outer[k] - inner))
    nodes = np.array(nodes); m = 2 * n + 1
    quads = [[i * m + k, (i + 1) * m + k, (i + 1) * m + k + 1, i * m + k + 1] for i in range(n) for k in range(2 * n)]
    return nodes, np.array(quads), m


def solve(n, element="Q4", E=210e3, nu=0.3, S=1.0, a=1.0, w=10.0):
    nodes, quads, m = quarter_mesh(n, a, w)
    D = D_matrix(E, nu)
    nd = len(nodes); K = np.zeros((2 * nd, 2 * nd)); F = np.zeros(2 * nd)
    elems = []
    for q in quads:
        if element == "Q4":
            elems.append(q)
        else:
            elems += [[q[0], q[1], q[2]], [q[0], q[2], q[3]]]
    for e in elems:
        X = nodes[e]
        if element == "Q4":
            k = q4_k(X, D)
        else:
            B, A = cst_B(X); k = B.T @ D @ B * A
        d = np.ravel([[2 * i, 2 * i + 1] for i in e])
        K[np.ix_(d, d)] += k
    # tension S in x on the edge x = w: consistent loads from edge segments
    edge = [i for i in range(nd) if abs(nodes[i, 0] - w) < 1e-9]
    edge.sort(key=lambda i: nodes[i, 1])
    for i, j in zip(edge[:-1], edge[1:]):
        h = nodes[j, 1] - nodes[i, 1]
        F[2 * i] += S * h / 2; F[2 * j] += S * h / 2
    fixed = [2 * i + 1 for i in range(nd) if abs(nodes[i, 1]) < 1e-9] + [2 * i for i in range(nd) if abs(nodes[i, 0]) < 1e-9]
    free = np.setdiff1d(np.arange(2 * nd), fixed)
    u = np.zeros(2 * nd); u[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])
    # sigma_x at the top of the hole (0, a): average of extrapolated stresses from elements touching that node
    top = m - 1                    # node at angle 90 degrees on the hole
    vals = []
    for e in elems:
        if top in e:
            X = nodes[e]; ue = u[np.ravel([[2 * i, 2 * i + 1] for i in e])]
            if element == "Q4":
                g = 1 / math.sqrt(3); pts = [(-g, -g), (g, -g), (g, g), (-g, g)]
                sg = np.array([D @ q4_B(X, *pt)[0] @ ue for pt in pts])
                # bilinear extrapolation from Gauss points to the corner nodes
                loc = list(e).index(top); cx, cy = [(-1, -1), (1, -1), (1, 1), (-1, 1)][loc]
                Ng = 0.25 * np.array([(1 + cx * math.sqrt(3) * s1) * (1 + cy * math.sqrt(3) * s2) for s1, s2 in [(-1, -1), (1, -1), (1, 1), (-1, 1)]])
                vals.append(Ng @ sg[:, 0])
            else:
                vals.append((D @ cst_B(X)[0] @ ue)[0])
    return np.mean(vals) / S, len(free)


if __name__ == "__main__":
    for kind in ("stress", "strain"):
        print(kind, D_matrix(210e3, 0.3, kind).round(1).tolist())
    # patch-style sanity: a single Q4 square under uniform strain gives D @ strain everywhere
    X = np.array([[0, 0], [2, 0], [2.5, 1.5], [0.3, 1.0]])
    eps = np.array([1e-3, -3e-4, 2e-4])
    ue = np.ravel([[eps[0] * x + eps[2] / 2 * y, eps[2] / 2 * x + eps[1] * y] for x, y in X])
    assert np.allclose(q4_B(X, 0.3, -0.7)[0] @ ue, eps)
    res = {}
    for el in ("CST", "Q4"):
        for n in (4, 8, 16, 32):
            kt, ndof = solve(n, el)
            res[(el, n)] = kt
            print(f"{el:3s} n = {n:2d} ({ndof} free dofs): sigma_x at the hole / applied = {kt:.4f}")
    ref = res[("Q4", 32)]
    # refinement: Q4 settles (16 to 32 changes < 0.2 %), CST climbs from below and is always further off
    assert res[("Q4", 4)] < res[("Q4", 8)] < res[("Q4", 16)] and abs(res[("Q4", 16)] - ref) < 0.002 * ref
    assert all(abs(res[("CST", n)] - ref) > abs(res[("Q4", n)] - ref) for n in (4, 8, 16))
    assert abs(ref - 3.0) < 0.1          # Kirsch (infinite plate) gives exactly 3
    big, _ = solve(32, "Q4", w=20.0)
    print(f"plate twice as wide and tall (hole diameter / width = 0.05): {big:.4f}, closer to the infinite-plate 3")
    assert abs(big - 3.0) < abs(ref - 3.0)
