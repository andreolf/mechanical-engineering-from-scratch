"""Patch test (MacNeal-Harder five-element patch, Q4 and CST) and a convergence study (Q4 on -lap u = f with a known solution). Written as pytest test functions; running the file calls them too."""
import math
import numpy as np


def D_ps(E, nu):
    return E / (1 - nu**2) * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])


def q4_B(X, xi, eta, shortcut=False):
    dN = 0.25 * np.array([[-(1 - eta), (1 - eta), (1 + eta), -(1 + eta)], [-(1 - xi), -(1 + xi), (1 + xi), (1 - xi)]])
    J = dN @ X; dNx = np.linalg.solve(J, dN)
    if shortcut:   # a classic bug: treat every element as a rectangle of its bounding-box size
        w, h = np.ptp(X[:, 0]), np.ptp(X[:, 1]); dNx = dN * np.array([[2 / w], [2 / h]])
    B = np.zeros((3, 8)); B[0, 0::2] = dNx[0]; B[1, 1::2] = dNx[1]; B[2, 0::2] = dNx[1]; B[2, 1::2] = dNx[0]
    return B, np.linalg.det(J)


def cst_B(X):
    (x1, y1), (x2, y2), (x3, y3) = X
    A2 = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
    b = np.array([y2 - y3, y3 - y1, y1 - y2]) / A2; c = np.array([x3 - x2, x1 - x3, x2 - x1]) / A2
    B = np.zeros((3, 6)); B[0, 0::2] = b; B[1, 1::2] = c; B[2, 0::2] = c; B[2, 1::2] = b
    return B, A2 / 2


GP = [(-1 / math.sqrt(3), -1 / math.sqrt(3)), (1 / math.sqrt(3), -1 / math.sqrt(3)), (1 / math.sqrt(3), 1 / math.sqrt(3)), (-1 / math.sqrt(3), 1 / math.sqrt(3))]

# MacNeal-Harder patch: 0.24 x 0.12 rectangle, four distorted interior nodes
NODES = np.array([[0, 0], [0.24, 0], [0.24, 0.12], [0, 0.12], [0.04, 0.02], [0.18, 0.03], [0.16, 0.08], [0.08, 0.08]])
QUADS = [[0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7]]
E, NU, T = 1.0e6, 0.25, 0.001


def exact(x, y):
    return 1e-3 * (x + y / 2), 1e-3 * (y + x / 2)


def patch(element, shortcut=False):
    D = D_ps(E, NU); n = len(NODES); K = np.zeros((2 * n, 2 * n))
    elems = QUADS if element == "Q4" else [t for q in QUADS for t in ([q[0], q[1], q[2]], [q[0], q[2], q[3]])]
    for e in elems:
        X = NODES[e]; d = np.ravel([[2 * i, 2 * i + 1] for i in e])
        if element == "Q4":
            k = sum(q4_B(X, *g, shortcut)[0].T @ D @ q4_B(X, *g, shortcut)[0] * q4_B(X, *g)[1] * T for g in GP)
        else:
            B, A = cst_B(X); k = B.T @ D @ B * A * T
        K[np.ix_(d, d)] += k
    u = np.zeros(2 * n); bnd = [0, 1, 2, 3]
    for i in bnd:
        u[2 * i], u[2 * i + 1] = exact(*NODES[i])
    fixed = np.ravel([[2 * i, 2 * i + 1] for i in bnd]); free = np.setdiff1d(np.arange(2 * n), fixed)
    u[free] = np.linalg.solve(K[np.ix_(free, free)], -K[np.ix_(free, fixed)] @ u[fixed])
    err_u = max(abs(u[2 * i] - exact(*NODES[i])[0]) + abs(u[2 * i + 1] - exact(*NODES[i])[1]) for i in range(4, 8))
    stresses = []
    for e in elems:
        ue = u[np.ravel([[2 * i, 2 * i + 1] for i in e])]
        pts = GP if element == "Q4" else [None]
        for g in pts:
            B = q4_B(NODES[e], *g, shortcut)[0] if element == "Q4" else cst_B(NODES[e])[0]
            stresses.append(D @ B @ ue)
    return err_u, np.array(stresses)


