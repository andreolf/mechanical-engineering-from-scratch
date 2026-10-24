"""Buckingham Pi groups as the null space of the dimension matrix."""
from fractions import Fraction
import numpy as np


def null_space_svd(A, tol=1e-12):
    """Orthonormal basis of the null space, from the SVD."""
    A = np.asarray(A, dtype=float)
    _, s, vt = np.linalg.svd(A)
    rank = int((s > tol * max(1.0, s[0])).sum())
    return vt[rank:].T, rank


def null_space_exact(A):
    """Rational basis of the null space by Gauss-Jordan elimination."""
    M = [[Fraction(x) for x in row] for row in A]
    rows, cols = len(M), len(M[0])
    pivots, r = [], 0
    for c in range(cols):
        p = next((i for i in range(r, rows) if M[i][c] != 0), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        M[r] = [x / M[r][c] for x in M[r]]
        for i in range(rows):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        pivots.append(c)
        r += 1
    free = [c for c in range(cols) if c not in pivots]
    basis = []
    for fcol in free:
        v = [Fraction(0)] * cols
        v[fcol] = Fraction(1)
        for i, pc in enumerate(pivots):
            v[pc] = -M[i][fcol]
        lead = next(x for x in v if x != 0)
        basis.append([x / lead for x in v])  # scale so the first exponent is 1
    return basis


def describe(names, v):
    return " ".join(f"{n}^{e}" for n, e in zip(names, v) if e != 0)


if __name__ == "__main__":
    # pendulum: columns T_p, l, g, m, theta0 ; rows M, L, T
    names = ["T_p", "l", "g", "m", "theta0"]
    A = [[0, 0, 0, 1, 0],
         [0, 1, 1, 0, 0],
         [1, 0, -2, 0, 0]]
    N, rank = null_space_svd(A)
    assert rank == 3 and N.shape[1] == 2
    assert np.allclose(np.asarray(A, float) @ N, 0, atol=1e-12)
    groups = null_space_exact(A)
    for v in groups:
        print("Pi:", describe(names, v))
    # first group is l^(-1/2) g^(1/2) T_p, i.e. T_p*sqrt(g/l)
    assert groups[0] == [1, Fraction(-1, 2), Fraction(1, 2), 0, 0]
    assert groups[1] == [0, 0, 0, 0, 1]

    # drag: F, rho, v, D, mu ; rows M, L, T
    D = [[1, 1, 0, 0, 1],
         [1, -3, 1, 1, -1],
         [-2, 0, -1, 0, -1]]
    g2 = null_space_exact(D)
    assert len(g2) == 2
    for v in g2:
        print("Pi:", describe(["F", "rho", "v", "D", "mu"], v))

    # worked example: water-tunnel speed and force ratio
    vm = 100 * 10 * (1.0e-6 / 1.5e-5)
    ratio = (1000 / 1.2) * (vm / 100) ** 2 * (1 / 10) ** 2
    assert abs(vm - 66.6667) < 1e-3 and abs(ratio - 3.7037) < 1e-3
    print(f"model speed {vm:.1f} km/h, force ratio {ratio:.2f}")
