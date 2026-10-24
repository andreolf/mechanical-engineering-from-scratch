"""Bending stress sigma = M y / I over a cross-section, checked by integrating the stress field."""
import math
import numpy as np


def stress_field(M, I, ys):
    """Positive M (sagging) compresses the top: sigma = -M y / I with y measured up from the neutral axis."""
    return -M * ys / I


if __name__ == "__main__":
    # a timber joist 50 x 200 mm, M = 6 kN m
    b, h, M = 50.0, 200.0, 6e6                    # mm, N mm
    I = b * h**3 / 12
    n = 2001
    y = np.linspace(-h / 2, h / 2, n); dy = h / (n - 1)
    s = stress_field(M, I, y)
    w = np.ones(n); w[1:-1:2] = 4; w[2:-1:2] = 2; w *= dy / 3 * b      # Simpson weights times width
    N, Mr = w @ s, -(w @ (s * y))
    print(f"joist: I = {I:.4e} mm^4, max stress {abs(s).max():.4f} MPa (M c / I = {M * (h / 2) / I:.4f}, 6M/(b h^2) = {6 * M / (b * h * h):.4f})")
    print(f"  resultant axial force {N:.2e} N (zero), resultant moment {Mr / 1e6:.6f} kN m (= M)")
    assert abs(abs(s).max() - M * (h / 2) / I) < 1e-9 and abs(N) < 1e-6 and abs(Mr - M) < 1e-3
    # a bamboo culm beam in Bali: outer diameter 100 mm, wall 8 mm, 3 m span, 2 kN at mid-span
    D, t, L, P = 100.0, 8.0, 3000.0, 2000.0
    d = D - 2 * t
    Ib = math.pi * (D**4 - d**4) / 64
    Mb = P * L / 4
    sb = Mb * (D / 2) / Ib
    print(f"bamboo culm: I = {Ib:.4e} mm^4, M = {Mb / 1e6:.2f} kN m, max bending stress {sb:.3f} MPa")
    # the same area as a solid rod would be much weaker
    A = math.pi * (D**2 - d**2) / 4; Ds = math.sqrt(4 * A / math.pi)
    ss = Mb * (Ds / 2) / (math.pi * Ds**4 / 64)
    print(f"  solid rod of the same area (D = {Ds:.2f} mm): {ss:.2f} MPa, {ss / sb:.2f} times higher")
    assert ss > 3 * sb
