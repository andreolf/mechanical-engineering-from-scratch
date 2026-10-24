"""Kirsch's solution: stresses round a circular hole in a wide plate under remote tension s (along x)."""
import math
import numpy as np


def kirsch_polar(s, a, r, th):
    """Return sigma_rr, sigma_tt, tau_rt at (r, theta), theta measured from the loading direction."""
    q = (a / r) ** 2
    srr = s / 2 * (1 - q) + s / 2 * (1 - 4 * q + 3 * q**2) * np.cos(2 * th)
    stt = s / 2 * (1 + q) - s / 2 * (1 + 3 * q**2) * np.cos(2 * th)
    trt = -s / 2 * (1 + 2 * q - 3 * q**2) * np.sin(2 * th)
    return srr, stt, trt


def kirsch_xy(s, a, x, y):
    r, th = np.hypot(x, y), np.arctan2(y, x)
    srr, stt, trt = kirsch_polar(s, a, r, th)
    c, sn = np.cos(th), np.sin(th)
    sxx = srr * c**2 + stt * sn**2 - 2 * trt * sn * c
    syy = srr * sn**2 + stt * c**2 + 2 * trt * sn * c
    txy = (srr - stt) * sn * c + trt * (c**2 - sn**2)
    return sxx, syy, txy


if __name__ == "__main__":
    s, a = 100.0, 5.0                                  # 100 MPa remote, 10 mm hole
    th = np.linspace(0, 2 * np.pi, 3601)
    _, stt, _ = kirsch_polar(s, a, a, th)
    i = int(np.argmax(stt))
    print(f"hoop stress on the hole edge: max {stt[i]:.2f} MPa at {math.degrees(th[i]):.1f} deg, min {stt.min():.2f} MPa at 0 deg")
    assert abs(stt.max() / s - 3) < 1e-9 and abs(stt.min() / s + 1) < 1e-9
    # the boundary is traction free
    srr, _, trt = kirsch_polar(s, a, a, th)
    assert np.allclose(srr, 0, atol=1e-9) and np.allclose(trt, 0, atol=1e-9)
    # decay along the line across the load through the hole centre (x = 0)
    for k in (1, 1.5, 2, 3, 5):
        sxx, _, _ = kirsch_xy(s, a, 0.0, k * a)
        print(f"  sigma_xx at y = {k:.1f} a: {sxx:.2f} MPa")
    sxx2, _, _ = kirsch_xy(s, a, 0.0, 2 * a)
    assert abs(sxx2 - s * (1 + 1 / 8 + 3 / 32)) < 1e-9
    # far away the plate doesn't notice the hole
    sxx, syy, txy = kirsch_xy(s, a, 400 * a, 300 * a)
    assert abs(sxx - s) < 0.01 and abs(syy) < 0.01 and abs(txy) < 0.01
    # map the field: grid of sigma_xx, its peak sits on the hole edge at 90 degrees
    X, Y = np.meshgrid(np.linspace(-20, 20, 401), np.linspace(-20, 20, 401))
    mask = np.hypot(X, Y) >= a
    Xs, Ys = np.where(mask, X, 2 * a), np.where(mask, Y, 0.0)     # dummy points inside the hole, masked out below
    F = np.where(mask, kirsch_xy(s, a, Xs, Ys)[0], np.nan)
    j = np.nanargmax(F)
    print(f"field peak {np.nanmax(F):.2f} MPa at ({X.flat[j]:.1f}, {Y.flat[j]:.1f}) mm")
    # an elliptical hole: Kt = 1 + 2 a/b (semi-axis a across the load)
    for ab in (1, 2, 5, 20):
        print(f"  ellipse a/b = {ab:2d}: Kt = {1 + 2 * ab}")
