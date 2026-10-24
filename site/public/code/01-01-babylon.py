"""Babylonian square root as a sequence, with an epsilon-N check."""
import math


def babylon(S, a0, steps):
    seq = [a0]
    for _ in range(steps):
        a = seq[-1]
        seq.append(0.5 * (a + S / a))
    return seq


def first_N(seq, L, eps):
    """Smallest N such that |a_n - L| < eps for every n >= N in the list (None if never)."""
    N = None
    for n, a in enumerate(seq):
        if abs(a - L) < eps:
            N = n if N is None else N
        else:
            N = None
    return N


if __name__ == "__main__":
    r2 = math.sqrt(2)
    seq = babylon(2.0, 1.0, 8)
    for n, a in enumerate(seq[:6]):
        print(n, f"{a:.15f}", f"{abs(a - r2):.1e}")
    assert first_N(seq, r2, 1e-12) < 7                       # the lesson's test
    assert all(a >= r2 - 1e-15 for a in seq[1:])             # bounded below
    assert all(b <= a + 1e-15 for a, b in zip(seq[1:], seq[2:]))  # decreasing
    # quadratic convergence: e_{n+1} ~ e_n^2 / (2 a_n)
    e = [a - r2 for a in seq]
    assert abs(e[3] / (e[2] ** 2 / (2 * seq[2])) - 1) < 1e-6
    assert first_N(babylon(2.0, 4.0, 10), r2, 1e-12) == 6
