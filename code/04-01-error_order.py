"""Measure convergence order from successive errors: Newton (p = 2) and secant (p = 1.618) on x^3 - 2x - 5."""
import math
import numpy as np

f = lambda x: x**3 - 2 * x - 5
df = lambda x: 3 * x**2 - 2
ROOT = 2.0945514815423265          # Wallis's classic cubic


def newton(x, n):
    xs = [x]
    for _ in range(n):
        x = x - f(x) / df(x); xs.append(x)
    return xs


def secant(x0, x1, n):
    xs = [x0, x1]
    for _ in range(n):
        if f(x1) == f(x0):
            break                                   # converged to machine precision
        x0, x1 = x1, x1 - f(x1) * (x1 - x0) / (f(x1) - f(x0)); xs.append(x1)
    return xs


def orders(errs):
    """p_n = log(e_{n+1}/e_n) / log(e_n/e_{n-1}) for each consecutive triple."""
    return [math.log(errs[i + 1] / errs[i]) / math.log(errs[i] / errs[i - 1]) for i in range(1, len(errs) - 1)]


def fit_order(h, e):
    """Slope of log e against log h: the order of a discretisation method."""
    return np.polyfit(np.log(h), np.log(e), 1)[0]


if __name__ == "__main__":
    en = [abs(x - ROOT) for x in newton(3.0, 6)]
    en = [e for e in en if e > 1e-15]
    es = [abs(x - ROOT) for x in secant(3.0, 2.8, 9)]
    es = [e for e in es if e > 1e-15]
    pn, ps = orders(en), orders(es)
    print("Newton errors:", " ".join(f"{e:.1e}" for e in en))
    print("Newton orders:", " ".join(f"{p:.3f}" for p in pn))
    print("secant orders:", " ".join(f"{p:.3f}" for p in ps))
    assert abs(pn[-1] - 2) < 0.05
    assert abs(ps[-1] - (1 + math.sqrt(5)) / 2) < 0.08
    # discretisation order: central difference of sin at x = 1
    h = np.array([0.1, 0.05, 0.025, 0.0125])
    e = np.abs((np.sin(1 + h) - np.sin(1 - h)) / (2 * h) - math.cos(1))
    p = fit_order(h, e)
    print(f"central difference observed order {p:.4f}")
    assert abs(p - 2) < 0.01
