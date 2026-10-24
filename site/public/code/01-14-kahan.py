"""Naive versus Kahan compensated summation, plus two convergent series."""
import math


def naive_sum(xs):
    s = 0.0
    for x in xs:
        s += x
    return s


def kahan_sum(xs):
    s = c = 0.0
    for x in xs:
        y = x - c
        t = s + y
        c = (t - s) - y      # what the addition just rounded away
        s = t
    return s


if __name__ == "__main__":
    n = 10_000_000
    xs = [0.1] * n
    ref = math.fsum(xs)                     # correctly rounded reference
    e_naive, e_kahan = abs(naive_sum(xs) - ref), abs(kahan_sum(xs) - ref)
    print(f"sum of 1e7 x 0.1: naive error {e_naive:.2e}, Kahan error {e_kahan:.2e}")
    assert e_kahan < e_naive / 1000         # the lesson's test

    e, h0, g = 0.8, 2.0, 9.81
    D = h0 + 2 * h0 * e**2 / (1 - e**2)
    D_partial = h0 + 2 * h0 * kahan_sum(e ** (2 * k) for k in range(1, 400))
    assert abs(D - 9.1111) < 1e-4 and abs(D - D_partial) < 1e-12
    t0 = math.sqrt(2 * h0 / g)
    assert abs(t0 * (1 + 2 * e / (1 - e)) - 5.7470) < 1e-3
    basel = kahan_sum(1.0 / (k * k) for k in range(1, 100_001))
    assert abs(basel - (math.pi**2 / 6 - 1 / 100_000)) < 1e-9   # tail of 1/k^2 is about 1/n
    print(f"bouncing ball travels {D:.3f} m")
