"""2D Poisson on a square: Jacobi, Gauss-Seidel and SOR with the optimal relaxation factor."""
import math
import numpy as np


def residual(u, f, h):
    r = np.zeros_like(u)
    r[1:-1, 1:-1] = f[1:-1, 1:-1] + (u[2:, 1:-1] + u[:-2, 1:-1] + u[1:-1, 2:] + u[1:-1, :-2] - 4 * u[1:-1, 1:-1]) / h**2
    return r


def solve(method, n, f, tol=1e-8, omega=1.0, maxit=100_000):
    """-lap u = f on the unit square, u = 0 on the boundary; returns the iteration count to reach a relative residual tol."""
    h = 1.0 / n; u = np.zeros((n + 1, n + 1)); r0 = np.linalg.norm(f[1:-1, 1:-1])
    for it in range(1, maxit + 1):
        if method == "jacobi":
            u[1:-1, 1:-1] = 0.25 * (u[2:, 1:-1] + u[:-2, 1:-1] + u[1:-1, 2:] + u[1:-1, :-2] + h * h * f[1:-1, 1:-1])
        else:                                      # Gauss-Seidel / SOR in red-black order, so each half-sweep vectorises
            for colour in (0, 1):
                m = np.zeros_like(u, bool); ii, jj = np.meshgrid(np.arange(n + 1), np.arange(n + 1), indexing="ij")
                m[1:-1, 1:-1] = ((ii + jj) % 2 == colour)[1:-1, 1:-1]
                gs = np.zeros_like(u)
                gs[1:-1, 1:-1] = 0.25 * (u[2:, 1:-1] + u[:-2, 1:-1] + u[1:-1, 2:] + u[1:-1, :-2] + h * h * f[1:-1, 1:-1])
                u[m] = (1 - omega) * u[m] + omega * gs[m]
        if np.linalg.norm(residual(u, f, h)[1:-1, 1:-1]) < tol * r0:
            return u, it
    raise RuntimeError("no convergence")


if __name__ == "__main__":
    n = 32
    x = np.linspace(0, 1, n + 1); X, Y = np.meshgrid(x, x, indexing="ij")
    f = 2 * math.pi**2 * np.sin(math.pi * X) * np.sin(math.pi * Y)     # exact u = sin(pi x) sin(pi y)
    omega_opt = 2 / (1 + math.sin(math.pi / n))
    print(f"n = {n}: optimal omega = 2 / (1 + sin(pi h)) = {omega_opt:.4f}")
    its = {}
    for name, meth, om in (("Jacobi", "jacobi", 1.0), ("Gauss-Seidel", "sor", 1.0), ("SOR (optimal)", "sor", omega_opt)):
        u, its[name] = solve(meth, n, f, omega=om)
        err = np.max(np.abs(u - np.sin(math.pi * X) * np.sin(math.pi * Y)))
        print(f"{name:14s}: {its[name]:5d} iterations, max error vs exact {err:.2e}")
    assert its["SOR (optimal)"] * 10 < its["Gauss-Seidel"]
    assert 1.7 < its["Jacobi"] / its["Gauss-Seidel"] < 2.3          # Gauss-Seidel is twice as fast as Jacobi
    # spectral radius of Jacobi: cos(pi h); iterations ~ ln(tol) / ln(rho)
    rho = math.cos(math.pi / n)
    print(f"Jacobi spectral radius cos(pi h) = {rho:.5f}: predicted about {math.log(1e-8) / math.log(rho):.0f} iterations")
    assert abs(its["Jacobi"] - math.log(1e-8) / math.log(rho)) < 5
