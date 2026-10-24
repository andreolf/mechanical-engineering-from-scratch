"""Lagrange interpolation in barycentric form: equispaced nodes (Runge) versus Chebyshev nodes."""
import numpy as np

runge = lambda x: 1 / (1 + 25 * x**2)


def bary_weights(xn):
    w = np.ones(len(xn))
    for j in range(len(xn)):
        w[j] = 1 / np.prod(xn[j] - np.delete(xn, j))
    return w


def interp(xn, yn, x):
    """Barycentric Lagrange formula: stable, O(n) per point once the weights are known."""
    w = bary_weights(xn)
    d = x[:, None] - xn[None, :]
    exact = np.isclose(d, 0, atol=1e-14)
    d[exact] = 1
    t = w / d
    p = (t @ yn) / t.sum(axis=1)
    rows, cols = np.nonzero(exact)
    p[rows] = yn[cols]
    return p


def equi(n):
    return np.linspace(-1, 1, n + 1)


def cheb(n):
    k = np.arange(n + 1)
    return np.cos((2 * k + 1) * np.pi / (2 * (n + 1)))


if __name__ == "__main__":
    x = np.linspace(-1, 1, 4001)
    # sanity: interpolating a cubic with 4+ nodes is exact
    xn = equi(5)
    assert np.max(np.abs(interp(xn, xn**3 - xn, x) - (x**3 - x))) < 1e-12
    print(" n   equispaced max error   Chebyshev max error")
    ce = []
    for n in (5, 10, 15, 20):
        ee = np.max(np.abs(interp(equi(n), runge(equi(n)), x) - runge(x)))
        ce.append(np.max(np.abs(interp(cheb(n), runge(cheb(n)), x) - runge(x))))
        print(f"{n:2d}   {ee:20.4f}   {ce[-1]:19.4f}")
    assert all(b < a for a, b in zip(ce, ce[1:]))          # Chebyshev error falls as n grows
    e20 = np.max(np.abs(interp(equi(20), runge(equi(20)), x) - runge(x)))
    assert e20 > 50                                         # Runge: equispaced error explodes
