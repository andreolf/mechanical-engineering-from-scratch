"""Beam deflection: integrate EI w'' = M twice, and solve EI w'''' = q by finite differences."""
import numpy as np


def cumtrapz(f, x):
    return np.concatenate([[0.0], np.cumsum((f[1:] + f[:-1]) / 2 * np.diff(x))])


def deflect_from_moment(x, M, EI, bc):
    """w is measured upward and sagging M is positive, so w'' = M / EI.
    bc = 'cantilever' (w = w' = 0 at x = 0) or 'simple' (w = 0 at both ends)."""
    th = cumtrapz(M / EI, x)
    w = cumtrapz(th, x)
    if bc == "simple":
        w = w - x / x[-1] * w[-1]            # add a rigid rotation so that w(L) = 0 too
    return w


def fd_simply_supported(q, L, EI, n=400):
    """EI w'''' = -q (q downward) with w = w'' = 0 at both ends, central differences on n intervals."""
    h = L / n; m = n - 1
    A = np.zeros((m, m))
    for i in range(m):
        for j, c in zip(range(i - 2, i + 3), (1, -4, 6, -4, 1)):
            if 0 <= j < m: A[i, j] += c
    A[0, 0] -= 1; A[-1, -1] -= 1            # ghost points: w_{-1} = -w_1 (w'' = 0 at a pinned end)
    w = np.linalg.solve(A / h**4, -q / EI * np.ones(m))
    return np.concatenate([[0], w, [0]])


if __name__ == "__main__":
    E, I = 210e3, 1.8456e7                  # MPa, mm^4 (the I-section from 06.10)
    EI = E * I
    # cantilever balcony beam, 1.8 m, 5 kN at the tip
    L, P = 1800.0, 5000.0
    x = np.linspace(0, L, 3601)
    w = deflect_from_moment(x, -P * (L - x), EI, "cantilever")
    print(f"cantilever tip deflection {-w[-1]:.4f} mm (P L^3 / 3EI = {P * L**3 / (3 * EI):.4f})")
    assert abs(-w[-1] - P * L**3 / (3 * EI)) < 1e-5
    # footbridge, simply supported 6 m, 5 kN/m = 5 N/mm
    L, q = 6000.0, 5.0
    x = np.linspace(0, L, 6001)
    w = deflect_from_moment(x, q * x * (L - x) / 2, EI, "simple")
    exact = 5 * q * L**4 / (384 * EI)
    print(f"footbridge mid-span deflection {-w.min():.4f} mm (5 q L^4 / 384 EI = {exact:.4f}), span / deflection = {L / exact:.0f}")
    assert abs(-w.min() - exact) < 1e-4
    wf = fd_simply_supported(q, L, EI)
    print(f"finite differences on EI w'''' = q: {-wf.min():.4f} mm")
    assert abs(-wf.min() - exact) < 1e-3 * exact
    # mid-span point load: P L^3 / 48 EI
    P = 20000.0
    w = deflect_from_moment(x, np.where(x < L / 2, P / 2 * x, P / 2 * (L - x)), EI, "simple")
    print(f"20 kN at mid-span: {-w.min():.4f} mm (P L^3 / 48 EI = {P * L**3 / (48 * EI):.4f})")
    assert abs(-w.min() - P * L**3 / (48 * EI)) < 1e-4
