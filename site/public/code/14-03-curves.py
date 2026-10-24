"""Bezier curves by de Casteljau and by Bernstein polynomials, and B-splines by de Boor's algorithm and the Cox-de Boor basis."""
import math
import numpy as np


def de_casteljau(P, t):
    Q = np.array(P, float)
    while len(Q) > 1:
        Q = (1 - t) * Q[:-1] + t * Q[1:]
    return Q[0]


def bernstein(P, t):
    n = len(P) - 1
    return sum(math.comb(n, i) * t ** i * (1 - t) ** (n - i) * np.asarray(P[i], float) for i in range(n + 1))


def find_span(U, p, u):
    n = len(U) - p - 2
    if u >= U[n + 1]: return n
    k = p
    while not (U[k] <= u < U[k + 1]): k += 1
    return k


def de_boor(P, U, p, u):
    k = find_span(U, p, u)
    d = [np.asarray(P[j + k - p], float) for j in range(p + 1)]
    for r in range(1, p + 1):
        for j in range(p, r - 1, -1):
            i = j + k - p
            a = (u - U[i]) / (U[i + p - r + 1] - U[i])
            d[j] = (1 - a) * d[j - 1] + a * d[j]
    return d[p]


def basis(U, p, i, u):
    """Cox-de Boor recursion for N_{i,p}(u). The last knot span is closed so that u = U[-1] works."""
    if p == 0:
        last = u == U[-1] and U[i + 1] == U[-1] and U[i] < U[i + 1]
        return 1.0 if (U[i] <= u < U[i + 1]) or last else 0.0
    a = 0.0 if U[i + p] == U[i] else (u - U[i]) / (U[i + p] - U[i]) * basis(U, p - 1, i, u)
    b = 0.0 if U[i + p + 1] == U[i + 1] else (U[i + p + 1] - u) / (U[i + p + 1] - U[i + 1]) * basis(U, p - 1, i + 1, u)
    return a + b


if __name__ == "__main__":
    # a velomobile nose fairing, a cubic Bezier from the tip (0, 0) to the shoulder (600, 250) mm
    P = [(0, 0), (0, 160), (300, 250), (600, 250)]
    ts = np.linspace(0, 1, 101)
    gap = max(np.abs(de_casteljau(P, t) - bernstein(P, t)).max() for t in ts)
    print(f"de Casteljau vs Bernstein: max difference {gap:.1e} mm; ends {de_casteljau(P, 0)} and {de_casteljau(P, 1)}")
    assert gap < 1e-9 and np.allclose(de_casteljau(P, 0), P[0]) and np.allclose(de_casteljau(P, 1), P[-1])
    # end tangent: B'(0) = n (P1 - P0)
    h = 1e-6
    d0 = (de_casteljau(P, h) - de_casteljau(P, 0)) / h
    print(f"end tangent from a difference quotient {d0.round(3)}, formula 3(P1 - P0) = {3*(np.array(P[1])-P[0])}")
    assert np.allclose(d0, 3 * (np.array(P[1]) - P[0]), atol=1e-2)
    mid = de_casteljau(P, 0.5)
    print(f"midpoint of the fairing at t = 0.5: {mid}")
    # a clamped cubic B-spline through 7 control points
    Q = [(0, 0), (100, 150), (250, 220), (400, 120), (500, 260), (650, 300), (800, 200)]
    p = 3
    U = [0, 0, 0, 0, 1, 2, 3, 4, 4, 4, 4]
    us = np.linspace(0, 4, 201)
    err = max(np.abs(de_boor(Q, U, p, u) - sum(basis(U, p, i, u) * np.array(Q[i], float) for i in range(len(Q)))).max() for u in us)
    pou = max(abs(sum(basis(U, p, i, u) for i in range(len(Q))) - 1) for u in us)
    print(f"de Boor vs basis sum: max difference {err:.1e}; partition of unity error {pou:.1e}")
    assert err < 1e-9 and pou < 1e-12
    assert np.allclose(de_boor(Q, U, p, 0), Q[0]) and np.allclose(de_boor(Q, U, p, 4), Q[-1])
    # local control: N_1,3 is non-zero only on (U[1], U[5]) = (0, 2), so moving control point 1 cannot touch the rest
    Q2 = list(Q); Q2[1] = (100, 50)
    changed = [u for u in us if np.abs(de_boor(Q, U, p, u) - de_boor(Q2, U, p, u)).max() > 1e-12]
    print(f"moving control point 1 changes the curve only for u in [{min(changed):.2f}, {max(changed):.2f}] (support of N_1,3 is (0, 2))")
    assert max(changed) < 2.0
