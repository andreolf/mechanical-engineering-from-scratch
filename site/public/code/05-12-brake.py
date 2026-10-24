"""A bicycle rim brake as a frame: two bodies (hand lever, brake arm) linked by the cable; solve each FBD."""
import math
import numpy as np


def solve_body(pivot, known, unknown_dirs):
    """Equilibrium of one body. pivot: point of the pin (2 unknowns); known: list of (point, F);
    unknown_dirs: list of (point, unit direction) for extra unknown force magnitudes. Returns [Rx, Ry, *magnitudes]."""
    cols = [((pivot), (1.0, 0.0)), ((pivot), (0.0, 1.0))] + list(unknown_dirs)
    A = np.array([[d[0] for _, d in cols], [d[1] for _, d in cols], [p[0] * d[1] - p[1] * d[0] for p, d in cols]])
    b = -np.array([sum(F[0] for _, F in known), sum(F[1] for _, F in known), sum(p[0] * F[1] - p[1] * F[0] for p, F in known)])
    return np.linalg.solve(A, b)


def unit(deg):
    return (math.cos(math.radians(deg)), math.sin(math.radians(deg)))


if __name__ == "__main__":
    F_hand = 60.0                      # newtons, one finger squeeze
    # hand lever: pivot at origin, finger force at 70 mm (perpendicular to the lever), cable anchor at 25 mm
    lever = solve_body((0, 0), [((0.070, 0), (0, -F_hand))], [((0.025, 0), (0, 1))])   # cable pulls along +y here
    T = lever[2]
    print(f"lever: pivot reaction ({lever[0]:.2f}, {lever[1]:.2f}) N, cable tension {T:.2f} N (ratio {T / F_hand:.3f} = 70/25)")
    assert abs(T / F_hand - 70 / 25) < 1e-12
    # brake arm: pivot at origin, cable pulls at 100 mm above the pivot horizontally, pad 40 mm above the pivot pushes back
    arm = solve_body((0, 0), [((0, 0.100), (-T, 0))], [((0, 0.040), (1, 0))])
    N = arm[2]
    print(f"brake arm: pivot reaction ({arm[0]:.2f}, {arm[1]:.2f}) N, pad force on the arm {N:.2f} N")
    assert abs(N / T - 100 / 40) < 1e-12
    print(f"overall mechanical advantage {N / F_hand:.2f} (= 70/25 x 100/40 = {70 / 25 * 100 / 40:.2f})")
    # braking force on the rim: two pads, rubber on aluminium mu ~ 0.6 (dry)
    mu = 0.6
    print(f"rim friction from two pads: {2 * mu * N:.1f} N")
    # a cable that pulls at 20 degrees off perpendicular loses a cos factor
    lever2 = solve_body((0, 0), [((0.070, 0), (0, -F_hand))], [((0.025, 0), unit(70))])
    print(f"cable at 20 deg off perpendicular: tension {lever2[2]:.2f} N (= {T:.2f} / cos 20)")
    assert abs(lever2[2] - T / math.cos(math.radians(20))) < 1e-9
