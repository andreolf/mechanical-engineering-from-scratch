"""Imperfect columns: amplification 1/(1 - P/Pcr) and the Perry-Robertson failure load."""
import math
import numpy as np


def bow_fd(P, L, EI, e0, n=200):
    """Solve EI w'' + P w = -P w0 with w0 = e0 sin(pi x / L), pinned ends, by finite differences.
    Returns the extra mid-span deflection w (not counting the initial bow)."""
    x = np.linspace(0, L, n + 1); h = L / n
    m = n - 1
    A = (np.diag(-2 * np.ones(m)) + np.diag(np.ones(m - 1), 1) + np.diag(np.ones(m - 1), -1)) * EI / h**2 + P * np.eye(m)
    w = np.zeros(n + 1)
    w[1:-1] = np.linalg.solve(A, -P * e0 * np.sin(np.pi * x[1:-1] / L))
    return x, w


def perry_load(A, I, c, L, E, fy, e0):
    """Axial load at which the extreme fibre first yields: P/A + P e0 c / (I (1 - P/Pcr)) = fy (bisection)."""
    Pcr = math.pi**2 * E * I / L**2
    f = lambda P: P / A + P * e0 * c / (I * (1 - P / Pcr)) - fy
    lo, hi = 0.0, min(Pcr, fy * A) * (1 - 1e-12)
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
    return 0.5 * (lo + hi), Pcr


if __name__ == "__main__":
    E, fy = 210e3, 235.0
    D, t, L = 48.3, 3.2, 3000.0                         # the scaffold tube from 06.19
    I = math.pi * (D**4 - (D - 2 * t) ** 4) / 64; A = math.pi * (D**2 - (D - 2 * t) ** 2) / 4; c = D / 2
    EI = E * I; Pcr = math.pi**2 * EI / L**2
    e0 = L / 1000                                       # a typical out-of-straightness, 3 mm
    for ratio in (0.25, 0.5, 0.8, 0.9, 0.95, 0.99):
        P = ratio * Pcr
        x, w = bow_fd(P, L, EI, e0)
        total = e0 + w[len(w) // 2]
        print(f"P/Pcr = {ratio:.2f}: total mid-span bow {total:7.3f} mm, amplification {total / e0:6.2f} (1/(1-P/Pcr) = {1/(1-ratio):6.2f})")
        # the discrete column's Pcr is 0.002 % low, an error the amplification magnifies by (1/(1-P/Pcr))^2
        assert abs(total / e0 - 1 / (1 - ratio)) < 5e-5 / (1 - ratio) ** 2
    # the bow grows without bound as P approaches Pcr
    ws = [e0 / (1 - r) for r in (0.99, 0.999, 0.9999)]
    assert ws[0] < ws[1] < ws[2] and ws[2] > 1000 * e0 * 0.99
    Pf, _ = perry_load(A, I, c, L, E, fy, e0)
    print(f"first yield of the bowed tube at {Pf/1e3:.2f} kN = {Pf/Pcr:.3f} Pcr (Euler {Pcr/1e3:.2f} kN, squash {fy*A/1e3:.1f} kN)")
    for L2 in (1000.0, 2000.0, 3000.0, 4000.0):
        Pf2, Pc2 = perry_load(A, I, c, L2, E, fy, L2 / 1000)
        print(f"  L = {L2/1e3:.0f} m: failure {Pf2/1e3:6.2f} kN, Euler {Pc2/1e3:7.2f} kN, squash {fy*A/1e3:.1f} kN")
