"""Jacobi, Gauss-Seidel, SOR and conjugate gradients on the 1D Poisson problem."""
import math
import numpy as np


def poisson1d(n):
    return 2 * np.eye(n) - np.eye(n, k=1) - np.eye(n, k=-1)


def sor(A, b, omega=1.0, tol=1e-8, max_iter=100000):
    """omega = 1 is Gauss-Seidel."""
    x = np.zeros_like(b); r0 = np.linalg.norm(b)
    for k in range(1, max_iter + 1):
        for i in range(len(b)):
            gs = (b[i] - A[i, :i] @ x[:i] - A[i, i + 1:] @ x[i + 1:]) / A[i, i]
            x[i] += omega * (gs - x[i])
        if np.linalg.norm(b - A @ x) < tol * r0:
            return x, k
    return x, max_iter


def jacobi(A, b, tol=1e-8, max_iter=100000):
    x = np.zeros_like(b); d = np.diag(A); R = A - np.diag(d); r0 = np.linalg.norm(b)
    for k in range(1, max_iter + 1):
        x = (b - R @ x) / d
        if np.linalg.norm(b - A @ x) < tol * r0:
            return x, k
    return x, max_iter


def cg(A, b, tol=1e-8):
    x = np.zeros_like(b); r = b.copy(); p = r.copy(); rr = r @ r; r0 = math.sqrt(rr)
    for k in range(1, 10 * len(b)):
        Ap = A @ p; alpha = rr / (p @ Ap)
        x += alpha * p; r -= alpha * Ap
        rr_new = r @ r
        if math.sqrt(rr_new) < tol * r0:
            return x, k
        p = r + (rr_new / rr) * p; rr = rr_new
    return x, k


if __name__ == "__main__":
    n = 40
    A = poisson1d(n); b = np.ones(n) / (n + 1) ** 2
    exact = np.linalg.solve(A, b)
    w_opt = 2 / (1 + math.sin(math.pi / (n + 1)))
    results = {"Jacobi": jacobi(A, b), "Gauss-Seidel": sor(A, b), f"SOR (w = {w_opt:.3f})": sor(A, b, w_opt), "CG": cg(A, b)}
    for name, (x, k) in results.items():
        print(f"{name:20s} {k:6d} iterations, error {np.linalg.norm(x - exact)/np.linalg.norm(exact):.1e}")
        assert np.linalg.norm(x - exact) < 1e-6 * np.linalg.norm(exact)
    kj, kg, ks, kc = (results[k][1] for k in results)
    # theory: residual iterations track the spectral-radius estimates within a factor of about 1.5
    rho = math.cos(math.pi / (n + 1))
    assert 0.6 < kj / (math.log(1e-8) / math.log(rho)) < 1.5 and 1.7 < kj / kg < 2.3
    assert ks < 200 and kc <= n
