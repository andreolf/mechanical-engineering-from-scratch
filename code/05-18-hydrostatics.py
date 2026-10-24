"""Hydrostatic force on a plane gate and its centre of pressure: closed form against direct integration."""
import math
import numpy as np

RHO, G = 1000.0, 9.81


def gate_force(b, s1, s2, alpha_deg=90.0):
    """Rectangular gate of width b, from slant distance s1 to s2 below the surface along a plane
    inclined at alpha to the horizontal. Returns (F in N, slant position of the centre of pressure)."""
    sa = math.sin(math.radians(alpha_deg))
    L = s2 - s1; A = b * L; sc = (s1 + s2) / 2
    F = RHO * G * (sc * sa) * A                              # pressure at the centroid times the area
    I = b * L**3 / 12
    return F, sc + I / (sc * A)                              # the centre of pressure lies below the centroid


def gate_force_numeric(b, s1, s2, alpha_deg=90.0, n=20001):
    sa = math.sin(math.radians(alpha_deg)); s = np.linspace(s1, s2, n); p = RHO * G * s * sa
    w = np.ones(n); w[1:-1:2] = 4; w[2:-1:2] = 2; w *= (s2 - s1) / (n - 1) / 3
    F = b * (w @ p); return F, b * (w @ (p * s)) / F


if __name__ == "__main__":
    # vertical gate from the surface to depth h: F = rho g b h^2 / 2 acting at 2h/3
    b, h = 3.0, 4.0
    F, scp = gate_force(b, 0, h)
    print(f"surface gate {b} m wide, {h} m deep: F = {F / 1e3:.2f} kN at depth {scp:.4f} m (2h/3 = {2 * h / 3:.4f})")
    assert abs(scp - 2 * h / 3) < 1e-12 and abs(F - RHO * G * b * h**2 / 2) < 1e-6
    # bottom outlet gate of an alpine dam: 2 m wide, 3 m tall, top edge 48.5 m below the surface
    F, scp = gate_force(2.0, 48.5, 51.5)
    Fn, sn = gate_force_numeric(2.0, 48.5, 51.5)
    print(f"outlet gate: F = {F / 1e6:.4f} MN, centre of pressure {scp:.4f} m deep (centroid 50 m): numeric {Fn / 1e6:.4f} MN at {sn:.4f} m")
    assert abs(F - Fn) < 1e-6 * F and abs(scp - sn) < 1e-9
    # inclined gate at 60 deg, slant 0 to 5 m
    F, scp = gate_force(2.0, 0, 5, 60)
    Fn, sn = gate_force_numeric(2.0, 0, 5, 60)
    print(f"inclined gate: F = {F / 1e3:.3f} kN at slant {scp:.4f} m (numeric {sn:.4f})")
    assert abs(F - Fn) < 1e-6 * F and abs(scp - sn) < 1e-9
    # overturning of a 1 m strip of a 60 m dam: resultant rho g h^2 / 2 at h/3 above the base
    H = 60.0
    P = RHO * G * H**2 / 2
    print(f"dam (per metre of crest): water push {P / 1e6:.3f} MN acting {H / 3:.0f} m above the base, overturning moment {P * H / 3 / 1e6:.2f} MN m")
