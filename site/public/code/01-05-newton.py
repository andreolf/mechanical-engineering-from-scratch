"""Safeguarded Newton's method with derivatives from dual numbers."""
import math


class Dual:
    def __init__(self, a, b=0.0): self.a, self.b = a, b
    def __add__(self, o): o = o if isinstance(o, Dual) else Dual(o); return Dual(self.a + o.a, self.b + o.b)
    __radd__ = __add__
    def __mul__(self, o): o = o if isinstance(o, Dual) else Dual(o); return Dual(self.a * o.a, self.a * o.b + self.b * o.a)
    __rmul__ = __mul__
    def __sub__(self, o): return self + (-1) * o


def cos(x):  return Dual(math.cos(x.a), -math.sin(x.a) * x.b)
def cosh(x): return Dual(math.cosh(x.a), math.sinh(x.a) * x.b)


def newton(f, x0, lo=None, hi=None, tol=1e-14, max_iter=50):
    """Newton steps; if a bracket [lo, hi] is given, any step leaving it becomes a bisection."""
    x, hist = x0, [x0]
    for _ in range(max_iter):
        y = f(Dual(x, 1.0))
        step = y.a / y.b if y.b != 0 else float("inf")
        x_new = x - step
        if lo is not None and not (lo < x_new < hi):
            x_new = 0.5 * (lo + hi)
        if lo is not None:   # shrink the bracket using the sign at x_new
            if f(Dual(lo)).a * f(Dual(x_new)).a <= 0: hi = x_new
            else: lo = x_new
        hist.append(x_new)
        if abs(x_new - x) < tol * max(1.0, abs(x_new)):
            return x_new, hist
        x = x_new
    raise RuntimeError("no convergence")


if __name__ == "__main__":
    f = lambda x: cos(x) * cosh(x) + 1
    root, hist = newton(f, 2.0)
    r = 1.8751040687119611
    errs = [abs(h - r) for h in hist]
    print("errors:", ", ".join(f"{e:.1e}" for e in errs[:5]))
    assert abs(root - r) < 1e-14
    # digits roughly double: log10 error ratio near 2 while far from machine precision
    d = [-math.log10(e) for e in errs[:4]]
    assert 1.6 < d[2] / d[1] < 2.6 and 1.6 < d[3] / d[2] < 2.6
    # sqrt(2): Newton equals the Babylonian iteration
    rt, h2 = newton(lambda x: x * x - 2, 1.0)
    assert abs(h2[2] - 17 / 12) < 1e-15 and abs(rt - math.sqrt(2)) < 1e-15
    # a bad start: x0 = 0.05 on x^2 - 2 shoots to about 20, the safeguard keeps it in [0, 3]
    rs, hs = newton(lambda x: x * x - 2, 0.05, lo=0.0, hi=3.0)
    assert max(hs) <= 3.0 and abs(rs - math.sqrt(2)) < 1e-12
