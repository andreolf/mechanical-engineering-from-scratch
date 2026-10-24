"""Double integrals by the midpoint rule and Monte Carlo: centroid and second moment of a T-section."""
import math
import numpy as np


def in_T(x, y):
    flange = (y >= 80) & (y <= 100) & (np.abs(x) <= 50)
    web = (y >= 0) & (y < 80) & (np.abs(x) <= 10)
    return flange | web


def midpoint_2d(f, region, x0, x1, y0, y1, n):
    hx, hy = (x1 - x0) / n, (y1 - y0) / n
    X, Y = np.meshgrid(x0 + hx * (np.arange(n) + 0.5), y0 + hy * (np.arange(n) + 0.5))
    return np.sum(f(X, Y) * region(X, Y)) * hx * hy


if __name__ == "__main__":
    one = lambda x, y: np.ones_like(x)
    n = 2000
    A = midpoint_2d(one, in_T, -50, 50, 0, 100, n)
    ybar = midpoint_2d(lambda x, y: y, in_T, -50, 50, 0, 100, n) / A
    I = midpoint_2d(lambda x, y: (y - ybar) ** 2, in_T, -50, 50, 0, 100, n)
    print(f"A = {A:.1f} mm^2, ybar = {ybar:.3f} mm, I = {I:.4e} mm^4")
    assert abs(A - 3600) < 1e-6 and abs(ybar - 244000 / 3600) < 1e-6
    I_exact = 100 * 20 ** 3 / 12 + 2000 * (90 - ybar) ** 2 + 20 * 80 ** 3 / 12 + 1600 * (40 - ybar) ** 2
    assert abs(I - I_exact) / I_exact < 1e-6 and abs(I_exact - 3142222.2) < 0.1
    # rectangle about its centroid: b h^3 / 12, and midpoint error falls like h^2 for a smooth integrand
    f = lambda x, y: np.exp(-x * y)
    exact = sum((-1) ** k / (math.factorial(k) * (k + 1) ** 2) for k in range(40))   # integral over the unit square
    errs = [abs(midpoint_2d(f, lambda x, y: True, 0, 1, 0, 1, m) - exact) for m in (20, 40, 80)]
    print("midpoint errors:", [f"{e:.1e}" for e in errs])
    assert 3.6 < errs[0] / errs[1] < 4.4 and 3.6 < errs[1] / errs[2] < 4.4
    # Monte Carlo on the T: error ~ 1 / sqrt(N)
    rng = np.random.default_rng(11)
    for N in (10 ** 4, 10 ** 6):
        x, y = rng.uniform(-50, 50, N), rng.uniform(0, 100, N)
        print(f"Monte Carlo area with N = {N:>7}: {1e4 * np.mean(in_T(x, y)):.1f} mm^2")
    assert abs(1e4 * np.mean(in_T(x, y)) - 3600) < 30
