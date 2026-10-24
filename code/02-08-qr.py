"""Classical and modified Gram-Schmidt versus Householder QR."""
import numpy as np


def cgs(A):
    m, n = A.shape; Q = np.zeros((m, n)); R = np.zeros((n, n))
    for j in range(n):
        R[:j, j] = Q[:, :j].T @ A[:, j]            # all coefficients from the original column
        v = A[:, j] - Q[:, :j] @ R[:j, j]
        R[j, j] = np.linalg.norm(v); Q[:, j] = v / R[j, j]
    return Q, R


def mgs(A):
    m, n = A.shape; V = A.astype(float).copy(); Q = np.zeros((m, n)); R = np.zeros((n, n))
    for j in range(n):
        R[j, j] = np.linalg.norm(V[:, j]); Q[:, j] = V[:, j] / R[j, j]
        for k in range(j + 1, n):                  # remove q_j from the remaining columns right away
            R[j, k] = Q[:, j] @ V[:, k]; V[:, k] -= R[j, k] * Q[:, j]
    return Q, R


def householder(A):
    m, n = A.shape; R = A.astype(float).copy(); Q = np.eye(m)
    for k in range(n):
        x = R[k:, k]; v = x.copy()
        v[0] += np.copysign(np.linalg.norm(x), x[0])   # sign choice avoids cancellation
        v /= np.linalg.norm(v)
        R[k:, :] -= 2 * np.outer(v, v @ R[k:, :])
        Q[:, k:] -= 2 * np.outer(Q[:, k:] @ v, v)
    return Q[:, :n], np.triu(R[:n])


hilbert = lambda n: 1.0 / (np.arange(n)[:, None] + np.arange(n)[None, :] + 1)

if __name__ == "__main__":
    A = np.array([[1, 1], [1, 0], [0, 1.0]])
    for f in (cgs, mgs, householder):
        Q, R = f(A)
        Q, R = Q * np.sign(np.diag(R)), R * np.sign(np.diag(R))[:, None]   # fix signs to compare
        assert np.allclose(Q @ R, A) and np.allclose(R, [[2 ** 0.5, 2 ** -0.5], [0, 1.5 ** 0.5]])
    print(" n   cond      CGS       MGS       Householder")
    for n in (6, 8, 10):
        H = hilbert(n)
        loss = [np.linalg.norm(f(H)[0].T @ f(H)[0] - np.eye(n)) for f in (cgs, mgs, householder)]
        print(f"{n:2d}  {np.linalg.cond(H):.1e}  " + "  ".join(f"{l:.1e}" for l in loss))
        assert loss[2] < 1e-14 < loss[1] < loss[0]
    # least squares through QR matches lstsq on a tall random problem
    rng = np.random.default_rng(6)
    B, y = rng.standard_normal((50, 4)), rng.standard_normal(50)
    Q, R = householder(B)
    assert np.allclose(np.linalg.solve(R, Q.T @ y), np.linalg.lstsq(B, y, rcond=None)[0])
