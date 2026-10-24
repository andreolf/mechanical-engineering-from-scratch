"""Method of sections on a Pratt truss bridge, checked against a full method-of-joints solve."""
import numpy as np


def solve_truss(nodes, members, supports, loads):
    nodes = np.asarray(nodes, float); n, m = len(nodes), len(members)
    A = np.zeros((2 * n, m + len(supports))); b = np.zeros(2 * n)
    for k, (i, j) in enumerate(members):
        e = (nodes[j] - nodes[i]) / np.linalg.norm(nodes[j] - nodes[i])
        A[2 * i:2 * i + 2, k] += e; A[2 * j:2 * j + 2, k] -= e
    for k, (node, d) in enumerate(supports):
        A[2 * node:2 * node + 2, m + k] += d
    for node, F in loads.items():
        b[2 * node:2 * node + 2] -= F
    x = np.linalg.solve(A, b)
    return x[:m], x[m:]


def section(nodes, members, cut, left, external):
    """Equilibrium of the part containing the nodes in `left`. cut: indices of the (three) cut members;
    external: list of ((x, y), (Fx, Fy)) acting on that part, reactions included. Returns the cut forces."""
    nodes = np.asarray(nodes, float)
    A = np.zeros((3, len(cut))); b = np.zeros(3)
    for c, k in enumerate(cut):
        i, j = members[k]
        inside, outside = (i, j) if i in left else (j, i)
        p = nodes[inside]; e = (nodes[outside] - p) / np.linalg.norm(nodes[outside] - p)   # tension pulls outward
        A[:, c] = [e[0], e[1], p[0] * e[1] - p[1] * e[0]]
    for (x, y), (fx, fy) in external:
        b -= [fx, fy, x * fy - y * fx]
    return np.linalg.solve(A, b)


def pratt(panels=6, a=3.0, h=4.0, P=12.0):
    bot = [(i * a, 0.0) for i in range(panels + 1)]            # nodes 0..6
    top = [(i * a, h) for i in range(1, panels)]                # nodes 7..11 above bottom nodes 1..5
    T = lambda i: panels + i                                    # top node above bottom node i
    members = [(i, i + 1) for i in range(panels)] + [(T(i), T(i + 1)) for i in range(1, panels - 1)]
    members += [(0, T(1)), (panels, T(panels - 1))] + [(i, T(i)) for i in range(1, panels)]
    half = panels // 2
    members += [(T(i), i + 1) for i in range(1, half)] + [(T(i), i - 1) for i in range(half + 1, panels)]
    supports = [(0, (1, 0)), (0, (0, 1)), (panels, (0, 1))]
    loads = {i: (0.0, -P) for i in range(1, panels)}
    return bot + top, members, supports, loads, T


if __name__ == "__main__":
    nodes, members, supports, loads, T = pratt()
    F, R = solve_truss(nodes, members, supports, loads)
    print(f"{len(nodes)} joints, {len(members)} members, reactions {np.round(R, 4)} kN")
    # cut through panel 3 (6 m < x < 9 m): top chord T2-T3, diagonal T2-3, bottom chord 2-3
    cut = [members.index((T(2), T(3))), members.index((T(2), 3)), members.index((2, 3))]
    left = {0, 1, 2, T(1), T(2)}
    ext = [((0, 0), (R[0], R[1]))] + [(nodes[i], loads[i]) for i in (1, 2)]
    Fs = section(nodes, members, cut, left, ext)
    for k, f in zip(cut, Fs):
        print(f"member {members[k]}: section {f:8.4f} kN, joints {F[k]:8.4f} kN")
    assert np.allclose(Fs, F[cut], atol=1e-9)
    # one equation each, by hand: moments about the intersection of the other two cut members
    bottom = (30 * 6 - 12 * 3) / 4            # about top node at (6, 4)
    top = -(30 * 9 - 12 * 6 - 12 * 3) / 4     # about bottom node at (9, 0)
    diag = (30 - 12 - 12) / 0.8               # vertical equilibrium, the chords are horizontal
    print(f"hand: bottom {bottom} kN, top {top} kN, diagonal {diag} kN")
    assert np.allclose(Fs, [top, diag, bottom])
