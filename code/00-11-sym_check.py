"""Check hand derivations with SymPy, with a numeric fallback when SymPy is missing."""
import math
import random


def numeric_equal(f, g, lo=0.2, hi=3.0, n=50, rtol=1e-6):
    rng = random.Random(0)
    for _ in range(n):
        x = rng.uniform(lo, hi)
        a, b = f(x), g(x)
        if abs(a - b) > rtol * max(1.0, abs(b)):
            return False
    return True


def central_diff(f, x, h=1e-5):
    return (f(x + h) - f(x - h)) / (2 * h)


if __name__ == "__main__":
    hand = lambda x: x**x * (math.log(x) + 1)          # my derivative of x^x
    assert numeric_equal(lambda x: central_diff(lambda t: t**t, x), hand)
    assert abs(hand(2) - 6.7725887) < 1e-6

    try:
        import sympy as sp
    except ImportError:
        print("SymPy not installed: numeric check passed, symbolic check skipped")
    else:
        x = sp.symbols("x", positive=True)
        assert sp.simplify(sp.diff(x**x, x) - x**x * (sp.log(x) + 1)) == 0

        P, L, E, I, s = sp.symbols("P L E I s", positive=True)
        w = -P * s**2 * (3 * L - s) / (6 * E * I)       # my hand result
        assert sp.simplify(E * I * sp.diff(w, s, 2) - (-P * (L - s))) == 0   # ODE
        assert w.subs(s, 0) == 0 and sp.diff(w, s).subs(s, 0) == 0          # BCs
        tip = sp.simplify(w.subs(s, L))
        assert sp.simplify(tip + P * L**3 / (3 * E * I)) == 0
        print("symbolic checks passed; tip =", tip)

    I_val = 0.05 * 0.1**3 / 12
    tip_mm = 1000 * 2**3 / (3 * 210e9 * I_val) * 1000
    assert abs(tip_mm - 3.0476) < 1e-3
    print(f"tip deflection {tip_mm:.2f} mm")
