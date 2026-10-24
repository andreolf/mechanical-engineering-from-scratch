"""Distributed transient conduction: explicit finite differences in 1D and 2D, checked against the Fourier series and the product solution."""
import math
import numpy as np


def slab_series(x, t, L, alpha, terms=200):
    """theta/theta_i for a slab -L..L, initially uniform, both faces suddenly held at the surrounding temperature."""
    s = np.zeros_like(np.asarray(x, dtype=float))
    for n in range(terms):
        lam = (2 * n + 1) * math.pi / (2 * L)
        s = s + 4 * (-1) ** n / ((2 * n + 1) * math.pi) * np.cos(lam * np.asarray(x)) * math.exp(-lam * lam * alpha * t)
    return s


def slab_fd(L, alpha, t_end, nx=81, r=0.4):
    """Explicit FTCS on -L..L with theta = 0 at both faces and theta = 1 inside at t = 0. r = alpha dt/dx^2."""
    x = np.linspace(-L, L, nx); dx = x[1] - x[0]
    dt = r * dx * dx / alpha; steps = int(round(t_end / dt)); dt = t_end / steps
    rr = alpha * dt / dx ** 2
    th = np.ones(nx); th[0] = th[-1] = 0.0
    for _ in range(steps):
        th[1:-1] = th[1:-1] + rr * (th[2:] - 2 * th[1:-1] + th[:-2])
    return x, th


def square_fd(L, alpha, t_end, n=41, r=0.2):
    x = np.linspace(-L, L, n); dx = x[1] - x[0]
    dt = r * dx * dx / alpha; steps = int(round(t_end / dt)); dt = t_end / steps
    rr = alpha * dt / dx ** 2
    th = np.ones((n, n)); th[0, :] = th[-1, :] = th[:, 0] = th[:, -1] = 0.0
    for _ in range(steps):
        th[1:-1, 1:-1] += rr * (th[2:, 1:-1] + th[:-2, 1:-1] + th[1:-1, 2:] + th[1:-1, :-2] - 4 * th[1:-1, 1:-1])
    return x, th


if __name__ == "__main__":
    # a 4 cm steak from the fridge (5 C) into a 60 C sous-vide bath; faces taken as held at 60 C (a stirred bath gives Bi > 10), alpha = 1.4e-7 m^2/s
    L, alpha, Ti, Tb = 0.02, 1.4e-7, 5.0, 60.0
    goal = (55.0 - Tb) / (Ti - Tb)
    a, b = 60.0, 1e5
    while b - a > 1e-3:
        c = 0.5 * (a + b)
        a, b = (c, b) if slab_series(0.0, c, L, alpha) > goal else (a, c)
    t55 = 0.5 * (a + b)
    print(f"steak centre reaches 55 C after {t55:.1f} s = {t55/60:.2f} min (Fo = {alpha*t55/L**2:.4f})")
    one_term = 4 / math.pi * math.exp(-(math.pi / 2) ** 2 * alpha * t55 / L ** 2)
    print(f"one-term series at that time: {one_term:.6f} vs full {goal:.6f}")
    assert abs(one_term - goal) < 1e-5
    x, th = slab_fd(L, alpha, t55)
    err = np.abs(th - slab_series(x, t55, L, alpha)).max()
    print(f"1D explicit FD (81 nodes, r = 0.4) vs series: max error {err:.2e}; centre {Tb + th[40]*(Ti-Tb):.3f} C")
    assert err < 2e-4
    # stability: r above 0.5 blows up
    _, bad = slab_fd(L, alpha, 600.0, r=0.6)
    print(f"r = 0.6 after 10 min: max |theta| = {np.abs(bad).max():.2e} (unstable)")
    assert np.abs(bad).max() > 10
    # 2D: a 4 x 4 cm square bar of the same meat. The product solution says theta_2D = theta_x * theta_y
    t = 1800.0
    x2, th2 = square_fd(L, alpha, t)
    exact2 = np.outer(slab_series(x2, t, L, alpha), slab_series(x2, t, L, alpha))
    err2 = np.abs(th2 - exact2).max()
    print(f"2D square after 30 min: centre {Tb + th2[20,20]*(Ti-Tb):.3f} C (product solution {Tb + exact2[20,20]*(Ti-Tb):.3f} C); max error {err2:.2e}")
    assert err2 < 1e-3
