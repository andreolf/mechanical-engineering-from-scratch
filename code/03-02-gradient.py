"""Gradients, directional derivatives and gradient descent on quadratic bowls."""
import math
import numpy as np


def num_grad(f, x, h=1e-6):
    x = np.asarray(x, float); g = np.zeros_like(x)
    for i in range(len(x)):
        e = np.zeros_like(x); e[i] = h
        g[i] = (f(x + e) - f(x - e)) / (2 * h)
    return g


def descend(grad, x0, eta, tol=1e-8, max_iter=100000):
    x = np.asarray(x0, float)
    for k in range(max_iter):
        g = grad(x)
        if np.linalg.norm(g) < tol:
            return x, k
        x = x - eta * g
        if not np.all(np.isfinite(x)) or np.linalg.norm(x) > 1e12:
            return x, -1                          # diverged
    return x, max_iter


if __name__ == "__main__":
    T = lambda p: 100 - 2 * p[0] ** 2 - p[1] ** 2
    g = num_grad(T, [1, 2])
    assert np.allclose(g, [-4, -4], atol=1e-6)
    u = np.array([3, 4]) / 5
    assert abs(g @ u + 5.6) < 1e-6 and abs(np.linalg.norm(g) - 4 * math.sqrt(2)) < 1e-6
    assert abs(g @ np.array([-2, 2])) < 1e-6                 # perpendicular to the isotherm
    q = -50 * g
    print(f"heat flux at (1, 2): {np.round(q, 3)} W/m^2, |q| = {np.linalg.norm(q):.1f}")
    # gradient descent on bowls with growing condition number
    print(" kappa  steps (best fixed step)  theory")
    for kappa in (2, 10, 100):
        A = np.diag([1.0, kappa])
        eta = 2 / (1 + kappa)                                # optimal fixed step
        x, k = descend(lambda x: A @ x, [1.0, 1.0], eta)
        rate = (kappa - 1) / (kappa + 1)
        theory = math.log(1e-8 / math.sqrt(1 + kappa ** 2)) / math.log(rate)
        print(f"{kappa:5d}  {k:8d}  {theory:10.0f}")
        assert k > 0 and abs(k - theory) < 0.1 * theory + 3
    # a step beyond 2 / lambda_max diverges
    assert descend(lambda x: np.diag([1.0, 10.0]) @ x, [1.0, 1.0], 2.05 / 10)[1] == -1
