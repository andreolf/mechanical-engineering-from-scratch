"""Torsion of circular shafts: tau = T r / J, phi = T L / (G J); solid against hollow."""
import math
import numpy as np


def J_tube(D, d=0.0):
    return math.pi * (D**4 - d**4) / 32


def J_numeric(D, d=0.0, n=200001):
    """J = int r^2 dA = int 2 pi r^3 dr."""
    r = np.linspace(d / 2, D / 2, n)
    return np.trapezoid(2 * math.pi * r**3, r)


if __name__ == "__main__":
    G = 80e3                                       # MPa, steel
    # a car propeller shaft: hollow steel 50 x 42 mm, 1.4 m long, 1.2 kN m
    D, d, L, T = 50.0, 42.0, 1400.0, 1.2e6
    J = J_tube(D, d)
    assert abs(J_numeric(D, d) - J) < 1e-6 * J
    tau, phi = T * (D / 2) / J, T * L / (G * J)
    print(f"hollow shaft: J = {J:.1f} mm^4 (numeric {J_numeric(D, d):.1f}), tau_max = {tau:.3f} MPa, twist {math.degrees(phi):.3f} deg")
    # a solid shaft with the same maximum stress
    Ds = (16 * T / (math.pi * tau)) ** (1 / 3)
    A_h, A_s = math.pi * (D**2 - d**2) / 4, math.pi * Ds**2 / 4
    print(f"solid shaft with the same tau_max: D = {Ds:.3f} mm, mass ratio solid / hollow = {A_s / A_h:.3f}")
    assert abs(T * (Ds / 2) / J_tube(Ds) - tau) < 1e-9
    # shear stress grows linearly with radius, so the core of a solid shaft does little work
    r = np.linspace(0, Ds / 2, 5)
    print("solid shaft tau at r = 0, R/4, R/2, 3R/4, R:", np.round(T * r / J_tube(Ds), 2), "MPa")
    # twist of the hollow shaft by integrating d(phi)/dx = T / (G J) along a stepped shaft: 0.9 m hollow + 0.5 m solid 40 mm
    phi2 = T * 900 / (G * J) + T * 500 / (G * J_tube(40.0))
    print(f"stepped shaft (0.9 m hollow + 0.5 m solid 40 mm): twist {math.degrees(phi2):.3f} deg")
