"""Power iteration and inverse iteration, checked on a two-mass system and random matrices."""
import math
import numpy as np


def power_iteration(A, iters=5000, tol=1e-13, seed=0):
    x = np.random.default_rng(seed).standard_normal(len(A))
    lam = 0.0
    for _ in range(iters):
        y = A @ x
        x_new = y / np.linalg.norm(y)
        lam_new = x_new @ A @ x_new                 # Rayleigh quotient
        # stop on the residual, not on lambda: lambda converges twice as fast as the vector
        if np.linalg.norm(A @ x_new - lam_new * x_new) < tol * abs(lam_new):
            return lam_new, x_new
        x, lam = x_new, lam_new
    return lam, x


def inverse_iteration(A, shift=0.0, iters=5000, tol=1e-13):
    n = len(A); x = np.ones(n) / math.sqrt(n); lam = None
    B = A - shift * np.eye(n)
    for _ in range(iters):
        y = np.linalg.solve(B, x)
        x = y / np.linalg.norm(y)
        lam_new = x @ A @ x
        if np.linalg.norm(A @ x - lam_new * x) < tol * np.abs(A).max():
            break
        lam = lam_new
    return lam_new, x


if __name__ == "__main__":
    k, m = 800.0, 2.0
    A = np.array([[2 * k, -k], [-k, k]]) / m
    lmax, vmax = power_iteration(A)
    lmin, vmin = inverse_iteration(A)
    print(f"omega_1 = {math.sqrt(lmin):.4f} rad/s, omega_2 = {math.sqrt(lmax):.4f} rad/s")
    phi = (1 + 5 ** 0.5) / 2
    assert abs(lmin - k / m * (3 - 5 ** 0.5) / 2) < 1e-9 and abs(lmax - k / m * (3 + 5 ** 0.5) / 2) < 1e-9
    assert abs(vmin[1] / vmin[0] - phi) < 1e-8 and abs(vmax[1] / vmax[0] + 1 / phi) < 1e-8
    assert abs(lmin + lmax - np.trace(A)) < 1e-9 and abs(lmin * lmax - np.linalg.det(A)) < 1e-6
    # symmetric random matrices: extreme eigenvalues match numpy
    rng = np.random.default_rng(7)
    B = rng.standard_normal((30, 30)); S = B @ B.T + np.eye(30)
    w = np.linalg.eigvalsh(S)
    assert abs(power_iteration(S, iters=20000)[0] - w[-1]) < 1e-8 * w[-1]
    assert abs(inverse_iteration(S)[0] - w[0]) < 1e-8 * w[-1]
    # a shift picks out an interior eigenvalue
    target = w[12] + 0.01
    assert abs(inverse_iteration(S, shift=target)[0] - w[12]) < 1e-8 * w[-1]
    print("power, inverse and shifted inverse iteration agree with numpy")
