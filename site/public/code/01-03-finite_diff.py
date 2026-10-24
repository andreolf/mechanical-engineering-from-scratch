"""Forward, backward and central differences, and their error slopes on a log-log plot."""
import math


def forward(f, x, h):  return (f(x + h) - f(x)) / h
def backward(f, x, h): return (f(x) - f(x - h)) / h
def central(f, x, h):  return (f(x + h) - f(x - h)) / (2 * h)


def slope(hs, errs):
    """Least-squares slope of log(err) against log(h)."""
    X = [math.log(h) for h in hs]; Y = [math.log(e) for e in errs]
    mx, my = sum(X) / len(X), sum(Y) / len(Y)
    return sum((a - mx) * (b - my) for a, b in zip(X, Y)) / sum((a - mx) ** 2 for a in X)


if __name__ == "__main__":
    f, x, exact = math.sin, 1.0, math.cos(1.0)
    hs = [10 ** (-k / 4) for k in range(4, 17)]      # 1e-1 .. 1e-4, truncation-dominated
    ef = [abs(forward(f, x, h) - exact) for h in hs]
    ec = [abs(central(f, x, h) - exact) for h in hs]
    pf, pc = slope(hs, ef), slope(hs, ec)
    print(f"forward slope {pf:.3f}, central slope {pc:.3f}")
    assert abs(pf - 1) < 0.05 and abs(pc - 2) < 0.05   # the lesson's test

    # predicted truncation error at h = 0.1
    assert abs(abs(forward(f, x, 0.1) - exact) / (0.05 * math.sin(1)) - 1) < 0.05
    # round-off: forward error at h = 1e-14 is far worse than at h = 1e-8
    assert abs(forward(f, x, 1e-14) - exact) > 100 * abs(forward(f, x, 1e-8) - exact)

    pos = lambda t: 2 * t * t
    assert abs(central(pos, 2.0, 0.1) - 8.0) < 1e-12
    assert abs(forward(pos, 2.0, 0.1) - 8.2) < 1e-9
