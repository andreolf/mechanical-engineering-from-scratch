"""Finite differences for -u'' = f on [0, L]: the second-difference matrix, a heated rod, and O(h^2) convergence."""
import math
import numpy as np


def second_difference(n, h):
    """(n-1)x(n-1) matrix for -u'' at the interior nodes, Dirichlet ends: tridiag(-1, 2, -1) / h^2."""
    return (2 * np.eye(n - 1) - np.eye(n - 1, k=1) - np.eye(n - 1, k=-1)) / h**2


def solve_poisson(f, L, n, ua, ub):
    x = np.linspace(0, L, n + 1); h = L / n
    A = second_difference(n, h)
    b = f(x[1:-1]).astype(float)
    b[0] += ua / h**2; b[-1] += ub / h**2         # known boundary values move to the right-hand side
    u = np.empty(n + 1); u[0], u[-1] = ua, ub
    u[1:-1] = np.linalg.solve(A, b)
    return x, u


if __name__ == "__main__":
    # a 100 mm steel rod carrying current: q = 1 MW/m^3 generated, k = 50 W/(m K), both ends held at 20 C
    q, k, L = 1e6, 50.0, 0.1
    x, T = solve_poisson(lambda x: np.full_like(x, q / k), L, 10, 20.0, 20.0)
    T_exact = 20 + q / (2 * k) * x * (L - x)
    print(f"heated rod, 10 cells: centre {T[5]:.4f} C (exact {20 + q * L**2 / (8 * k):.4f} C)")
    assert np.max(np.abs(T - T_exact)) < 1e-10      # exact: the solution is quadratic, so the stencil has no error
    # convergence on u = sin(pi x): -u'' = pi^2 sin(pi x)
    errs = []
    for n in (10, 20, 40, 80):
        x, u = solve_poisson(lambda x: math.pi**2 * np.sin(math.pi * x), 1.0, n, 0.0, 0.0)
        errs.append(np.max(np.abs(u - np.sin(math.pi * x))))
    orders = [math.log2(a / b) for a, b in zip(errs, errs[1:])]
    print("max errors:", " ".join(f"{e:.2e}" for e in errs), " orders:", " ".join(f"{p:.3f}" for p in orders))
    assert all(abs(p - 2) < 0.02 for p in orders)
    # the matrix is symmetric positive definite with known eigenvalues (4/h^2) sin^2(k pi h / 2)
    n, h = 10, 0.1
    lam = np.sort(np.linalg.eigvalsh(second_difference(n, h)))
    assert np.allclose(lam, np.sort(4 / h**2 * np.sin(np.arange(1, n) * math.pi * h / 2) ** 2))
    print(f"smallest eigenvalue {lam[0]:.4f} vs pi^2 = {math.pi**2:.4f}")
