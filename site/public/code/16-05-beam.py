"""Euler-Bernoulli beam elements: Hermite cubic shape functions, the 4x4 stiffness matrix (closed form and by integrating N''), consistent loads; one element gives the exact cantilever tip deflection."""
import math
import numpy as np


def hermite(xi, L):
    """Shape functions on xi in [0, 1] for dofs [v1, theta1, v2, theta2], and their second derivatives wrt x."""
    N = np.array([1 - 3 * xi**2 + 2 * xi**3, L * (xi - 2 * xi**2 + xi**3), 3 * xi**2 - 2 * xi**3, L * (-xi**2 + xi**3)])
    d2 = np.array([-6 + 12 * xi, L * (-4 + 6 * xi), 6 - 12 * xi, L * (-2 + 6 * xi)]) / L**2
    return N, d2


def k_beam(EI, L):
    return EI / L**3 * np.array([[12, 6 * L, -12, 6 * L], [6 * L, 4 * L**2, -6 * L, 2 * L**2],
                                 [-12, -6 * L, 12, -6 * L], [6 * L, 2 * L**2, -6 * L, 4 * L**2]])


def k_beam_integrated(EI, L, ng=3):
    x, w = np.polynomial.legendre.leggauss(ng)
    xi, w = (x + 1) / 2, w / 2
    K = np.zeros((4, 4))
    for a, wa in zip(xi, w):
        _, B = hermite(a, L)
        K += EI * np.outer(B, B) * wa * L
    return K


def solve_beam(L_total, ne, EI, q=0.0, tip_load=0.0, bc="cantilever"):
    L = L_total / ne
    n = 2 * (ne + 1)
    K = np.zeros((n, n)); F = np.zeros(n)
    fe = q * np.array([L / 2, L**2 / 12, L / 2, -L**2 / 12])   # consistent load for uniform q
    for e in range(ne):
        d = np.arange(2 * e, 2 * e + 4)
        K[np.ix_(d, d)] += k_beam(EI, L)
        F[d] += fe
    F[-2] += tip_load
    fixed = [0, 1] if bc == "cantilever" else [0, n - 2]
    free = [i for i in range(n) if i not in fixed]
    u = np.zeros(n)
    u[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])
    return u


if __name__ == "__main__":
    EI, L = 2.0e5, 3.0          # N m^2 (a 3 m aluminium diving board, roughly), m
    assert np.allclose(k_beam_integrated(EI, 1.7), k_beam(EI, 1.7))
    P = -800.0
    u = solve_beam(L, 1, EI, tip_load=P)
    exact = P * L**3 / (3 * EI)
    print(f"one element, tip load {P} N: tip deflection {1000*u[2]:.4f} mm, exact PL^3/3EI {1000*exact:.4f} mm; tip rotation {u[3]:.6f} (exact {P*L**2/(2*EI):.6f})")
    assert abs(u[2] - exact) < 1e-12 and abs(u[3] - P * L**2 / (2 * EI)) < 1e-12
    # uniform load: nodal values exact with consistent loads, interior only approximate with few elements
    q = -500.0
    for ne in (1, 2, 4):
        u = solve_beam(L, ne, EI, q=q)
        print(f"{ne} element(s), uniform load: tip {1000*u[-2]:.4f} mm (exact qL^4/8EI = {1000*q*L**4/(8*EI):.4f})")
        assert abs(u[-2] - q * L**4 / (8 * EI)) < 1e-12
    # simply supported, 4 elements: mid-span deflection 5qL^4/384EI
    u = solve_beam(L, 4, EI, q=q, bc="simple")
    print(f"simply supported mid-span {1000*u[4]:.4f} mm, exact {1000*5*q*L**4/(384*EI):.4f}")
    assert abs(u[4] - 5 * q * L**4 / (384 * EI)) < 1e-12
    # between nodes the cubic is not the exact quartic: one element, mid-span of the cantilever under q
    u = solve_beam(L, 1, EI, q=q)
    N, _ = hermite(0.5, L)
    x = L / 2
    ex = q * x**2 * (6 * L**2 - 4 * L * x + x**2) / (24 * EI)
    print(f"one element, uniform load, mid-length: FEM {1000*N@u:.4f} mm vs exact {1000*ex:.4f} mm")
    assert abs(N @ u - ex) > 1e-4
