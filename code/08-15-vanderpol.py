"""Self-excited vibration: the Van der Pol oscillator and its limit cycle."""
import math
import numpy as np


def vdp(mu, s0, t_end, dt=1e-3):
    f = lambda s: np.array([s[1], mu * (1 - s[0]**2) * s[1] - s[0]])
    s = np.array(s0, float); out = [s.copy()]
    for _ in range(int(round(t_end / dt))):
        k1 = f(s); k2 = f(s + dt/2*k1); k3 = f(s + dt/2*k2); k4 = f(s + dt*k3)
        s = s + dt/6*(k1 + 2*k2 + 2*k3 + k4); out.append(s.copy())
    return np.arange(len(out)) * dt, np.array(out)


def cycle_stats(t, s, t_from):
    x = s[:, 0]; sel = t > t_from
    i = np.where((x[:-1] < 0) & (x[1:] >= 0) & sel[:-1])[0]
    tc = t[i] - x[i] * (t[i+1] - t[i]) / (x[i+1] - x[i])
    return x[sel].max(), np.mean(np.diff(tc))


if __name__ == "__main__":
    mu = 1.0
    starts = [(0.01, 0.0), (0.5, 0.0), (3.0, 0.0), (-4.0, 4.0), (0.0, -6.0)]
    res = []
    for s0 in starts:
        t, s = vdp(mu, s0, 80.0)
        A, T = cycle_stats(t, s, 50.0); res.append((A, T))
        print(f"start {s0}: limit-cycle amplitude {A:.4f}, period {T:.4f}")
    A0, T0 = res[0]
    assert all(abs(A - A0) < 1e-3 and abs(T - T0) < 1e-3 for A, T in res)
    assert abs(A0 - 2.0086) < 2e-3 and abs(T0 - 6.6633) < 2e-3
    # energy balance: negative damping inside |x| < 1 pumps energy in, positive damping outside takes it out
    t, s = vdp(mu, (0.01, 0.0), 80.0)
    sel = t > 60; x, v = s[sel, 0], s[sel, 1]; dt = t[1] - t[0]
    pumped = np.sum(mu * (1 - x**2) * v * v * (np.abs(x) < 1)) * dt
    removed = np.sum(mu * (1 - x**2) * v * v * (np.abs(x) >= 1)) * dt
    print(f"over 20 s on the cycle: energy pumped in {pumped:.3f}, removed {-removed:.3f} (net {pumped + removed:.1e})")
    for m in (0.1, 5.0):
        t, s = vdp(m, (0.5, 0.0), 120.0, 5e-4)
        A, T = cycle_stats(t, s, 80.0)
        print(f"mu = {m}: amplitude {A:.4f}, period {T:.4f} (small mu: 2 and 2 pi; large mu: relaxation, T ~ (3 - 2 ln 2) mu = {(3-2*math.log(2))*m:.3f})")
