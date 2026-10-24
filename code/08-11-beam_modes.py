"""Bending vibration of beams: roots of the cantilever frequency equation cos(bL) cosh(bL) = -1, checked by finite elements."""
import math
import numpy as np
from scipy.optimize import brentq
from scipy.linalg import eigh


def cantilever_roots(n):
    """beta_n L from cos x cosh x + 1 = 0, bracketed near (2n - 1) pi / 2."""
    f = lambda x: math.cos(x) * math.cosh(x) + 1
    return [brentq(f, (i - 0.5) * math.pi - 1.2 if i > 1 else 1.0, (i - 0.5) * math.pi + 1.2 if i > 1 else 2.5, xtol=1e-14) for i in range(1, n + 1)]


def fe_cantilever(L, EI, rhoA, ne):
    """Euler-Bernoulli Hermite beam elements, consistent mass; clamped at x = 0."""
    h = L / ne
    k = EI / h**3 * np.array([[12, 6*h, -12, 6*h], [6*h, 4*h*h, -6*h, 2*h*h], [-12, -6*h, 12, -6*h], [6*h, 2*h*h, -6*h, 4*h*h]])
    m = rhoA * h / 420 * np.array([[156, 22*h, 54, -13*h], [22*h, 4*h*h, 13*h, -3*h*h], [54, 13*h, 156, -22*h], [-13*h, -3*h*h, -22*h, 4*h*h]])
    n = 2 * (ne + 1); K = np.zeros((n, n)); M = np.zeros((n, n))
    for e in range(ne):
        s = slice(2 * e, 2 * e + 4); K[s, s] += k; M[s, s] += m
    return np.sqrt(eigh(K[2:, 2:], M[2:, 2:], eigvals_only=True)) / (2 * math.pi)


if __name__ == "__main__":
    b = cantilever_roots(4)
    print("beta_n L:", [round(x, 4) for x in b])
    assert abs(b[0] - 1.8751) < 1e-4
    print("ratios f_n / f_1:", [round((x / b[0])**2, 3) for x in b])
    # a steel ruler clamped to a desk: 300 mm overhang, 25 mm wide, 1 mm thick
    E, rho, w, t, L = 200e9, 7850.0, 0.025, 0.001, 0.30
    EI = E * w * t**3 / 12; rhoA = rho * w * t
    f = [x**2 / (2 * math.pi) * math.sqrt(EI / (rhoA * L**4)) for x in b]
    print(f"ruler: f1..f4 = {', '.join(f'{x:.2f}' for x in f)} Hz")
    fe = fe_cantilever(L, EI, rhoA, 40)
    print(f"finite elements (40 elements): {', '.join(f'{x:.2f}' for x in fe[:4])} Hz")
    print("relative differences:", [f"{x:.1e}" for x in np.abs(fe[:4] / np.array(f) - 1)])
    assert np.allclose(fe[:4], f, rtol=1e-5)
    # halve the overhang: frequency x 4
    print(f"150 mm overhang: f1 = {b[0]**2/(2*math.pi)*math.sqrt(EI/(rhoA*0.15**4)):.2f} Hz")
