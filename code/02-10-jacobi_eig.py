"""Jacobi eigenvalue method for symmetric matrices, with principal stresses as the test case."""
import math
import numpy as np


def jacobi_eig(A, tol=1e-14, max_rot=10000):
    A = np.array(A, dtype=float); n = len(A); Q = np.eye(n)
    for _ in range(max_rot):
        off = np.abs(A - np.diag(np.diag(A)))
        p, q = np.unravel_index(np.argmax(off), off.shape)
        if off[p, q] < tol * max(1.0, np.abs(np.diag(A)).max()):
            break
        theta = 0.5 * math.atan2(2 * A[p, q], A[p, p] - A[q, q])   # the principal-axis angle
        c, s = math.cos(theta), math.sin(theta)
        J = np.eye(n); J[p, p] = J[q, q] = c; J[p, q] = -s; J[q, p] = s
        A = J.T @ A @ J
        Q = Q @ J
    return np.diag(A), Q


def principal_2d(sx, sy, txy):
    c, r = (sx + sy) / 2, math.hypot((sx - sy) / 2, txy)
    return c + r, c - r, 0.5 * math.degrees(math.atan2(2 * txy, sx - sy))


if __name__ == "__main__":
    s1, s2, th = principal_2d(80, 20, 30)
    print(f"sigma1 = {s1:.2f} MPa, sigma2 = {s2:.2f} MPa, theta = {th:.1f} deg")
    assert abs(s1 - (50 + 30 * 2 ** 0.5)) < 1e-12 and abs(th - 22.5) < 1e-12
    w, Q = jacobi_eig([[80, 30], [30, 20]])
    assert np.allclose(sorted(w), [s2, s1]) and np.allclose(Q.T @ Q, np.eye(2))
    # the eigenvector of sigma1 points at 22.5 degrees
    v = Q[:, np.argmax(w)]
    assert abs(abs(math.degrees(math.atan2(v[1], v[0]))) % 180 - 22.5) < 1e-9
    # a 3D stress tensor (MPa)
    S = np.array([[50, 20, -10], [20, -30, 15], [-10, 15, 40.0]])
    w, Q = jacobi_eig(S)
    assert np.allclose(sorted(w), np.linalg.eigvalsh(S)) and np.allclose(Q @ np.diag(w) @ Q.T, S)
    assert np.allclose(Q.T @ Q, np.eye(3), atol=1e-13)
    print("3D principal stresses:", np.round(sorted(w, reverse=True), 3))
    # random symmetric matrices
    rng = np.random.default_rng(8)
    for n in (4, 8, 12):
        B = rng.standard_normal((n, n)); B = B + B.T
        w, Q = jacobi_eig(B)
        assert np.allclose(sorted(w), np.linalg.eigvalsh(B)) and np.allclose(Q.T @ Q, np.eye(n))
