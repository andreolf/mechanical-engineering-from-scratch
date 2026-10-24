"""Axial and torsional vibration of rods: a lumped-mass model of a fixed-free rod converging to f_n = (2n - 1) c / (4 L)."""
import math
import numpy as np
from scipy.linalg import eigh


def rod_modes(L, EA, rhoA, ne, fixed_free=True):
    """Linear finite elements (consistent mass) for a uniform rod; returns natural frequencies in Hz."""
    h = L / ne
    ke = EA / h * np.array([[1, -1], [-1, 1]]); me = rhoA * h / 6 * np.array([[2, 1], [1, 2]])
    K = np.zeros((ne + 1, ne + 1)); M = np.zeros_like(K)
    for e in range(ne):
        K[e:e+2, e:e+2] += ke; M[e:e+2, e:e+2] += me
    keep = slice(1, None) if fixed_free else slice(1, -1)
    w2 = eigh(K[keep, keep], M[keep, keep], eigvals_only=True)
    return np.sqrt(w2) / (2 * math.pi)


if __name__ == "__main__":
    E, G, rho = 210e9, 81e9, 7850.0
    c, ct = math.sqrt(E / rho), math.sqrt(G / rho)
    print(f"steel: axial wave speed {c:.1f} m/s, torsional {ct:.1f} m/s")
    L, A = 2.0, 1e-4
    for ne in (5, 20, 80):
        f = rod_modes(L, E * A, rho * A, ne)
        print(f"{ne:3d} elements: f1..f3 = {', '.join(f'{x:.2f}' for x in f[:3])} Hz")
    exact = [(2 * n - 1) * c / (4 * L) for n in (1, 2, 3)]
    print(f"exact (2n - 1) c / (4L): {', '.join(f'{x:.2f}' for x in exact)} Hz")
    f = rod_modes(L, E * A, rho * A, 400)
    assert abs(f[0] / exact[0] - 1) < 1e-5 and abs(f[2] / exact[2] - 1) < 1e-4
    ff = rod_modes(L, E * A, rho * A, 400, fixed_free=False)
    print(f"fixed-fixed: f1 = {ff[0]:.2f} Hz (c / 2L = {c/(2*L):.2f}), f2 / f1 = {ff[1]/ff[0]:.4f}")
    # torsion uses the same equation with GJ and rho J: a 3000 m drill string, fixed at the rig, free at the bit
    Ld = 3000.0
    print(f"drill string {Ld:.0f} m, torsional f1 = c_t / (4 L) = {ct/(4*Ld):.4f} Hz (period {4*Ld/ct:.2f} s)")
    J = math.pi / 32 * (0.127**4 - 0.108**4)
    fd = rod_modes(Ld, G * J, rho * J, 300)
    print(f"finite elements for the drill pipe: {fd[0]:.4f} Hz")
    assert abs(fd[0] / (ct / (4 * Ld)) - 1) < 1e-4
