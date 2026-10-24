"""Axial bars: delta = sum N L / (E A) for stepped bars, plus self-weight and a tapered bar by integration."""
import math
import numpy as np


def stepped(segments):
    """segments: (L, A, E, N) with N the internal axial force in that segment (tension positive). Returns total stretch."""
    return sum(N * L / (E * A) for L, A, E, N in segments)


def integrate_stretch(N, A, E, L, n=20001):
    """delta = int_0^L N(x) / (E A(x)) dx by Simpson's rule."""
    x = np.linspace(0, L, n); f = N(x) / (E * A(x))
    w = np.ones(n); w[1:-1:2] = 4; w[2:-1:2] = 2
    return L / (n - 1) / 3 * (w @ f)


if __name__ == "__main__":
    # the brake cable from lesson 05.12: steel, 1.5 mm diameter, 1.8 m long, 168 N
    A = math.pi * 0.75**2
    d = stepped([(1800, A, 200e3, 168)])
    print(f"brake cable stretch {d:.4f} mm (stress {168 / A:.2f} MPa)")
    # stepped bar: steel rod 400 mm of 20 mm diameter then aluminium 300 mm of 30 mm diameter;
    # 30 kN pulls at the free end and 10 kN pushes back at the joint
    As, Aa = math.pi * 10**2, math.pi * 15**2
    segs = [(400, As, 210e3, 30e3 - 10e3), (300, Aa, 70e3, 30e3)]   # steel next to the wall carries 20 kN, aluminium 30 kN
    d = stepped(segs)
    print(f"stepped bar: steel {segs[0][3] * 400 / (210e3 * As):.4f} mm + aluminium {30e3 * 300 / (70e3 * Aa):.4f} mm = {d:.4f} mm")
    # check by integrating the aluminium piece numerically
    num = 20e3 * 400 / (210e3 * As) + integrate_stretch(lambda x: 30e3 + 0 * x, lambda x: Aa + 0 * x, 70e3, 300)
    assert abs(num - d) < 1e-9
    # a hanging steel cable under its own weight: N(x) = rho g A (L - x), delta = rho g L^2 / (2 E)
    L = 1000e3                                 # mm
    rg = 7850 * 9.81 * 1e-9                    # rho g in N/mm^3
    d_self = integrate_stretch(lambda x: rg * 1.0 * (L - x), lambda x: 1.0 + 0 * x, 210e3, L)
    print(f"1 km steel cable hanging under its own weight stretches {d_self:.3f} mm (rho g L^2 / 2E = {rg * L**2 / (2 * 210e3):.3f})")
    assert abs(d_self - rg * L**2 / (2 * 210e3)) < 1e-6
    # tapered round bar (radius r1 -> r2 linearly): closed form delta = P L / (E pi r1 r2)
    P, Lt, r1, r2 = 50e3, 500.0, 15.0, 10.0
    d_t = integrate_stretch(lambda x: P + 0 * x, lambda x: math.pi * (r1 + (r2 - r1) * x / Lt) ** 2, 210e3, Lt)
    print(f"tapered bar: {d_t:.6f} mm, closed form {P * Lt / (210e3 * math.pi * r1 * r2):.6f} mm")
    assert abs(d_t - P * Lt / (210e3 * math.pi * r1 * r2)) < 1e-9
