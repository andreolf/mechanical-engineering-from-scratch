"""Integrals in polar and spherical coordinates, checked against closed forms."""
import math
import numpy as np


def polar_integral(f, r0, r1, n_r=400, n_t=400):
    """Midpoint rule over an annulus with the Jacobian r."""
    hr, ht = (r1 - r0) / n_r, 2 * math.pi / n_t
    r = r0 + hr * (np.arange(n_r) + 0.5)
    t = ht * (np.arange(n_t) + 0.5)
    R, T = np.meshgrid(r, t)
    return np.sum(f(R, T) * R) * hr * ht


def J_hollow(D, d):
    return math.pi / 32 * (D ** 4 - d ** 4)


if __name__ == "__main__":
    J = polar_integral(lambda r, t: r ** 2, 20, 25)
    print(f"J numeric {J:.1f} mm^4, formula {J_hollow(50, 40):.1f} mm^4")
    assert abs(J - J_hollow(50, 40)) / J < 1e-5
    tau_A = 500e3 * 25 / J_hollow(50, 40)
    tau_B = 500e3 * 15 / J_hollow(30, 0)
    print(f"hollow {tau_A:.1f} MPa, solid {tau_B:.1f} MPa")
    assert abs(tau_A - 34.505) < 1e-3 and abs(tau_B - 94.314) < 1e-3
    # forgetting the Jacobian gives the wrong area of a disc
    with_j = polar_integral(lambda r, t: np.ones_like(r), 0, 1)
    without = np.sum(np.ones((400, 400))) * (1 / 400) * (2 * math.pi / 400)
    assert abs(with_j - math.pi) < 1e-9 and abs(without - 2 * math.pi) < 1e-9
    # sphere volume in spherical coordinates
    n = 200; hp = math.pi / n; hr = 1 / n
    rho = hr * (np.arange(n) + 0.5); phi = hp * (np.arange(n) + 0.5)
    P, Rh = np.meshgrid(phi, rho)
    V = 2 * math.pi * np.sum(Rh ** 2 * np.sin(P)) * hr * hp
    assert abs(V - 4 / 3 * math.pi) < 1e-3
    # the Gaussian integral via polar coordinates: (integral e^{-x^2})^2 = pi
    G = polar_integral(lambda r, t: np.exp(-r ** 2), 0, 8, 8000, 4)
    assert abs(G - math.pi) < 1e-6
    print("disc, sphere and Gaussian integrals all check out")
