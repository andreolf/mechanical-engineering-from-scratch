"""Steady heat in a square plate: five-point stencil with SOR, checked against the series solution."""
import math
import numpy as np


def sinh_ratio(a, b):
    """sinh(a) / sinh(b) for 0 <= a <= b without overflow."""
    return math.exp(a - b) * (1 - math.exp(-2 * a)) / (1 - math.exp(-2 * b))


def series(x, y, T0=100.0, terms=301):
    return sum(4 * T0 / (n * math.pi) * math.sin(n * math.pi * x) * sinh_ratio(n * math.pi * y, n * math.pi)
               for n in range(1, terms, 2))


def solve_plate(n, T_top=100.0, tol=1e-10):
    T = np.zeros((n, n)); T[-1, :] = T_top        # row index = y; top row is y = 1
    T[-1, 0] = T[-1, -1] = T_top / 2              # corners: average of the two edges
    w = 2 / (1 + math.sin(math.pi / (n - 1)))     # optimal SOR factor for the square
    for sweep in range(20000):
        change = 0.0
        for j in range(1, n - 1):
            for i in range(1, n - 1):
                new = 0.25 * (T[j, i + 1] + T[j, i - 1] + T[j + 1, i] + T[j - 1, i])
                d = w * (new - T[j, i]); T[j, i] += d; change = max(change, abs(d))
        if change < tol:
            return T, sweep + 1
    return T, sweep + 1


if __name__ == "__main__":
    assert abs(series(0.5, 0.5) - 25) < 1e-9
    print(f"series: centre {series(0.5, 0.5):.4f}, (0.5, 0.75) {series(0.5, 0.75):.3f}, (0.5, 0.25) {series(0.5, 0.25):.3f}")
    errs = []
    for n in (21, 41):
        T, sweeps = solve_plate(n)
        c, q = T[(n - 1) // 2, (n - 1) // 2], T[3 * (n - 1) // 4, (n - 1) // 2]
        errs.append(abs(q - series(0.5, 0.75)))
        print(f"{n}x{n} grid: centre {c:.4f} C after {sweeps} SOR sweeps, error at (0.5, 0.75) {errs[-1]:.4f}")
        assert abs(c - 25) < 0.02
        assert T.max() <= 100 + 1e-12 and T.min() >= -1e-12          # maximum principle
    assert 3.0 < errs[0] / errs[1] < 5.0                              # second order
