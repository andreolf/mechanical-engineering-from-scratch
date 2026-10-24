"""Euler buckling from a discretised column: beam finite elements give K phi = P Kg phi."""
import math
import numpy as np


def column_matrices(L, EI, n):
    """Assemble bending stiffness K and geometric stiffness Kg (per unit axial load) for n Hermite beam elements."""
    l = L / n
    k = EI / l**3 * np.array([[12, 6*l, -12, 6*l], [6*l, 4*l*l, -6*l, 2*l*l], [-12, -6*l, 12, -6*l], [6*l, 2*l*l, -6*l, 4*l*l]])
    g = 1 / (30 * l) * np.array([[36, 3*l, -36, 3*l], [3*l, 4*l*l, -3*l, -l*l], [-36, -3*l, 36, -3*l], [3*l, -l*l, -3*l, 4*l*l]])
    N = 2 * (n + 1)
    K, Kg = np.zeros((N, N)), np.zeros((N, N))
    for e in range(n):
        idx = slice(2 * e, 2 * e + 4)
        K[idx, idx] += k; Kg[idx, idx] += g
    return K, Kg


def critical_load(L, EI, n, ends):
    """ends: 'pinned-pinned', 'fixed-free', 'fixed-fixed' or 'fixed-pinned'. DOFs per node: (w, slope)."""
    K, Kg = column_matrices(L, EI, n)
    last = 2 * n
    fixed = {"pinned-pinned": [0, last], "fixed-free": [0, 1], "fixed-fixed": [0, 1, last, last + 1], "fixed-pinned": [0, 1, last]}[ends]
    free = [i for i in range(K.shape[0]) if i not in fixed]
    Kr, Gr = K[np.ix_(free, free)], Kg[np.ix_(free, free)]
    lam = np.linalg.eigvals(np.linalg.solve(Gr, Kr))
    return float(np.min(lam.real[lam.real > 0]))


if __name__ == "__main__":
    E = 210e3
    # a scaffold tube 48.3 x 3.2 mm, 3 m between joints
    D, t, L = 48.3, 3.2, 3000.0
    I = math.pi * (D**4 - (D - 2 * t) ** 4) / 64; A = math.pi * (D**2 - (D - 2 * t) ** 2) / 4
    EI = E * I
    euler = math.pi**2 * EI / L**2
    print(f"scaffold tube: I = {I:.0f} mm^4, A = {A:.1f} mm^2, Euler load (pinned) {euler/1e3:.3f} kN")
    for n in (2, 4, 8, 16):
        Pn = critical_load(L, EI, n, "pinned-pinned")
        print(f"  {n:2d} elements: {Pn/1e3:.4f} kN (error {(Pn/euler - 1)*100:.4f} %)")
    assert abs(critical_load(L, EI, 16, "pinned-pinned") / euler - 1) < 1e-5
    for ends, K in (("fixed-free", 2.0), ("fixed-fixed", 0.5), ("fixed-pinned", 0.6992)):
        Pn = critical_load(L, EI, 32, ends)
        Keff = math.pi * math.sqrt(EI / Pn) / L
        print(f"  {ends}: {Pn/1e3:.3f} kN, effective length factor K = {Keff:.4f} (textbook {K})")
        assert abs(Keff - K) < 1e-3
    print(f"squash load at 235 MPa: {235 * A / 1e3:.1f} kN; slenderness L/r = {L / math.sqrt(I / A):.1f}")
