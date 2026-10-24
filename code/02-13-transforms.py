"""Rotation matrices, homogeneous transforms and tensor rotation."""
import math
import numpy as np


def rot2(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[c, -s], [s, c]])


def rot3(axis, t):
    c, s = math.cos(t), math.sin(t)
    i, j = {"x": (1, 2), "y": (2, 0), "z": (0, 1)}[axis]
    R = np.eye(3); R[i, i] = R[j, j] = c; R[i, j] = -s; R[j, i] = s
    return R


def homog(R, t):
    n = len(t); T = np.eye(n + 1); T[:n, :n] = R; T[:n, n] = t
    return T


def arm_tip(L1, L2, t1, t2):
    T1 = homog(rot2(t1), rot2(t1) @ [L1, 0])
    T2 = homog(rot2(t2), rot2(t2) @ [L2, 0])
    return (T1 @ T2 @ [0, 0, 1])[:2]


if __name__ == "__main__":
    tip = arm_tip(0.4, 0.3, math.radians(30), math.radians(45))
    print("tip:", np.round(tip, 4))
    assert np.allclose(tip, [0.4 * math.cos(math.pi / 6) + 0.3 * math.cos(math.radians(75)),
                             0.4 * math.sin(math.pi / 6) + 0.3 * math.sin(math.radians(75))], atol=1e-15)
    rng = np.random.default_rng(10)
    for _ in range(100):
        R = rot3("x", rng.uniform(-3, 3)) @ rot3("y", rng.uniform(-3, 3)) @ rot3("z", rng.uniform(-3, 3))
        assert np.allclose(R.T @ R, np.eye(3), atol=1e-14) and abs(np.linalg.det(R) - 1) < 1e-14
        v = rng.standard_normal(3)
        assert abs(np.linalg.norm(R @ v) - np.linalg.norm(v)) < 1e-13
    # order matters in 3D
    A = rot3("z", math.pi / 2) @ rot3("x", math.pi / 2)
    B = rot3("x", math.pi / 2) @ rot3("z", math.pi / 2)
    assert not np.allclose(A, B)
    print("Rz Rx e_y =", np.round(A @ [0, 1, 0], 12), " Rx Rz e_y =", np.round(B @ [0, 1, 0], 12))
    # rotating the axes by the principal angle diagonalises the stress tensor
    S = np.array([[80, 30], [30, 20.0]])
    R = rot2(math.radians(22.5))
    Sp = R.T @ S @ R
    assert abs(Sp[0, 1]) < 1e-12 and np.allclose(np.diag(Sp), [50 + 30 * 2 ** 0.5, 50 - 30 * 2 ** 0.5])
    assert abs(np.trace(Sp) - np.trace(S)) < 1e-12        # invariants survive any rotation
    print("rotated stress tensor:\n", np.round(Sp, 6))
