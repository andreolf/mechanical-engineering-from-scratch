"""Determinants by elimination versus cofactor expansion."""
import itertools
import math
import time
import numpy as np


def det_lu(A):
    A = np.array(A, dtype=float); n = len(A); sign = 1.0
    for k in range(n):
        p = k + np.argmax(np.abs(A[k:, k]))
        if A[p, k] == 0.0:
            return 0.0
        if p != k:
            A[[k, p]] = A[[p, k]]; sign = -sign
        A[k + 1:, k:] -= np.outer(A[k + 1:, k] / A[k, k], A[k, k:])
    return sign * np.prod(np.diag(A))


def det_cofactor(A):
    n = len(A)
    if n == 1:
        return A[0][0]
    return sum((-1) ** j * A[0][j] * det_cofactor([row[:j] + row[j + 1:] for row in A[1:]]) for j in range(n))


if __name__ == "__main__":
    K = [[2, -1, 0], [-1, 2, -1], [0, -1, 1]]
    assert abs(det_lu(K) - 1) < 1e-14 and det_cofactor(K) == 1
    free = [[1, -1, 0], [-1, 2, -1], [0, -1, 1]]
    assert abs(det_lu(free)) < 1e-14 and np.allclose(np.array(free) @ [1, 1, 1], 0)
    rng = np.random.default_rng(4)
    A, B = rng.standard_normal((6, 6)), rng.standard_normal((6, 6))
    assert np.isclose(det_lu(A @ B), det_lu(A) * det_lu(B))
    assert np.isclose(det_lu(3 * A), 3 ** 6 * det_lu(A))
    assert np.isclose(det_lu(A), det_cofactor(A.tolist())) and np.isclose(det_lu(A), np.linalg.det(A))
    # swapping two rows flips the sign
    S = A.copy(); S[[0, 3]] = S[[3, 0]]
    assert np.isclose(det_lu(S), -det_lu(A))
    for n in (6, 7, 8):
        M = rng.standard_normal((n, n)).tolist()
        t = time.perf_counter(); det_cofactor(M); tc = time.perf_counter() - t
        t = time.perf_counter(); det_lu(M); tl = time.perf_counter() - t
        print(f"n = {n}: cofactor {tc*1e3:8.1f} ms, elimination {tl*1e3:6.2f} ms")
