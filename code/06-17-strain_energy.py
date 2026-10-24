"""Strain energy U = integral of sigma epsilon / 2 over the volume, for a bar, a beam and a shaft."""
import math
import numpy as np


def bar_energy(P, L, E, A):
    return P**2 * L / (2 * E * A)


def beam_energy(M_of_x, L, E, I, n=20001):
    x = np.linspace(0, L, n)
    return np.trapezoid(M_of_x(x) ** 2 / (2 * E * I), x)


def shaft_energy(T, L, G, J):
    return T**2 * L / (2 * G * J)


def energy_density_volume(sig_fn, E, xs, ys, b):
    """Integrate sigma^2 / (2E) over a rectangular beam volume (x along, y across the depth)."""
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    u = sig_fn(X, Y) ** 2 / (2 * E)
    return np.trapezoid(np.trapezoid(u, ys, axis=1), xs) * b


if __name__ == "__main__":
    E, G = 210e3, 80e3
    # 1. a 20 mm steel tie, 2 m long, 30 kN
    P, L, A = 30e3, 2000.0, math.pi * 20**2 / 4
    U = bar_energy(P, L, E, A); delta = P * L / (E * A)
    print(f"bar: U = {U/1e3:.4f} J, P delta / 2 = {P*delta/2/1e3:.4f} J")
    assert abs(U - P * delta / 2) < 1e-9 * U
    # 2. the balcony cantilever from 06.11: 5 kN at the tip of 1.8 m, I = 1.8456e7 mm^4
    P, L, I = 5e3, 1800.0, 1.8456e7
    U = beam_energy(lambda x: -P * (L - x), L, E, I); delta = P * L**3 / (3 * E * I)
    print(f"beam: U = {U/1e3:.4f} J, P delta / 2 = {P*delta/2/1e3:.4f} J")
    assert abs(U - P * delta / 2) < 1e-6 * U
    # 3. the propeller shaft from 06.14
    T, L, J = 1.2e6, 1400.0, math.pi * (50**4 - 42**4) / 32
    U = shaft_energy(T, L, G, J); phi = T * L / (G * J)
    print(f"shaft: U = {U/1e3:.4f} J, T phi / 2 = {T*phi/2/1e3:.4f} J")
    assert abs(U - T * phi / 2) < 1e-9 * U
    # 4. how well each uses the material: same peak stress 200 MPa, compare energy per unit volume
    s0 = 200.0; u0 = s0**2 / (2 * E)
    b, h, L = 20.0, 40.0, 500.0
    xs, ys = np.linspace(0, L, 401), np.linspace(-h / 2, h / 2, 401)
    # cantilever with tip load, sized so the root fibre reaches s0: sigma = s0 (1 - x/L) (2y/h)
    Ub = energy_density_volume(lambda X, Y: s0 * (1 - X / L) * (2 * Y / h), E, xs, ys, b)
    ratio = Ub / (u0 * b * h * L)
    print(f"energy stored per unit volume, relative to a uniformly stressed bar: tip-loaded cantilever {ratio:.4f} (1/9 = {1/9:.4f})")
    assert abs(ratio - 1 / 9) < 1e-4
