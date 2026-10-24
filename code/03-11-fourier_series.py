"""Fourier coefficients by numerical integration, Parseval's theorem and the Gibbs overshoot."""
import math
import numpy as np


def coefficients(f, L, N, m=20000):
    x = -L + 2 * L * (np.arange(m) + 0.5) / m            # midpoint rule, spectrally accurate for periodic f
    fx = f(x); dx = 2 * L / m
    a = [np.sum(fx * np.cos(n * math.pi * x / L)) * dx / L for n in range(N + 1)]
    b = [0.0] + [np.sum(fx * np.sin(n * math.pi * x / L)) * dx / L for n in range(1, N + 1)]
    return np.array(a), np.array(b)


def partial_sum(a, b, L, x):
    s = a[0] / 2 * np.ones_like(x)
    for n in range(1, len(a)):
        s += a[n] * np.cos(n * math.pi * x / L) + b[n] * np.sin(n * math.pi * x / L)
    return s


if __name__ == "__main__":
    square = lambda x: np.sign(np.sin(x))
    a, b = coefficients(square, math.pi, 15)
    expected = [4 / (math.pi * n) if n % 2 else 0.0 for n in range(1, 16)]
    assert np.allclose(b[1:], expected, atol=1e-6) and np.allclose(a, 0, atol=1e-9)
    print("square wave b_1..b_5:", np.round(b[1:6], 4))
    # Parseval: mean square of the square wave is 1
    a, b = coefficients(square, math.pi, 4001)
    assert abs(0.5 * np.sum(b[1:] ** 2) - 1) < 1e-3
    # Gibbs: the peak of the partial sum tends to 1.1790, not 1
    x = np.linspace(1e-6, math.pi - 1e-6, 200001)
    peaks = [partial_sum(*coefficients(square, math.pi, 2 * N), math.pi, x).max() for N in (10, 50)]
    print("Gibbs peaks:", np.round(peaks, 4))
    assert all(abs(p - 1.1790) < 2e-3 for p in peaks)
    # coefficient decay: jump -> 1/n, kink -> 1/n^2
    tri = lambda x: 2 / math.pi * np.arcsin(np.sin(x))
    _, bt = coefficients(tri, math.pi, 21)
    assert abs(abs(bt[1] / bt[21]) - 21 ** 2) < 1 and abs(b[1] / b[21] - 21) < 0.01
    # the cam example: third harmonic at resonance dominates
    F3, F1 = 400 / (3 * math.pi), 400 / math.pi
    print(f"fundamental x 1.125 = {F1 * 1.125:.0f} N, third harmonic x 10 = {F3 * 10:.0f} N")
    assert F3 * 10 > 2.9 * F1 * 1.125
