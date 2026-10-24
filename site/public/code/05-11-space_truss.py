"""Space trusses: 3 equations per joint, Maxwell's count m + r = 3j, and a rank check."""
import math
import numpy as np


def solve_space_truss(nodes, members, supports, loads):
    """supports: (node, unit direction) per reaction component; loads {node: (Fx, Fy, Fz)}. Tension positive."""
    nodes = np.asarray(nodes, float); n, m, r = len(nodes), len(members), len(supports)
    A = np.zeros((3 * n, m + r)); b = np.zeros(3 * n)
    for k, (i, j) in enumerate(members):
        e = (nodes[j] - nodes[i]) / np.linalg.norm(nodes[j] - nodes[i])
        A[3 * i:3 * i + 3, k] += e; A[3 * j:3 * j + 3, k] -= e
    for k, (node, d) in enumerate(supports):
        A[3 * node:3 * node + 3, m + k] += d
    for node, F in loads.items():
        b[3 * node:3 * node + 3] -= F
    rank = np.linalg.matrix_rank(A)
    if A.shape[0] != A.shape[1] or rank < A.shape[1]:
        return None, rank, A.shape
    x = np.linalg.solve(A, b)
    return x[:m], rank, A.shape


def pinned(nodes_idx):
    return [(i, d) for i in nodes_idx for d in ((1, 0, 0), (0, 1, 0), (0, 0, 1))]


if __name__ == "__main__":
    # tripod (the simplest space truss): apex 4 m above an equilateral base of radius 1.5 m, legs pinned at the feet
    a, h, P = 1.5, 4.0, 12.0
    feet = [(a * math.cos(t), a * math.sin(t), 0.0) for t in np.radians([90, 210, 330])]
    nodes = [(0, 0, h)] + feet
    members = [(0, 1), (0, 2), (0, 3)]
    F, rank, shape = solve_space_truss(nodes, members, pinned([1, 2, 3]), {0: (0, 0, -P)})
    L = math.hypot(a, h)
    print(f"tripod legs: {np.round(F, 4)} kN (hand: -P L / (3 h) = {-P * L / (3 * h):.4f})")
    assert np.allclose(F, -P * L / (3 * h))
    # a sideways pull of 2 kN at the apex: one leg goes into tension
    F2, *_ = solve_space_truss(nodes, members, pinned([1, 2, 3]), {0: (0, -3.0, -P)})
    print(f"with 3 kN sideways: {np.round(F2, 4)} kN")
    assert abs(F2.sum() * h / L + P) < 1e-9          # vertical equilibrium still holds at the apex
    # a small ski-lift pylon: 2 m square base pinned, 1 m square top at 6 m
    base = [(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)]
    top = [(-0.5, -0.5, 6), (0.5, -0.5, 6), (0.5, 0.5, 6), (-0.5, 0.5, 6)]
    nodes = base + top
    legs = [(i, i + 4) for i in range(4)]
    ring = [(4 + i, 4 + (i + 1) % 4) for i in range(4)]
    side_diag = [(i, 4 + (i + 1) % 4) for i in range(4)]
    loads = {4: (0, 0, -5), 5: (0, 0, -5), 6: (3, 0, -5), 7: (3, 0, -5)}   # rope weight plus a wind push in x
    m = legs + ring + side_diag
    print(f"pylon: j = {len(nodes)}, m = {len(m)}, r = 12, Maxwell m + r - 3j = {len(m) + 12 - 3 * len(nodes)}")
    F, rank, shape = solve_space_truss(nodes, m, pinned(range(4)), loads)
    print(f"  four braced side faces: rank {rank} of {shape[1]}")
    for mb, f in zip(m, F):
        print(f"    member {mb}: {f:8.3f} kN")
    assert F is not None
    m2 = [mb for mb in m if mb != (0, 5)] + [(2, 5)]          # cross-brace one face twice, leave the front face unbraced
    F2, rank2, shape2 = solve_space_truss(nodes, m2, pinned(range(4)), loads)
    print(f"  front face unbraced, side face double-braced: m + r - 3j = {len(m2) + 12 - 3 * len(nodes)}, rank {rank2} of {shape2[1]} -> mechanism")
    assert F2 is None and rank2 < shape2[1]               # the unbraced side face can shear: counting is not enough
