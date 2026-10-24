"""Orthographic projection as linear maps: project a 3D wireframe of a stepped block to front, top and side views and compare with the hand-drawn views."""
import numpy as np

# a stepped block: 60 long (x), 40 deep (y), 30 high (z), with the top-right 25 x 15 step cut away along the full depth
P = np.array([[0, 0, 0], [60, 0, 0], [60, 0, 15], [35, 0, 15], [35, 0, 30], [0, 0, 30]], dtype=float)
V = np.vstack([P, P + [0, 40, 0]])                        # front profile (y = 0) and back profile (y = 40)
E = [(i, (i + 1) % 6) for i in range(6)] + [(i + 6, (i + 1) % 6 + 6) for i in range(6)] + [(i, i + 6) for i in range(6)]

# the three principal views are linear maps R^3 -> R^2 (drop one coordinate)
FRONT = np.array([[1, 0, 0], [0, 0, 1]])                 # look along +y: see x across, z up
TOP = np.array([[1, 0, 0], [0, 1, 0]])                   # look down -z: see x across, y up
SIDE = np.array([[0, 1, 0], [0, 0, 1]])                  # look along -x (from the right): see y across, z up


def project(M, verts, edges):
    """Project every edge and return the set of distinct 2D segments (zero-length ones dropped; overlapping ones merged by endpoints)."""
    q = verts @ M.T
    segs = set()
    for a, b in edges:
        pa, pb = tuple(np.round(q[a], 9)), tuple(np.round(q[b], 9))
        if pa != pb:
            segs.add(tuple(sorted((pa, pb))))
    return segs


def split_collinear(segs):
    """Break segments at every vertex lying on them, so views compare as sets of minimal segments."""
    pts = {p for s in segs for p in s}
    out = set()
    for a, b in segs:
        a_, b_ = np.array(a), np.array(b); d = b_ - a_; L2 = d @ d
        on = sorted({p for p in pts if abs(d[0] * (p[1] - a_[1]) - d[1] * (p[0] - a_[0])) < 1e-9 and -1e-9 <= (np.array(p) - a_) @ d <= L2 + 1e-9},
                    key=lambda p: (np.array(p) - a_) @ d)
        out |= {tuple(sorted((on[i], on[i + 1]))) for i in range(len(on) - 1)}
    return out


def seg(x1, y1, x2, y2):
    return tuple(sorted(((float(x1), float(y1)), (float(x2), float(y2)))))


if __name__ == "__main__":
    # hand-drawn views (as you would sketch them on grid paper)
    hand_front = {seg(0, 0, 60, 0), seg(60, 0, 60, 15), seg(60, 15, 35, 15), seg(35, 15, 35, 30), seg(35, 30, 0, 30), seg(0, 30, 0, 0)}
    hand_top = {seg(0, 0, 35, 0), seg(35, 0, 60, 0), seg(60, 0, 60, 40), seg(60, 40, 35, 40), seg(35, 40, 0, 40), seg(0, 40, 0, 0), seg(35, 0, 35, 40)}
    hand_side = {seg(0, 0, 40, 0), seg(40, 0, 40, 15), seg(40, 15, 40, 30), seg(40, 30, 0, 30), seg(0, 30, 0, 15), seg(0, 15, 0, 0), seg(0, 15, 40, 15)}
    for name, M, hand in (("front", FRONT, hand_front), ("top", TOP, hand_top), ("side", SIDE, hand_side)):
        got = split_collinear(project(M, V, E))
        print(f"{name}: {len(got)} segments, matches the hand drawing: {got == split_collinear(hand)}")
        assert got == split_collinear(hand)
    # projection matrices are idempotent when embedded in 3D: P = M^T M satisfies P @ P = P
    for M in (FRONT, TOP, SIDE):
        Pm = M.T @ M
        assert np.allclose(Pm @ Pm, Pm)
    # isometric view: rotate 45 deg about z, then atan(1/sqrt 2) = 35.264 deg about x, then drop the depth axis
    a, b = np.radians(45), np.arctan(1 / np.sqrt(2))
    Rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, np.cos(b), -np.sin(b)], [0, np.sin(b), np.cos(b)]])
    ISO = np.array([[1, 0, 0], [0, 0, 1]]) @ Rx @ Rz
    k = np.linalg.norm(ISO, axis=0)
    print(f"isometric foreshortening of x, y, z axes: {k.round(6)} (sqrt(2/3) = {np.sqrt(2/3):.6f}); tilt {np.degrees(b):.3f} deg")
    assert np.allclose(k, np.sqrt(2 / 3))
