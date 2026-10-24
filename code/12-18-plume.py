"""A dye slug in the Limmat: 1D advection-dispersion, finite volumes against the Gaussian solution, with mass conservation."""
import math
import numpy as np


def gaussian(x, t, M, A, U, D, x0=0.0):
    return M / (A * math.sqrt(4 * math.pi * D * t)) * np.exp(-(x - x0 - U * t) ** 2 / (4 * D * t))


def simulate(M, A, U, D, L, n, t_end, x0, t0):
    """Conservative finite volumes: upwind advection (U > 0) with a second-order flux limiter, central diffusion,
    zero flux at both ends. Starts from the Gaussian at time t0 so that the initial condition is smooth."""
    dx = L / n; x = (np.arange(n) + 0.5) * dx
    c = gaussian(x, t0, M, A, U, D, x0)
    dt = 0.4 * min(dx / U, dx * dx / (2 * D)); steps = int(math.ceil((t_end - t0) / dt)); dt = (t_end - t0) / steps
    for _ in range(steps):
        # face fluxes F[i] between cells i-1 and i (F[0] and F[n] are the closed ends)
        dc = np.diff(c)
        r = np.zeros(n - 1); r[1:] = dc[:-1] / np.where(np.abs(dc[1:]) > 1e-300, dc[1:], 1e-300)
        phi = np.maximum(0, np.minimum(1, r))                        # minmod limiter
        cface = c[:-1] + 0.5 * phi * dc * (1 - U * dt / dx)
        F = np.zeros(n + 1)
        F[1:-1] = U * cface - D * dc / dx
        c = c - dt / dx * (F[1:] - F[:-1])
    return x, c, dx


if __name__ == "__main__":
    # Limmat below Zurich: 40 m wide, 2.5 m deep, 1 m/s, shear velocity 0.08 m/s
    W, h, U, ustar = 40.0, 2.5, 1.0, 0.08
    A = W * h
    D = 0.011 * U ** 2 * W ** 2 / (h * ustar)                      # Fischer's longitudinal dispersion estimate
    print(f"longitudinal dispersion D = {D:.1f} m^2/s")
    M = 10.0                                                      # 10 kg of tracer dye
    for t in (500.0, 2000.0, 8000.0):
        cmax = M / (A * math.sqrt(4 * math.pi * D * t))
        print(f"t = {t:6.0f} s: cloud centre {U*t/1000:.1f} km downstream, peak {cmax*1e6:.2f} mg/m^3 (ug/L), width 4 sigma = {4*math.sqrt(2*D*t):.0f} m")
    x, c, dx = simulate(M, A, U, D, L=20000.0, n=2000, t_end=8000.0, x0=500.0, t0=500.0)
    mass = c.sum() * dx * A
    exact = gaussian(x, 8000.0, M, A, U, D, 500.0)
    print(f"finite volumes after 8000 s: mass {mass:.12f} kg, peak {c.max()*1e6:.3f} vs Gaussian {exact.max()*1e6:.3f} ug/L, "
          f"max error {np.abs(c-exact).max()/exact.max()*100:.2f} % of the peak")
    m0 = gaussian(x, 500.0, M, A, U, D, 500.0).sum() * dx * A
    assert abs(mass - m0) < 1e-12 * M                            # total mass conserved to rounding
    assert np.abs(c - exact).max() < 0.005 * exact.max()          # and the shape matches the Gaussian (domain long enough that no dye reaches the ends)
    print(f"initial mass on the grid {m0:.12f} kg")
