"""Gauss-Legendre nodes and weights by Golub-Welsch, exactness check and a beam-section integral."""
import math
import numpy as np


def gauss_legendre(n):
    """Eigenvalues of the symmetric tridiagonal Jacobi matrix are the nodes; weights come from the eigenvectors."""
    k = np.arange(1, n)
    beta = k / np.sqrt(4 * k**2 - 1)
    J = np.diag(beta, 1) + np.diag(beta, -1)
    x, V = np.linalg.eigh(J)
    w = 2 * V[0] ** 2
    return x, w


def integrate(f, a, b, n):
    x, w = gauss_legendre(n)
    return 0.5 * (b - a) * np.sum(w * f(0.5 * (b - a) * x + 0.5 * (a + b)))


def simpson(f, a, b, m):
    x = np.linspace(a, b, m + 1); y = f(x); h = (b - a) / m
    return h / 3 * (y[0] + y[-1] + 4 * y[1:-1:2].sum() + 2 * y[2:-1:2].sum())


if __name__ == "__main__":
    x2, w2 = gauss_legendre(2)
    print("2-point nodes", x2, "weights", w2)
    assert np.allclose(x2, [-1 / math.sqrt(3), 1 / math.sqrt(3)]) and np.allclose(w2, [1, 1])
    for n in range(1, 9):
        x, w = gauss_legendre(n)
        for d in range(2 * n):                          # exact up to degree 2n - 1
            exact = 2 / (d + 1) if d % 2 == 0 else 0.0
            assert abs(np.sum(w * x**d) - exact) < 1e-13, (n, d)
        d = 2 * n
        assert abs(np.sum(w * x**d) - 2 / (d + 1)) > 1e-6     # and not beyond
    ref, wref = np.polynomial.legendre.leggauss(5)
    assert np.allclose(gauss_legendre(5)[0], ref) and np.allclose(gauss_legendre(5)[1], wref)
    print("n-point rule exact to degree 2n - 1 for n = 1..8; matches numpy leggauss")
    # smooth non-polynomial: integral of exp(-x^2) on [0, 2]
    f = lambda x: np.exp(-x**2)
    exact = math.sqrt(math.pi) / 2 * math.erf(2)
    for n in (2, 3, 4, 5, 6):
        print(f"Gauss {n} points: error {abs(integrate(f, 0, 2, n) - exact):.2e}")
    print(f"Simpson, 5 points: error {abs(simpson(f, 0, 2, 4) - exact):.2e}")
    assert abs(integrate(f, 0, 2, 6) - exact) < 1e-6
