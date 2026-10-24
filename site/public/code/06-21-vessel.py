"""Thin-walled pressure vessels and a penstock wall-thickness calculator for an alpine hydro plant."""
import math
import numpy as np


def hoop_axial(p, r, t):
    return p * r / t, p * r / (2 * t)


def hoop_by_integration(p, r, t, n=200001):
    """Cut a 1 mm long ring in half: the vertical pressure resultant on the half must equal 2 * hoop force."""
    th = np.linspace(0, np.pi, n)
    Fy = np.trapezoid(p * r * np.sin(th), th)        # = 2 p r per unit length
    return Fy / (2 * t)


def axial_by_integration(p, r, t, n=200001):
    """End cap: pressure on the disc area pi r^2 is carried by the wall area 2 pi r t."""
    rr = np.linspace(0, r, n)
    F = np.trapezoid(p * 2 * np.pi * rr, rr)
    return F / (2 * np.pi * r * t)


def penstock_thickness(head_m, D_mm, allow=160.0, joint=0.9, surge=1.25, corrosion=2.0, rho=1000.0, g=9.81):
    """Wall thickness (mm) along a penstock: static head plus a water-hammer surge allowance."""
    p = rho * g * head_m * surge / 1e6               # MPa
    return p * (D_mm / 2) / (allow * joint) + corrosion, p


if __name__ == "__main__":
    # check the formulas by equilibrium
    p, r, t = 2.0, 500.0, 10.0
    h, a = hoop_axial(p, r, t)
    hi, ai = hoop_by_integration(p, r, t), axial_by_integration(p, r, t)
    print(f"p = 2 MPa, r = 500, t = 10: hoop {h:.2f} MPa (integrated {hi:.4f}), axial {a:.2f} MPa (integrated {ai:.4f}), ratio {h / a:.1f}")
    assert abs(hi - h) < 1e-6 * h and abs(ai - a) < 1e-6 * a and abs(h / a - 2) < 1e-12
    # alpine penstock, 1.2 m diameter, dropping 650 m from the intake to the turbines
    D = 1200.0
    for head in (0, 100, 200, 300, 400, 500, 650):
        tt, pp = penstock_thickness(head, D)
        print(f"  head {head:3d} m: design pressure {pp:5.2f} MPa, wall {tt:5.1f} mm")
    t_bot, p_bot = penstock_thickness(650, D)
    t_use = math.ceil(t_bot)
    hs, ax = hoop_axial(p_bot, D / 2, t_use - 2.0)
    print(f"bottom section: use {t_use} mm plate; with 2 mm corroded away, hoop {hs:.1f} MPa, axial {ax:.1f} MPa")
    assert hs <= 160 * 0.9 + 1e-9
    # a sphere of the same radius and wall carries half the hoop stress
    print(f"sphere, same p, r, t: {p * r / (2 * t):.1f} MPa in every direction")
