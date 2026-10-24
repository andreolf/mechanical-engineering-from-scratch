"""Direct stiffness method for 2D pin-jointed trusses."""
import math
import numpy as np


def solve_truss(nodes, bars, EA, supports, loads):
    """nodes: [(x, y)], bars: [(i, j)], EA: float or list, supports: {node: (fix_x, fix_y)}, loads: {node: (Fx, Fy)}."""
    n = len(nodes); K = np.zeros((2 * n, 2 * n)); f = np.zeros(2 * n)
    EA = [EA] * len(bars) if np.isscalar(EA) else EA
    geo = []
    for (i, j), ea in zip(bars, EA):
        dx, dy = np.subtract(nodes[j], nodes[i]); L = math.hypot(dx, dy); c, s = dx / L, dy / L
        g = np.array([-c, -s, c, s]); dofs = [2 * i, 2 * i + 1, 2 * j, 2 * j + 1]
        K[np.ix_(dofs, dofs)] += ea / L * np.outer(g, g)
        geo.append((dofs, g, ea / L))
    for node, (fx, fy) in loads.items():
        f[2 * node] += fx; f[2 * node + 1] += fy
    fixed = [2 * k + d for k, fix in supports.items() for d in (0, 1) if fix[d]]
    free = [d for d in range(2 * n) if d not in fixed]
    u = np.zeros(2 * n)
    Kff = K[np.ix_(free, free)]
    L = np.linalg.cholesky(Kff)                      # fails loudly if the truss is a mechanism
    u[free] = np.linalg.solve(L.T, np.linalg.solve(L, f[free]))
    N = np.array([k * g @ u[d] for d, g, k in geo])
    R = K @ u - f
    return u, N, R


if __name__ == "__main__":
    nodes = [(0, 0), (4, 0), (2, 1.5)]
    u, N, R = solve_truss(nodes, [(0, 2), (1, 2)], 1e8, {0: (1, 1), 1: (1, 1)}, {2: (0, -1e4)})
    print(f"apex deflection {u[5]*1e3:.4f} mm, bar forces {np.round(N, 1)} N, reactions {np.round(R[:4], 1)} N")
    assert abs(u[4]) < 1e-15 and abs(u[5] + 1e4 / 2.88e7) < 1e-15
    assert np.allclose(N, -1e4 / 1.2) and np.allclose(R[:4], [1e4 / 1.2 * 0.8, 5e3, -1e4 / 1.2 * 0.8, 5e3])  # reactions on the truss: inward, upward
    assert abs(R[1] + R[3] - 1e4) < 1e-9 and abs(R[0] + R[2]) < 1e-9          # global equilibrium
    # a Warren truss: 4 bays, 10 kN at every bottom joint; compare midspan chord force with statics
    bay, h, nb = 2.0, 1.5, 4
    bot = [(bay * i, 0.0) for i in range(nb + 1)]; top = [(bay * (i + 0.5), h) for i in range(nb)]
    nodes = bot + top; T = lambda i: nb + 1 + i
    bars = [(i, i + 1) for i in range(nb)] + [(T(i), T(i + 1)) for i in range(nb - 1)] \
         + [(i, T(i)) for i in range(nb)] + [(i + 1, T(i)) for i in range(nb)]
    loads = {i: (0, -1e4) for i in range(1, nb)}
    u, N, R = solve_truss(nodes, bars, 1e8, {0: (1, 1), nb: (0, 1)}, loads)
    # method of sections at midspan: the top chord over the middle (between top nodes 1 and 2) carries M/h
    M_mid = 1.5e4 * 4.0 - 1e4 * 2.0                    # reaction 15 kN times 4 m minus the load at 2 m
    i_top = nb + 1                                      # bar index of the top chord T(1)-T(2)
    print(f"Warren truss: midspan top chord {N[i_top]/1e3:.2f} kN, statics {-M_mid/h/1e3:.2f} kN")
    assert abs(N[i_top] + M_mid / h) < 1e-6 and abs(R[1] + R[2 * nb + 1] - 3e4) < 1e-6
    try:
        solve_truss([(0, 0), (1, 0)], [(0, 1)], 1e8, {0: (1, 1)}, {1: (0, -1)}); raise AssertionError
    except np.linalg.LinAlgError:
        print("a single bar with a free end is correctly rejected as a mechanism")
