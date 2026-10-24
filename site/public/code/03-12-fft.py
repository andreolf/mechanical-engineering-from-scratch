"""A recursive radix-2 FFT checked against NumPy, plus resolution, leakage and windowing."""
import cmath
import math
import time
import numpy as np


def fft(x):
    n = len(x)
    if n == 1:
        return [complex(x[0])]
    if n % 2:
        raise ValueError("length must be a power of two")
    E, O = fft(x[0::2]), fft(x[1::2])
    tw = [cmath.exp(-2j * math.pi * k / n) * O[k] for k in range(n // 2)]
    return [E[k] + tw[k] for k in range(n // 2)] + [E[k] - tw[k] for k in range(n // 2)]


def dft(x):
    n = len(x)
    return [sum(x[m] * cmath.exp(-2j * math.pi * k * m / n) for m in range(n)) for k in range(n)]


def amplitude_spectrum(x, window=None):
    n = len(x); w = np.ones(n) if window is None else window
    X = np.fft.rfft(x * w)
    return 2 * np.abs(X) / (n * w.mean())


if __name__ == "__main__":
    rng = np.random.default_rng(14)
    x = rng.standard_normal(256)
    assert np.allclose(fft(list(x)), np.fft.fft(x)) and np.allclose(dft(list(x[:64])), np.fft.fft(x[:64]))
    for n in (256, 1024):
        s = list(rng.standard_normal(n))
        t = time.perf_counter(); fft(s); tf = time.perf_counter() - t
        t = time.perf_counter(); dft(s[:256]); td = (time.perf_counter() - t) * (n / 256) ** 2
        print(f"N = {n}: recursive FFT {tf*1e3:6.1f} ms, DFT (scaled estimate) {td*1e3:8.0f} ms")
    fs, N = 1024, 1024
    t = np.arange(N) / fs
    sig = 2.0 * np.sin(2 * math.pi * 50 * t) + 0.5 * np.sin(2 * math.pi * 120 * t) + 0.05 * rng.standard_normal(N)
    A = amplitude_spectrum(sig)
    print(f"bins 50 and 120: {A[50]:.3f}, {A[120]:.3f} m/s^2")
    assert abs(A[50] - 2) < 0.02 and abs(A[120] - 0.5) < 0.02
    off = 2.0 * np.sin(2 * math.pi * 50.5 * t)
    rect, hann = amplitude_spectrum(off), amplitude_spectrum(off, np.sin(math.pi * np.arange(N) / N) ** 2)
    print(f"50.5 Hz tone: rectangular peak {rect.max():.2f}, Hann peak {hann.max():.2f}; 10 bins away {rect[60]:.4f} vs {hann[60]:.5f}")
    assert 1.2 < rect.max() < 1.35 and 1.6 < hann.max() < 1.8 and rect[60] > 50 * hann[60]
