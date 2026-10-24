"""Bisection with a guaranteed error bound, applied to the cantilever frequency equation."""
import math


def bisect(f, a, b, tol=1e-12, max_iter=200):
    fa, fb = f(a), f(b)
    if fa * fb > 0:
        raise ValueError("no sign change: the IVT gives no guarantee on this bracket")
    history = []
    for n in range(max_iter):
        m = 0.5 * (a + b)
        fm = f(m)
        history.append((a, b))
        if fa * fm <= 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
        if b - a < tol:
            break
    return 0.5 * (a + b), history


if __name__ == "__main__":
    f = lambda x: math.cos(x) * math.cosh(x) + 1
    root, hist = bisect(f, 1.0, 3.0)
    print(f"beta*L = {root:.10f}, (beta*L)^2 = {root**2:.6f}, {len(hist)} steps")
    assert abs(root - 1.8751040687) < 1e-9
    # the error never exceeds the theoretical bound (b-a)/2^(n+1) for the midpoint
    for n, (a, b) in enumerate(hist):
        m = 0.5 * (a + b)
        assert abs(root - m) <= 2.0 / 2 ** (n + 1) + 1e-12
    assert math.ceil(math.log2(2 / 1e-6)) == 21
    try:
        bisect(lambda x: x * x + 1, -1, 1)
    except ValueError as e:
        print("refused:", e)
