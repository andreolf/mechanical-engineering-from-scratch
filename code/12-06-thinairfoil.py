"""Thin airfoil theory: lift slope, zero-lift angle and pitching moment from the camber line, via Glauert integrals."""
import math
import numpy as np


def naca4_slope(x, m, p):
    """dz/dx of a NACA 4-digit mean camber line (max camber m at chord position p)."""
    return np.where(x < p, 2 * m / p ** 2 * (p - x), 2 * m / (1 - p) ** 2 * (p - x))


def glauert(m, p, alpha, n=200000):
    """A0, A1, A2 with x = (1 - cos t)/2. Midpoint rule in t avoids the endpoints."""
    t = (np.arange(n) + 0.5) * math.pi / n; dt = math.pi / n
    dz = naca4_slope((1 - np.cos(t)) / 2, m, p) if m > 0 else np.zeros(n)
    A0 = alpha - np.sum(dz) * dt / math.pi
    A1 = 2 / math.pi * np.sum(dz * np.cos(t)) * dt
    A2 = 2 / math.pi * np.sum(dz * np.cos(2 * t)) * dt
    return A0, A1, A2


def coefficients(m, p, alpha):
    A0, A1, A2 = glauert(m, p, alpha)
    CL = math.pi * (2 * A0 + A1)
    Cm4 = math.pi / 4 * (A2 - A1)
    return CL, Cm4


if __name__ == "__main__":
    # symmetric plate: C_L = 2 pi alpha
    a = math.radians(4)
    CL, Cm = coefficients(0, 0.4, a)
    print(f"flat plate at 4 deg: C_L = {CL:.5f} (2 pi alpha = {2*math.pi*a:.5f}), C_m,c/4 = {Cm:.5f}")
    assert abs(CL - 2 * math.pi * a) < 1e-12 and abs(Cm) < 1e-12
    # NACA 2412: 2 % camber at 40 % chord
    m, p = 0.02, 0.4
    c1, _ = coefficients(m, p, math.radians(2)); c2, Cm = coefficients(m, p, math.radians(6))
    slope = (c2 - c1) / math.radians(4)
    a0 = math.radians(2) - c1 / slope
    print(f"NACA 2412: lift slope {slope:.6f} per rad (2 pi = {2*math.pi:.6f}), zero-lift angle {math.degrees(a0):.3f} deg, C_m,c/4 = {Cm:.4f}")
    assert abs(slope - 2 * math.pi) < 1e-9                                  # camber shifts the line, it doesn't change the slope
    for deg in (0, 4, 8):
        print(f"  alpha = {deg} deg: C_L = {coefficients(m, p, math.radians(deg))[0]:.4f}")
    # a kite over Bali: 2.5 m^2, 8 m/s wind, 6 deg, aspect-ratio correction left out (lesson 12.07 and beyond)
    CL = coefficients(m, p, math.radians(6))[0]
    print(f"kite lift (2D estimate): {0.5*1.16*8**2*2.5*CL:.1f} N")
