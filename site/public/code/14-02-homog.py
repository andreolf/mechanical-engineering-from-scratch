"""Homogeneous coordinates: a small 4x4 transform library with composition and inverse, and the proof that order matters."""
import math
import numpy as np


def translate(tx, ty, tz):
    T = np.eye(4); T[:3, 3] = (tx, ty, tz); return T


def rotate(axis, deg):
    """Rotation about a unit axis through the origin, by Rodrigues' formula."""
    k = np.asarray(axis, float); k = k / np.linalg.norm(k)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    t = math.radians(deg)
    R = np.eye(4); R[:3, :3] = np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K
    return R


def scale(sx, sy, sz):
    return np.diag([sx, sy, sz, 1.0])


def compose(*Ms):
    """compose(A, B, C) applies A first, then B, then C: the matrix is C @ B @ A."""
    out = np.eye(4)
    for M in Ms:
        out = M @ out
    return out


def rigid_inverse(M):
    """Inverse of a rotation + translation without a general matrix inverse: [R t]^-1 = [R^T, -R^T t]."""
    R, t = M[:3, :3], M[:3, 3]
    out = np.eye(4); out[:3, :3] = R.T; out[:3, 3] = -R.T @ t
    return out


def apply(M, pts):
    P = np.hstack([np.asarray(pts, float), np.ones((len(pts), 1))])
    return (P @ M.T)[:, :3]


if __name__ == "__main__":
    p = np.array([[100.0, 0, 0]])
    A = compose(rotate([0, 0, 1], 90), translate(50, 0, 0))   # rotate, then translate
    B = compose(translate(50, 0, 0), rotate([0, 0, 1], 90))   # translate, then rotate
    pa, pb = apply(A, p)[0], apply(B, p)[0]
    print(f"point (100, 0, 0): rotate-then-translate -> {pa.round(9)}, translate-then-rotate -> {pb.round(9)}")
    assert np.allclose(pa, [50, 100, 0]) and np.allclose(pb, [0, 150, 0]) and not np.allclose(A, B)
    # rotation about a point c: move c to the origin, rotate, move back
    # a Subak weir gate: a 1.2 m panel hinged at its top edge (0, 0, 1.5) swings up 60 deg about the x axis
    hinge = np.array([0.0, 0.0, 1.5])
    G = compose(translate(*-hinge), rotate([1, 0, 0], 60), translate(*hinge))
    bottom = apply(G, [[0.0, 0.0, 0.3]])[0]
    print(f"gate bottom edge moves from (0, 0, 0.3) to {bottom.round(6)}; distance to hinge {np.linalg.norm(bottom - hinge):.9f} m")
    assert abs(np.linalg.norm(bottom - hinge) - 1.2) < 1e-12 and abs(bottom[2] - (1.5 - 1.2 * math.cos(math.radians(60)))) < 1e-12
    # rigid inverse agrees with the general inverse, and M @ M^-1 = I
    M = compose(rotate([1, 2, 3], 37), translate(4, -5, 6), rotate([0, 1, 0], -20))
    assert np.allclose(rigid_inverse(M), np.linalg.inv(M)) and np.allclose(M @ rigid_inverse(M), np.eye(4))
    # rotation blocks are orthonormal with determinant +1
    R = M[:3, :3]
    print(f"det R = {np.linalg.det(R):.12f}, max |R^T R - I| = {np.abs(R.T @ R - np.eye(3)).max():.1e}")
    assert abs(np.linalg.det(R) - 1) < 1e-12
    # six bolt holes on a 100 mm pitch circle by repeated 60-degree rotation of one hole
    hole = np.array([[50.0, 0, 0]])
    holes = np.vstack([apply(rotate([0, 0, 1], 60 * i), hole) for i in range(6)])
    gaps = np.linalg.norm(holes - np.roll(holes, 1, axis=0), axis=1)
    print(f"bolt circle: neighbouring holes {gaps.round(9)} mm apart (equals the radius for six holes)")
    assert np.allclose(gaps, 50)
