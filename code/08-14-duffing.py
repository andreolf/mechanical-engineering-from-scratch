"""The Duffing oscillator: frequency sweeps up and down show the jump phenomenon and hysteresis."""
import math
import numpy as np

zeta, beta, F = 0.02, 1.0, 0.1          # x'' + 2 zeta x' + x + beta x^3 = F cos(w t)


def rk4_cycles(s, w, cycles, per=80):
    dt = 2 * math.pi / w / per; t = 0.0; xs = []
    f = lambda t, s: np.array([s[1], F * math.cos(w * t) - 2 * zeta * s[1] - s[0] - beta * s[0]**3])
    for i in range(cycles * per):
        k1 = f(t, s); k2 = f(t + dt/2, s + dt/2*k1); k3 = f(t + dt/2, s + dt/2*k2); k4 = f(t + dt, s + dt*k3)
        s = s + dt/6*(k1 + 2*k2 + 2*k3 + k4); t += dt; xs.append(s[0])
    return s, np.array(xs)


def sweep(ws, cycles=150, keep=20):
    """Step the forcing frequency, starting each step from the previous end state (t restarts at a whole cycle)."""
    s = np.zeros(2); amp = []
    for w in ws:
        s, xs = rk4_cycles(s, w, cycles)
        amp.append((xs[-80 * keep:].max() - xs[-80 * keep:].min()) / 2)
    return np.array(amp)


def harmonic_balance(w):
    """Amplitudes A > 0 solving [(1 - w^2) A + 3/4 beta A^3]^2 + (2 zeta w A)^2 = F^2 (a cubic in A^2)."""
    a = 9 / 16 * beta**2; b = 1.5 * beta * (1 - w * w); c = (1 - w * w)**2 + (2 * zeta * w)**2
    r = np.roots([a, b, c, -F * F])
    return sorted(math.sqrt(z.real) for z in r if abs(z.imag) < 1e-9 and z.real > 0)


if __name__ == "__main__":
    ws = np.linspace(0.8, 2.0, 61)
    up = sweep(ws); down = sweep(ws[::-1])[::-1]
    for w, a, b in zip(ws[::6], up[::6], down[::6]):
        print(f"w = {w:.2f}: sweep up {a:.4f}, sweep down {b:.4f}, harmonic balance {', '.join(f'{x:.4f}' for x in harmonic_balance(w))}")
    gap = np.abs(up - down)
    print(f"largest up/down difference {gap.max():.3f} at w = {ws[np.argmax(gap)]:.2f}")
    assert gap.max() > 0.5
    # where both agree with harmonic balance (single-valued region) the sweep is accurate
    for w, a in zip(ws, up):
        hb = harmonic_balance(w)
        if len(hb) == 1: assert abs(a / hb[0] - 1) < 0.03, (w, a, hb)
    i_up = np.argmax(np.diff(up) < -0.3); i_dn = np.argmax(np.diff(down) < -0.3)
    assert np.any(np.diff(up) < -0.3) and np.any(np.diff(down) < -0.3) and ws[i_dn] < ws[i_up]
    print(f"jump down during the upward sweep between w = {ws[i_up]:.2f} and {ws[i_up+1]:.2f}; jump up during the downward sweep between {ws[i_dn]:.2f} and {ws[i_dn+1]:.2f}")
    # the linear oscillator (beta = 0) has no hysteresis
    beta = 0.0
    lu = sweep(ws[::4], 300); ld = sweep(ws[::4][::-1], 300)[::-1]
    print(f"linear: largest up/down difference {np.abs(lu - ld).max():.1e}")
    assert np.abs(lu - ld).max() < 1e-3
