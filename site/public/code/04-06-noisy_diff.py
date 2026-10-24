"""Differentiating noisy measurements: raw differences amplify noise like sigma/h; Savitzky-Golay fits a local polynomial first."""
import numpy as np


def savgol_coeffs(half, order, deriv, h):
    """Least-squares polynomial of given order on 2*half+1 points; return the weights for the deriv-th derivative at the centre."""
    k = np.arange(-half, half + 1)
    A = np.vander(k, order + 1, increasing=True)          # columns 1, k, k^2, ...
    pinv = np.linalg.pinv(A)                               # (order+1) x (2 half + 1)
    fact = np.prod(np.arange(1, deriv + 1)) if deriv else 1
    return fact * pinv[deriv] / h**deriv


def savgol(y, half, order, deriv, h):
    c = savgol_coeffs(half, order, deriv, h)
    out = np.convolve(y, c[::-1], mode="same")
    out[:half] = np.nan; out[-half:] = np.nan              # no full window at the ends
    return out


if __name__ == "__main__":
    rng = np.random.default_rng(1)
    # a test-rig position sensor: x(t) = 0.05 sin(2 pi 1.5 t) m, sampled at 1 kHz with 0.1 mm noise
    h = 1e-3; t = np.arange(0, 2, h)
    x_true = 0.05 * np.sin(2 * np.pi * 1.5 * t); v_true = 0.05 * 2 * np.pi * 1.5 * np.cos(2 * np.pi * 1.5 * t)
    x = x_true + rng.normal(0, 1e-4, t.size)
    v_raw = np.full_like(x, np.nan); v_raw[1:-1] = (x[2:] - x[:-2]) / (2 * h)
    v_sg = savgol(x, 25, 2, 1, h)
    m = slice(30, -30)
    e_raw = np.sqrt(np.nanmean((v_raw[m] - v_true[m]) ** 2)); e_sg = np.sqrt(np.nanmean((v_sg[m] - v_true[m]) ** 2))
    print(f"peak true speed {v_true.max():.4f} m/s")
    print(f"RMS velocity error: raw central difference {e_raw:.4f} m/s, Savitzky-Golay (51 points, quadratic) {e_sg:.5f} m/s")
    print(f"predicted raw noise sigma/(sqrt(2) h) = {1e-4 / (np.sqrt(2) * h):.4f} m/s")
    assert e_sg < e_raw / 10
    assert abs(e_raw - 1e-4 / (np.sqrt(2) * h)) < 0.01
    # SG weights reproduce derivatives of polynomials up to the fitted order exactly
    c = savgol_coeffs(3, 2, 1, 1.0)
    k = np.arange(-3, 4)
    assert abs(c @ (2 + 3 * k + 0.5 * k**2) - 3) < 1e-12
    from scipy.signal import savgol_filter
    ref = savgol_filter(x, 51, 2, deriv=1, delta=h)
    assert np.allclose(ref[m], v_sg[m], atol=1e-10)
    print("matches scipy.signal.savgol_filter")
