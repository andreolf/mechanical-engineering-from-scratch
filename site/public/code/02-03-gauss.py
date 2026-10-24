"""Gaussian elimination with partial pivoting, tested against NumPy."""
import time
import numpy as np


def solve(A, b, pivot=True):
    A = [list(map(float, r)) for r in A]
    b = list(map(float, b))
    n = len(b)
    for k in range(n - 1):
        if pivot:
            p = max(range(k, n), key=lambda i: abs(A[i][k]))
            A[k], A[p] = A[p], A[k]
            b[k], b[p] = b[p], b[k]
        if A[k][k] == 0.0:
            raise ZeroDivisionError("zero pivot")
        for i in range(k + 1, n):
            l = A[i][k] / A[k][k]
            if l == 0.0:
                continue
            for j in range(k, n):
                A[i][j] -= l * A[k][j]
            b[i] -= l * b[k]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (b[i] - sum(A[i][j] * x[j] for j in range(i + 1, n))) / A[i][i]
    return x


if __name__ == "__main__":
    x = solve([[2, 1, -1], [-3, -1, 2], [-2, 1, 2]], [8, -11, -3], pivot=False)
    assert np.allclose(x, [2, 3, -1], atol=1e-14)
    # tiny pivot: wrong without pivoting, right with it
    bad = solve([[1e-20, 1], [1, 1]], [1, 2], pivot=False)
    good = solve([[1e-20, 1], [1, 1]], [1, 2])
    print("no pivoting:", bad, " partial pivoting:", good)
    assert abs(bad[0]) < 1e-12 and abs(good[0] - 1) < 1e-15 and abs(good[1] - 1) < 1e-15
    # random systems match numpy, residuals at rounding level
    rng = np.random.default_rng(0)
    for n in (5, 40, 120):
        A = rng.standard_normal((n, n)); b = rng.standard_normal(n)
        t = time.perf_counter(); x = np.array(solve(A, b)); t = time.perf_counter() - t
        r = np.linalg.norm(A @ x - b) / (np.linalg.norm(A) * np.linalg.norm(x))
        assert np.allclose(x, np.linalg.solve(A, b), rtol=1e-8, atol=1e-10) and r < 1e-14
        print(f"n = {n:4d}: relative residual {r:.1e}, pure Python {t*1e3:7.1f} ms")
