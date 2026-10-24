"""Verification by the method of manufactured solutions: pick u, derive f, check the observed order of a 2D Poisson solver."""
import math
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

# manufactured solution (not a polynomial, not separable into one Fourier mode, nonzero boundary values)
u_m = lambda x, y: np.sin(math.pi * x) * np.exp(y) + x * y**2
# f = -lap u, derived by hand: -(-pi^2 sin(pi x) e^y + sin(pi x) e^y + 2x)
f_m = lambda x, y: (math.pi**2 - 1) * np.sin(math.pi * x) * np.exp(y) - 2 * x


def poisson_solve(n, f, g, bug=False):
    """5-point Laplacian on the unit square with Dirichlet data g. bug=True plants a classic mistake."""
    h = 1.0 / n; m = n - 1
    x = np.linspace(0, 1, n + 1); X, Y = np.meshgrid(x, x, indexing="ij")
    T = sp.diags([-1.0, 2.0, -1.0], [-1, 0, 1], shape=(m, m))
    I = sp.identity(m)
    hA = 1.0 / (n + 1) if bug else h                  # the planted bug: an off-by-one grid spacing in the matrix
    A = (sp.kron(T, I) + sp.kron(I, T)) / hA**2
    b = f(X[1:-1, 1:-1], Y[1:-1, 1:-1]).copy()
    G = g(X, Y)
    b[0, :] += G[0, 1:-1] / hA**2; b[-1, :] += G[-1, 1:-1] / hA**2
    b[:, 0] += G[1:-1, 0] / hA**2; b[:, -1] += G[1:-1, -1] / hA**2
    U = G.copy(); U[1:-1, 1:-1] = spla.spsolve(A.tocsc(), b.ravel()).reshape(m, m)
    return X, Y, U


def observed_orders(bug=False, ns=(8, 16, 32, 64, 128)):
    errs = []
    for n in ns:
        X, Y, U = poisson_solve(n, f_m, u_m, bug)
        errs.append(np.max(np.abs(U - u_m(X, Y))))
    return errs, [math.log2(a / b) for a, b in zip(errs, errs[1:])]


if __name__ == "__main__":
    # check the hand derivation of f with a finite-difference Laplacian of u at a point
    x0, y0, d = 0.3, 0.7, 1e-4
    lap = (u_m(x0 + d, y0) + u_m(x0 - d, y0) + u_m(x0, y0 + d) + u_m(x0, y0 - d) - 4 * u_m(x0, y0)) / d**2
    assert abs(-lap - f_m(x0, y0)) < 1e-4
    errs, p = observed_orders()
    print("correct solver: errors", " ".join(f"{e:.2e}" for e in errs), "| observed orders", " ".join(f"{q:.3f}" for q in p))
    assert abs(p[-1] - 2) < 0.02
    errs_b, p_b = observed_orders(bug=True)
    print("planted bug:    errors", " ".join(f"{e:.2e}" for e in errs_b), "| observed orders", " ".join(f"{q:.3f}" for q in p_b))
    assert errs_b[-1] < 0.02 and abs(p_b[-1] - 1) < 0.1     # small errors that look fine, but first order: MMS exposes it
