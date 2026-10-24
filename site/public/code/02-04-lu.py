"""LU decomposition with partial pivoting: factor once, solve many load cases."""
import numpy as np


def lu_factor(A):
    A = np.array(A, dtype=float)
    n = A.shape[0]
    perm = np.arange(n)
    swaps = 0
    for k in range(n - 1):
        p = k + np.argmax(np.abs(A[k:, k]))
        if p != k:
            A[[k, p]] = A[[p, k]]; perm[[k, p]] = perm[[p, k]]; swaps += 1
        A[k + 1:, k] /= A[k, k]                                    # multipliers stored in place
        A[k + 1:, k + 1:] -= np.outer(A[k + 1:, k], A[k, k + 1:])  # update the trailing block
    return A, perm, swaps


def lu_solve(F, perm, b):
    n = len(b)
    y = np.array(b, dtype=float)[perm]
    for i in range(n):                    # forward, unit diagonal
        y[i] -= F[i, :i] @ y[:i]
    x = y.copy()
    for i in range(n - 1, -1, -1):        # back
        x[i] = (y[i] - F[i, i + 1:] @ x[i + 1:]) / F[i, i]
    return x


def det(F, swaps):
    return (-1) ** swaps * np.prod(np.diag(F))


if __name__ == "__main__":
    A = [[2, 1, -1], [-3, -1, 2], [-2, 1, 2]]
    F, perm, s = lu_factor(A)
    L = np.tril(F, -1) + np.eye(3); U = np.triu(F)
    assert np.allclose(L @ U, np.array(A, float)[perm])
    assert np.allclose(lu_solve(F, perm, [1, 0, 0]), [4, -2, 5])
    assert np.allclose(lu_solve(F, perm, [8, -11, -3]), [2, 3, -1])
    assert abs(det(F, s) - (-1)) < 1e-12
    # many load cases on a bigger matrix: all match numpy
    rng = np.random.default_rng(2)
    n = 200
    K = rng.standard_normal((n, n)) + n * np.eye(n)
    F, perm, s = lu_factor(K)
    B = rng.standard_normal((n, 25))
    X = np.column_stack([lu_solve(F, perm, B[:, j]) for j in range(25)])
    assert np.allclose(K @ X, B, atol=1e-10)
    assert np.isclose(det(F, s), np.linalg.det(K), rtol=1e-9)
    print(f"factored once, solved 25 load cases; work ratio ~ {(2/3*n**3 + 25*2*n**2)/(25*2/3*n**3):.3f} of re-eliminating each time")
