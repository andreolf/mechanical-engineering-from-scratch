"""Monte Carlo a Fermi estimate with log-uniform inputs, using only the standard library."""
import math
import random


def log_uniform(best, k, rng):
    return best * k ** rng.uniform(-1.0, 1.0)


def canal_volume(rng, k=2.0):
    w = log_uniform(0.8, k, rng)    # width, m
    d = log_uniform(0.3, k, rng)    # depth, m
    v = log_uniform(0.5, k, rng)    # mean speed, m/s
    return w * d * v * 86400.0      # m^3 per day


def percentile(sorted_xs, p):
    i = p * (len(sorted_xs) - 1)
    lo, hi = math.floor(i), math.ceil(i)
    return sorted_xs[lo] + (sorted_xs[hi] - sorted_xs[lo]) * (i - lo)


if __name__ == "__main__":
    rng = random.Random(42)
    xs = sorted(canal_volume(rng) for _ in range(200_000))
    med, p05, p95 = (percentile(xs, p) for p in (0.5, 0.05, 0.95))
    hand = 0.8 * 0.3 * 0.5 * 86400
    sigma = math.log(2) * math.sqrt(3 / 3)
    print(f"hand {hand:.0f}, median {med:.0f}, 90% [{p05:.0f}, {p95:.0f}]")
    # median within one decade of the hand calculation (the lesson's test)
    assert abs(math.log10(med / hand)) < 1
    # in fact the median sits on the hand value, because log-errors are symmetric
    assert abs(med / hand - 1) < 0.02
    # the quadrature formula predicts the 90% factor within a few percent
    assert abs((p95 / med) / math.exp(1.645 * sigma) - 1) < 0.06
