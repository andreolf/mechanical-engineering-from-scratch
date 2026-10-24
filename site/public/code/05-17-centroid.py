"""Centroids: composite shapes (add and subtract parts), the polygon (shoelace) formula, and Pappus-Guldinus."""
import math
import numpy as np


def composite(parts):
    """parts: (area, xc, yc); holes have negative area. Returns (A, x_bar, y_bar)."""
    A = sum(a for a, _, _ in parts)
    return A, sum(a * x for a, x, _ in parts) / A, sum(a * y for a, _, y in parts) / A


def polygon_centroid(pts):
    """Shoelace formula for a simple polygon with vertices in order."""
    p = np.asarray(pts, float); x, y = p[:, 0], p[:, 1]; xn, yn = np.roll(x, -1), np.roll(y, -1)
    cr = x * yn - xn * y
    A = cr.sum() / 2
    return A, ((x + xn) * cr).sum() / (6 * A), ((y + yn) * cr).sum() / (6 * A)


if __name__ == "__main__":
    # T-section of a footbridge beam (mm): flange 200 x 30 on top of a 30 x 170 web
    A, xb, yb = composite([(200 * 30, 0, 170 + 15), (30 * 170, 0, 85)])
    Ap, xp, yp = polygon_centroid([(-15, 0), (15, 0), (15, 170), (100, 170), (100, 200), (-100, 200), (-100, 170), (-15, 170)])
    print(f"T-section: A = {A:.0f} mm^2, centroid {yb:.4f} mm above the bottom (polygon: {yp:.4f})")
    assert abs(A - Ap) < 1e-9 and abs(yb - yp) < 1e-9 and abs(xp) < 1e-12
    # L-bracket: a 100 x 10 base and a 10 x 70 upright
    A, xb, yb = composite([(100 * 10, 50, 5), (10 * 70, 5, 45)])
    Ap, xp, yp = polygon_centroid([(0, 0), (100, 0), (100, 10), (10, 10), (10, 80), (0, 80)])
    print(f"L-bracket: centroid ({xb:.4f}, {yb:.4f}) mm (polygon: ({xp:.4f}, {yp:.4f}))")
    assert np.allclose([xb, yb], [xp, yp])
    # a plate with a circular hole: subtract the hole as negative area
    A, xb, yb = composite([(300 * 200, 150, 100), (-math.pi * 40**2, 220, 100)])
    print(f"plate 300 x 200 with an 80 mm hole at x = 220: centroid x = {xb:.4f} mm (shifts away from the hole)")
    assert xb < 150
    # Pappus-Guldinus: volume = 2 pi x_bar A. A bike-tyre-like torus: tube radius 0.02 m at radius 0.33 m
    r, R = 0.02, 0.33
    V = 2 * math.pi * R * math.pi * r**2
    print(f"torus volume by Pappus: {V * 1e6:.3f} cm^3")
    # check Pappus on a cone (right triangle of base r, height h revolved about the h side): V = pi r^2 h / 3
    rc, hc = 0.5, 1.2
    Vc = 2 * math.pi * (rc / 3) * (rc * hc / 2)
    assert abs(Vc - math.pi * rc**2 * hc / 3) < 1e-12
    print(f"cone by Pappus {Vc:.6f} = pi r^2 h / 3 = {math.pi * rc**2 * hc / 3:.6f} m^3")
