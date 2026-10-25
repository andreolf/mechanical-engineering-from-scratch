"""Sampling and aliasing: a from-scratch FFT finds the frequency a sampled sine appears at, and a
spoked wheel filmed at 25 frames per second shows the wagon-wheel effect. numpy only."""
import numpy as np

def fft(x):
    """Recursive radix-2 Cooley-Tukey FFT (len(x) a power of two)."""
    x = np.asarray(x, complex); n = len(x)
    if n == 1: return x
    e, o = fft(x[0::2]), fft(x[1::2])
    w = np.exp(-2j * np.pi * np.arange(n // 2) / n) * o
    return np.concatenate([e + w, e - w])

def alias(f, fs):
    """Apparent frequency of a sine at f sampled at fs: fold into [0, fs/2]."""
    return abs(f - fs * np.round(f / fs))

x = np.random.default_rng(0).standard_normal(256)
assert np.allclose(fft(x), np.fft.fft(x))                         # check the FFT against numpy's

fs, N = 200.0, 1024                                               # 200 Hz logger, 1024 samples
t = np.arange(N) / fs
win = 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(N) / N)            # Hann window against leakage
freqs = np.arange(N // 2 + 1) * fs / N
print("  true f    peak of FFT   alias formula")
for f in (30.0, 90.0, 110.0, 180.0, 230.0, 397.0):
    X = np.abs(fft(win * np.sin(2 * np.pi * f * t)))[: N // 2 + 1]
    k = np.argmax(X)
    d = 0.5 * (np.log(X[k - 1]) - np.log(X[k + 1])) / (np.log(X[k - 1]) - 2 * np.log(X[k]) + np.log(X[k + 1])) if 0 < k < N // 2 else 0
    fp = (k + d) * fs / N                                          # parabolic interpolation of the log peak
    print(f"{f:8.1f} {fp:12.3f} {alias(f, fs):12.3f}")
    assert abs(fp - alias(f, fs)) < 0.02

# the wagon-wheel effect: a 6-spoke rim at 50 km/h, filmed at 25 frames per second
v, D, spokes, fps = 50 / 3.6, 0.63, 6, 25.0
frot = v / (np.pi * D)                                             # rev/s
pitch = 2 * np.pi / spokes                                         # the picture repeats every spoke
frames = np.arange(50)
theta = 2 * np.pi * frot * frames / fps                            # true wheel angle at each frame
seen = np.unwrap(np.mod(theta, pitch) * spokes) / spokes           # the eye tracks the nearest spoke (minimal motion)
f_app = np.polyfit(frames / fps, seen, 1)[0] / (2 * np.pi)
f_pred = (frot * spokes - fps * np.round(frot * spokes / fps)) / spokes   # signed alias of the spoke frequency
print(f"wheel {frot:.4f} rev/s, spoke-passing frequency {frot*spokes:.3f} Hz; on film it turns {f_app:+.4f} rev/s (formula {f_pred:+.4f})")
assert abs(f_app - f_pred) < 1e-9 and f_app < 0                    # it appears to turn backwards
v_still = [fps * k / spokes * np.pi * D * 3.6 for k in (1, 2)]
print(f"the wheel looks frozen at {v_still[0]:.2f} and {v_still[1]:.2f} km/h")
assert abs(alias(v_still[0] / 3.6 / (np.pi * D) * spokes, fps)) < 1e-9
