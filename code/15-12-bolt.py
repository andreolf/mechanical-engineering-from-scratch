"""Bolted joint: bolt and member stiffness, the joint diagram, how an external load is shared, and the separation load. The load share is checked by simulating the bolt and members as two springs."""
import math
import numpy as np


def bolt_stiffness(d, At, ld, lt, E):
    """Unthreaded shank length ld and threaded length lt inside the grip act as springs in series."""
    Ad = math.pi * d**2 / 4
    return Ad * At * E / (Ad * lt + At * ld)


def member_stiffness(d, l, E):
    """Shigley's frustum (30 degree cone) result for two equal steel members, washer face 1.5 d, total grip l."""
    return 0.5774 * math.pi * E * d / (2 * math.log(5 * (0.5774 * l + 0.5 * d) / (0.5774 * l + 2.5 * d)))


def joint_forces(Fi, kb, km, P):
    """Simulate the joint as two springs held at the same extension: find the extension that balances P."""
    # after preload, bolt force = Fi + kb x, member force = Fi - km x (while compressed); equilibrium: Fb - Fm = P
    def residual(x):
        Fb = Fi + kb * x
        Fm = max(Fi - km * x, 0.0)     # members cannot pull: once separated they carry nothing
        return Fb - Fm - P
    lo, hi = 0.0, 10 * (P + Fi) / kb + 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if residual(mid) > 0:
            hi = mid
        else:
            lo = mid
    x = 0.5 * (lo + hi)
    return Fi + kb * x, max(Fi - km * x, 0.0)


if __name__ == "__main__":
    # M10 x 1.5 property class 8.8 through two 15 mm steel plates, 40 mm long bolt
    d, At, Sp, E = 10.0, 58.0, 600.0, 207e3
    l, L = 30.0, 40.0
    LT = 2 * d + 6                  # threaded length of a short bolt
    ld = L - LT; lt = l - ld
    kb = bolt_stiffness(d, At, ld, lt, E)
    km = member_stiffness(d, l, E)
    C = kb / (kb + km)
    Fi = 0.75 * At * Sp             # preload 75% of proof load for a reusable joint
    print(f"kb = {kb/1000:.1f} kN/mm, km = {km/1000:.1f} kN/mm, joint constant C = {C:.4f}")
    print(f"preload {Fi/1000:.2f} kN, tightening torque about {0.2*Fi*d/1000:.1f} N m (K = 0.2)")
    for P in (5000.0, 15000.0, 30000.0, 40000.0):
        Fb, Fm = joint_forces(Fi, kb, km, P)
        if P < Fi / (1 - C):
            assert abs((Fb - Fi) - C * P) < 1e-6 * P  # the bolt sees only the fraction C of the external load
        else:
            assert Fm == 0 and abs(Fb - P) < 1e-6 * P  # separated: the bolt carries everything
        print(f"P = {P/1000:5.1f} kN: bolt {Fb/1000:.3f} kN, members {Fm/1000:.3f} kN")
    P0 = Fi / (1 - C)
    print(f"separation load {P0/1000:.2f} kN; bolt stress at P = 15 kN: {joint_forces(Fi, kb, km, 15000)[0]/At:.1f} MPa (proof 600)")
