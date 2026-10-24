"""Vorticity and circulation of a Rankine vortex: finite-difference curl, line integrals, and the solid-body core."""
import numpy as np


def rankine(x, y, Gamma, a):
    """Velocity of a Rankine vortex: solid-body rotation inside radius a, free (irrotational) vortex outside."""
    r = np.hypot(x, y) + 1e-300
    ut = np.where(r < a, Gamma * r / (2 * np.pi * a * a), Gamma / (2 * np.pi * r))
    return -ut * y / r, ut * x / r


def vorticity(u, v, dx):
    """omega_z = dv/dx - du/dy by central differences (arrays indexed [y, x])."""
    return (v[1:-1, 2:] - v[1:-1, :-2]) / (2 * dx) - (u[2:, 1:-1] - u[:-2, 1:-1]) / (2 * dx)


def circulation(Gamma, a, R, n=4000):
    """Line integral of u . dl around a circle of radius R."""
    th = np.linspace(0, 2 * np.pi, n + 1)
    x, y = R * np.cos(th), R * np.sin(th)
    u, v = rankine(x, y, Gamma, a)
    return float(np.sum(((u[1:] + u[:-1]) * np.diff(x) + (v[1:] + v[:-1]) * np.diff(y)) / 2))


if __name__ == "__main__":
    # an eddy behind a boulder in a river: circulation 2 m^2/s, core radius 0.4 m
    Gamma, a = 2.0, 0.4
    x = np.linspace(-1.2, 1.2, 241); dx = x[1] - x[0]; X, Y = np.meshgrid(x, x)
    u, v = rankine(X, Y, Gamma, a)
    w = vorticity(u, v, dx); R = np.hypot(X, Y)[1:-1, 1:-1]
    Omega = Gamma / (2 * np.pi * a * a)
    core, outer = w[R < 0.3], w[R > 0.5]
    print(f"core angular velocity {Omega:.4f} rad/s; vorticity in the core {core.mean():.4f} (2 Omega = {2*Omega:.4f}), outside {np.abs(outer).max():.2e}")
    assert np.allclose(core, 2 * Omega, rtol=1e-9) and np.abs(outer).max() < 1e-3 * 2 * Omega   # outside: zero up to truncation error
    for Rc in (0.2, 0.4, 0.8, 1.6):
        c = circulation(Gamma, a, Rc)
        print(f"  circulation around r = {Rc}: {c:.5f} m^2/s (enclosed vorticity x area: {2*Omega*np.pi*min(Rc, a)**2:.5f})")
        assert abs(c - 2 * Omega * np.pi * min(Rc, a) ** 2) < 1e-5
    print(f"peak swirl speed at the core edge {Gamma/(2*np.pi*a):.4f} m/s; a coconut at r = 1 m circles once every {2*np.pi*1/(Gamma/(2*np.pi*1)):.1f} s")
