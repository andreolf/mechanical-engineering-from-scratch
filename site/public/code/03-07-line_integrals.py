"""Line integrals along parametrised paths; testing whether a force field is conservative."""
import math
import numpy as np


def line_integral(F, r, dr, a, b, n=20000):
    """Gauss-Legendre-free version: composite Simpson on t."""
    t = np.linspace(a, b, n + 1)
    vals = np.array([np.dot(F(*r(ti)), dr(ti)) for ti in t])
    h = (b - a) / n
    return h / 3 * (vals[0] + vals[-1] + 4 * vals[1:-1:2].sum() + 2 * vals[2:-1:2].sum())


def is_conservative_2d(P, Q, pts, h=1e-5):
    return all(abs((Q(x + h, y) - Q(x - h, y)) / (2 * h) - (P(x, y + h) - P(x, y - h)) / (2 * h)) < 1e-6 for x, y in pts)


if __name__ == "__main__":
    line = (lambda t: (1 - t, t), lambda t: (-1.0, 1.0), 0, 1)
    arc = (lambda t: (math.cos(t), math.sin(t)), lambda t: (-math.sin(t), math.cos(t)), 0, math.pi / 2)
    F1 = lambda x, y: (2 * x * y, x * x)
    F2 = lambda x, y: (-y, x)
    W = {(f, p): line_integral(F, *path) for f, F in (("F1", F1), ("F2", F2)) for p, path in (("line", line), ("arc", arc))}
    for k, v in W.items():
        print(f"{k[0]} along the {k[1]:4s}: {v:.6f} J")
    assert abs(W["F1", "line"]) < 1e-10 and abs(W["F1", "arc"]) < 1e-10
    assert abs(W["F2", "line"] - 1) < 1e-10 and abs(W["F2", "arc"] - math.pi / 2) < 1e-10
    rng = np.random.default_rng(12); pts = rng.uniform(-2, 2, (50, 2))
    assert is_conservative_2d(lambda x, y: 2 * x * y, lambda x, y: x * x, pts)
    assert not is_conservative_2d(lambda x, y: -y, lambda x, y: x, pts)
    # gravity on a helical path: work depends only on the height drop
    m, g = 2.0, 9.81
    helix = (lambda t: (math.cos(t), math.sin(t), -0.1 * t), lambda t: (-math.sin(t), math.cos(t), -0.1), 0, 10 * math.pi)
    Wg = line_integral(lambda x, y, z: (0, 0, -m * g), *helix)
    assert abs(Wg - m * g * math.pi) < 1e-9
    print(f"gravity on a helix dropping {math.pi:.3f} m: {Wg:.4f} J = m g h")
