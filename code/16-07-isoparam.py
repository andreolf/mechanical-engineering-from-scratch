"""Isoparametric Q4 mapping: shape functions, the Jacobian, 2x2 Gauss quadrature on a distorted quad, checked against the polygon (shoelace) formulas; detects an inverted element."""
import numpy as np

GP = np.array([-1, 1]) / np.sqrt(3.0)


def q4_shape(xi, eta):
    N = 0.25 * np.array([(1 - xi) * (1 - eta), (1 + xi) * (1 - eta), (1 + xi) * (1 + eta), (1 - xi) * (1 + eta)])
    dN = 0.25 * np.array([[-(1 - eta), (1 - eta), (1 + eta), -(1 + eta)],
                          [-(1 - xi), -(1 + xi), (1 + xi), (1 - xi)]])
    return N, dN


def jacobian(X, xi, eta):
    _, dN = q4_shape(xi, eta)
    return dN @ X            # rows: d/dxi, d/deta; cols: x, y


def integrate(X, f, gp=GP, w=None):
    w = np.ones(len(gp)) if w is None else w
    total = 0.0
    for a, wa in zip(gp, w):
        for b, wb in zip(gp, w):
            N, _ = q4_shape(a, b)
            x, y = N @ X
            total += f(x, y) * np.linalg.det(jacobian(X, a, b)) * wa * wb
    return total


def shoelace(X):
    x, y = X[:, 0], X[:, 1]
    xn, yn = np.roll(x, -1), np.roll(y, -1)
    cr = x * yn - xn * y
    A = cr.sum() / 2
    Sx = ((x + xn) * cr).sum() / 6          # integral of x dA
    Ixx = ((x**2 + x * xn + xn**2) * cr).sum() / 12   # integral of x^2 dA
    return A, Sx, Ixx


def min_detJ(X, n=21):
    s = np.linspace(-1, 1, n)
    return min(np.linalg.det(jacobian(X, a, b)) for a in s for b in s)


if __name__ == "__main__":
    X = np.array([[0.0, 0.0], [4.0, 0.5], [3.2, 3.0], [0.6, 2.2]])   # a distorted quad, corners counter-clockwise
    A, Sx, Ixx = shoelace(X)
    Ai = integrate(X, lambda x, y: 1.0)
    Si = integrate(X, lambda x, y: x)
    Ii = integrate(X, lambda x, y: x * x)
    print(f"area: Gauss {Ai:.10f}, shoelace {A:.10f}")
    print(f"integral of x: Gauss {Si:.10f}, polygon {Sx:.10f}; centroid x = {Si/Ai:.6f}")
    print(f"integral of x^2: Gauss {Ii:.10f}, polygon {Ixx:.10f}")
    assert abs(Ai - A) < 1e-12 and abs(Si - Sx) < 1e-12 and abs(Ii - Ixx) < 1e-11
    J0 = jacobian(X, 0, 0)
    print("J at the centre:", J0.round(4).tolist(), "det", round(np.linalg.det(J0), 6), "(= area/4: det J is linear in xi and eta for a Q4)")
    assert abs(np.linalg.det(J0) - A / 4) < 1e-12
    print(f"min det J over the element: {min_detJ(X):.4f}")
    assert min_detJ(X) > 0
    # pull corner 3 past the diagonal: the quad becomes non-convex and det J goes negative near that corner
    Xbad = X.copy(); Xbad[2] = [1.2, 0.9]
    m = min_detJ(Xbad)
    print(f"non-convex quad: min det J = {m:.4f} (negative: inverted region, the element is unusable)")
    assert m < 0
