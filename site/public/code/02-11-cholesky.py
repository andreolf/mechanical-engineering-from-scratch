"""Cholesky factorisation, a positive-definiteness test, and the energy principle."""
import math
import numpy as np


class NotPositiveDefinite(ValueError):
    pass


def cholesky(K):
    K = np.array(K, dtype=float); n = len(K); L = np.zeros_like(K)
    for j in range(n):
        d = K[j, j] - L[j, :j] @ L[j, :j]
        if d <= 1e-14 * abs(K[j, j]):
            raise NotPositiveDefinite(f"pivot {j} is {d:.3g}")
        L[j, j] = math.sqrt(d)
        L[j + 1:, j] = (K[j + 1:, j] - L[j + 1:, :j] @ L[j, :j]) / L[j, j]
    return L


def solve_spd(K, f):
    L = cholesky(K)
    y = np.linalg.solve(L, f)        # triangular solves (np.linalg.solve is fine for clarity here)
    return np.linalg.solve(L.T, y)


def is_pd(K):
    try:
        cholesky(K); return True
    except NotPositiveDefinite:
        return False


if __name__ == "__main__":
    K = 1000 * np.array([[2, -1], [-1, 1.0]])
    u = np.array([1.0, 2.0])
    U = 0.5 * u @ K @ u
    assert abs(U - 1000) < 1e-12
    L = cholesky(K / 1000)
    assert np.allclose(L, [[2 ** 0.5, 0], [-(0.5 ** 0.5), 0.5 ** 0.5]]) and np.allclose(L @ L.T, K / 1000)
    assert not is_pd([[1, -1], [-1, 1]]) and not is_pd([[1, 2], [2, 1]])
    # spring chain of n springs fixed at one end: PD; energy minimum = solution
    n = 50
    Kc = 2 * np.eye(n) - np.eye(n, k=1) - np.eye(n, k=-1); Kc[-1, -1] = 1
    f = np.zeros(n); f[-1] = 1.0                      # unit pull at the free end
    u = solve_spd(Kc, f)
    assert np.allclose(u, np.arange(1, n + 1))        # each spring stretches by 1
    Pi = lambda v: 0.5 * v @ Kc @ v - f @ v
    rng = np.random.default_rng(9)
    assert all(Pi(u + 1e-3 * rng.standard_normal(n)) > Pi(u) for _ in range(200))
    # random PD matrices: eigenvalues positive, Cholesky matches numpy
    for _ in range(20):
        B = rng.standard_normal((8, 8)); S = B @ B.T + 0.1 * np.eye(8)
        assert is_pd(S) and np.all(np.linalg.eigvalsh(S) > 0) and np.allclose(cholesky(S), np.linalg.cholesky(S))
    print(f"strain energy {U:.0f} N mm; 50-spring chain solved by Cholesky; energy is minimal at the solution")
