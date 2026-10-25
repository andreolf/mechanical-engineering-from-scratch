"""IIR low-pass filters from their difference equations: a first-order RC filter and a second-order
Butterworth biquad designed with the bilinear transform. Checked against the exact digital frequency
response, and against scipy.signal if it happens to be installed. The filter itself is numpy only."""
import numpy as np

def butter2(fc, fs):
    """2nd-order Butterworth low-pass H(s) = w^2 / (s^2 + sqrt2 w s + w^2), bilinear transform
    s = (2/T)(z-1)/(z+1) with the cutoff pre-warped so |H| = 1/sqrt2 exactly at fc."""
    K = np.tan(np.pi * fc / fs)                      # = w_analogue T / 2 after pre-warping
    a0 = 1 + np.sqrt(2) * K + K * K
    b = np.array([K * K, 2 * K * K, K * K]) / a0
    a = np.array([1.0, 2 * (K * K - 1) / a0, (1 - np.sqrt(2) * K + K * K) / a0])
    return b, a

def rc1(fc, fs):
    """1st-order RC low-pass 1/(1 + s RC) by the bilinear transform, pre-warped at fc."""
    K = np.tan(np.pi * fc / fs)
    return np.array([K, K]) / (1 + K), np.array([1.0, (K - 1) / (1 + K)])

def lfilter(b, a, x):
    """Direct form I: a0 y[n] = sum b_k x[n-k] - sum_{k>=1} a_k y[n-k]."""
    y = np.zeros(len(x))
    for n in range(len(x)):
        acc = 0.0
        for k in range(len(b)):
            if n - k >= 0: acc += b[k] * x[n - k]
        for k in range(1, len(a)):
            if n - k >= 0: acc -= a[k] * y[n - k]
        y[n] = acc / a[0]
    return y

def freqz(b, a, f, fs):
    z = np.exp(1j * 2 * np.pi * np.asarray(f) / fs)
    return np.polyval(b[::-1], 1 / z) / np.polyval(a[::-1], 1 / z)

fs, fc = 500.0, 10.0
b, a = butter2(fc, fs)
print("biquad b =", np.round(b, 8), " a =", np.round(a, 8))
poles = np.roots(a)
print(f"poles |z| = {np.abs(poles).round(6)} (inside the unit circle, so stable)")
assert np.all(np.abs(poles) < 1)

# exact digital magnitude: the bilinear map turns f into tan(pi f / fs), so |H| = 1/sqrt(1 + (tan/tan_c)^4)
for f in (2.0, 10.0, 50.0):
    H = abs(freqz(b, a, f, fs))
    ex = 1 / np.sqrt(1 + (np.tan(np.pi * f / fs) / np.tan(np.pi * fc / fs)) ** 4)
    an = 1 / np.sqrt(1 + (f / fc) ** 4)
    print(f"f = {f:5.1f} Hz: |H| = {H:.6f} ({20*np.log10(H):7.2f} dB); exact {ex:.6f}; analogue prototype {an:.6f}")
    assert abs(H - ex) < 1e-12

# a vibrating sensor: 2 Hz motion of 1 g plus 0.5 g of 50 Hz mains pick-up and white noise
t = np.arange(0, 10, 1 / fs)
rng = np.random.default_rng(3)
x = np.sin(2 * np.pi * 2 * t) + 0.5 * np.sin(2 * np.pi * 50 * t) + 0.1 * rng.standard_normal(len(t))
y = lfilter(b, a, x)
ss = t > 2                                            # drop the start-up transient
def amp(sig, f):                                      # least-squares amplitude of one tone
    M = np.column_stack([np.sin(2 * np.pi * f * t[ss]), np.cos(2 * np.pi * f * t[ss])])
    return np.hypot(*np.linalg.lstsq(M, sig[ss], rcond=None)[0])
for f, A in ((2.0, 1.0), (50.0, 0.5)):
    print(f"{f:4.0f} Hz tone: in {amp(x, f):.4f}, out {amp(y, f):.4f}, gain {amp(y, f)/amp(x, f):.4f} (|H| = {abs(freqz(b, a, f, fs)):.4f})")
    assert abs(amp(y, f) / amp(x, f) - abs(freqz(b, a, f, fs))) < 0.01
lag = -np.angle(freqz(b, a, 2.0, fs)) / (2 * np.pi * 2.0)
print(f"phase lag at 2 Hz = {np.degrees(-np.angle(freqz(b, a, 2.0, fs))):.2f} deg = {lag*1e3:.2f} ms delay")

b1, a1 = rc1(fc, fs)
assert abs(abs(freqz(b1, a1, fc, fs)) - 1 / np.sqrt(2)) < 1e-12
print(f"first-order RC at 50 Hz: |H| = {abs(freqz(b1, a1, 50, fs)):.4f}, Butterworth: {abs(freqz(b, a, 50, fs)):.4f}")

try:
    from scipy import signal                         # optional cross-check, not needed to run the lesson
    bs, as_ = signal.butter(2, fc, fs=fs)
    assert np.allclose(bs, b) and np.allclose(as_, a) and np.allclose(signal.lfilter(b, a, x), y)
    print("matches scipy.signal.butter and scipy.signal.lfilter")
except ImportError:
    print("scipy not installed: skipped the optional cross-check")
