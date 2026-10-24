"""Partial derivatives by central differences, the total differential and error propagation."""
import math


def partial(f, x, i, h=None):
    """Central difference in variable i at point x (a list)."""
    h = h or 1e-6 * max(1.0, abs(x[i]))
    xp, xm = list(x), list(x)
    xp[i] += h; xm[i] -= h
    return (f(xp) - f(xm)) / (2 * h)


def grad(f, x):
    return [partial(f, x, i) for i in range(len(x))]


def propagate(f, x, sigmas):
    g = grad(f, x)
    return math.sqrt(sum((gi * si) ** 2 for gi, si in zip(g, sigmas)))


if __name__ == "__main__":
    m, R = 1.0, 287.0
    p = lambda v: m * R * v[0] / v[1]           # v = [T, V]
    x0 = [300.0, 0.5]
    dpdT, dpdV = grad(p, x0)
    print(f"dp/dT = {dpdT:.3f} Pa/K, dp/dV = {dpdV:.1f} Pa/m^3")
    assert abs(dpdT - 574) < 1e-5 and abs(dpdV + 344400) < 1e-2
    dp_lin = dpdT * 2 + dpdV * 0.01
    dp_exact = p([302, 0.51]) - p(x0)
    print(f"linear estimate {dp_lin:.0f} Pa, exact {dp_exact:.0f} Pa")
    assert abs(dp_lin + 2296) < 0.1 and abs(dp_exact + 2251) < 1
    # the estimate improves quadratically as the change shrinks
    errs = []
    for s in (1.0, 0.1, 0.01):
        lin = dpdT * 2 * s + dpdV * 0.01 * s
        errs.append(abs(p([300 + 2 * s, 0.5 + 0.01 * s]) - p(x0) - lin))
    assert 80 < errs[0] / errs[1] < 120 and 80 < errs[1] / errs[2] < 120
    sigma_p = propagate(p, x0, [0.5, 0.002])
    print(f"sigma_p = {sigma_p:.0f} Pa")
    assert abs(sigma_p - math.hypot(287, 688.8)) < 0.5
    # mixed partials commute for a smooth function
    f = lambda v: math.sin(v[0] * v[1]) + v[0] ** 3 * v[1]
    fx = lambda v: partial(f, v, 0, 1e-4)
    fy = lambda v: partial(f, v, 1, 1e-4)
    a, b = partial(fx, [0.7, 1.3], 1, 1e-4), partial(fy, [0.7, 1.3], 0, 1e-4)
    assert abs(a - b) < 1e-5
