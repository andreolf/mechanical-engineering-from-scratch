"""Buoyancy and stability: draft and metacentric height of a box barge, and the righting arm found by integrating the heeled underwater section."""
import numpy as np

RHO = 1025.0       # seawater


def draft(mass, L, B):
    return mass / (RHO * L * B)


def gm(B, T, KG):
    """Metacentric height of a box hull: KB + BM - KG, with BM = I/V = B^2/(12 T)."""
    return T / 2 + B * B / (12 * T) - KG


def polygon_centroid(P):
    if len(P) < 3:
        return 0.0, 0.0, 0.0
    x, y = P[:, 0], P[:, 1]
    xn, yn = np.roll(x, -1), np.roll(y, -1)
    c = x * yn - xn * y
    A = c.sum() / 2
    return A, (x + xn) @ c / (6 * A), (y + yn) @ c / (6 * A)


def clip_below(P, a, b):
    """Part of polygon P below the line y = a x + b (Sutherland-Hodgman against one edge)."""
    out = []
    for i in range(len(P)):
        p, q = P[i], P[(i + 1) % len(P)]
        fp, fq = p[1] - a * p[0] - b, q[1] - a * q[0] - b
        if fp <= 0: out.append(p)
        if fp * fq < 0:
            t = fp / (fp - fq); out.append(p + t * (q - p))
    return np.array(out)


def righting_arm(B, D, T, KG, theta):
    """GZ (m) at heel theta: tilt the waterline about the centreline, adjust its height to keep the displaced area, and
    measure the horizontal distance between the centre of buoyancy and G."""
    hull = np.array([[-B / 2, 0], [B / 2, 0], [B / 2, D], [-B / 2, D]], float)
    a = np.tan(theta); target = B * T
    lo, hi = -D, 2 * D
    for _ in range(80):
        b = (lo + hi) / 2
        A = polygon_centroid(clip_below(hull, a, b))[0]
        lo, hi = (b, hi) if A < target else (lo, b)
    _, xb, yb = polygon_centroid(clip_below(hull, a, b))
    # rotate into the ship's heeled frame: GZ is the horizontal lever between B and G
    c, s = np.cos(theta), np.sin(theta)
    return (xb - 0) * c + (yb - KG) * s


if __name__ == "__main__":
    # a 20 m x 6 m x 2.5 m barge displacing 150 t, centre of gravity 1.8 m above the keel
    L, B, D, m, KG = 20.0, 6.0, 2.5, 150e3, 1.8
    T = draft(m, L, B)
    print(f"draft {T:.4f} m, KB {T/2:.4f} m, BM {B*B/(12*T):.4f} m, GM {gm(B, T, KG):.4f} m")
    for deg in (1, 5, 10):
        th = np.radians(deg)
        print(f"  heel {deg:2d} deg: GZ {righting_arm(B, D, T, KG, th):.4f} m (GM sin theta {gm(B, T, KG)*np.sin(th):.4f})")
    for deg in (5, 10, 15):                                                             # wall-sided formula for a box
        th = np.radians(deg); bm = B * B / (12 * T)
        assert abs(righting_arm(B, D, T, KG, th) - np.sin(th) * (gm(B, T, KG) + bm / 2 * np.tan(th) ** 2)) < 1e-6
    th = np.radians(0.5)
    assert abs(righting_arm(B, D, T, KG, th) / np.sin(th) - gm(B, T, KG)) < 2e-3        # small angles: GZ = GM sin theta
    for kg in (1.0, 2.0, 3.0, 4.0):                                                     # stable iff GM > 0
        g, z = gm(B, T, kg), righting_arm(B, D, T, kg, np.radians(2))
        assert (g > 0) == (z > 0)
        print(f"  KG {kg} m: GM {g:+.3f} m, {'stable' if g > 0 else 'capsizes'}")
    # a coconut: a husked nut of mass 1.2 kg and volume 1.9 L floats with this fraction submerged in fresh water
    print(f"coconut submerged fraction: {1.2/(1000*1.9e-3):.3f}")
