"""Natural cubic spline from scratch: second-derivative unknowns, Thomas tridiagonal solve, C2 check."""
import numpy as np


def thomas(a, b, c, d):
    """Solve a tridiagonal system: a sub-, b main, c super-diagonal (a[0] and c[-1] unused)."""
    n = len(b); cp = np.zeros(n); dp = np.zeros(n)
    cp[0], dp[0] = c[0] / b[0], d[0] / b[0]
    for i in range(1, n):
        m = b[i] - a[i] * cp[i - 1]
        cp[i] = c[i] / m if i < n - 1 else 0.0
        dp[i] = (d[i] - a[i] * dp[i - 1]) / m
    x = np.zeros(n); x[-1] = dp[-1]
    for i in range(n - 2, -1, -1):
        x[i] = dp[i] - cp[i] * x[i + 1]
    return x


def natural_spline(x, y):
    """Return the knot second derivatives M (M_0 = M_n = 0)."""
    h = np.diff(x); n = len(x) - 1
    a = np.r_[0, h[1:-1]]; b = 2 * (h[:-1] + h[1:]); c = np.r_[h[1:-1], 0]
    d = 6 * ((y[2:] - y[1:-1]) / h[1:] - (y[1:-1] - y[:-2]) / h[:-1])
    M = np.zeros(n + 1); M[1:-1] = thomas(a, b, c, d)
    return M


def evaluate(x, y, M, t, der=0):
    i = np.clip(np.searchsorted(x, t) - 1, 0, len(x) - 2)
    h = x[i + 1] - x[i]; A = (x[i + 1] - t) / h; B = (t - x[i]) / h
    if der == 0:
        return A * y[i] + B * y[i + 1] + ((A**3 - A) * M[i] + (B**3 - B) * M[i + 1]) * h * h / 6
    if der == 1:
        return (y[i + 1] - y[i]) / h + ((1 - 3 * A**2) * M[i] + (3 * B**2 - 1) * M[i + 1]) * h / 6
    return A * M[i] + B * M[i + 1]


if __name__ == "__main__":
    # hand example: knots (0,0), (1,1), (2,0), (3,1)
    x = np.array([0.0, 1, 2, 3]); y = np.array([0.0, 1, 0, 1])
    M = natural_spline(x, y)
    print("knot second derivatives:", M, " S(0.5) =", evaluate(x, y, M, np.array([0.5]))[0])
    assert np.allclose(M, [0, -4, 4, 0]) and abs(evaluate(x, y, M, np.array([0.5]))[0] - 0.75) < 1e-12
    # a tube centreline sampled at uneven stations (mm)
    xs = np.array([0, 60, 150, 260, 400, 520, 600.0]); ys = np.array([0, 18, 40, 52, 47, 30, 22.0])
    M = natural_spline(xs, ys)
    eps = 1e-7
    for k in xs[1:-1]:
        for der in (0, 1, 2):
            left, right = evaluate(xs, ys, M, np.array([k - eps]), der)[0], evaluate(xs, ys, M, np.array([k + eps]), der)[0]
            assert abs(left - right) < 1e-4, (k, der, left, right)
    print("value, slope and curvature are continuous at every interior knot")
    from scipy.interpolate import CubicSpline
    t = np.linspace(0, 600, 1201)
    ref = CubicSpline(xs, ys, bc_type="natural")(t)
    print(f"max difference from scipy CubicSpline(natural): {np.max(np.abs(evaluate(xs, ys, M, t) - ref)):.2e} mm")
    assert np.max(np.abs(evaluate(xs, ys, M, t) - ref)) < 1e-10
