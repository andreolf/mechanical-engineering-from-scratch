"""Planar frame solver (3 dofs per node: u, v, theta) for a steel bike frame; reactions checked against statics and global equilibrium."""
import math
import numpy as np


def k_frame(E, A, I, x1, y1, x2, y2):
    L = math.hypot(x2 - x1, y2 - y1)
    c, s = (x2 - x1) / L, (y2 - y1) / L
    a, b, d, e = E * A / L, 12 * E * I / L**3, 6 * E * I / L**2, E * I / L
    kl = np.array([[a, 0, 0, -a, 0, 0], [0, b, d, 0, -b, d], [0, d, 4 * e, 0, -d, 2 * e],
                   [-a, 0, 0, a, 0, 0], [0, -b, -d, 0, b, -d], [0, d, 2 * e, 0, -d, 4 * e]])
    T = np.zeros((6, 6))
    for i in (0, 3):
        T[i:i + 3, i:i + 3] = [[c, s, 0], [-s, c, 0], [0, 0, 1]]
    return T.T @ kl @ T, T, kl, L


def tube(D, t):
    d = D - 2 * t
    return math.pi * (D**2 - d**2) / 4, math.pi * (D**4 - d**4) / 64


def solve_frame(nodes, elems, E, loads, fixed):
    n = 3 * len(nodes)
    K = np.zeros((n, n)); F = np.zeros(n)
    for (i, j, A, I) in elems:
        k, *_ = k_frame(E, A, I, *nodes[i], *nodes[j])
        d = [3 * i, 3 * i + 1, 3 * i + 2, 3 * j, 3 * j + 1, 3 * j + 2]
        K[np.ix_(d, d)] += k
    for dof, val in loads.items():
        F[dof] += val
    free = [i for i in range(n) if i not in fixed]
    u = np.zeros(n)
    u[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])
    R = K @ u - F
    return u, R


# node coordinates in metres (rear axle at the origin)
NODES = [(0.0, 0.0),      # 0 rear axle
         (0.41, -0.07),   # 1 bottom bracket
         (0.25, 0.48),    # 2 seat cluster
         (0.86, 0.50),    # 3 head tube top
         (0.90, 0.36),    # 4 head tube bottom
         (0.99, 0.0)]     # 5 front axle (fork as one straight member)
MAIN, STAY, FORK = tube(0.0286, 0.0009), tube(0.016, 0.0008), tube(0.025, 0.0015)
ELEMS = [(0, 1, *STAY), (0, 2, *STAY), (1, 2, *MAIN), (2, 3, *MAIN), (1, 4, *MAIN), (3, 4, *MAIN), (4, 5, *FORK)]
E = 200e9


def bike(saddle=-700.0, pedal=-300.0, bars=-200.0):
    loads = {3 * 2 + 1: saddle, 3 * 1 + 1: pedal, 3 * 3 + 1: bars}
    fixed = [0, 1, 3 * 5 + 1]          # pin at the rear axle, roller at the front axle
    return solve_frame(NODES, ELEMS, E, loads, fixed), loads


if __name__ == "__main__":
    (u, R), loads = bike()
    Ry_rear, Ry_front, Rx_rear = R[1], R[16], R[0]
    print(f"reactions: rear {Ry_rear:.2f} N (horizontal {Rx_rear:.2e}), front {Ry_front:.2f} N")
    # statics: moments about the rear axle
    Mload = sum(val * NODES[dof // 3][0] for dof, val in loads.items())
    front_statics = -Mload / NODES[5][0]
    print(f"front reaction by moments: {front_statics:.2f} N")
    assert abs(Ry_front - front_statics) < 1e-6
    Fy = sum(loads.values())
    assert abs(Ry_rear + Ry_front + Fy) < 1e-6 and abs(Rx_rear) < 1e-6
    # all free-dof residuals vanish
    free = [i for i in range(18) if i not in (0, 1, 16)]
    assert np.max(np.abs(R[free])) < 1e-6
    print(f"seat cluster drops {1000*u[7]:.4f} mm, bottom bracket {1000*u[4]:.4f} mm; front axle slides {1000*u[15]:.4f} mm")
    # member end forces: axial force in each tube from local displacements
    for (i, j, A, I) in ELEMS:
        k, T, kl, L = k_frame(E, A, I, *NODES[i], *NODES[j])
        d = [3 * i, 3 * i + 1, 3 * i + 2, 3 * j, 3 * j + 1, 3 * j + 2]
        f = kl @ (T @ u[d])
        print(f"member {i}-{j}: axial {f[3]:8.1f} N, end moments {f[2]:6.2f} / {f[5]:6.2f} N m")
    # sanity: a single horizontal frame member as a cantilever gives PL^3/3EI and PL/EA
    A, I = MAIN
    (uc, _) = solve_frame([(0, 0), (0.6, 0)], [(0, 1, A, I)], E, {4: -100.0, 3: 1000.0}, [0, 1, 2])
    assert abs(uc[4] + 100 * 0.6**3 / (3 * E * I)) < 1e-12 and abs(uc[3] - 1000 * 0.6 / (E * A)) < 1e-15
