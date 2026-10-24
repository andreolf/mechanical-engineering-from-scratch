"""A bar fixed at both ends: equilibrium + compatibility + Hooke's law, checked with a small stiffness-matrix model."""
import numpy as np


def fixed_fixed(P, a, L1_EA, L2_EA):
    """Load P at the step between part 1 (wall A side) and part 2 (wall B side). L_EA = L / (E A) of each part.
    Equilibrium: RA + RB = P. Compatibility: total stretch zero -> RA * f1 = RB * f2 (part 1 stretches, part 2 shortens)."""
    RA = P * L2_EA / (L1_EA + L2_EA)
    return RA, P - RA


def fe_bar(lengths, EAs, loads):
    """1D finite elements: nodes at the ends of each part; both end nodes fixed. loads: force at each interior node."""
    n = len(lengths) + 1
    K = np.zeros((n, n))
    for e, (L, EA) in enumerate(zip(lengths, EAs)):
        k = EA / L
        K[e:e + 2, e:e + 2] += k * np.array([[1, -1], [-1, 1]])
    f = np.zeros(n); f[1:-1] = loads
    u = np.zeros(n); u[1:-1] = np.linalg.solve(K[1:-1, 1:-1], f[1:-1])
    R = K @ u - f
    return u, R


if __name__ == "__main__":
    # uniform bar: P at distance a from wall A: RA = P b / L, RB = P a / L
    P, a, b, EA = 60e3, 300.0, 700.0, 210e3 * 400
    RA, RB = fixed_fixed(P, a, a / EA, b / EA)
    print(f"uniform bar: RA = {RA / 1e3:.3f} kN, RB = {RB / 1e3:.3f} kN (P b/L = {P * b / 1000 / 1e3:.3f})")
    assert abs(RA + RB - P) < 1e-9 and abs(RA - P * b / (a + b)) < 1e-9
    u, R = fe_bar([a, b], [EA, EA], [P])
    print(f"  stiffness model: load-point displacement {u[1]:.5f} mm, wall reactions {np.round(-R[[0, -1]] / 1e3, 3)} kN")
    assert np.allclose(-R[[0, -1]], [RA, RB]) and abs(u[1] - RA * a / EA) < 1e-12
    # steel part 300 mm (A = 400 mm^2) and aluminium part 700 mm (A = 600 mm^2): the stiffer side takes more
    f1, f2 = 300 / (210e3 * 400), 700 / (70e3 * 600)
    RA, RB = fixed_fixed(P, 300, f1, f2)
    u, R = fe_bar([300, 700], [210e3 * 400, 70e3 * 600], [P])
    print(f"steel/aluminium bar: RA = {RA / 1e3:.3f} kN (steel side), RB = {RB / 1e3:.3f} kN; stresses {RA / 400:.2f} and {-RB / 600:.2f} MPa")
    assert np.allclose(-R[[0, -1]], [RA, RB]) and abs(RA + RB - P) < 1e-9
    # several loads: reactions still sum to the total applied load
    u, R = fe_bar([200, 300, 500], [EA, EA / 2, EA], [25e3, 8e3])
    print(f"two loads (25 kN and 8 kN): reactions {np.round(-R[[0, -1]] / 1e3, 4)} kN, sum {-R[[0, -1]].sum() / 1e3:.4f} kN")
    assert abs(-R[[0, -1]].sum() - 33e3) < 1e-6
