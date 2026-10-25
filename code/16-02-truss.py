"""2D truss by the direct stiffness method: bar stiffness rotated to global axes, assembly, supports, member forces; checked against the method of joints for a statically determinate footbridge truss."""
import math
import numpy as np


def bar_stiffness(xy1, xy2, EA):
    dx, dy = np.subtract(xy2, xy1)
    L = math.hypot(dx, dy)
    c, s = dx / L, dy / L
    t = np.array([c, s, -c, -s])
    return EA / L * np.outer(t, t), L, c, s


def solve_truss(nodes, bars, EA, supports, loads):
    """nodes: (n, 2) array; bars: list of (i, j); supports: list of fixed dof indices; loads: {dof: force}."""
    n = len(nodes)
    K = np.zeros((2 * n, 2 * n))
    for i, j in bars:
        k, *_ = bar_stiffness(nodes[i], nodes[j], EA)
        d = [2 * i, 2 * i + 1, 2 * j, 2 * j + 1]
        K[np.ix_(d, d)] += k
    F = np.zeros(2 * n)
    for dof, f in loads.items():
        F[dof] += f
    free = [d for d in range(2 * n) if d not in supports]
    u = np.zeros(2 * n)
    u[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])
    N = []
    for i, j in bars:
        _, L, c, s = bar_stiffness(nodes[i], nodes[j], EA)
        N.append(EA / L * (c * (u[2 * j] - u[2 * i]) + s * (u[2 * j + 1] - u[2 * i + 1])))
    return u, np.array(N), K @ u - F


def method_of_joints(nodes, bars, supports, loads):
    """Equilibrium at every joint: unknowns are the bar forces (tension +) and the support reactions."""
    n = len(nodes)
    m = len(bars) + len(supports)
    A = np.zeros((2 * n, m)); b = np.zeros(2 * n)
    for e, (i, j) in enumerate(bars):
        dx, dy = np.subtract(nodes[j], nodes[i]); L = math.hypot(dx, dy)
        c, s = dx / L, dy / L
        A[2 * i, e] += c; A[2 * i + 1, e] += s      # tension pulls joint i towards j
        A[2 * j, e] -= c; A[2 * j + 1, e] -= s
    for r, dof in enumerate(supports):
        A[dof, len(bars) + r] = 1.0
    for dof, f in loads.items():
        b[dof] -= f
    assert A.shape[0] == A.shape[1], "not statically determinate"
    x = np.linalg.solve(A, b)
    return x[:len(bars)], x[len(bars):]


if __name__ == "__main__":
    # Pratt footbridge truss: 4 panels of 3 m, 2.5 m deep, steel bars EA = 210 GPa x 1200 mm^2
    P, H = 3.0, 2.5
    bottom = [(k * P, 0.0) for k in range(5)]
    top = [(k * P, H) for k in range(1, 4)]
    nodes = np.array(bottom + top)                       # 0-4 bottom, 5-7 top
    bars = [(0, 1), (1, 2), (2, 3), (3, 4), (5, 6), (6, 7), (0, 5), (4, 7),
            (1, 5), (2, 6), (3, 7), (5, 2), (7, 2)]
    EA = 210e9 * 1200e-6
    supports = [0, 1, 9]                                 # pin at node 0, roller (vertical) at node 4
    loads = {3: -20e3, 5: -30e3, 7: -20e3}               # deck loads at the bottom joints 1, 2, 3 (N)
    u, N, R = solve_truss(nodes, bars, EA, supports, loads)
    Nj, Rj = method_of_joints(nodes, bars, supports, loads)
    for e, (i, j) in enumerate(bars):
        print(f"bar {i}-{j}: FEM {N[e]/1000:8.3f} kN, joints {Nj[e]/1000:8.3f} kN")
    assert np.allclose(N, Nj, atol=1e-6)                 # determinate: stiffness method = statics
    assert np.allclose(R[supports], Rj, atol=1e-6)
    print(f"reactions {Rj/1000} kN; mid-span deflection {-u[5]*1000:.3f} mm")
    assert abs(Rj[1] + Rj[2] - 70e3) < 1e-6
