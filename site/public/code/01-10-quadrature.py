"""Composite trapezoid and Simpson rules, with convergence checks."""
import math


def trapezoid(f, a, b, n):
    h = (b - a) / n
    return h * (0.5 * f(a) + sum(f(a + i * h) for i in range(1, n)) + 0.5 * f(b))


def simpson(f, a, b, n):
    if n % 2:
        raise ValueError("Simpson's rule needs an even number of slices")
    h = (b - a) / n
    s = f(a) + f(b)
    s += 4 * sum(f(a + i * h) for i in range(1, n, 2))
    s += 2 * sum(f(a + i * h) for i in range(2, n, 2))
    return h / 3 * s


def order(rule, f, a, b, exact, ns=(4, 8, 16, 32)):
    e = [abs(rule(f, a, b, n) - exact) for n in ns]
    return sum(math.log2(e[i] / e[i + 1]) for i in range(len(e) - 1)) / (len(e) - 1)


if __name__ == "__main__":
    f = lambda V: 100.0 / V
    W = 100 * math.log(2)
    T, S = trapezoid(f, 0.5, 1.0, 4), simpson(f, 0.5, 1.0, 4)
    print(f"trapezoid {T:.4f}, Simpson {S:.4f}, exact {W:.4f}")
    assert abs(T - 69.7024) < 1e-4 and abs(S - 69.3254) < 1e-4
    assert abs(order(trapezoid, f, 0.5, 1, W) - 2) < 0.05
    assert abs(order(simpson, f, 0.5, 1, W) - 4) < 0.1
    # Simpson integrates any cubic exactly, even with one panel (the lesson's test)
    for c in [(1, 0, 0, 0), (0, 1, 0, 0), (2, -3, 5, 7), (-1, 4, 0.5, 2)]:
        cubic = lambda x, c=c: c[0] * x**3 + c[1] * x**2 + c[2] * x + c[3]
        exact = c[0] * 16 / 4 + c[1] * 8 / 3 + c[2] * 2 + c[3] * 2      # integral on [0, 2]
        assert abs(simpson(cubic, 0, 2, 2) - exact) < 1e-12
