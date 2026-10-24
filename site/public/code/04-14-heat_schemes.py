"""Heat equation u_t = alpha u_xx: FTCS (explicit, needs r <= 1/2) and Crank-Nicolson (implicit, unconditionally stable)."""
import math
import numpy as np
from scipy.linalg import solve_banded

ALPHA, L, T0 = 9.7e-5, 0.5, 100.0      # aluminium rod, 0.5 m, initially 100 C, ends plunged into 0 C


def exact(x, t, terms=401):
    return sum(4 * T0 / (k * math.pi) * np.sin(k * math.pi * x / L) * math.exp(-ALPHA * (k * math.pi / L) ** 2 * t)
               for k in range(1, terms, 2))


def ftcs(n, r, t_end):
    dx = L / n; steps = max(1, round(t_end * ALPHA / (r * dx * dx))); r = ALPHA * (t_end / steps) / dx**2   # land exactly on t_end
    u = np.full(n + 1, T0); u[0] = u[-1] = 0.0
    for _ in range(steps):
        u[1:-1] = u[1:-1] + r * (u[2:] - 2 * u[1:-1] + u[:-2])
    return u, r, steps


def crank_nicolson(n, r, t_end):
    dx = L / n; steps = max(1, round(t_end * ALPHA / (r * dx * dx))); r = ALPHA * (t_end / steps) / dx**2; m = n - 1
    ab = np.zeros((3, m)); ab[0, 1:] = -r / 2; ab[1, :] = 1 + r; ab[2, :-1] = -r / 2     # (I + r/2 A) on the left
    u = np.full(n + 1, T0); u[0] = u[-1] = 0.0
    for _ in range(steps):
        rhs = (1 - r) * u[1:-1] + r / 2 * (u[2:] + u[:-2])                                  # (I - r/2 A) on the right
        u[1:-1] = solve_banded((1, 1), ab, rhs)
    return u, r, steps


if __name__ == "__main__":
    n, t_end = 50, 600.0
    ex = exact(L / 2, t_end)
    print(f"exact centre temperature after {t_end:.0f} s: {ex:.4f} C")
    for r in (0.25, 0.5, 0.52):
        u, ra, steps = ftcs(n, r, t_end)
        c = u[n // 2]
        print(f"FTCS r = {ra:.3f}: centre {c:.4f} C after {steps} steps" if abs(c) < 1e4 else f"FTCS r = {ra:.3f}: centre {c:.2e} C after {steps} steps: blown up")
    u, ra, _ = ftcs(n, 0.4, t_end); assert abs(u[n // 2] - ex) < 0.1
    u, ra, _ = ftcs(n, 0.52, 3 * t_end); assert ra > 0.5 and np.max(np.abs(u)) > 1e3     # blows up just past r = 1/2
    for r in (0.5, 5, 50):
        u, ra, steps = crank_nicolson(n, r, t_end)
        print(f"Crank-Nicolson r = {ra:.2f}: centre {u[n // 2]:.4f} C after {steps} steps, error {abs(u[n // 2] - ex):.4f} C")
        assert abs(u[n // 2] - ex) < 0.3
