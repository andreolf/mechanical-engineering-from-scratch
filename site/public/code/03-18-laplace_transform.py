"""Step response by partial fractions (from the poles) checked against direct ODE integration."""
import math
import numpy as np


def step_response_2nd(m, c, k, F, t):
    """Closed form for an underdamped system starting at rest."""
    wn = math.sqrt(k / m); z = c / (2 * math.sqrt(k * m)); wd = wn * math.sqrt(1 - z * z); s = z * wn
    return F / k * (1 - np.exp(-s * t) * (np.cos(wd * t) + s / wd * np.sin(wd * t)))


def residues(num, den):
    """Partial fractions for distinct poles: X(s) = sum r_i / (s - p_i)."""
    p = np.roots(den); dden = np.polyder(den)
    return p, np.polyval(num, p) / np.polyval(dden, p)


def rk4(f, y0, t):
    y = np.array(y0, float); out = [y.copy()]
    for a, b in zip(t[:-1], t[1:]):
        h = b - a; k1 = f(a, y); k2 = f(a + h / 2, y + h / 2 * k1); k3 = f(a + h / 2, y + h / 2 * k2); k4 = f(b, y + h * k3)
        y = y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4); out.append(y.copy())
    return np.array(out)


if __name__ == "__main__":
    m, c, k, F = 1.0, 4.0, 20.0, 10.0
    t = np.linspace(0, 4, 4001)
    p, r = residues([F], np.polymul([1, 0], [m, c, k]))
    x_pf = np.real(sum(ri * np.exp(pi * t) for pi, ri in zip(p, r)))
    x_cf = step_response_2nd(m, c, k, F, t)
    x_ode = rk4(lambda _, y: np.array([y[1], (F - c * y[1] - k * y[0]) / m]), [0, 0], t)[:, 0]
    print("poles:", np.round(p, 6))
    assert np.max(np.abs(x_pf - x_cf)) < 1e-12 and np.max(np.abs(x_ode - x_cf)) < 1e-10
    i = np.argmax(x_cf)
    print(f"peak {x_cf[i]:.4f} m at t = {t[i]:.3f} s, final value {x_cf[-1]:.4f} m")
    assert abs(t[i] - math.pi / 4) < 1e-3 and abs(x_cf[i] / 0.5 - 1 - math.exp(-math.pi / 2)) < 1e-6
    # final value theorem: lim s->0 of s X(s) = F / k
    s = 1e-9
    assert abs(s * F / (s * (m * s * s + c * s + k)) - F / k) < 1e-9
