"""Bisection, secant and a simplified Brent method, raced on the Colebrook friction-factor equation."""
import math


def bisection(f, a, b, tol=1e-12):
    fa = f(a); n = 0
    while b - a > tol:
        m = 0.5 * (a + b); fm = f(m); n += 1
        if fa * fm <= 0:
            b = m
        else:
            a, fa = m, fm
    return 0.5 * (a + b), n


def secant(f, x0, x1, tol=1e-12, maxit=100):
    f0, f1 = f(x0), f(x1)
    for n in range(1, maxit + 1):
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        x0, f0, x1, f1 = x1, f1, x2, f(x2)
        if abs(x1 - x0) < tol:
            return x1, n
    raise RuntimeError("secant did not converge")


def brent(f, a, b, tol=1e-12, maxit=200):
    """Keep a bracket; try inverse quadratic / secant steps, fall back to bisection when they misbehave."""
    fa, fb = f(a), f(b)
    if fa * fb > 0:
        raise ValueError("root not bracketed")
    if abs(fa) < abs(fb):
        a, b, fa, fb = b, a, fb, fa
    c, fc, n = a, fa, 0
    while abs(b - a) > tol and fb != 0 and n < maxit:
        n += 1
        if fa != fc and fb != fc:          # inverse quadratic interpolation through (a, b, c)
            s = (a * fb * fc / ((fa - fb) * (fa - fc)) + b * fa * fc / ((fb - fa) * (fb - fc))
                 + c * fa * fb / ((fc - fa) * (fc - fb)))
        else:                              # secant
            s = b - fb * (b - a) / (fb - fa)
        lo, hi = sorted(((3 * a + b) / 4, b))
        if not (lo < s < hi) or abs(s - b) >= abs(b - c) / 2:
            s = 0.5 * (a + b)              # bisection: guaranteed progress
        fs = f(s)
        c, fc = b, fb
        if fa * fs < 0:
            b, fb = s, fs
        else:
            a, fa = s, fs
        if abs(fa) < abs(fb):
            a, b, fa, fb = b, a, fb, fa
    return b, n


def colebrook(Re, rel):
    """Residual in x = 1/sqrt(f): x + 2 log10(rel/3.7 + 2.51 x / Re) = 0."""
    return lambda x: x + 2 * math.log10(rel / 3.7 + 2.51 * x / Re)


if __name__ == "__main__":
    g = colebrook(1e5, 1e-4)
    xb, nb = bisection(g, 1, 20)
    xs, ns = secant(g, 1, 20)
    xr, nr = brent(g, 1, 20)
    fric = 1 / xr**2
    print(f"Colebrook Re = 1e5, eps/D = 1e-4: f = {fric:.5f}")
    print(f"iterations: bisection {nb}, secant {ns}, Brent {nr}")
    assert abs(xb - xr) < 1e-10 and abs(xs - xr) < 1e-10
    assert nr < nb
    # a suite of awkward bracketed functions: Brent must never fail
    suite = [(lambda x: x**3 - 2 * x - 5, 2, 3), (lambda x: math.atan(x - 1) * 100, -5, 30),
             (lambda x: (x - 1) ** 3, 0, 3.3), (lambda x: math.exp(x) - 1e6, 0, 30),
             (lambda x: x - math.cos(x), 0, 1), (lambda x: 1 / (x - 0.3) + 1 if x != 0.3 else 1e300, -2, 0.29)]
    for h, a, b in suite:
        r, n = brent(h, a, b)
        assert abs(h(r)) < 1e-6 or abs(r - 1) < 1e-4, (r, h(r))
    print("Brent solved all", len(suite), "bracketed test functions")
