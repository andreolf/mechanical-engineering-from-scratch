"""Support reactions of a pin-roller beam with point loads, distributed loads and couples, plus a 3D platform."""
import numpy as np


def beam_reactions(a, b, points=(), udls=(), couples=()):
    """Pin at x = a, roller at x = b. Loads positive downward (kN), couples counter-clockwise (kN m).
    points: (x, P); udls: (x1, x2, q); couples: (x, M). Returns (Ra, Rb), both positive upward."""
    loads = list(points) + [((x1 + x2) / 2, q * (x2 - x1)) for x1, x2, q in udls]   # each UDL becomes its resultant
    # unknowns [Ra, Rb]: sum Fy = 0 and sum M about the pin = 0 (horizontal reaction is zero for vertical loads)
    A = np.array([[1.0, 1.0], [0.0, b - a]])
    rhs = np.array([sum(P for _, P in loads), sum(P * (x - a) for x, P in loads) - sum(M for _, M in couples)])
    return np.linalg.solve(A, rhs)


def platform(cables, weights):
    """Rigid horizontal platform hung from three vertical cables at (x, y); weights (x, y, W). Returns tensions."""
    A = np.array([[1, 1, 1], [y for _, y in cables], [x for x, _ in cables]], float)
    rhs = np.array([sum(W for *_, W in weights), sum(W * y for _, y, W in weights), sum(W * x for x, _, W in weights)])
    return np.linalg.solve(A, rhs)       # rows: sum Fz = 0, sum Mx = 0, sum My = 0


if __name__ == "__main__":
    # footbridge beam: pin at 0, roller at 6 m, overhang to 8 m
    Ra, Rb = beam_reactions(0, 6, points=[(2, 20), (8, 10)], udls=[(0, 6, 5)])
    print(f"overhanging beam: Ra = {Ra:.4f} kN, Rb = {Rb:.4f} kN")
    # hand: moments about A: Rb*6 = 20*2 + 30*3 + 10*8 = 210 -> Rb = 35, Ra = 60 - 35 = 25
    assert abs(Rb - 35) < 1e-12 and abs(Ra - 25) < 1e-12
    # check sum of moments about the roller too
    assert abs(-Ra * 6 + 20 * 4 + 30 * 3 - 10 * 2) < 1e-12
    # a couple only: reactions form an equal and opposite couple
    Ra2, Rb2 = beam_reactions(0, 5, couples=[(2.0, 15.0)])
    print(f"15 kN m couple on a 5 m span: Ra = {Ra2:.1f}, Rb = {Rb2:.1f} kN (position of the couple doesn't matter)")
    assert abs(Ra2 - 3) < 1e-12 and abs(Rb2 + 3) < 1e-12
    # 3D: a 2 m x 1.2 m stage platform on three cables
    cables = [(0, 0), (2, 0), (1, 1.2)]
    T = platform(cables, [(1.0, 0.6, 3.0), (1.6, 0.3, 1.5)])
    print(f"stage platform cable tensions: {np.round(T, 4)} kN")
    assert abs(T.sum() - 4.5) < 1e-12
    assert abs(T @ [y for _, y in cables] - (3 * 0.6 + 1.5 * 0.3)) < 1e-12
