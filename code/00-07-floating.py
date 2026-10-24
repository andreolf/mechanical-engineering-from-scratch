"""Machine epsilon, cancellation and two stable rewrites."""
import math


def machine_epsilon():
    eps = 1.0
    while 1.0 + eps / 2 > 1.0:
        eps /= 2
    return eps


def f_naive(x):
    return (1 - math.cos(x)) / x**2


def f_stable(x):
    s = math.sin(x / 2)
    return 2 * s * s / x**2


def quad_roots_naive(a, b, c):
    d = math.sqrt(b * b - 4 * a * c)
    return (-b + d) / (2 * a), (-b - d) / (2 * a)


def quad_roots_stable(a, b, c):
    d = math.sqrt(b * b - 4 * a * c)
    q = -0.5 * (b + math.copysign(d, b))   # no cancellation in q
    return q / a, c / q


if __name__ == "__main__":
    eps = machine_epsilon()
    assert eps == 2.0**-52
    assert abs(f_stable(1e-8) - 0.5) < 1e-10          # the lesson's test
    assert f_naive(1e-8) == 0.0                         # all digits gone
    for x in (1e-1, 1e-3, 1e-5, 1e-7):
        print(f"x={x:.0e}  naive={f_naive(x):.16f}  stable={f_stable(x):.16f}")

    big, small = quad_roots_stable(1.0, -1e8, 1.0)
    _, small_naive = sorted(quad_roots_naive(1.0, -1e8, 1.0))[::-1]
    assert abs(small - 1e-8) / 1e-8 < 1e-15
    assert abs(small_naive - 1e-8) / 1e-8 > 0.2        # 25% wrong
    print(f"small root: naive {small_naive:.6e}, stable {small:.6e}")
