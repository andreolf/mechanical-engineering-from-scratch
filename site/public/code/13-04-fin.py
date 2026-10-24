"""Fins: a finite-difference solve of the fin equation theta'' = m^2 theta, against the analytic profile, heat rate and efficiency."""
import math
import numpy as np


def fin_fd(L, m, hk, n=2001):
    """theta(0) = 1 at the base; convective tip: -k theta' = h theta at x = L (hk = h/k). Second-order tip via a ghost node."""
    x = np.linspace(0, L, n); dx = x[1]
    A = np.zeros((n, n)); b = np.zeros(n)
    A[0, 0] = 1.0; b[0] = 1.0
    for i in range(1, n - 1):
        A[i, i - 1] = A[i, i + 1] = 1.0; A[i, i] = -2.0 - (m * dx) ** 2
    A[-1, -2] = 2.0; A[-1, -1] = -2.0 - (m * dx) ** 2 - 2 * dx * hk  # ghost node eliminated with the tip condition
    return x, np.linalg.solve(A, b)


def fin_exact(x, L, m, hk):
    a = hk / m
    return (np.cosh(m * (L - x)) + a * np.sinh(m * (L - x))) / (math.cosh(m * L) + a * math.sinh(m * L))


def fin_heat(L, m, hk, M):
    a = hk / m
    return M * (math.sinh(m * L) + a * math.cosh(m * L)) / (math.cosh(m * L) + a * math.sinh(m * L))


if __name__ == "__main__":
    # an aluminium pin fin on a CPU cooler: d = 3 mm, L = 30 mm, k = 200, fan-driven h = 40 W/(m^2 K), base 40 K above the air
    d, L, k, h, tb = 0.003, 0.030, 200.0, 40.0, 40.0
    P, A = math.pi * d, math.pi * d * d / 4
    m = math.sqrt(h * P / (k * A)); M = math.sqrt(h * P * k * A) * tb
    x, th = fin_fd(L, m, h / k)
    err = np.abs(th - fin_exact(x, L, m, h / k)).max()
    print(f"m = {m:.4f} 1/m, mL = {m*L:.4f}; tip excess temperature {th[-1]*tb:.4f} K; FD vs analytic max error {err:.1e}")
    assert err < 1e-6
    q = fin_heat(L, m, h / k, M)
    q_fd = -k * A * tb * (-3 * th[0] + 4 * th[1] - th[2]) / (2 * x[1])
    eta = q / (h * (P * L + A) * tb)
    print(f"heat rate {q:.5f} W (from the FD base gradient {q_fd:.5f} W); efficiency {eta:.4f}; effectiveness {q/(h*A*tb):.2f}")
    assert abs(q_fd - q) < 1e-4 * q
    # long-fin limit: q -> sqrt(h P k A) theta_b
    for Lx in (0.03, 0.1, 0.3, 1.0):
        print(f"  L = {Lx:4.2f} m: q = {fin_heat(Lx, m, h/k, M):.5f} W (long-fin limit {M:.5f} W)")
    assert abs(fin_heat(1.0, m, h / k, M) - M) < 1e-9 * M
