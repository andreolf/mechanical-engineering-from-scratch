"""Potential flow past a cylinder: Laplace check, surface speed, zero drag and Kutta-Joukowski lift."""
import math
import numpy as np


def psi_cyl(x, y, U=1.0, R=1.0, Gam=0.0):
    r2 = x * x + y * y
    return U * y * (1 - R * R / r2) + Gam / (2 * math.pi) * 0.5 * np.log(r2 / R ** 2)   # Gam > 0: clockwise vortex


def velocity(psi, x, y, h=1e-5):
    return (psi(x, y + h) - psi(x, y - h)) / (2 * h), -(psi(x + h, y) - psi(x - h, y)) / (2 * h)


def surface_forces(U, R, Gam, rho, n=20000):
    th = 2 * math.pi * (np.arange(n) + 0.5) / n
    ut = -2 * U * np.sin(th) - Gam / (2 * math.pi * R)            # tangential speed; Gam > 0 is clockwise
    p = 0.5 * rho * (U ** 2 - ut ** 2)                             # Bernoulli, p_inf = 0
    ds = R * 2 * math.pi / n
    return -np.sum(p * np.cos(th)) * ds, -np.sum(p * np.sin(th)) * ds   # drag, lift per unit span


if __name__ == "__main__":
    # Laplace's equation holds away from the cylinder (5-point stencil)
    h = 1e-3
    for x, y in [(1.5, 0.3), (-2, 1), (0.2, 1.7)]:
        lap = (psi_cyl(x + h, y) + psi_cyl(x - h, y) + psi_cyl(x, y + h) + psi_cyl(x, y - h) - 4 * psi_cyl(x, y)) / h ** 2
        assert abs(lap) < 1e-5
    # the cylinder is a streamline and the surface speed is 2 U sin(theta)
    U, R = 10.0, 0.1
    psi = lambda x, y: psi_cyl(x, y, U, R)
    for th in np.linspace(0.1, 3.0, 7):
        x, y = R * math.cos(th), R * math.sin(th)
        assert abs(psi(x, y)) < 1e-12
        u, v = velocity(psi, 1.0001 * x, 1.0001 * y)
        assert abs(math.hypot(u, v) - 2 * U * math.sin(th)) < 0.01
    print(f"max surface speed {2*U:.0f} m/s, Cp min = {1 - 4:.0f}, suction {-3 * 0.5 * 1.2 * U**2:.0f} Pa")
    D, L = surface_forces(U, R, 0.0, 1.2)
    assert abs(D) < 1e-9 and abs(L) < 1e-9                         # d'Alembert's paradox
    D, L = surface_forces(U, R, 4.0, 1.2)
    print(f"with circulation 4 m^2/s: drag {D:.2e} N/m, lift {L:.4f} N/m (rho U Gamma = {1.2*U*4:.1f})")
    assert abs(D) < 1e-9 and abs(L - 1.2 * U * 4.0) < 1e-6
