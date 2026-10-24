"""Tensor-product Bezier surfaces: evaluate a bicubic patch, its partial derivatives and unit normals, and check them on a surface with a known normal."""
import math
import numpy as np


def bern3(t):
    return np.array([(1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3])


def dbern3(t):
    return np.array([-3 * (1 - t) ** 2, 3 * (1 - t) ** 2 - 6 * t * (1 - t), 6 * t * (1 - t) - 3 * t * t, 3 * t * t])


def patch(Pn, u, v):
    """Pn has shape (4, 4, 3). Returns S, S_u, S_v."""
    bu, bv, du, dv = bern3(u), bern3(v), dbern3(u), dbern3(v)
    S = np.einsum("i,j,ijk->k", bu, bv, Pn)
    Su = np.einsum("i,j,ijk->k", du, bv, Pn)
    Sv = np.einsum("i,j,ijk->k", bu, dv, Pn)
    return S, Su, Sv


def normal(Pn, u, v):
    _, Su, Sv = patch(Pn, u, v)
    n = np.cross(Su, Sv)
    return n / np.linalg.norm(n)


if __name__ == "__main__":
    # a hyperbolic-paraboloid roof, 10 x 10 m, z = x y / 25 for x, y in [-5, 5]. Degree elevation makes it an exact bicubic patch:
    # control points sit at thirds of the square, with z = x_i y_j / 25 (the surface is bilinear in u and v)
    g = np.linspace(-5, 5, 4)
    Pn = np.array([[[x, y, x * y / 25] for y in g] for x in g])
    worst_s = worst_n = worst_unit = 0.0
    for u in np.linspace(0, 1, 21):
        for v in np.linspace(0, 1, 21):
            S, Su, Sv = patch(Pn, u, v)
            x, y = S[0], S[1]
            worst_s = max(worst_s, abs(S[2] - x * y / 25))
            n = normal(Pn, u, v)
            exact = np.array([-y / 25, -x / 25, 1.0]); exact /= np.linalg.norm(exact)
            worst_n = max(worst_n, np.abs(n - exact).max())
            worst_unit = max(worst_unit, abs(np.linalg.norm(n) - 1))
    print(f"roof patch: surface error {worst_s:.1e} m, normal error {worst_n:.1e}, |n| - 1 at most {worst_unit:.1e}")
    assert worst_s < 1e-12 and worst_n < 1e-12 and worst_unit < 1e-14
    # corners interpolate the corner control points
    for (u, v, i, j) in ((0, 0, 0, 0), (1, 0, 3, 0), (0, 1, 0, 3), (1, 1, 3, 3)):
        assert np.allclose(patch(Pn, u, v)[0], Pn[i, j])
    n_c = normal(Pn, 1, 1)
    print(f"normal at the high corner (5, 5, 1): {n_c.round(6)}; tilt from vertical {math.degrees(math.acos(n_c[2])):.4f} deg")
    # surface area by integrating |S_u x S_v| (Gauss-Legendre, 12 x 12) against a fine triangulation
    xg, wg = np.polynomial.legendre.leggauss(12); xg = (xg + 1) / 2; wg = wg / 2
    area = sum(wg[a] * wg[b] * np.linalg.norm(np.cross(*patch(Pn, xg[a], xg[b])[1:])) for a in range(12) for b in range(12))
    N = 200; tri = 0.0
    pts = np.array([[patch(Pn, u, v)[0] for v in np.linspace(0, 1, N + 1)] for u in np.linspace(0, 1, N + 1)])
    for i in range(N):
        a, b, c, d = pts[i, :-1], pts[i + 1, :-1], pts[i + 1, 1:], pts[i, 1:]
        tri += 0.5 * (np.linalg.norm(np.cross(b - a, c - a), axis=1).sum() + np.linalg.norm(np.cross(c - a, d - a), axis=1).sum())
    print(f"roof area: {area:.6f} m^2 by Gauss-Legendre, {tri:.6f} m^2 from 80000 triangles (plan area 100 m^2)")
    assert abs(area - tri) < 1e-4 * area
