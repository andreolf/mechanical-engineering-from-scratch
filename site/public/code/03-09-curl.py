"""Circulation around loops and numerical curl; Stokes' theorem for forced and free vortices."""
import math
import numpy as np


def circulation(u, cx, cy, R, n=4000):
    t = 2 * math.pi * (np.arange(n) + 0.5) / n
    x, y = cx + R * np.cos(t), cy + R * np.sin(t)
    ux, uy = u(x, y)
    return np.sum(ux * (-R * np.sin(t)) + uy * (R * np.cos(t))) * 2 * math.pi / n


def curl_z(u, x, y, h=1e-5):
    return (u(x + h, y)[1] - u(x - h, y)[1]) / (2 * h) - (u(x, y + h)[0] - u(x, y - h)[0]) / (2 * h)


if __name__ == "__main__":
    Om = 3.0
    forced = lambda x, y: (-Om * y, Om * x)
    G = circulation(forced, 0, 0, 0.5)
    print(f"forced vortex: circulation {G:.6f} m^2/s, curl x area {curl_z(forced, 0.2, -0.1) * math.pi * 0.25:.6f}")
    assert abs(G - 2 * math.pi * 0.25 * Om) < 1e-10 and abs(curl_z(forced, 0.2, -0.1) - 2 * Om) < 1e-8
    # free vortex: zero curl away from the axis, but circulation Gamma around any loop that encloses it
    Gam = 4.712
    free = lambda x, y: (-Gam / (2 * math.pi) * y / (x * x + y * y), Gam / (2 * math.pi) * x / (x * x + y * y))
    for R in (0.1, 1.0, 5.0):
        assert abs(circulation(free, 0, 0, R) - Gam) < 1e-9
    assert abs(circulation(free, 2.0, 0.0, 0.5)) < 1e-9          # a loop that doesn't enclose the axis
    for p in [(0.3, 0.4), (-1, 2), (2, -0.5)]:
        assert abs(curl_z(free, *p)) < 1e-6
    # Green's theorem on a square for a field with non-uniform curl: F = (-y^3, x^3), curl = 3x^2 + 3y^2
    F = lambda x, y: (-y ** 3, x ** 3)
    s = np.linspace(-1, 1, 200001); ds = s[1] - s[0]
    edges = (np.trapezoid(F(s, -1 + 0 * s)[0], s) + np.trapezoid(F(1 + 0 * s, s)[1], s)
             - np.trapezoid(F(s, 1 + 0 * s)[0], s) - np.trapezoid(F(-1 + 0 * s, s)[1], s))
    assert abs(edges - 8.0) < 1e-6          # double integral of 3x^2 + 3y^2 over [-1, 1]^2 is 8
    print("Stokes and Green verified for forced, free and polynomial fields")
