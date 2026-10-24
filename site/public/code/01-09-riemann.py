"""Left, right and midpoint Riemann sums and their convergence rates."""
import math


def riemann(f, a, b, n, rule="mid"):
    h = (b - a) / n
    off = {"left": 0.0, "mid": 0.5, "right": 1.0}[rule]
    return h * sum(f(a + (i + off) * h) for i in range(n))


def rate(f, a, b, exact, rule, ns=(8, 16, 32, 64, 128, 256)):
    """Observed order p in error ~ n^-p, from successive doublings."""
    e = [abs(riemann(f, a, b, n, rule) - exact) for n in ns]
    return sum(math.log2(e[i] / e[i + 1]) for i in range(len(e) - 1)) / (len(e) - 1)


if __name__ == "__main__":
    p1, V1, V2 = 1e5, 1e-3, 0.5e-3
    p = lambda V: p1 * V1 / V
    W = p1 * V1 * math.log(V1 / V2)
    left, mid = riemann(p, V2, V1, 4, "left"), riemann(p, V2, V1, 4, "mid")
    print(f"exact {W:.4f} J, left {left:.4f}, mid {mid:.4f}")
    assert abs(W - 69.3147) < 1e-4 and abs(left - 75.9524) < 1e-4 and abs(mid - 69.1220) < 1e-4
    r_left, r_mid = rate(p, V2, V1, W, "left"), rate(p, V2, V1, W, "mid")
    print(f"observed order: left {r_left:.3f}, midpoint {r_mid:.3f}")
    assert abs(r_left - 1) < 0.05 and abs(r_mid - 2) < 0.02   # midpoint is O(1/n^2)
