"""Castigliano's theorem on a ceiling bike hook: a straight shank plus a semicircular J."""
import math
import numpy as np


def hook_geometry(a, R, n_shank=2001, n_arc=4001):
    """Centreline from the ceiling (0, 0) down the shank to (0, -a), then round a semicircle of radius R.
    Returns points, arc length steps, and the index of the lowest point of the J (where the rim sits)."""
    ys = np.linspace(0, -a, n_shank)
    shank = np.column_stack([np.zeros_like(ys), ys])
    ph = np.linspace(0, np.pi, n_arc)[1:]
    arc = np.column_stack([R - R * np.cos(ph), -a - R * np.sin(ph)])
    pts = np.vstack([shank, arc])
    ds = np.r_[0, np.hypot(*np.diff(pts, axis=0).T)]
    i_low = n_shank - 1 + (n_arc - 1) // 2
    return pts, ds, i_low


def moment(pts, i_load, P, Q):
    """Bending moment (N mm) from a downward load P and a sideways load Q (+x) at point i_load."""
    xL, yL = pts[i_load]
    M = np.zeros(len(pts))
    r = pts[: i_load + 1]
    # moment about each section of the loads beyond it (only sections between the ceiling and the load are loaded)
    M[: i_load + 1] = -P * (xL - r[:, 0]) - Q * (yL - r[:, 1])
    return M


def energy(pts, ds, i_load, P, Q, EI):
    M = moment(pts, i_load, P, Q)
    f = M**2 / (2 * EI)
    return np.sum(0.5 * (f[1:] + f[:-1]) * ds[1:])


def direct_displacement(pts, ds, i_load, P, Q, EI):
    """Integrate curvature: each little segment rotates by M ds / EI, swinging the load point about it."""
    M = moment(pts, i_load, P, Q)
    k = 0.5 * (M[1:] + M[:-1]) / EI * ds[1:]          # rotation of each segment (counter-clockwise positive)
    mid = 0.5 * (pts[1:] + pts[:-1])
    rel = pts[i_load] - mid
    m = np.arange(len(k)) < i_load
    ux = np.sum(-k[m] * rel[m, 1]); uy = np.sum(k[m] * rel[m, 0])
    return ux, uy


if __name__ == "__main__":
    E, d, a, R = 210e3, 8.0, 100.0, 40.0
    EI = E * math.pi * d**4 / 64
    P = 15 * 9.81                                          # a 15 kg bike
    pts, ds, iL = hook_geometry(a, R)
    print(f"load point {pts[iL].round(3)} (bottom of the J), EI = {EI:.4e} N mm^2")
    # Castigliano: delta = dU/dP, sideways movement = dU/dQ at Q = 0 (a dummy load)
    h = 1e-3
    dv = (energy(pts, ds, iL, P + h, 0, EI) - energy(pts, ds, iL, P - h, 0, EI)) / (2 * h)
    dh = (energy(pts, ds, iL, P, h, EI) - energy(pts, ds, iL, P, -h, EI)) / (2 * h)
    hand_v = P * R**2 * a / EI + math.pi * P * R**3 / (4 * EI)
    hand_h = P * R * (a + R) ** 2 / (2 * EI)
    print(f"Castigliano: down {dv:.4f} mm (hand {hand_v:.4f}), sideways {dh:.4f} mm (hand {hand_h:.4f})")
    ux, uy = direct_displacement(pts, ds, iL, P, 0, EI)
    print(f"direct integration of curvature: ux = {ux:+.4f} mm, uy = {uy:+.4f} mm")
    assert abs(dv - hand_v) < 1e-3 * hand_v and abs(abs(dh) - hand_h) < 1e-3 * hand_h
    assert abs(-uy - dv) < 1e-3 * dv and abs(abs(ux) - abs(dh)) < 1e-3 * abs(dh)
    s = P * R * (d / 2) / (math.pi * d**4 / 64)
    print(f"bending stress in the shank {s:.1f} MPa; the load point swings back towards the shank {abs(ux)/abs(uy):.2f} times as far as it drops")
