"""Gradient descent versus BFGS with an Armijo backtracking line search on the Rosenbrock valley."""
import numpy as np


def rosen(x):
    return (1 - x[0]) ** 2 + 100 * (x[1] - x[0] ** 2) ** 2


def rosen_grad(x):
    return np.array([-2 * (1 - x[0]) - 400 * x[0] * (x[1] - x[0] ** 2), 200 * (x[1] - x[0] ** 2)])


def armijo(f, x, fx, g, p, c1=1e-4, shrink=0.5):
    """Backtrack from a full step until the decrease is at least c1 * alpha * g.p."""
    a, slope = 1.0, g @ p
    while f(x + a * p) > fx + c1 * a * slope:
        a *= shrink
    return a


def bfgs(f, grad, x, tol=1e-10, maxit=500):
    n = len(x); Hinv = np.eye(n); g = grad(x); path = [x.copy()]; evals = 0
    for k in range(maxit):
        if np.linalg.norm(g) < tol:
            break
        p = -Hinv @ g
        a = armijo(f, x, f(x), g, p)
        s = a * p; x_new = x + s; g_new = grad(x_new); y = g_new - g
        if y @ s > 1e-12:                               # curvature condition keeps Hinv positive definite
            rho = 1 / (y @ s); I = np.eye(n)
            Hinv = (I - rho * np.outer(s, y)) @ Hinv @ (I - rho * np.outer(y, s)) + rho * np.outer(s, s)
        x, g = x_new, g_new; path.append(x.copy())
    return x, k, np.array(path)


def gradient_descent(f, grad, x, tol=1e-10, maxit=100_000):
    g = grad(x)
    for k in range(maxit):
        if np.linalg.norm(g) < tol:
            break
        p = -g
        x = x + armijo(f, x, f(x), g, p) * p; g = grad(x)
    return x, k


if __name__ == "__main__":
    x0 = np.array([-1.2, 1.0])                          # the classic start
    xb, kb, path = bfgs(rosen, rosen_grad, x0.copy())
    xg, kg = gradient_descent(rosen, rosen_grad, x0.copy())
    print(f"BFGS: ({xb[0]:.8f}, {xb[1]:.8f}) after {kb} iterations")
    print(f"gradient descent: ({xg[0]:.6f}, {xg[1]:.6f}) after {kg} iterations")
    assert np.linalg.norm(xb - 1) < 1e-6 and kb < 100
    assert kg > 20 * kb
    from scipy.optimize import minimize
    r = minimize(rosen, x0, jac=rosen_grad, method="BFGS")
    print(f"scipy BFGS: {r.nit} iterations, x = {r.x.round(6)}")
