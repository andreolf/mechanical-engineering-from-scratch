"""CFD mesh quality for a 2D quad mesh, with the checkMesh-style metrics a finite-volume
solver cares about: face non-orthogonality, face skewness, cell aspect ratio and
equiangle skewness. A graded channel-with-bump mesh passes; three nodes dragged out of
place are flagged. Then the first-cell height for a target y+. numpy only."""
import numpy as np

nx, ny = 40, 16
s = np.linspace(0, 1, ny + 1)
eta = 1 - np.tanh(2.0 * (1 - s)) / np.tanh(2.0)       # cells cluster toward the lower wall
xg = np.linspace(0, 4, nx + 1)
bump = 0.15 * np.exp(-((xg - 2) / 0.4) ** 2)
P = np.zeros((nx + 1, ny + 1, 2))
for i in range(nx + 1):
    P[i, :, 0] = xg[i]
    P[i, :, 1] = bump[i] + (1 - bump[i]) * eta        # follow the bump, flat at the top

def quality(P):
    nx, ny = P.shape[0] - 1, P.shape[1] - 1
    # cell centroids (area-weighted, from the two triangles) and areas
    A = P[:-1, :-1]; B = P[1:, :-1]; Cc = P[1:, 1:]; Dd = P[:-1, 1:]
    cross = lambda u, v: u[..., 0] * v[..., 1] - u[..., 1] * v[..., 0]
    a1 = 0.5 * cross(B - A, Cc - A); a2 = 0.5 * cross(Cc - A, Dd - A)
    area = a1 + a2
    cen = ((A + B + Cc) / 3 * a1[..., None] + (A + Cc + Dd) / 3 * a2[..., None]) / area[..., None]
    nonorth = np.zeros((nx, ny)); skew = np.zeros((nx, ny))
    def face(p0, p1, cO, cN):
        fc = 0.5 * (p0 + p1); t = p1 - p0
        n = np.stack([t[..., 1], -t[..., 0]], -1); n /= np.linalg.norm(n, axis=-1, keepdims=True)
        d = cN - cO
        cosang = abs(np.sum(n * d, -1)) / np.linalg.norm(d, axis=-1)
        ang = np.degrees(np.arccos(np.clip(cosang, -1, 1)))
        # skewness: distance from the face centre to where the line cO-cN crosses the face, over |d|
        lam = cross(p0 - cO, t) / cross(d, t)
        xi = cO + lam[..., None] * d
        sk = np.linalg.norm(fc - xi, axis=-1) / np.linalg.norm(d, axis=-1)
        return ang, sk
    # vertical internal faces between cells (i-1, j) and (i, j)
    angV, skV = face(P[1:-1, :-1], P[1:-1, 1:], cen[:-1], cen[1:])
    angH, skH = face(P[:-1, 1:-1], P[1:, 1:-1], cen[:, :-1], cen[:, 1:])
    for arr, val in ((nonorth, (angV, angH)), (skew, (skV, skH))):
        v, h = val
        arr[:-1] = np.maximum(arr[:-1], v); arr[1:] = np.maximum(arr[1:], v)
        arr[:, :-1] = np.maximum(arr[:, :-1], h); arr[:, 1:] = np.maximum(arr[:, 1:], h)
    # equiangle skewness and aspect ratio per cell
    corners = [A, B, Cc, Dd]
    angs = []
    for k in range(4):
        p, q, r = corners[k - 1], corners[k], corners[(k + 1) % 4]
        u, v = p - q, r - q
        angs.append(np.degrees(np.arccos(np.clip(np.sum(u * v, -1) / (np.linalg.norm(u, axis=-1) * np.linalg.norm(v, axis=-1)), -1, 1))))
    angs = np.array(angs)
    eqskew = np.maximum((angs.max(0) - 90) / 90, (90 - angs.min(0)) / 90)
    edges = np.array([np.linalg.norm(corners[(k + 1) % 4] - corners[k], axis=-1) for k in range(4)])
    aspect = edges.max(0) / edges.min(0)
    return dict(area=area, nonorth=nonorth, skew=skew, eqskew=eqskew, aspect=aspect)

def report(name, q):
    bad = (q["nonorth"] > 70) | (q["skew"] > 0.5) | (q["eqskew"] > 0.85) | (q["area"] <= 0)
    print(f"{name}: min area {q['area'].min():.2e}, max non-orthogonality {q['nonorth'].max():.1f} deg, max skewness {q['skew'].max():.3f}, "
          f"max equiangle skewness {q['eqskew'].max():.3f}, max aspect ratio {q['aspect'].max():.1f}; flagged cells: {bad.sum()}")
    return bad

q = quality(P)
bad0 = report("graded bump mesh", q)
assert bad0.sum() == 0 and q["area"].min() > 0

# drag three interior nodes out of place, as a bad hand edit or a failed smoother would
Pb = P.copy()
moved = [(10, 8), (25, 4), (30, 12)]
Pb[10, 8] += [0.08, 0.05]
Pb[25, 4] += [0.09, -0.02]
Pb[30, 12] += [0.08, 0.09]
qb = quality(Pb)
bad = report("damaged mesh", qb)
touch = np.zeros((nx, ny), bool)
for (i, j) in moved:
    touch[max(i - 1, 0):i + 1, max(j - 1, 0):j + 1] = True
idx = np.argwhere(bad)
print("flagged cells:", [tuple(map(int, c)) for c in idx])
near = touch.copy()                                   # cells touching a moved node, or sharing a face with one
near[1:] |= touch[:-1]; near[:-1] |= touch[1:]; near[:, 1:] |= touch[:, :-1]; near[:, :-1] |= touch[:, 1:]
assert bad.sum() > 0 and np.all(near[bad])            # nothing far from the damage is flagged
assert all(bad[max(i - 1, 0):i + 1, max(j - 1, 0):j + 1].any() for (i, j) in moved)   # and each damage spot is caught

# first-cell height for a target y+ on a flat plate (Schlichting's turbulent skin friction)
def first_cell(U, L, nu, yplus):
    Re = U * L / nu
    Cf = 0.026 * Re ** (-1 / 7)
    ut = U * np.sqrt(Cf / 2)
    return yplus * nu / ut, Re, Cf
for name, U, L, nu, yp in (("river reach, water", 1.0, 10.0, 1e-6, 30), ("car, air", 30.0, 4.0, 1.5e-5, 1), ("wind-tunnel model, air", 20.0, 0.5, 1.5e-5, 1)):
    y, Re, Cf = first_cell(U, L, nu, yp)
    print(f"{name}: Re_L = {Re:.2e}, Cf = {Cf:.5f}, first cell centre for y+ = {yp}: {y*1e3:.4f} mm")
y, *_ = first_cell(30.0, 4.0, 1.5e-5, 1)
assert 0.005e-3 < y < 0.02e-3
print(f"cells in the graded mesh: first cell height {(P[0,1,1]-P[0,0,1])*1e3:.1f} mm on a 1 m channel; growth ratio near the wall {((P[0,2,1]-P[0,1,1])/(P[0,1,1]-P[0,0,1])):.3f}")
