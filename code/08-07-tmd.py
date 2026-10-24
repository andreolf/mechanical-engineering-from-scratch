"""Tuned mass damper on a footbridge: Den Hartog tuning, then a numerical optimum with SciPy."""
import math
import numpy as np
from scipy.optimize import minimize


def response(r, mu, f, zt, zs=0.0):
    """|X1| / (F0 / k1) of the structure (mass ratio mu, TMD frequency ratio f, TMD damping zt, structural damping zs)
    at forcing ratio r = w / w1, from the 2x2 complex frequency-response solve."""
    out = np.empty_like(r)
    for i, ri in enumerate(r):
        # units: m1 = 1, k1 = 1, w1 = 1
        m2 = mu; k2 = mu * f**2; c2 = 2 * zt * mu * f; c1 = 2 * zs
        A = np.array([[1 + k2 - ri**2 + 1j * ri * (c1 + c2), -k2 - 1j * ri * c2],
                      [-k2 - 1j * ri * c2, k2 - m2 * ri**2 + 1j * ri * c2]])
        out[i] = abs(np.linalg.solve(A, [1.0, 0.0])[0])
    return out


R = np.linspace(0.7, 1.3, 3001)
peak = lambda mu, f, zt, zs: response(R, mu, f, zt, zs).max()

if __name__ == "__main__":
    M1, f1, zs = 50e3, 2.0, 0.005             # modal mass (kg), first vertical mode (Hz), steel bridge damping
    mu = 0.02
    print(f"no TMD: peak amplification 1/(2 zeta) = {1/(2*zs):.1f}")
    f_dh = 1 / (1 + mu); z_dh = math.sqrt(3 * mu / (8 * (1 + mu)**3))
    p_dh = peak(mu, f_dh, z_dh, zs)
    print(f"Den Hartog, mu = {mu}: TMD mass {mu*M1:.0f} kg, tuned to {f_dh*f1:.4f} Hz, damping {z_dh:.4f}; peak {p_dh:.2f} (formula sqrt(1 + 2/mu) = {math.sqrt(1+2/mu):.2f} for an undamped bridge)")
    res = minimize(lambda q: peak(mu, q[0], q[1], zs), [f_dh, z_dh], method="Nelder-Mead", options={"xatol": 1e-5, "fatol": 1e-4})
    print(f"numerical optimum: f = {res.x[0]:.4f}, zeta = {res.x[1]:.4f}, peak {res.fun:.2f}")
    assert res.fun <= p_dh + 1e-9 and res.fun < 1 / (2 * zs) / 5
    # mistuning: the TMD loses much of its effect if the bridge frequency is off by 5 %
    p_off = peak(mu, f_dh / 1.05, z_dh, zs)
    print(f"TMD tuned for 2.00 Hz on a bridge that is really at 2.10 Hz: peak {p_off:.2f}")
    # untuned (TMD at the wrong frequency or locked) for comparison
    p_lock = peak(mu, 3.0, z_dh, zs)
    print(f"TMD tuned to 3 times the bridge frequency: peak {p_lock:.2f}")
    assert p_dh < p_off < p_lock
    for m in (0.01, 0.05):
        print(f"mu = {m}: Den Hartog peak {peak(m, 1/(1+m), math.sqrt(3*m/(8*(1+m)**3)), zs):.2f}")
