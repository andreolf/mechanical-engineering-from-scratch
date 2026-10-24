"""Second moments of area: composite sections with the parallel-axis theorem, checked by a polygon formula."""
import math
import numpy as np


def rects(parts):
    """parts: (b, h, yc) rectangles centred on the y axis. Returns A, centroid y, I about the centroidal x axis."""
    A = sum(b * h for b, h, _ in parts)
    yb = sum(b * h * yc for b, h, yc in parts) / A
    I = sum(b * h**3 / 12 + b * h * (yc - yb) ** 2 for b, h, yc in parts)     # parallel-axis theorem
    return A, yb, I


def polygon_props(pts):
    """Area, centroid y and I about the centroidal x axis of a simple polygon (Green's theorem)."""
    p = np.asarray(pts, float); x, y = p[:, 0], p[:, 1]; xn, yn = np.roll(x, -1), np.roll(y, -1)
    cr = x * yn - xn * y
    A = cr.sum() / 2; yb = ((y + yn) * cr).sum() / (6 * A)
    Ix0 = ((y**2 + y * yn + yn**2) * cr).sum() / 12
    return A, yb, Ix0 - A * yb**2


def tube(D, d):
    return math.pi * (D**2 - d**2) / 4, math.pi * (D**4 - d**4) / 64


if __name__ == "__main__":
    # I-section like an IPE 200 without root fillets: h 200, b 100, flanges 8.5, web 5.6
    h, b, tf, tw = 200.0, 100.0, 8.5, 5.6
    A, yb, I = rects([(b, tf, h - tf / 2), (tw, h - 2 * tf, h / 2), (b, tf, tf / 2)])
    pts = [(-b / 2, 0), (b / 2, 0), (b / 2, tf), (tw / 2, tf), (tw / 2, h - tf), (b / 2, h - tf), (b / 2, h), (-b / 2, h),
           (-b / 2, h - tf), (-tw / 2, h - tf), (-tw / 2, tf), (-b / 2, tf)]
    Ap, ybp, Ip = polygon_props(pts)
    print(f"I-section: A = {A:.1f} mm^2, I = {I:.4e} mm^4 (polygon {Ip:.4e})")
    assert abs(A - Ap) < 1e-9 and abs(I - Ip) < 1e-6 * I
    # T-section from lesson 05.17: flange 200 x 30 over a 30 x 170 web
    At, ybt, It = rects([(200, 30, 185), (30, 170, 85)])
    print(f"T-section: centroid {ybt:.4f} mm, I = {It:.4e} mm^4")
    # equal area comparison: square, round bar, tube, I-section
    s = math.sqrt(A); Isq = s**4 / 12
    Dr = math.sqrt(4 * A / math.pi); Ir = math.pi * Dr**4 / 64
    # a tube of the same area with 100 mm outside diameter
    d_in = math.sqrt(100**2 - 4 * A / math.pi); At_, It_ = tube(100, d_in)
    for name, val in (("square", Isq), ("round bar", Ir), (f"tube 100 x {(100 - d_in) / 2:.2f}", It_), ("I-section", I)):
        print(f"  same area {A:.0f} mm^2, {name:16s}: I = {val:.4e} mm^4 ({val / Isq:5.1f} x the square)")
    assert I > It_ > Ir and I > 20 * Isq and abs(At_ - A) < 1e-9
