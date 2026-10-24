"""Lagrange multipliers by Newton's method on the stationarity system, checked by brute force."""
import math
import numpy as np


def solve_lagrange(grad_f, hess_f, g, grad_g, hess_g, x0, lam0=0.0, tol=1e-12):
    """Newton on F(x, lam) = [grad f - lam grad g, g] = 0."""
    z = np.append(np.asarray(x0, float), lam0)
    for _ in range(100):
        x, lam = z[:-1], z[-1]
        F = np.append(grad_f(x) - lam * grad_g(x), g(x))
        if np.linalg.norm(F) < tol:
            break
        n = len(x); J = np.zeros((n + 1, n + 1))
        J[:n, :n] = hess_f(x) - lam * hess_g(x)
        J[:n, n] = -grad_g(x); J[n, :n] = grad_g(x)
        z = z - np.linalg.solve(J, F)
    return z[:-1], z[-1]


if __name__ == "__main__":
    V = 1e-3
    A = lambda x: 2 * math.pi * x[0] ** 2 + 2 * math.pi * x[0] * x[1]
    gA = lambda x: np.array([4 * math.pi * x[0] + 2 * math.pi * x[1], 2 * math.pi * x[0]])
    hA = lambda x: np.array([[4 * math.pi, 2 * math.pi], [2 * math.pi, 0]])
    g = lambda x: math.pi * x[0] ** 2 * x[1] - V
    gg = lambda x: np.array([2 * math.pi * x[0] * x[1], math.pi * x[0] ** 2])
    hg = lambda x: np.array([[2 * math.pi * x[1], 2 * math.pi * x[0]], [2 * math.pi * x[0], 0]])
    (r, h), lam = solve_lagrange(gA, hA, g, gg, hg, [0.05, 0.1], 40.0)   # Newton needs a sensible start
    print(f"r = {r*1e3:.2f} mm, h = {h*1e3:.2f} mm, area = {A([r, h])*1e4:.1f} cm^2, lambda = {lam:.2f} 1/m")
    assert abs(h - 2 * r) < 1e-12 and abs(r - (V / (2 * math.pi)) ** (1 / 3)) < 1e-12 and abs(lam - 2 / r) < 1e-9
    # brute force: eliminate h with the constraint and scan r
    rs = np.linspace(0.02, 0.12, 200001)
    areas = 2 * math.pi * rs ** 2 + 2 * V / rs
    assert abs(rs[np.argmin(areas)] - r) < 1e-6
    # the multiplier is the shadow price dA*/dV
    Astar = lambda V: 6 * math.pi * (V / (2 * math.pi)) ** (2 / 3)
    dV = 1e-9
    assert abs((Astar(V + dV) - Astar(V - dV)) / (2 * dV) - lam) < 1e-4
    print("multiplier matches the sensitivity of the optimal area to the volume")
