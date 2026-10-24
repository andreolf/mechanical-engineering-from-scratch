"""Laminar flat-plate convection from scratch: the Blasius and Pohlhausen similarity equations by RK4 shooting, giving Nu_x = 0.332 Re^1/2 Pr^1/3."""
import math


def rk4(f, y, eta_end, n=4000):
    h = eta_end / n
    for _ in range(n):
        k1 = f(y); k2 = f([a + h / 2 * b for a, b in zip(y, k1)]); k3 = f([a + h / 2 * b for a, b in zip(y, k2)]); k4 = f([a + h * b for a, b in zip(y, k3)])
        y = [a + h / 6 * (b + 2 * c + 2 * d + e) for a, b, c, d, e in zip(y, k1, k2, k3, k4)]
    return y


def bisect(g, a, b, tol=1e-12):
    ga = g(a)
    while b - a > tol:
        c = 0.5 * (a + b); gc = g(c)
        if (ga < 0) == (gc < 0): a, ga = c, gc
        else: b = c
    return 0.5 * (a + b)


def blasius_fpp0(eta_end=12.0):
    """f''' + f f''/2 = 0, f(0) = f'(0) = 0, f'(inf) = 1. Returns f''(0)."""
    rhs = lambda y: [y[1], y[2], -0.5 * y[0] * y[2]]
    return bisect(lambda s: rk4(rhs, [0.0, 0.0, s], eta_end)[1] - 1.0, 0.1, 1.0)


def nusselt_coefficient(Pr, s, eta_end=12.0):
    """theta'' + Pr f theta'/2 = 0 with theta(0) = 0, theta(inf) = 1 (theta = (T - Tw)/(Tinf - Tw)). Nu_x / Re_x^1/2 = theta'(0).
    The equation is linear in theta, so integrate once with theta'(0) = 1 and rescale."""
    rhs = lambda y: [y[1], y[2], -0.5 * y[0] * y[2], y[4], -0.5 * Pr * y[0] * y[4]]
    y = rk4(rhs, [0.0, 0.0, s, 0.0, 1.0], eta_end if Pr >= 1 else eta_end * 1.5)
    return 1.0 / y[3]


if __name__ == "__main__":
    s = blasius_fpp0()
    print(f"Blasius f''(0) = {s:.6f}")
    assert abs(s - 0.332057) < 1e-5
    for Pr in (0.7, 1.0, 5.0, 10.0):
        c = nusselt_coefficient(Pr, s)
        print(f"  Pr = {Pr:4}: Nu_x/Re^1/2 = {c:.5f}, correlation 0.332 Pr^1/3 = {0.332*Pr**(1/3):.5f}")
        assert abs(c - 0.332 * Pr ** (1 / 3)) < 0.02 * c  # the correlation is a fit, good to about 2% for 0.6 < Pr < 10
    assert abs(nusselt_coefficient(1.0, s) - s) < 1e-6  # Pr = 1: the Reynolds analogy, theta = f'
    # a 0.5 m solar panel in a 3 m/s breeze, air at 30 C
    nu, k, Pr, U, L, dT = 1.608e-5, 0.02588, 0.7282, 3.0, 0.5, 25.0
    Re = U * L / nu
    Nu = 0.664 * Re ** 0.5 * Pr ** (1 / 3)
    h = Nu * k / L
    print(f"panel: Re_L = {Re:.0f} (laminar, < 5e5); Nu_avg = {Nu:.3f}; h_avg = {h:.4f} W/(m^2 K); heat loss per metre of width at 25 K: {h*L*dT:.3f} W")
    # the average is twice the trailing-edge local value: integrate the local h numerically
    n = 200000
    hx = lambda x: 0.332 * (U * x / nu) ** 0.5 * Pr ** (1 / 3) * k / x
    havg = sum(hx((i + 0.5) * L / n) for i in range(n)) / n
    print(f"numerical average of local h: {havg:.4f}; local h at the trailing edge {hx(L):.4f}")
    assert abs(havg - h) < 2e-3 * h and abs(h - 2 * hx(L)) < 1e-9 * h
