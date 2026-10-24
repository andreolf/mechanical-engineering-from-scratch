"""Lumped cooling: the exponential law, checked by RK4, and tested against the exact sphere series to see where Bi < 0.1 matters."""
import math


def rk4_cool(T0, Tinf, tau, t_end, n=2000):
    f = lambda T: -(T - Tinf) / tau
    T, dt = T0, t_end / n
    for _ in range(n):
        k1 = f(T); k2 = f(T + dt / 2 * k1); k3 = f(T + dt / 2 * k2); k4 = f(T + dt * k3)
        T += dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return T


def bisect(g, a, b, tol=1e-13):
    ga = g(a)
    while b - a > tol:
        c = 0.5 * (a + b); gc = g(c)
        if (ga < 0) == (gc < 0): a, ga = c, gc
        else: b = c
    return 0.5 * (a + b)


def sphere_roots(Bi, n=40):
    """Roots of 1 - z cot z = Bi (Bi on the radius), one in each interval ((k-1) pi, k pi)."""
    g = lambda z: 1 - z / math.tan(z) - Bi
    return [bisect(g, (k - 1) * math.pi + 1e-9, k * math.pi - 1e-9) for k in range(1, n + 1)]


def sphere_exact(Bi, Fo, roots):
    """Centre and volume-mean dimensionless temperature theta/theta_i of a sphere."""
    centre = mean = 0.0
    for z in roots:
        C = 4 * (math.sin(z) - z * math.cos(z)) / (2 * z - math.sin(2 * z))
        e = math.exp(-z * z * Fo)
        centre += C * e
        mean += C * e * 3 * (math.sin(z) - z * math.cos(z)) / z ** 3
    return centre, mean


if __name__ == "__main__":
    # a coconut from a 30 C market stall into a 4 C fridge: treated as a water sphere, r = 6 cm, shell ignored, h = 10 (still fridge air)
    r, rho, c, k, h = 0.06, 1000.0, 4180.0, 0.6, 10.0
    Ti, Tinf, Tgoal = 30.0, 4.0, 8.0
    Lc = r / 3
    Bi = h * Lc / k
    tau = rho * c * Lc / h
    t8 = tau * math.log((Ti - Tinf) / (Tgoal - Tinf))
    print(f"coconut: Bi = hLc/k = {Bi:.4f} (> 0.1), tau = {tau:.0f} s = {tau/3600:.4f} h; lumped time to 8 C: {t8/3600:.4f} h")
    assert abs(rk4_cool(Ti, Tinf, tau, t8) - Tgoal) < 1e-9
    roots = sphere_roots(h * r / k)
    alpha = k / (rho * c)
    Fo = alpha * t8 / r ** 2
    cen, mean = sphere_exact(h * r / k, Fo, roots)
    print(f"exact sphere at that time: mean {Tinf + mean*(Ti-Tinf):.4f} C, centre {Tinf + cen*(Ti-Tinf):.4f} C")
    tm = bisect(lambda t: sphere_exact(h * r / k, alpha * t / r**2, roots)[1] - (Tgoal - Tinf) / (Ti - Tinf), 100, 1e6, 1e-3)
    tc = bisect(lambda t: sphere_exact(h * r / k, alpha * t / r**2, roots)[0] - (Tgoal - Tinf) / (Ti - Tinf), 100, 1e6, 1e-3)
    print(f"exact: mean reaches 8 C after {tm/3600:.4f} h, centre after {tc/3600:.4f} h")
    assert tc > tm > t8
    # a valid case: a 10 mm steel bearing ball quenched in oil, h = 100
    r, rho, c, k, h = 0.005, 7800.0, 470.0, 45.0, 100.0
    Bi = h * r / 3 / k; tau = rho * c * r / 3 / h
    roots = sphere_roots(h * r / k)
    worst = max(abs(math.exp(-t / tau) - sphere_exact(h * r / k, k / (rho * c) * t / r**2, roots)[1]) for t in range(5, 1001, 5))
    print(f"steel ball: Bi = {Bi:.5f}, tau = {tau:.2f} s; lumped vs exact mean, worst gap {worst:.1e}")
    assert worst < 1e-3
