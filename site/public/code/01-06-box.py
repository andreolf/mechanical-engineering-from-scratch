"""Maximise the volume of an open box folded from sheet: calculus versus a numerical search."""
import math


def volume(x, a, b=None):
    b = a if b is None else b
    return x * (a - 2 * x) * (b - 2 * x)


def golden_max(f, lo, hi, tol=1e-10):
    """Golden-section search for the maximum of a unimodal function on [lo, hi]."""
    g = (math.sqrt(5) - 1) / 2
    c, d = hi - g * (hi - lo), lo + g * (hi - lo)
    while hi - lo > tol:
        if f(c) > f(d):
            hi, d = d, c
            c = hi - g * (hi - lo)
        else:
            lo, c = c, d
            d = lo + g * (hi - lo)
    return 0.5 * (lo + hi)


def best_cut_rect(a, b):
    """Stationary point of x(a-2x)(b-2x): 12x^2 - 4(a+b)x + ab = 0, smaller root."""
    return ((a + b) - math.sqrt((a + b) ** 2 - 3 * a * b)) / 6


if __name__ == "__main__":
    a = 600.0
    x_num = golden_max(lambda x: volume(x, a), 0, a / 2)
    assert abs(x_num - a / 6) < 1e-6                       # the lesson's test
    assert abs(volume(a / 6, a) - 2 * a**3 / 27) < 1e-6
    print(f"cut {x_num:.4f} mm, volume {volume(x_num, a) / 1e6:.3f} L")
    assert abs(volume(90, a) / volume(100, a) - 0.99225) < 1e-5
    x_r = best_cut_rect(400, 250)
    assert abs(x_r - 50) < 1e-12 and abs(volume(x_r, 400, 250) - 2.25e6) < 1e-6
    assert abs(golden_max(lambda x: volume(x, 400, 250), 0, 125) - 50) < 1e-6
