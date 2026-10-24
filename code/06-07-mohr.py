"""2D stress transformation and Mohr's circle; principal stresses equal the eigenvalues of sigma."""
import math
import numpy as np


def rotate(sx, sy, txy, theta):
    """Stresses on an element rotated by theta (counter-clockwise)."""
    c, s = math.cos(2 * theta), math.sin(2 * theta)
    m, d = (sx + sy) / 2, (sx - sy) / 2
    return m + d * c + txy * s, m - d * c - txy * s, -d * s + txy * c


def mohr(sx, sy, txy):
    """Centre, radius, principal stresses and the angle of the first principal direction."""
    C = (sx + sy) / 2; R = math.hypot((sx - sy) / 2, txy)
    return C, R, C + R, C - R, 0.5 * math.atan2(2 * txy, sx - sy)


if __name__ == "__main__":
    sx, sy, txy = 80.0, -20.0, 30.0
    C, R, s1, s2, tp = mohr(sx, sy, txy)
    print(f"Mohr's circle: centre {C:.1f} MPa, radius {R:.4f} MPa -> sigma1 {s1:.4f}, sigma2 {s2:.4f} MPa, at {math.degrees(tp):.4f} deg; max in-plane shear {R:.4f} MPa")
    ev = np.linalg.eigvalsh(np.array([[sx, txy], [txy, sy]]))
    assert np.allclose(sorted([s1, s2]), ev)
    # rotating the element to the principal angle kills the shear stress
    a, b, t = rotate(sx, sy, txy, tp)
    assert abs(t) < 1e-12 and abs(a - s1) < 1e-12
    # every rotated state lies on the circle, and the sum sx + sy is invariant
    for deg in range(0, 180, 15):
        a, b, t = rotate(sx, sy, txy, math.radians(deg))
        assert abs(math.hypot(a - C, t) - R) < 1e-12 and abs(a + b - (sx + sy)) < 1e-12
    print("all rotated states lie on the circle; sigma_x + sigma_y is invariant")
    # the bike tube from 06.01: 60 MPa axial, 25 MPa shear
    C, R, s1, s2, tp = mohr(60, 0, 25)
    print(f"bike tube: sigma1 {s1:.4f}, sigma2 {s2:.4f} MPa at {math.degrees(tp):.4f} deg")
    # pure shear: principal stresses +tau and -tau at 45 deg
    C, R, s1, s2, tp = mohr(0, 0, 50)
    assert abs(s1 - 50) < 1e-12 and abs(s2 + 50) < 1e-12 and abs(math.degrees(tp) - 45) < 1e-12
