"""Green's function of a simply supported beam: superposition, reciprocity and textbook checks."""
import numpy as np


def G(x, xi, L, EI):
    """Deflection at x from a unit downward load at xi (positive downward)."""
    x, xi = np.broadcast_arrays(np.asarray(x, float), np.asarray(xi, float))
    lo, hi = np.minimum(x, xi), np.maximum(x, xi)
    b = L - hi
    return b * lo * (L ** 2 - b ** 2 - lo ** 2) / (6 * EI * L)


def deflection(x, q, L, EI, n=20001):
    xi = np.linspace(0, L, n)
    return np.trapezoid(G(x, xi, L, EI) * q(xi), xi)


if __name__ == "__main__":
    L, EI = 4.0, 200e9 * 1943e-8
    P, w = 1e4, 5e3
    d_point = P * G(L / 2, L / 2, L, EI)
    d_udl = deflection(L / 2, lambda s: w * np.ones_like(s), L, EI)
    print(f"point load {d_point*1e3:.3f} mm, uniform load {d_udl*1e3:.3f} mm, both {1e3*(d_point+d_udl):.2f} mm")
    assert abs(d_point - P * L ** 3 / (48 * EI)) < 1e-15
    assert abs(d_udl - 5 * w * L ** 4 / (384 * EI)) < 1e-9
    # reciprocity: G(x, xi) = G(xi, x)
    rng = np.random.default_rng(15)
    a, b = rng.uniform(0, L, 100), rng.uniform(0, L, 100)
    assert np.allclose(G(a, b, L, EI), G(b, a, L, EI), rtol=0, atol=1e-18)
    print(f"influence: 10 kN at 1 m gives {P * G(2, 1, L, EI) * 1e3:.3f} mm at midspan")
    # a point load as the limit of a narrow uniform patch
    for width in (0.4, 0.04):
        patch = lambda s, wd=width: np.where(np.abs(s - L / 2) < wd / 2, P / wd, 0.0)
        print(f"patch of width {width} m: {deflection(L / 2, patch, L, EI, 400001) * 1e3:.4f} mm")
    assert abs(deflection(L / 2, lambda s: np.where(np.abs(s - 2) < 0.02, P / 0.04, 0.0), L, EI, 400001) - d_point) < 1e-3 * d_point
    # a triangular load rising from 0 to w: by symmetry its midspan deflection is half the uniform one
    q_tri = lambda s: w * s / L
    d_tri = deflection(L / 2, q_tri, L, EI)
    assert abs(d_tri - 0.5 * d_udl) < 1e-12          # mirror it and add: the two triangles make a uniform load
