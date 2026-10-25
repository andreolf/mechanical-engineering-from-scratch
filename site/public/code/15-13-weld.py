"""Fillet weld group under eccentric load: welds treated as lines, direct and torsional shear on the throat, checked by summing small weld elements."""
import math
import numpy as np


def weld_elements(segments, n=4000):
    """segments: list of ((x0, y0), (x1, y1)) weld lines. Returns element midpoints and lengths."""
    pts, lens = [], []
    for (x0, y0), (x1, y1) in segments:
        t = (np.arange(n) + 0.5) / n
        pts.append(np.column_stack([x0 + (x1 - x0) * t, y0 + (y1 - y0) * t]))
        lens.append(np.full(n, math.hypot(x1 - x0, y1 - y0) / n))
    return np.vstack(pts), np.concatenate(lens)


def weld_group_stress(segments, h, F, load_point):
    """Vertical downward load F at load_point. Returns the max shear stress on the throat and where it occurs."""
    P, dl = weld_elements(segments)
    t = 0.707 * h
    A = t * dl.sum()
    c = (P * dl[:, None]).sum(0) / dl.sum()                       # weld group centroid
    r = P - c
    J = t * (dl * (r**2).sum(1)).sum()                             # polar moment of the throat area
    M = F * (load_point[0] - c[0])                                 # moment of the downward force about the centroid
    direct = np.array([0.0, -F / A])
    # torsional shear is perpendicular to r, magnitude M r / J; clockwise for a load to the right
    tors = (M / J) * np.column_stack([r[:, 1], -r[:, 0]])
    tau = np.linalg.norm(direct + tors, axis=1)
    k = int(np.argmax(tau))
    return tau[k], P[k], A, J, c


if __name__ == "__main__":
    # trailer hitch bracket: two horizontal 50 mm fillet welds, 80 mm apart, load 10 kN at 150 mm from the weld centroid
    b, d, F = 50.0, 80.0, 10000.0
    segs = [((0, d / 2), (b, d / 2)), ((0, -d / 2), (b, -d / 2))]
    load = (b / 2 + 150.0, 0.0)
    for h in (4.0, 6.0, 8.0):
        tau, where, A, J, c = weld_group_stress(segs, h, F, load)
        # textbook line formulas: A = 0.707 h (2b), Ju = b (3 d^2 + b^2)/6, J = 0.707 h Ju
        t = 0.707 * h
        Ju = b * (3 * d**2 + b**2) / 6
        rmax = math.hypot(b / 2, d / 2)
        M = F * 150.0
        tx = M * (d / 2) / (t * Ju)                      # horizontal component at the far corner
        ty = F / (t * 2 * b) + M * (b / 2) / (t * Ju)    # vertical: direct plus torsion
        hand = math.hypot(tx, ty)
        print(f"h = {h} mm: throat {t:.3f} mm, J = {J:.0f} mm^4 (line formula {t*Ju:.0f}), max shear {tau:.1f} MPa at ({where[0]:.1f}, {where[1]:.1f}); hand {hand:.1f} MPa")
        assert abs(J / (t * Ju) - 1) < 1e-6 and abs(tau / hand - 1) < 1e-3
        if h == 4.0:
            tau4 = tau
        else:
            assert abs(tau * h - tau4 * 4.0) < 1e-3 * tau4 * 4  # stress is inversely proportional to the throat
    # size for an allowable shear of 145 MPa (0.3 x 482 MPa, E70 electrode)
    h_req = 4.0 * tau4 / 145.0
    print(f"required leg size for 145 MPa: {h_req:.2f} mm -> next standard size up")
