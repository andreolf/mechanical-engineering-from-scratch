"""Planar rigid-body kinematics: v_B = v_A + omega x r_AB, and the instantaneous centre of zero velocity."""
import math
import numpy as np


def cross_z(w, r):
    """omega (about z) x r for a planar vector r."""
    return np.array([-w * r[1], w * r[0]])


def velocity(vA, w, A, P):
    return vA + cross_z(w, np.asarray(P) - np.asarray(A))


def instant_centre(vA, w, A):
    """Point with zero velocity: I = A + (k x vA) / w."""
    return np.asarray(A) + np.array([-vA[1], vA[0]]) / w


def slider_crank(r, l, theta, w_crank):
    """Crank OA (radius r) turning at w_crank, rod AB (length l), piston B sliding on the x axis."""
    A = r * np.array([math.cos(theta), math.sin(theta)])
    B = np.array([A[0] + math.sqrt(l**2 - A[1] ** 2), 0.0])
    vA = cross_z(w_crank, A)
    rAB = B - A
    w_rod = -vA[1] / rAB[0]                    # B moves horizontally, so its y-velocity is zero
    vB = velocity(vA, w_rod, A, B)
    return A, B, vA, w_rod, vB


if __name__ == "__main__":
    # a bicycle wheel rolling without slip: r = 0.35 m at 8 m/s; the contact point is the instantaneous centre
    R, V = 0.35, 8.0
    w = -V / R                                   # clockwise when rolling to the right
    C = np.array([0.0, R])
    for name, P in (("contact", (0, 0)), ("top", (0, 2 * R)), ("front", (R, R))):
        print(f"wheel {name:7s}: v = {np.round(velocity(np.array([V, 0]), w, C, P), 4)} m/s")
    assert np.allclose(velocity(np.array([V, 0]), w, C, (0, 0)), 0) and np.allclose(instant_centre(np.array([V, 0.0]), w, C), (0, 0))
    # slider-crank of a small engine: r = 50 mm, l = 200 mm, 100 rad/s, crank at 60 deg
    A, B, vA, w_rod, vB = slider_crank(0.05, 0.2, math.radians(60), 100.0)
    I = instant_centre(vA, w_rod, A)
    print(f"crank pin A = {np.round(A, 5)}, piston B = {np.round(B, 5)} m")
    print(f"rod angular velocity {w_rod:.4f} rad/s, piston velocity {vB[0]:.4f} m/s")
    print(f"rod instantaneous centre I = {np.round(I, 5)} m")
    assert np.allclose(velocity(vA, w_rod, A, I), 0, atol=1e-12)          # the instantaneous centre has zero velocity
    assert abs(abs(vB[0]) - abs(w_rod) * np.linalg.norm(B - I)) < 1e-12    # |v| = |omega| * distance from I
    # cross-check the piston speed by differentiating the position numerically
    h = 1e-7
    xB = lambda th: slider_crank(0.05, 0.2, th, 100.0)[1][0]
    assert abs((xB(math.radians(60) + h) - xB(math.radians(60) - h)) / (2 * h) * 100.0 - vB[0]) < 1e-5
