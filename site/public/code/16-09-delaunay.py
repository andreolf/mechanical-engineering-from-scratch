"""A small meshing pipeline from scratch: points on a dam cross-section, Bowyer-Watson Delaunay triangulation, quality (radius ratio), Laplacian smoothing; checks for no inverted elements and the empty-circumcircle property."""
import math
import numpy as np

DAM = np.array([[0.0, 0.0], [45.0, 0.0], [8.0, 60.0], [0.0, 60.0]])   # gravity dam profile (m), counter-clockwise


def circumcircle(P, t):
    (ax, ay), (bx, by), (cx, cy) = P[t[0]], P[t[1]], P[t[2]]
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay) + (cx**2 + cy**2) * (ay - by)) / d
    uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx) + (cx**2 + cy**2) * (bx - ax)) / d
    return ux, uy, (ax - ux)**2 + (ay - uy)**2


def area(P, t):
    (ax, ay), (bx, by), (cx, cy) = P[t[0]], P[t[1]], P[t[2]]
    return 0.5 * ((bx - ax) * (cy - ay) - (cx - ax) * (by - ay))


def bowyer_watson(pts):
    lo, hi = pts.min(0), pts.max(0); span = (hi - lo).max() * 20; mid = (lo + hi) / 2
    P = np.vstack([pts, [[mid[0] - span, mid[1] - span], [mid[0] + span, mid[1] - span], [mid[0], mid[1] + span]]])
    n = len(pts); tris = {(n, n + 1, n + 2): circumcircle(P, (n, n + 1, n + 2))}
    for i in range(n):
        x, y = P[i]
        bad = [t for t, (ux, uy, r2) in tris.items() if (x - ux)**2 + (y - uy)**2 < r2 * (1 - 1e-12)]
        edges = {}
        for t in bad:
            for e in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
                k = tuple(sorted(e)); edges[k] = edges.get(k, 0) + 1
            del tris[t]
        for t in bad:
            for e in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
                if edges[tuple(sorted(e))] == 1:      # boundary of the cavity
                    nt = (e[0], e[1], i)
                    if area(P, nt) < 0: nt = (e[1], e[0], i)
                    tris[nt] = circumcircle(P, nt)
    T = np.array([t for t in tris if max(t) < n])
    return T


def quality(P, t):
    """Radius ratio 2 r_in / R: 1 for an equilateral triangle, 0 for a sliver."""
    a, b, c = (np.linalg.norm(P[t[1]] - P[t[2]]), np.linalg.norm(P[t[2]] - P[t[0]]), np.linalg.norm(P[t[0]] - P[t[1]]))
    s = (a + b + c) / 2; A = abs(area(P, t))
    return 2 * (A / s) / (a * b * c / (4 * A))


def inside(poly, x, y):
    return all((poly[(k + 1) % len(poly)][0] - poly[k][0]) * (y - poly[k][1]) - (poly[(k + 1) % len(poly)][1] - poly[k][1]) * (x - poly[k][0]) >= 0 for k in range(len(poly)))


def seed_points(poly, h):
    pts = []
    for k in range(len(poly)):          # boundary points at spacing about h
        a, b = poly[k], poly[(k + 1) % len(poly)]
        m = max(1, round(np.linalg.norm(b - a) / h))
        pts += [a + (b - a) * j / m for j in range(m)]
    bd = np.array(pts)
    row = 0
    for y in np.arange(h * 0.5, poly[:, 1].max(), h * math.sqrt(3) / 2):   # hexagonal interior lattice
        for x in np.arange((row % 2) * h / 2 + h * 0.3, poly[:, 0].max(), h):
            if inside(poly, x, y) and np.min(np.hypot(bd[:, 0] - x, bd[:, 1] - y)) > 0.6 * h:
                pts.append(np.array([x, y]))
        row += 1
    return np.array(pts), len(bd)


def smooth(P, T, nb, iters=5):
    P = P.copy(); nbrs = [set() for _ in P]
    for t in T:
        for a in t:
            nbrs[a].update(t)
    for _ in range(iters):
        for i in range(nb, len(P)):
            nb_i = list(nbrs[i] - {i}); P[i] = P[nb_i].mean(0)
    return P


if __name__ == "__main__":
    pts, nb = seed_points(DAM, 5.0)
    T = bowyer_watson(pts)
    # Euler: for a triangulation of a convex region, triangles = 2 n - b - 2 (n points, b on the hull)
    print(f"{len(pts)} points ({nb} on the boundary), {len(T)} triangles; Euler formula gives {2*len(pts) - nb - 2}")
    assert len(T) == 2 * len(pts) - nb - 2
    A = np.array([area(pts, t) for t in T])
    assert A.min() > 0, "inverted element"
    assert abs(A.sum() - 0.5 * (45 + 8) * 60) < 1e-8
    for t in T:      # empty circumcircle: no other point strictly inside
        ux, uy, r2 = circumcircle(pts, t)
        d2 = (pts[:, 0] - ux)**2 + (pts[:, 1] - uy)**2
        d2[list(t)] = np.inf
        assert d2.min() >= r2 * (1 - 1e-9)
    q = np.array([quality(pts, t) for t in T])
    print(f"total area {A.sum():.4f} m^2 (trapezoid 1590); quality min {q.min():.3f}, mean {q.mean():.3f}; {np.sum(q < 0.5)} below 0.5")
    P2 = smooth(pts, T, nb)
    A2 = np.array([area(P2, t) for t in T]); q2 = np.array([quality(P2, t) for t in T])
    print(f"after 5 Laplacian smoothing sweeps: min area {A2.min():.3f}, quality min {q2.min():.3f}, mean {q2.mean():.3f}")
    assert A2.min() > 0 and q2.mean() >= q.mean() - 1e-9
    # same boundary, interior points scattered at random: still valid, but worse quality
    rng = np.random.default_rng(16)
    inner = []
    while len(inner) < len(pts) - nb:
        x, y = rng.uniform(0, 45), rng.uniform(0, 60)
        if inside(DAM, x, y) and np.min(np.hypot(pts[:nb, 0] - x, pts[:nb, 1] - y)) > 1.0:
            inner.append([x, y])
    Pr = np.vstack([pts[:nb], inner]); Tr = bowyer_watson(Pr)
    qr = np.array([quality(Pr, t) for t in Tr])
    print(f"random interior points: {len(Tr)} triangles, quality min {qr.min():.3f}, mean {qr.mean():.3f}")
    assert min(area(Pr, t) for t in Tr) > 0 and qr.min() < q.min()
