"""Viscous damping: simulate a decaying oscillation and recover the damping ratio from the logarithmic decrement."""
import math
import numpy as np


def free_decay(m, c, k, x0, t_end, dt):
    """RK4 on x'' = -(c x' + k x) / m."""
    f = lambda s: np.array([s[1], -(c * s[1] + k * s[0]) / m])
    s = np.array([x0, 0.0]); out = [s[0]]
    for _ in range(int(round(t_end / dt))):
        k1 = f(s); k2 = f(s + dt / 2 * k1); k3 = f(s + dt / 2 * k2); k4 = f(s + dt * k3)
        s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4); out.append(s[0])
    return np.arange(len(out)) * dt, np.array(out)


def peaks(t, x):
    """Local maxima refined with a parabola through three samples."""
    i = np.where((x[1:-1] > x[:-2]) & (x[1:-1] >= x[2:]) & (x[1:-1] > 0))[0] + 1
    a, b, c = x[i - 1], x[i], x[i + 1]
    d = 0.5 * (a - c) / (a - 2 * b + c)
    return t[i] + d * (t[1] - t[0]), b - 0.25 * (a - c) * d


def zeta_from_decrement(xp, n=1):
    """delta = ln(x_i / x_{i+n}) / n, then zeta = delta / sqrt(4 pi^2 + delta^2)."""
    delta = math.log(xp[0] / xp[n]) / n
    return delta / math.sqrt(4 * math.pi**2 + delta**2), delta


if __name__ == "__main__":
    m, k, c = 300.0, 30e3, 1200.0
    zeta = c / (2 * math.sqrt(k * m))
    wn = math.sqrt(k / m); wd = wn * math.sqrt(1 - zeta**2)
    print(f"zeta = c / (2 sqrt(k m)) = {zeta:.3f}, omega_d = {wd:.4f} rad/s")
    t, x = free_decay(m, c, k, 0.05, 4.0, 1e-3)
    tp, xp = peaks(t, x)
    z_est, delta = zeta_from_decrement(xp, 1)
    print(f"first peaks: {', '.join(f'{v*1000:.2f}' for v in xp[:4])} mm; ratio per cycle {xp[1]/xp[0]:.4f}")
    print(f"log decrement {delta:.4f} (theory {2*math.pi*zeta/math.sqrt(1-zeta**2):.4f}); estimated zeta {z_est:.4f}")
    assert abs(z_est / zeta - 1) < 0.02
    print(f"damped period from peaks {np.mean(np.diff(tp)):.4f} s, theory {2*math.pi/wd:.4f} s")
    # a lightly damped structure: count many cycles for accuracy
    c2 = 2 * 0.01 * math.sqrt(k * m)
    t, x = free_decay(m, c2, k, 0.05, 20.0, 1e-3)
    tp, xp = peaks(t, x)
    z1, _ = zeta_from_decrement(xp, 1); z10, _ = zeta_from_decrement(xp, 10)
    print(f"zeta 0.01: one-cycle estimate {z1:.5f}, ten-cycle estimate {z10:.5f}")
    assert abs(z10 / 0.01 - 1) < 0.02
    # with measurement noise: smooth with a 21-sample moving average, take the largest sample near each
    # expected peak, then fit a straight line to ln(peak) over many cycles
    rng = np.random.default_rng(1); xn = np.convolve(x + rng.normal(0, 5e-4, x.size), np.ones(21) / 21, mode="same")
    Td = 2 * math.pi / (wn * math.sqrt(1 - 0.01**2)); dt = t[1] - t[0]
    cyc = np.array([np.max(xn[int((j - 0.05) * Td / dt):int((j + 0.05) * Td / dt)]) for j in range(1, 30)])
    z1n, _ = zeta_from_decrement(cyc, 1)
    slope = np.polyfit(np.arange(1, 30), np.log(cyc), 1)[0]
    zfit = -slope / math.sqrt(4 * math.pi**2 + slope**2)
    print(f"with 0.5 mm noise: one-cycle estimate {z1n:.4f}, straight-line fit over 29 cycles {zfit:.4f}")
    assert abs(zfit / 0.01 - 1) < 0.05
