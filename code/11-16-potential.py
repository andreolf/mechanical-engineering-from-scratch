"""Potential flow past a cylinder with circulation: complex potential, surface pressure, and the Kutta-Joukowski lift by integration."""
import numpy as np

RHO = 1.2


def velocity(z, U, a, Gamma):
    """dw/dz = u - i v for w = U (z + a^2/z) - i Gamma/(2 pi) log z (circulation positive anticlockwise)."""
    dw = U * (1 - a * a / z ** 2) - 1j * Gamma / (2 * np.pi * z)
    return dw.real, -dw.imag


def surface_forces(U, a, Gamma, n=20000):
    """Integrate the Bernoulli pressure p - p_inf = rho/2 (U^2 - |u|^2) around the cylinder."""
    th = np.linspace(0, 2 * np.pi, n, endpoint=False); dth = 2 * np.pi / n
    z = a * np.exp(1j * th)
    u, v = velocity(z, U, a, Gamma)
    cp = 1 - (u * u + v * v) / U ** 2
    p = 0.5 * RHO * U ** 2 * cp
    # outward normal (cos, sin); force on body = -integral p n dl
    Fx = -np.sum(p * np.cos(th)) * a * dth
    Fy = -np.sum(p * np.sin(th)) * a * dth
    return Fx, Fy, th, cp


if __name__ == "__main__":
    U, a = 10.0, 0.5
    for Gamma in (0.0, -20.0, -50.0, -4 * np.pi * U * a):           # the last one merges the stagnation points at the bottom
        Fx, Fy, th, cp = surface_forces(U, a, Gamma)
        print(f"Gamma = {Gamma:8.3f} m^2/s: drag {Fx:+.2e} N/m, lift {Fy:9.4f} N/m (rho U |Gamma| = {RHO*U*abs(Gamma):.4f})")
        assert abs(Fx) < 1e-8 and abs(Fy - (-RHO * U * Gamma)) < 1e-6     # d'Alembert and Kutta-Joukowski (clockwise Gamma lifts up)
    Fx, Fy, th, cp = surface_forces(U, a, 0.0)
    print(f"no circulation: Cp = {cp[0]:.3f} at the stagnation points, {cp.min():.3f} at the top and bottom")
    # stagnation points on the surface: sin(theta) = Gamma / (4 pi U a)
    G = -20.0
    print(f"Gamma = {G}: stagnation points at {np.degrees(np.arcsin(G/(4*np.pi*U*a))):.2f} and {180-np.degrees(np.arcsin(G/(4*np.pi*U*a))):.2f} deg")
