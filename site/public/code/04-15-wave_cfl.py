"""Leapfrog for the wave equation u_tt = c^2 u_xx on a guitar string: stable for CFL = c dt/dx <= 1, exact at CFL = 1."""
import numpy as np

L, F1 = 0.648, 329.63          # high E string: scale length (m) and fundamental (Hz)
C = 2 * L * F1                 # wave speed, m/s


def pluck(x, a=0.2 * L, height=2e-3):
    return np.where(x < a, height * x / a, height * (L - x) / (L - a))


def leapfrog(n, cfl, t_end):
    dx = L / n; steps = max(1, round(t_end * C / (cfl * dx))); dt = t_end / steps; s2 = (C * dt / dx) ** 2
    x = np.linspace(0, L, n + 1)
    u_old = pluck(x)
    u = u_old.copy()                                       # first step from rest: u1 = u0 + (s^2 / 2) * second difference
    u[1:-1] = u_old[1:-1] + 0.5 * s2 * (u_old[2:] - 2 * u_old[1:-1] + u_old[:-2])
    for _ in range(steps - 1):
        u_new = np.zeros_like(u)
        u_new[1:-1] = 2 * u[1:-1] - u_old[1:-1] + s2 * (u[2:] - 2 * u[1:-1] + u[:-2])
        u_old, u = u, u_new
    return x, u, C * dt / dx, steps


if __name__ == "__main__":
    period = 1 / F1
    print(f"wave speed c = 2 L f = {C:.1f} m/s, period {period * 1e3:.4f} ms")
    n = 100
    for cfl in (1.0, 0.5, 1.02):
        x, u, s, steps = leapfrog(n, cfl, period)
        err = np.max(np.abs(u - pluck(x)))                # after one period the string is back in its plucked shape
        print(f"CFL {s:.3f}: {steps} steps, max deviation from the plucked shape after one period {err * 1e3:.3g} mm")
    x, u, s, _ = leapfrog(n, 1.0, period); assert np.max(np.abs(u - pluck(x))) < 1e-12        # exact at CFL = 1
    x, u, s, _ = leapfrog(n, 0.5, period); assert 1e-6 < np.max(np.abs(u - pluck(x))) < 5e-4  # stable, slightly dispersive
    x, u, s, _ = leapfrog(n, 1.02, 3 * period); assert np.max(np.abs(u)) > 1                   # unstable past CFL = 1
    dx = L / n
    print(f"stability limit dt <= dx / c = {dx / C * 1e6:.3f} us for {n} cells")
