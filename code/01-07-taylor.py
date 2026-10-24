"""Taylor polynomials of sin and exp, checked against the Lagrange remainder bound."""
import math


def taylor_sin(x, n):
    """Degree-n Taylor polynomial of sin around 0."""
    s, term, k = 0.0, x, 1
    while k <= n:
        s += term
        term *= -x * x / ((k + 1) * (k + 2))
        k += 2
    return s


def taylor_exp(x, n):
    s, term = 0.0, 1.0
    for k in range(n + 1):
        s += term
        term *= x / (k + 1)
    return s


def lagrange_bound(M, x, n):
    return M * abs(x) ** (n + 1) / math.factorial(n + 1)


if __name__ == "__main__":
    # the lesson's test: actual error is always below the Lagrange bound
    for n in range(1, 16):
        for i in range(-40, 41):
            x = i / 10
            assert abs(math.sin(x) - taylor_sin(x, n)) <= lagrange_bound(1.0, x, n) + 1e-15
            if 0 <= x <= 1:
                assert abs(math.exp(x) - taylor_exp(x, n)) <= lagrange_bound(math.e, x, n) + 1e-15
    err = math.sin(0.5) - taylor_sin(0.5, 3)
    assert abs(err - 2.5887e-4) < 1e-8 and err < lagrange_bound(1, 0.5, 4)
    n = next(n for n in range(30) if lagrange_bound(math.e, 1.0, n) < 1e-6)
    assert n == 9
    print(f"sin(0.5) error {err:.3e}; e to 1e-6 needs degree {n}")
