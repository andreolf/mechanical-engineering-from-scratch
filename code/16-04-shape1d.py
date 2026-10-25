"""1D finite elements with linear and quadratic Lagrange shape functions on the reference element; convergence study shows quadratic elements converge faster."""
import math
import numpy as np


def gauss(n):
    x, w = np.polynomial.legendre.leggauss(n)
    return x, w


def shape(order, xi):
    """Lagrange shape functions and their derivatives on xi in [-1, 1]."""
    if order == 1:
        N = np.array([(1 - xi) / 2, (1 + xi) / 2])
        dN = np.array([-0.5 + 0 * xi, 0.5 + 0 * xi])
    else:  # nodes at -1, 0, 1
        N = np.array([xi * (xi - 1) / 2, 1 - xi**2, xi * (xi + 1) / 2])
        dN = np.array([xi - 0.5, -2 * xi, xi + 0.5])
    return N, dN


def solve(order, ne, f, EA=1.0, L=1.0):
    """-(EA u')' = f on [0, L], u(0) = u(L) = 0."""
    nn = order * ne + 1
    x_nodes = np.linspace(0, L, nn)
    K = np.zeros((nn, nn)); F = np.zeros(nn)
    xg, wg = gauss(order + 2)
    for e in range(ne):
        dofs = np.arange(order * e, order * e + order + 1)
        a, b = x_nodes[dofs[0]], x_nodes[dofs[-1]]
        J = (b - a) / 2
        N, dN = shape(order, xg)
        x = a + (xg + 1) * J
        B = dN / J
        K[np.ix_(dofs, dofs)] += EA * (B * wg) @ B.T * J
        F[dofs] += (N * wg) @ f(x) * J
    u = np.zeros(nn)
    u[1:-1] = np.linalg.solve(K[1:-1, 1:-1], F[1:-1])
    return x_nodes, u


def l2_error(order, ne, x_nodes, u, exact, L=1.0):
    xg, wg = gauss(8)
    err = 0.0
    for e in range(ne):
        dofs = np.arange(order * e, order * e + order + 1)
        a, b = x_nodes[dofs[0]], x_nodes[dofs[-1]]
        J = (b - a) / 2
        N, _ = shape(order, xg)
        x = a + (xg + 1) * J
        err += np.sum(wg * (u[dofs] @ N - exact(x)) ** 2) * J
    return math.sqrt(err)


if __name__ == "__main__":
    f = lambda x: math.pi**2 * np.sin(math.pi * x)
    exact = lambda x: np.sin(math.pi * x)
    # partition of unity on the reference element
    for order in (1, 2):
        N, dN = shape(order, np.linspace(-1, 1, 7))
        assert np.allclose(N.sum(0), 1) and np.allclose(dN.sum(0), 0)
    rates = {}
    for order in (1, 2):
        errs, hs = [], []
        for ne in (4, 8, 16, 32):
            x, u = solve(order, ne, f)
            errs.append(l2_error(order, ne, x, u, exact)); hs.append(1 / ne)
        slope = np.polyfit(np.log(hs), np.log(errs), 1)[0]
        rates[order] = slope
        print(f"order {order}: L2 errors {['%.3e' % e for e in errs]}, convergence rate {slope:.3f}")
    assert abs(rates[1] - 2) < 0.1 and abs(rates[2] - 3) < 0.15 and rates[2] > rates[1]
    # same number of unknowns (17 nodes): quadratic is far more accurate
    x1, u1 = solve(1, 16, f); x2, u2 = solve(2, 8, f)
    e1, e2 = l2_error(1, 16, x1, u1, exact), l2_error(2, 8, x2, u2, exact)
    print(f"17 nodes each: linear error {e1:.3e}, quadratic error {e2:.3e} ({e1/e2:.1f} times smaller)")
    assert e2 < e1
