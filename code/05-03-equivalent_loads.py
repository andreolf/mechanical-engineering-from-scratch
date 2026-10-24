"""Reduce a distributed load to one resultant force at one location, by numerical integration."""
import numpy as np


def reduce_load(q, a, b, n=20001):
    """Resultant R = int q dx and its line of action x_bar = int x q dx / R (Simpson's rule)."""
    x = np.linspace(a, b, n); y = q(x); h = (b - a) / (n - 1)
    w = np.ones(n); w[1:-1:2] = 4; w[2:-1:2] = 2; w *= h / 3
    R = w @ y; M = w @ (x * y)
    return R, M / R


def reduce_system(forces, about=0.0):
    """Point loads (x, F) in 2D: equivalent force and moment at a chosen point, then the single-force position."""
    R = sum(F for _, F in forces); M = sum(F * (x - about) for x, F in forces)
    return R, M, about + M / R


if __name__ == "__main__":
    L = 6.0
    # triangular load rising from 0 to 4 kN/m: resultant w L / 2 at 2L/3 from the zero end, i.e. L/3 from the peak
    R, xb = reduce_load(lambda x: 4.0 * x / L, 0, L)
    print(f"triangle: R = {R:.6f} kN at x = {xb:.6f} m (L/3 from the high end = {L - L / 3:.1f} m)")
    assert abs(R - 12) < 1e-9 and abs(xb - 2 * L / 3) < 1e-9
    # trapezoid on a footbridge deck: 2 kN/m to 5 kN/m over 6 m = rectangle + triangle
    R, xb = reduce_load(lambda x: 2 + 3 * x / L, 0, L)
    R_hand = 2 * L + 3 * L / 2; x_hand = (2 * L * L / 2 + 3 * L / 2 * 2 * L / 3) / R_hand
    print(f"trapezoid: R = {R:.4f} kN at x = {xb:.4f} m (hand: {R_hand:.1f} kN at {x_hand:.4f} m)")
    assert abs(R - R_hand) < 1e-9 and abs(xb - x_hand) < 1e-9
    # wind on a bamboo scaffold: q = q0 (z / H)^(2/7) power-law profile, H = 12 m, q0 = 0.9 kN/m
    H, q0 = 12.0, 0.9
    R, zb = reduce_load(lambda z: q0 * (z / H) ** (2 / 7), 0, H)
    print(f"wind on scaffold: R = {R:.4f} kN acting {zb:.4f} m up (exact {q0 * H * 7 / 9:.4f} kN at {H * 9 / 16:.4f} m)")
    assert abs(R - q0 * H * 7 / 9) < 1e-4 and abs(zb - 9 * H / 16) < 1e-4    # z^(2/7) has an infinite slope at z = 0, so Simpson converges slowly there
    # several point loads on a beam: one force and its line of action
    R, M0, x = reduce_system([(1.0, 10.0), (2.5, 4.0), (4.0, -3.0), (5.0, 8.0)])
    print(f"point loads: R = {R:.1f} kN, moment about x = 0: {M0:.1f} kN m, single force at x = {x:.4f} m")
