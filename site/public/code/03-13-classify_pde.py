"""Classify second-order PDEs and compute characteristic directions."""
import math
import numpy as np


def classify(A, B, C, tol=1e-12):
    d = B * B - 4 * A * C
    return "hyperbolic" if d > tol else "elliptic" if d < -tol else "parabolic"


def characteristic_slopes(A, B, C):
    """Roots of A (dy/dx)^2 - B (dy/dx) + C = 0, real only for hyperbolic or parabolic equations."""
    d = B * B - 4 * A * C
    if d < 0:
        return ()
    return tuple(sorted(((B - math.sqrt(d)) / (2 * A), (B + math.sqrt(d)) / (2 * A))))


if __name__ == "__main__":
    assert classify(3, 2, 1) == "elliptic" and classify(1, -4, 4) == "parabolic"
    assert classify(1, 0, 1) == "elliptic"                 # Laplace
    assert classify(1.2e-5, 0, 0) == "parabolic"           # heat, with y = t
    assert classify(343.0 ** 2, 0, -1) == "hyperbolic"     # wave, with y = t
    for M in (0.5, 0.99, 1.5, 2.0, 3.0):
        kind = classify(1 - M * M, 0, 1)
        line = f"M = {M}: {kind}"
        if M > 1:
            s = characteristic_slopes(1 - M * M, 0, 1)
            mu = math.degrees(math.atan(abs(s[1])))
            assert abs(mu - math.degrees(math.asin(1 / M))) < 1e-9
            line += f", Mach angle {mu:.2f} deg"
        print(line)
    # wave equation: characteristics x +- c t, so dt/dx = +-1/c
    s = characteristic_slopes(1.0, 0.0, -1 / 343.0 ** 2)
    assert np.allclose(np.abs(s), 1 / 343.0)
    # numerical check: a wave pulse moves exactly along its characteristic
    c = 2.0; f = lambda z: np.exp(-50 * z ** 2)
    x = np.linspace(-1, 5, 6001)
    for t in (0.5, 1.0, 1.5):
        u = 0.5 * (f(x - c * t) + f(x + c * t))
        right = x[x > 0][np.argmax(u[x > 0])]
        assert abs(right - c * t) < 2e-3
