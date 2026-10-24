"""Surface finish in turning: build the feed-mark profile left by a round tool nose and compute Ra and Rt, compared with f^2/(32 r) and f^2/(8 r)."""
import math
import numpy as np


def profile(f, r, n_marks=10, pts=20000):
    """Height of the turned surface: overlapping arcs of radius r every f along the axis (mm)."""
    x = np.linspace(0, n_marks * f, n_marks * pts, endpoint=False)
    xc = (np.floor(x / f) + 0.5) * f                       # nearest arc centre
    z = r - np.sqrt(r * r - (x - xc) ** 2)                 # height above the arc bottom
    return x, z


def Ra_Rt(z):
    m = z.mean()
    return float(np.mean(np.abs(z - m))), float(z.max() - z.min())


def scallop(step, R):
    """Cusp height between ball-nose passes of radius R spaced step apart."""
    return R - math.sqrt(R * R - (step / 2) ** 2)


if __name__ == "__main__":
    r = 0.8   # mm tool nose radius
    for f in (0.05, 0.1, 0.2, 0.3):
        x, z = profile(f, r)
        Ra, Rt = Ra_Rt(z)
        print(f"feed {f} mm/rev: Ra {Ra*1000:.3f} um (formula {f*f/(32*r)*1000:.3f}), Rt {Rt*1000:.3f} um (formula {f*f/(8*r)*1000:.3f})")
        assert abs(Rt - f * f / (8 * r)) / Rt < 0.02
        assert abs(Ra - f * f / (32 * r)) / Ra < 0.05
    f_needed = math.sqrt(1.6e-3 * 32 * r)
    print(f"largest feed for Ra 1.6 um with r = 0.8 mm: {f_needed:.3f} mm/rev")
    print(f"ball-nose 6 mm, 0.5 mm stepover: scallop {scallop(0.5, 3.0)*1000:.2f} um")
    assert abs(scallop(0.5, 3.0) - 0.5**2 / (8 * 3.0)) < 1e-4
