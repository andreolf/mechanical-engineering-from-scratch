"""Vibrating string: modal synthesis of a plucked guitar string, checked against a finite-difference wave simulation."""
import math
import numpy as np


def pluck_modes(L, xp, h, N):
    """Fourier sine coefficients of a triangle of height h plucked at xp."""
    n = np.arange(1, N + 1)
    return n, 2 * h * L**2 / (n**2 * math.pi**2 * xp * (L - xp)) * np.sin(n * math.pi * xp / L)


def synth(L, c, xp, h, x_obs, t, N=40, decay=0.0):
    n, b = pluck_modes(L, xp, h, N)
    wn = n * math.pi * c / L
    return (b * np.sin(n * math.pi * x_obs / L))[None, :] @ (np.cos(np.outer(wn, t)) * np.exp(-decay * n[:, None] * t[None, :]))


def fd_string(L, c, xp, h, x_obs, T, nx=400):
    """Leapfrog on y_tt = c^2 y_xx with Courant number 1 (exact for the 1D wave equation on the grid)."""
    dx = L / nx; dt = dx / c; x = np.linspace(0, L, nx + 1)
    y = np.where(x < xp, h * x / xp, h * (L - x) / (L - xp))
    yp = y.copy(); yp[1:-1] = y[1:-1] + 0.5 * (y[2:] - 2 * y[1:-1] + y[:-2])   # first step from rest
    io = int(round(x_obs / dx)); rec = [y[io], yp[io]]
    for _ in range(int(T / dt) - 1):
        yn = np.zeros_like(y); yn[1:-1] = 2 * yp[1:-1] - y[1:-1] + (yp[2:] - 2 * yp[1:-1] + yp[:-2])
        y, yp = yp, yn; rec.append(yp[io])
    return np.arange(len(rec)) * dt, np.array(rec)


if __name__ == "__main__":
    L, T, f1 = 0.65, 70.0, 329.63          # high E string on a guitar: scale length, tension, pitch
    c = 2 * L * f1; mu = T / c**2
    print(f"wave speed {c:.1f} m/s, string mass {mu*1e3:.4f} g/m ({mu*L*1e3:.4f} g)")
    xp, h = L / 5, 0.003                    # plucked a fifth of the way along, 3 mm
    n, b = pluck_modes(L, xp, h, 12)
    print("modal amplitudes (mm):", np.round(b * 1000, 4))
    assert abs(b[4]) < 1e-15 and abs(b[9]) < 1e-15        # every 5th harmonic is missing
    tt, yfd = fd_string(L, c, xp, h, 0.1, 0.05, nx=500)
    ys = synth(L, c, xp, h, 0.1, tt, N=500)[0]
    print(f"finite differences vs modal sum at x = 0.1 m over 0.05 s: max difference {np.max(np.abs(yfd - ys))*1e6:.3f} um")
    assert np.max(np.abs(yfd - ys)) < 2e-5
    # spectrum of one second of synthesised sound (with a little decay) at the bridge pickup position
    fs = 44100; t = np.arange(fs) / fs
    y = synth(L, c, xp, h, 0.05, t, N=40, decay=0.5)[0]
    Y = np.abs(np.fft.rfft(y * np.hanning(len(y)))); fr = np.fft.rfftfreq(len(y), 1 / fs)
    # peak frequencies refined with a parabola through the log-magnitude of three bins
    lY = np.log(Y + 1e-30); pk = []
    for i in range(1, len(Y) - 1):
        if Y[i] > Y[i-1] and Y[i] >= Y[i+1] and Y[i] > 1e-3 * Y.max():
            d = 0.5 * (lY[i-1] - lY[i+1]) / (lY[i-1] - 2 * lY[i] + lY[i+1]); pk.append(fr[i] + d * (fr[1] - fr[0]))
    print("spectral peaks (Hz):", [round(float(p), 2) for p in pk[:10]])
    ratios = np.array(pk[:8]) / pk[0]
    print("ratios to the fundamental:", np.round(ratios, 4))
    assert np.allclose(ratios, np.round(ratios), atol=0.002) and abs(pk[0] - f1) < 0.05
    assert 5 not in np.round(ratios)                        # the 5th harmonic is silent
