"""Heat equation in a rod: Fourier series solution checked against an explicit finite-difference march."""
import math
import numpy as np


def series(x, t, L, alpha, T0=100.0, terms=2001):
    s = np.zeros_like(x, dtype=float)
    for n in range(1, terms, 2):
        s += 4 * T0 / (n * math.pi) * np.sin(n * math.pi * x / L) * math.exp(-alpha * (n * math.pi / L) ** 2 * t)
    return s


def explicit_fd(L, alpha, t_end, nx=101, T0=100.0, r=0.4):
    x = np.linspace(0, L, nx); dx = x[1] - x[0]
    dt = r * dx * dx / alpha                    # r = alpha dt / dx^2 must stay below 1/2 (lesson 04.14)
    steps = int(round(t_end / dt)); dt = t_end / steps
    T = np.full(nx, T0); T[0] = T[-1] = 0.0
    for _ in range(steps):
        T[1:-1] += alpha * dt / dx ** 2 * (T[2:] - 2 * T[1:-1] + T[:-2])
    return x, T


if __name__ == "__main__":
    L, a = 0.5, 1.2e-5
    tau = L * L / (math.pi ** 2 * a)
    print(f"tau_1 = {tau:.0f} s = {tau/60:.1f} min")
    centre = {m: series(np.array([L / 2]), m * 60, L, a)[0] for m in (10, 30, 60, 120)}
    for m, v in centre.items():
        print(f"centre after {m:3d} min: {v:6.2f} C")
    assert abs(centre[60] - 400 / math.pi * math.exp(-3600 / tau)) < 0.01
    assert abs(centre[10] - 92.56) < 0.01 and abs(centre[30] - 54.25) < 0.01
    t45 = tau * math.log(400 / math.pi / 45)
    print(f"time to 45 C: {t45/60:.1f} min")
    # the finite-difference march agrees with the series
    x, T = explicit_fd(L, a, 1800)
    assert np.max(np.abs(T - series(x, 1800, L, a))) < 0.05
    # energy decays monotonically and the maximum principle holds
    profiles = [series(x, m * 60, L, a) for m in range(1, 121, 10)]
    assert all(p.max() <= 100 + 1e-9 and p.min() >= -1e-9 for p in profiles)
    assert all(np.sum(p2) < np.sum(p1) for p1, p2 in zip(profiles, profiles[1:]))