def poisson_q4(n):
    """-lap u = 2 pi^2 sin(pi x) sin(pi y) on the unit square, u = 0 on the edges; returns the L2 and energy-norm errors."""
    h = 1 / n; xs = np.linspace(0, 1, n + 1)
    idx = np.arange((n + 1) ** 2).reshape(n + 1, n + 1)
    K = np.zeros(((n + 1) ** 2,) * 2); F = np.zeros((n + 1) ** 2)
    g3 = np.polynomial.legendre.leggauss(3)
    for j in range(n):
        for i in range(n):
            e = [idx[j, i], idx[j, i + 1], idx[j + 1, i + 1], idx[j + 1, i]]
            X = np.array([[xs[i], xs[j]], [xs[i + 1], xs[j]], [xs[i + 1], xs[j + 1]], [xs[i], xs[j + 1]]])
            for a, wa in zip(*g3):
                for b, wb in zip(*g3):
                    N = 0.25 * np.array([(1 - a) * (1 - b), (1 + a) * (1 - b), (1 + a) * (1 + b), (1 - a) * (1 + b)])
                    dN = 0.25 * np.array([[-(1 - b), (1 - b), (1 + b), -(1 + b)], [-(1 - a), -(1 + a), (1 + a), (1 - a)]])
                    J = dN @ X; dNx = np.linalg.solve(J, dN); w = wa * wb * np.linalg.det(J)
                    x, y = N @ X
                    K[np.ix_(e, e)] += dNx.T @ dNx * w
                    F[e] += N * 2 * math.pi**2 * math.sin(math.pi * x) * math.sin(math.pi * y) * w
    bnd = np.unique(np.concatenate([idx[0], idx[-1], idx[:, 0], idx[:, -1]]))
    free = np.setdiff1d(np.arange(len(F)), bnd); u = np.zeros(len(F))
    u[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])
    eL2 = eH1 = 0.0
    for j in range(n):
        for i in range(n):
            e = [idx[j, i], idx[j, i + 1], idx[j + 1, i + 1], idx[j + 1, i]]
            X = np.array([[xs[i], xs[j]], [xs[i + 1], xs[j]], [xs[i + 1], xs[j + 1]], [xs[i], xs[j + 1]]])
            for a, wa in zip(*g3):
                for b, wb in zip(*g3):
                    N = 0.25 * np.array([(1 - a) * (1 - b), (1 + a) * (1 - b), (1 + a) * (1 + b), (1 - a) * (1 + b)])
                    dN = 0.25 * np.array([[-(1 - b), (1 - b), (1 + b), -(1 + b)], [-(1 - a), -(1 + a), (1 + a), (1 - a)]])
                    J = dN @ X; dNx = np.linalg.solve(J, dN); w = wa * wb * np.linalg.det(J); x, y = N @ X
                    s, c = math.sin, math.cos; p = math.pi
                    ex = s(p * x) * s(p * y); gx, gy = p * c(p * x) * s(p * y), p * s(p * x) * c(p * y)
                    eL2 += (N @ u[e] - ex) ** 2 * w
                    g = dNx @ u[e]; eH1 += ((g[0] - gx) ** 2 + (g[1] - gy) ** 2) * w
    return math.sqrt(eL2), math.sqrt(eH1)


def test_patch_q4():
    err, S = patch("Q4")
    assert err < 1e-15 and np.max(np.abs(S - [1333.3333333333333, 1333.3333333333333, 400.0])) < 1e-9


def test_patch_cst():
    err, S = patch("CST")
    assert err < 1e-15 and np.max(np.abs(S - [1333.3333333333333, 1333.3333333333333, 400.0])) < 1e-9


def test_patch_catches_shortcut():
    err, S = patch("Q4", shortcut=True)
    assert err > 1e-6


def test_convergence_rates():
    hs = [4, 8, 16, 32]; E2 = np.array([poisson_q4(n) for n in hs])
    rL2 = np.polyfit(np.log(1 / np.array(hs)), np.log(E2[:, 0]), 1)[0]
    rH1 = np.polyfit(np.log(1 / np.array(hs)), np.log(E2[:, 1]), 1)[0]
    assert abs(rL2 - 2) < 0.1 and abs(rH1 - 1) < 0.1
    return hs, E2, rL2, rH1


if __name__ == "__main__":
    for el in ("Q4", "CST"):
        err, S = patch(el)
        print(f"{el} patch: interior displacement error {err:.1e}; stresses at all points: sx {S[:,0].min():.10f}..{S[:,0].max():.10f}, txy {S[:,2].min():.10f}..{S[:,2].max():.10f}")
    test_patch_q4(); test_patch_cst(); test_patch_catches_shortcut()
    err, S = patch("Q4", shortcut=True)
    print(f"Q4 with the rectangle shortcut: interior error {err:.3e}, sx from {S[:,0].min():.1f} to {S[:,0].max():.1f}: patch test FAILS, as it should")
    hs, E2, rL2, rH1 = test_convergence_rates()
    for n, (a, b) in zip(hs, E2):
        print(f"n = {n:2d}: L2 error {a:.4e}, energy (H1 seminorm) error {b:.4e}")
    print(f"fitted rates: L2 {rL2:.3f} (theory 2), energy {rH1:.3f} (theory 1)")
