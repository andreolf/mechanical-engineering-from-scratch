"""Rank and null space by row reduction with a tolerance, checked against the SVD."""
import math
import numpy as np


def rref(A, tol=None):
    R = np.array(A, dtype=float); m, n = R.shape
    tol = tol if tol is not None else max(m, n) * np.finfo(float).eps * max(1.0, np.abs(R).max())
    pivots, row = [], 0
    for col in range(n):
        if row == m:
            break
        p = row + np.argmax(np.abs(R[row:, col]))
        if abs(R[p, col]) <= tol:
            R[row:, col] = 0.0
            continue
        R[[row, p]] = R[[p, row]]
        R[row] /= R[row, col]
        for i in range(m):
            if i != row:
                R[i] -= R[i, col] * R[row]
        pivots.append(col); row += 1
    return R, pivots


def null_space(A):
    R, piv = rref(A); n = R.shape[1]
    free = [j for j in range(n) if j not in piv]
    basis = []
    for f in free:
        v = np.zeros(n); v[f] = 1.0
        for i, p in enumerate(piv):
            v[p] = -R[i, f]
        basis.append(v)
    return np.array(basis).T if basis else np.zeros((n, 0))


def rank_svd(A):
    s = np.linalg.svd(np.array(A, float), compute_uv=False)
    return int(np.sum(s > s[0] * max(np.shape(A)) * np.finfo(float).eps))


def truss_stiffness(nodes, bars, EA=1.0):
    K = np.zeros((2 * len(nodes), 2 * len(nodes)))
    for i, j in bars:
        d = np.subtract(nodes[j], nodes[i]); L = math.hypot(*d); c, s = d / L
        k = EA / L * np.outer([-c, -s, c, s], [-c, -s, c, s])
        idx = [2 * i, 2 * i + 1, 2 * j, 2 * j + 1]
        K[np.ix_(idx, idx)] += k
    return K


if __name__ == "__main__":
    K = [[1, -1, 0], [-1, 2, -1], [0, -1, 1]]
    R, piv = rref(K)
    N = null_space(K)
    assert len(piv) == 2 and rank_svd(K) == 2 and N.shape == (3, 1)
    assert np.allclose(N[:, 0] / N[0, 0], [1, 1, 1])
    # a free triangle truss: rank 3, null space = 2 translations + 1 rotation
    tri = truss_stiffness([(0, 0), (2, 0), (1, 1.6)], [(0, 1), (1, 2), (2, 0)])
    Nt = null_space(tri)
    print("triangle truss: rank", len(rref(tri)[1]), "svd rank", rank_svd(tri), "null dim", Nt.shape[1])
    assert len(rref(tri)[1]) == 3 == rank_svd(tri) and Nt.shape[1] == 3
    assert np.allclose(tri @ Nt, 0, atol=1e-12)
    rot = np.array([c for x, y in [(0, 0), (2, 0), (1, 1.6)] for c in (-y, x)])  # small rotation: u = -y, v = x
    assert np.allclose(tri @ rot, 0, atol=1e-12)
    # rank-nullity on random low-rank matrices
    rng = np.random.default_rng(5)
    for r in range(1, 6):
        A = rng.standard_normal((7, r)) @ rng.standard_normal((r, 6))
        assert rank_svd(A) == r and len(rref(A)[1]) == r and null_space(A).shape[1] == 6 - r
    print("rank-nullity holds for all tests")
