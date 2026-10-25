"""Involute gear geometry: the tooth profile, contact found numerically on two rotating involutes, a constant velocity ratio along the line of action, and the contact ratio."""
import math
import numpy as np


def inv(phi):
    return math.tan(phi) - phi


def involute_point(rb, t, rot=0.0):
    """Point on the involute of a base circle rb at roll angle t, rotated by rot."""
    x = rb * (math.cos(t) + t * math.sin(t))
    y = rb * (math.sin(t) - t * math.cos(t))
    c, s = math.cos(rot), math.sin(rot)
    return np.array([c * x - s * y, s * x + c * y])


def involute_normal(t, rot=0.0):
    """Unit normal of the involute at roll angle t (it is tangent to the base circle)."""
    a = t + rot
    return np.array([math.sin(a), -math.cos(a)])


def gear_data(m, z, phi):
    r = m * z / 2
    return {"r": r, "rb": r * math.cos(phi), "ra": r + m, "rf": r - 1.25 * m}


def contact_ratio(m, z1, z2, phi):
    g1, g2 = gear_data(m, z1, phi), gear_data(m, z2, phi)
    a = g1["r"] + g2["r"]
    path = math.sqrt(g1["ra"]**2 - g1["rb"]**2) + math.sqrt(g2["ra"]**2 - g2["rb"]**2) - a * math.sin(phi)
    return path / (math.pi * m * math.cos(phi)), path


def bisect(f, lo, hi, n=200):
    flo = f(lo)
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        if (f(mid) > 0) == (flo > 0):
            lo, flo = mid, f(mid)
        else:
            hi = mid
    return 0.5 * (lo + hi)


if __name__ == "__main__":
    m, z1, z2, phi = 2.0, 18, 45, math.radians(20)
    g1, g2 = gear_data(m, z1, phi), gear_data(m, z2, phi)
    a = g1["r"] + g2["r"]
    print(f"pitch radii {g1['r']} and {g2['r']} mm, base radii {g1['rb']:.4f} and {g2['rb']:.4f} mm, centre distance {a} mm")
    # gear 1 at the origin, gear 2 at (a, 0). The line of action touches base circle 1 at T1 and passes the pitch point.
    T1 = g1["rb"] * np.array([math.cos(phi), math.sin(phi)])
    d = np.array([math.sin(phi), -math.cos(phi)])
    O2 = np.array([a, 0.0])
    T2 = O2 - g2["rb"] * np.array([math.cos(phi), math.sin(phi)])
    ratios, prev = [], None
    for th1 in np.linspace(-0.15, 0.15, 31):
        rot1 = phi - math.tan(phi) + th1          # at th1 = 0 the flank touches at the pitch point
        # contact = the point of flank 1 lying on the line of action, found by bisection on the roll angle
        f = lambda t: (lambda q: d[0] * q[1] - d[1] * q[0])(involute_point(g1["rb"], t, rot1) - T1)
        t = bisect(f, 1e-9, 1.2)
        P = involute_point(g1["rb"], t, rot1)
        assert abs(abs(involute_normal(t, rot1) @ d) - 1) < 1e-9   # flank normal lies along the line of action
        # gear 2: its flank (an involute of base circle 2) must pass through P; that fixes its rotation beta
        q = P - O2
        t2 = math.sqrt(max((q @ q) / g2["rb"] ** 2 - 1, 0.0))
        beta = math.atan2(q[1], q[0]) - math.atan2(math.sin(t2) - t2 * math.cos(t2), math.cos(t2) + t2 * math.sin(t2))
        B2 = O2 + g2["rb"] * np.array([math.cos(beta + t2), math.sin(beta + t2)])
        assert np.linalg.norm(B2 - T2) < 1e-6                       # gear 2's flank normal also runs along the line of action
        if prev is not None:
            d_beta = (beta - prev[1] + math.pi) % (2 * math.pi) - math.pi
            ratios.append(-d_beta / (th1 - prev[0]))
        prev = (th1, beta)
    ratios = np.array(ratios)
    print(f"velocity ratio along the mesh: min {ratios.min():.9f}, max {ratios.max():.9f}, expected z1/z2 = {z1/z2:.9f}")
    assert np.all(np.abs(ratios - z1 / z2) < 1e-6)
    cr, path = contact_ratio(m, z1, z2, phi)
    print(f"length of action {path:.4f} mm, base pitch {math.pi*m*math.cos(phi):.4f} mm, contact ratio {cr:.4f}")
    assert 1.2 < cr < 2
    # tooth thickness at the tip from the involute function
    phia = math.acos(g1["rb"] / g1["ra"])
    s_tip = 2 * g1["ra"] * (math.pi / (2 * z1) + inv(phi) - inv(phia))
    print(f"pinion tip thickness {s_tip:.4f} mm (should exceed about 0.25 m = {0.25*m} mm)")
    assert s_tip > 0.25 * m
