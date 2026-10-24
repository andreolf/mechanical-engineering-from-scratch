"""Catenary y = a cosh(x/a): find a for a given span and cable length, then sag and tensions."""
import math
import numpy as np


def catenary_a(S, L, tol=1e-12):
    """Solve 2 a sinh(S / (2 a)) = L for a by bisection (the left side falls monotonically from inf to S)."""
    if L <= S:
        raise ValueError("cable must be longer than the span")
    f = lambda a: 2 * a * math.sinh(S / (2 * a)) - L
    lo, hi = S / 1000, S * 1000.0
    while f(lo) > 1e300 or math.isinf(f(lo)):
        lo *= 2
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if f(mid) > 0: lo = mid
        else: hi = mid
        if hi - lo < tol * hi: break
    return 0.5 * (lo + hi)


def arc_length(a, S, n=20001):
    """Integrate sqrt(1 + y'^2) with y' = sinh(x / a) by Simpson's rule."""
    x = np.linspace(-S / 2, S / 2, n); g = np.sqrt(1 + np.sinh(x / a) ** 2); h = S / (n - 1)
    w = np.ones(n); w[1:-1:2] = 4; w[2:-1:2] = 2
    return h / 3 * (w @ g)


if __name__ == "__main__":
    # an alpine cable-car track rope between two towers at the same height: span 400 m, rope 404 m, 30 kg/m
    S, L, w = 400.0, 404.0, 30 * 9.81 / 1000        # w in kN/m
    a = catenary_a(S, L)
    sag = a * (math.cosh(S / (2 * a)) - 1)
    H = w * a; Tmax = w * a * math.cosh(S / (2 * a))
    print(f"a = {a:.3f} m, sag = {sag:.3f} m, horizontal tension H = {H:.2f} kN, tension at the towers {Tmax:.2f} kN")
    assert abs(arc_length(a, S) - L) < 1e-6                     # the length integral returns the specified length
    assert abs(Tmax - (H + w * sag)) < 1e-9                     # T = w y: tension grows by w times the height climbed
    # parabolic approximation: L ~ S + 8 d^2 / (3 S)  ->  d = sqrt(3 S (L - S) / 8)
    d_par = math.sqrt(3 * S * (L - S) / 8); H_par = w * S**2 / (8 * d_par)
    print(f"parabola: sag {d_par:.3f} m ({(d_par / sag - 1) * 100:.2f} % off), H = {H_par:.2f} kN")
    assert abs(d_par / sag - 1) < 0.01
    # a slack chain: span 10 m, length 14 m: the parabola is now poor
    a2 = catenary_a(10, 14); sag2 = a2 * (math.cosh(5 / a2) - 1); d2 = math.sqrt(3 * 10 * 4 / 8)
    print(f"slack chain: catenary sag {sag2:.3f} m, parabola {d2:.3f} m")
    assert abs(arc_length(a2, 10) - 14) < 1e-6 and abs(d2 / sag2 - 1) > 0.05
