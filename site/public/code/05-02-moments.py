"""Moments M = r x F about any point, and the couple: same moment about every point."""
import math
import numpy as np


def moment(F, at, about=(0.0, 0.0, 0.0)):
    r = np.array(at, float) - np.array(about, float)
    return np.cross(r, np.array(F, float))


def moment_2d(F, at, about=(0.0, 0.0)):
    """Scalar z-moment, counter-clockwise positive: M = rx Fy - ry Fx."""
    rx, ry = at[0] - about[0], at[1] - about[1]
    return rx * F[1] - ry * F[0]


if __name__ == "__main__":
    # a spanner: 120 N pushed at 70 deg to a 250 mm handle
    L, P, ang = 0.25, 120.0, math.radians(70)
    F = (P * math.cos(ang), P * math.sin(ang))
    M = moment_2d(F, (L, 0.0))
    print(f"spanner moment {M:.3f} N m (= P L sin 70 = {P * L * math.sin(ang):.3f}); lever arm {M / P * 1e3:.1f} mm")
    assert abs(M - P * L * math.sin(ang)) < 1e-12
    # Varignon: moment of the resultant equals the sum of the moments of the components
    assert abs(moment_2d((F[0], 0), (L, 0)) + moment_2d((0, F[1]), (L, 0)) - M) < 1e-12
    # a couple: +F at A and -F at B; its moment is the same about every point
    Fc, A, B = np.array([0.0, 50.0, 0.0]), np.array([0.2, 0.0, 0.0]), np.array([-0.2, 0.0, 0.0])
    rng = np.random.default_rng(3)
    Ms = [moment(Fc, A, p) + moment(-Fc, B, p) for p in rng.uniform(-5, 5, (20, 3))]
    print(f"couple moment {Ms[0]} N m about 20 random points: spread {np.ptp(np.array(Ms), axis=0).max():.1e}")
    assert all(np.allclose(m, Ms[0]) for m in Ms) and abs(Ms[0][2] - 50 * 0.4) < 1e-12
    # 3D: a 200 N pull on a valve wheel rim, moment about the stem axis
    Fv, at = np.array([0.0, 200.0, -50.0]), np.array([0.15, 0.0, 0.3])
    Mo = moment(Fv, at)
    axis = np.array([0.0, 0.0, 1.0])
    print(f"valve: moment about the origin {np.round(Mo, 3)} N m; about the stem (z) axis {Mo @ axis:.3f} N m")
    assert abs(Mo @ axis - 0.15 * 200) < 1e-12
