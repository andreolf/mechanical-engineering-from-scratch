"""NURBS: a full circle as a degree-2 rational B-spline, checked to be exactly round, against a plain polynomial approximation that is not."""
import math
import numpy as np


def find_span(U, p, u):
    n = len(U) - p - 2
    if u >= U[n + 1]: return n
    k = p
    while not (U[k] <= u < U[k + 1]): k += 1
    return k


def nurbs_point(P, W, U, p, u):
    """De Boor in homogeneous coordinates (w x, w y, w), then divide by w."""
    Pw = [np.array([P[i][0] * W[i], P[i][1] * W[i], W[i]], float) for i in range(len(P))]
    k = find_span(U, p, u)
    d = [Pw[j + k - p].copy() for j in range(p + 1)]
    for r in range(1, p + 1):
        for j in range(p, r - 1, -1):
            i = j + k - p
            a = (u - U[i]) / (U[i + p - r + 1] - U[i])
            d[j] = (1 - a) * d[j - 1] + a * d[j]
    return d[p][:2] / d[p][2]


def rational_quadratic(P0, P1, P2, w, t):
    b = np.array([(1 - t) ** 2, 2 * t * (1 - t) * w, t * t])
    return (b[0] * np.array(P0) + b[1] * np.array(P1) + b[2] * np.array(P2)) / b.sum()


if __name__ == "__main__":
    R = 31.0   # a 62 mm flange, radius in mm
    s = math.sqrt(2) / 2
    P = [(R, 0), (R, R), (0, R), (-R, R), (-R, 0), (-R, -R), (0, -R), (R, -R), (R, 0)]
    W = [1, s, 1, s, 1, s, 1, s, 1]
    U = [0, 0, 0, 0.25, 0.25, 0.5, 0.5, 0.75, 0.75, 1, 1, 1]
    us = np.linspace(0, 1, 10001)
    pts = np.array([nurbs_point(P, W, U, 2, u) for u in us])
    r = np.hypot(pts[:, 0], pts[:, 1])
    print(f"NURBS circle, R = {R} mm: radius error over 10001 points max {np.abs(r - R).max():.1e} mm")
    assert np.abs(r - R).max() < 1e-12
    # the parametrisation is not uniform in angle: speed varies, but the shape is exact
    ang = np.unwrap(np.arctan2(pts[:, 1], pts[:, 0]))
    print(f"angle at u = 0.125, the middle of the first quarter: {math.degrees(ang[1250]):.4f} deg (45 by symmetry)")
    assert abs(math.degrees(ang[1250]) - 45) < 1e-9
    q = math.degrees(ang[625])
    print(f"angle at u = 0.0625: {q:.4f} deg, not 22.5: the speed is non-uniform")
    # the same quarter with weight 1 (a plain quadratic Bezier) is a parabola, not a circle
    tq = np.linspace(0, 1, 2001)
    rq = [np.hypot(*rational_quadratic((R, 0), (R, R), (0, R), 1.0, t)) for t in tq]
    print(f"polynomial (w = 1) quarter arc: radius ranges {min(rq):.4f} to {max(rq):.4f} mm, bulging out by up to {max(rq) - R:.4f} mm")
    assert max(rq) - R > 1.5
    # conic family: w < 1 ellipse, w = 1 parabola, w > 1 hyperbola; the curve's shoulder point at t = 1/2 is the clean test
    for w in (0.5, s, 1.0, 2.0):
        m = rational_quadratic((R, 0), (R, R), (0, R), w, 0.5)
        print(f"  w = {w:.4f}: shoulder point at radius {np.hypot(*m):.4f} mm")
    assert abs(np.hypot(*rational_quadratic((R, 0), (R, R), (0, R), s, 0.5)) - R) < 1e-12
