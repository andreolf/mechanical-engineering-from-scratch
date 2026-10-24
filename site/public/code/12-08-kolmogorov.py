"""Turbulence phenomenology: Kolmogorov scales, and a synthetic signal with a -5/3 spectrum analysed by FFT."""
import math
import numpy as np


def kolmogorov(nu, eps):
    eta = (nu ** 3 / eps) ** 0.25
    tau = (nu / eps) ** 0.5
    u = (nu * eps) ** 0.25
    return eta, tau, u


def synthetic_signal(n, dt, slope=-5 / 3, f0=0.05, seed=1):
    """Random Gaussian Fourier coefficients whose expected power falls as f^slope above f0."""
    rng = np.random.default_rng(seed)
    f = np.fft.rfftfreq(n, dt)
    S = np.zeros_like(f); S[1:] = (1 + (f[1:] / f0) ** 2) ** (slope / 2)
    coef = np.sqrt(S / 2) * (rng.standard_normal(len(f)) + 1j * rng.standard_normal(len(f)))
    u = np.fft.irfft(coef, n)
    return u / u.std()


def spectrum_slope(u, dt, fmin, fmax):
    f = np.fft.rfftfreq(len(u), dt)
    P = np.abs(np.fft.rfft(u)) ** 2
    sel = (f >= fmin) & (f <= fmax)
    return np.polyfit(np.log(f[sel]), np.log(P[sel]), 1)[0]


if __name__ == "__main__":
    # the Rhine near Basel: 2 m/s, 6 m deep; large eddies ~ depth, velocity fluctuation ~ 10 % of the mean
    nu = 1.0e-6; u_rms = 0.2; L = 6.0
    eps = u_rms ** 3 / L
    eta, tau, ueta = kolmogorov(nu, eps)
    print(f"dissipation eps ~ u'^3/L = {eps:.6f} W/kg")
    print(f"Kolmogorov length {eta*1000:.4f} mm, time {tau*1000:.2f} ms, velocity {ueta*1000:.3f} mm/s")
    assert abs(eta * ueta / nu - 1) < 1e-12                    # the Reynolds number of the smallest eddies is 1
    print(f"scale separation L/eta = {L/eta:.0f} = Re_L^(3/4) = {(u_rms*L/nu)**0.75:.0f}")
    assert abs(L / eta - (u_rms * L / nu) ** 0.75) < 1e-6 * L / eta
    # synthetic velocity record at 1 kHz
    dt = 1e-3; u = synthetic_signal(2 ** 16, dt)
    s = spectrum_slope(u, dt, 1.0, 100.0)
    print(f"synthetic record: mean {u.mean():.2e}, rms {u.std():.3f}, fitted spectral slope {s:.4f} (-5/3 = {-5/3:.4f})")
    assert abs(s + 5 / 3) < 0.05
