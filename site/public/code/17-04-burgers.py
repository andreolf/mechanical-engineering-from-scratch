"""Inviscid Burgers' equation u_t + (u^2/2)_x = 0 with the Rusanov (local Lax-Friedrichs) flux and a minmod-limited MUSCL reconstruction. A smooth sine steepens into a shock at the predicted time; a Riemann step moves at the Rankine-Hugoniot speed (uL + uR)/2."""
import math
import numpy as np


def flux(u):
    return 0.5 * u * u


def rusanov(uL, uR):
    a = np.maximum(np.abs(uL), np.abs(uR))
    return 0.5 * (flux(uL) + flux(uR)) - 0.5 * a * (uR - uL)


def minmod(a, b):
    return np.where(a * b > 0, np.sign(a) * np.minimum(np.abs(a), np.abs(b)), 0.0)


def rhs(u, dx, bc):
    ue = np.concatenate([[u[0], u[0]], u, [u[-1], u[-1]]]) if bc == "outflow" else np.concatenate([u[-2:], u, u[:2]])
    s = minmod(ue[1:-1] - ue[:-2], ue[2:] - ue[1:-1])          # limited slopes, cells -1 .. N
    uc = ue[1:-1]
    uL = (uc + 0.5 * s)[:-1]; uR = (uc - 0.5 * s)[1:]          # states at faces -1/2 .. N-1/2
    F = rusanov(uL, uR)
    return -(F[1:] - F[:-1]) / dx


def solve(u0, x, T, cfl=0.4, bc="periodic"):
    u = u0.copy(); dx = x[1] - x[0]; t = 0.0
    while t < T - 1e-14:
        dt = min(cfl * dx / max(np.abs(u).max(), 1e-12), T - t)
        u1 = u + dt * rhs(u, dx, bc); u = 0.5 * (u + u1 + dt * rhs(u1, dx, bc))   # Heun (SSP-RK2)
        t += dt
    return u


if __name__ == "__main__":
    # 1) Riemann problem: uL = 1, uR = 0 -> shock at speed 1/2
    N = 400; x = np.linspace(-1, 3, N, endpoint=False) + 2 / N
    u0 = np.where(x < 0, 1.0, 0.0)
    for T in (1.0, 2.0):
        u = solve(u0, x, T, bc="outflow")
        xs = x[np.argmin(np.abs(u - 0.5))]                     # where u crosses the mid value
        mass = (u.sum() - u0.sum()) * (x[1] - x[0])
        print(f"step 1 -> 0, t = {T}: shock at x = {xs:.4f} (Rankine-Hugoniot {0.5*T:.4f}); mass gained {mass:.6f} (inflow 1 x 0.5 x t = {0.5*T:.4f})")
        assert abs(xs - 0.5 * T) < 2 * (x[1] - x[0])
    # 2) a sine on a periodic domain: u = 1 + 0.5 sin(2 pi x). Characteristics cross at t* = 1/max(-u0') = 1/pi
    N = 800; x = (np.arange(N) + 0.5) / N; u0 = 1 + 0.5 * np.sin(2 * np.pi * x)
    tstar = 1 / (0.5 * 2 * np.pi)
    steep = []
    for T in (0.5 * tstar, 0.9 * tstar, 1.2 * tstar, 2 * tstar):
        u = solve(u0, x, T)
        g = np.max(np.abs(np.diff(u))) * N
        steep.append(g)
        print(f"t = {T:.4f} ({T/tstar:.1f} t*): steepest slope {g:8.2f}, min {u.min():.4f}, max {u.max():.4f}, mean {u.mean():.12f}")
    # before t* the exact steepest slope is pi / (1 - t/t*); afterwards the slope is limited only by the grid
    assert abs(steep[0] - math.pi / 0.5) < 0.05 * math.pi / 0.5 and steep[2] > 100
    # 3) weak solution check on the sine: after the shock forms the jump moves at the average of the states on either side
    u = solve(u0, x, 2 * tstar); i = np.argmax(np.abs(np.diff(u)))
    uL, uR = u[i - 3], u[i + 4]
    print(f"at 2 t*: states either side of the shock {uL:.3f} and {uR:.3f}; Rankine-Hugoniot speed {(uL+uR)/2:.3f} (= mean of u, 1, by symmetry)")
    assert abs((uL + uR) / 2 - 1) < 0.02
    xs = (x[i] + x[i + 1]) / 2; pred = (0.5 + 2 * tstar) % 1.0
    print(f"shock position {xs:.4f}; predicted 0.5 + 1 x t = {pred:.4f} (it starts where u0 = 1 on the falling side)")
    assert abs(xs - pred) < 2 / N
