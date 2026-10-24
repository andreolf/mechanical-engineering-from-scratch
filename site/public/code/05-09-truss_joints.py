"""Plane truss by the method of joints: assemble 2 equations per joint and solve for all member forces at once."""
import math
import numpy as np


def solve_truss(nodes, members, supports, loads):
    """nodes: (x, y); members: (i, j); supports: (node, (dx, dy)) unit reaction directions;
    loads: {node: (Fx, Fy)}. Returns member forces (tension positive) and reactions."""
    nodes = np.asarray(nodes, float)
    n, m, r = len(nodes), len(members), len(supports)
    A = np.zeros((2 * n, m + r)); b = np.zeros(2 * n)
    for k, (i, j) in enumerate(members):
        e = (nodes[j] - nodes[i]) / np.linalg.norm(nodes[j] - nodes[i])
        A[2 * i:2 * i + 2, k] += e          # a tension member pulls joint i towards j
        A[2 * j:2 * j + 2, k] -= e
    for k, (node, d) in enumerate(supports):
        A[2 * node:2 * node + 2, m + k] += d
    for node, F in loads.items():
        b[2 * node:2 * node + 2] -= F
    if np.linalg.matrix_rank(A) < m + r or 2 * n != m + r:
        raise ValueError("not a determinate truss (mechanism or redundant members)")
    x = np.linalg.solve(A, b)
    return x[:m], x[m:]


def warren(panels=3, a=4.0, P=10.0):
    """Warren truss of equilateral triangles: bottom chord nodes 0..panels, top nodes above the mid-points."""
    h = a * math.sin(math.radians(60))
    bot = [(i * a, 0.0) for i in range(panels + 1)]
    top = [((i + 0.5) * a, h) for i in range(panels)]
    nodes = bot + top
    nb = panels + 1
    members = [(i, i + 1) for i in range(panels)]                          # bottom chord
    members += [(nb + i, nb + i + 1) for i in range(panels - 1)]           # top chord
    for i in range(panels):
        members += [(i, nb + i), (nb + i, i + 1)]                          # diagonals
    supports = [(0, (1, 0)), (0, (0, 1)), (panels, (0, 1))]               # pin left, roller right
    loads = {i: (0.0, -P) for i in range(1, panels)}
    return nodes, members, supports, loads


if __name__ == "__main__":
    nodes, members, supports, loads = warren()
    F, R = solve_truss(nodes, members, supports, loads)
    for (i, j), f in zip(members, F):
        print(f"member {i}-{j}: {f:8.4f} kN {'tension' if f > 1e-9 else 'compression' if f < -1e-9 else 'zero'}")
    print("reactions", np.round(R, 4))
    # hand solution at joint 0: Ay = 10, diagonal 0-4 at 60 deg: F sin60 + 10 = 0, bottom: F01 + F cos60 = 0
    k04 = members.index((0, 4)); k01 = members.index((0, 1))
    assert abs(F[k04] + 10 / math.sin(math.radians(60))) < 1e-9 and abs(F[k01] - 10 / math.tan(math.radians(60))) < 1e-9
    assert np.allclose(R, [0, 10, 10])
    assert len(members) == 2 * len(nodes) - 3
    # break the bridge: delete a diagonal and the truss becomes a mechanism
    try:
        solve_truss(nodes, [mb for mb in members if mb != (4, 1)], supports, loads)
        raise AssertionError("should have failed")
    except ValueError as err:
        print("without member 4-1:", err)
