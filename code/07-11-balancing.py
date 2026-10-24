"""Two-plane balancing of a rotor: correction masses that cancel both the net force and the net moment."""
import math
import numpy as np


def unbalance(masses):
    """masses: list of (m kg, r m, angle rad, z m). Returns the force vector per omega^2 (kg m) and moment per omega^2 (kg m^2) about z = 0."""
    F = np.zeros(2); M = np.zeros(2)
    for m, r, a, z in masses:
        u = m * r * np.array([math.cos(a), math.sin(a)])
        F += u; M += u * z
    return F, M


def two_plane_correction(masses, zL, zR, rc):
    """Find correction masses at radius rc in planes zL and zR so the total force and moment vanish."""
    F, M = unbalance(masses)
    # unknown vectors uL, uR (m r in each plane): uL + uR = -F,  uL zL + uR zR = -M
    uR = (-M + F * zL) / (zR - zL)
    uL = -F - uR
    out = []
    for u, z in ((uL, zL), (uR, zR)):
        out.append((np.linalg.norm(u) / rc, rc, math.atan2(u[1], u[0]), z))
    return out


if __name__ == "__main__":
    # a 0.6 m long fan rotor with three small unbalances (kg, m, angle, axial position)
    rotor = [(0.020, 0.10, math.radians(30), 0.10), (0.015, 0.12, math.radians(160), 0.30), (0.010, 0.08, math.radians(270), 0.50)]
    F, M = unbalance(rotor)
    w = 3000 * 2 * math.pi / 60
    print(f"unbalance: m r = {np.linalg.norm(F)*1e3:.3f} g m, moment m r z = {np.linalg.norm(M)*1e3:.3f} g m^2; at 3000 rpm the bearings feel up to {np.linalg.norm(F)*w**2:.1f} N")
    # static balance only: one mass in the middle plane cancels the force but leaves a moment
    zc = 0.3
    Fs = -F
    static = rotor + [(np.linalg.norm(Fs) / 0.1, 0.1, math.atan2(Fs[1], Fs[0]), zc)]
    F1, M1 = unbalance(static)
    print(f"static balance only: residual force {np.linalg.norm(F1):.1e}, residual moment {np.linalg.norm(M1)*1e3:.3f} g m^2 (dynamic unbalance remains)")
    corr = two_plane_correction(rotor, 0.0, 0.6, 0.1)
    for m, r, a, z in corr:
        print(f"  correction at z = {z:.1f} m: {m*1e3:.2f} g at r = {r} m, angle {math.degrees(a):.1f} deg")
    F2, M2 = unbalance(rotor + corr)
    print(f"after two-plane balancing: force {np.linalg.norm(F2):.1e} kg m, moment {np.linalg.norm(M2):.1e} kg m^2")
    assert np.linalg.norm(F2) < 1e-15 and np.linalg.norm(M2) < 1e-15
