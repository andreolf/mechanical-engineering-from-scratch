"""Improper integrals made proper by substitution, then integrated with Simpson's rule."""
import math


def simpson(f, a, b, n=200):
    h = (b - a) / n
    s = f(a) + f(b) + 4 * sum(f(a + i * h) for i in range(1, n, 2)) + 2 * sum(f(a + i * h) for i in range(2, n, 2))
    return h / 3 * s


def integral_to_infinity(f, a, n=200):
    """int_a^inf f(x) dx with x = a/t, t in (0, 1]: dx = -a/t^2 dt."""
    def g(t):
        t = max(t, 1e-8)   # the value at t = 0 is a limit; evaluate just inside it
        x = a / t
        return f(x) * a / (t * t)
    return simpson(g, 0.0, 1.0, n)


def integral_sqrt_singular(g, n=200):
    """int_0^1 g(x)/sqrt(x) dx with x = u^2: becomes int_0^1 2 g(u^2) du."""
    return simpson(lambda u: 2.0 * g(u * u), 0.0, 1.0, n)


if __name__ == "__main__":
    I1 = integral_to_infinity(lambda x: 1 / x**2, 1.0)
    print(f"int_1^inf 1/x^2 = {I1:.12f}")
    assert abs(I1 - 1.0) < 1e-8                                   # the lesson's test
    I2 = integral_sqrt_singular(lambda x: 1.0)
    assert abs(I2 - 2.0) < 1e-12
    I3 = integral_sqrt_singular(math.cos)                         # int_0^1 cos(x)/sqrt(x) dx
    assert abs(I3 - 1.8090484758005) < 1e-9
    GM, R = 3.986e14, 6.371e6
    w = integral_to_infinity(lambda r: GM / r**2, R)
    v = math.sqrt(2 * w)
    print(f"escape: {w / 1e6:.2f} MJ/kg, {v / 1000:.2f} km/s")
    assert abs(v - 11186.1) < 1
