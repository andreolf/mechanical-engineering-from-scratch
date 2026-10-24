"""Least-squares fits by normal equations and by QR, with an orthogonality check."""
import numpy as np


def fit_normal(A, b):
    return np.linalg.solve(A.T @ A, A.T @ b)


def fit_qr(A, b):
    Q, R = np.linalg.qr(A)          # reduced QR: A = QR, Q has orthonormal columns
    return np.linalg.solve(R, Q.T @ b)


if __name__ == "__main__":
    x = np.array([0, 1, 2, 3, 4, 5.0])
    F = np.array([0.1, 2.6, 4.7, 7.4, 9.6, 12.1])
    A = np.column_stack([x, np.ones_like(x)])
    k, F0 = fit_normal(A, F)
    r = F - A @ np.array([k, F0])
    print(f"k = {k:.4f} N/mm, F0 = {F0:.4f} N, |r| = {np.linalg.norm(r):.4f} N")
    assert abs(k - 251.1 / 105) < 1e-12 and abs(F0 - 11 / 105) < 1e-12
    assert np.allclose(A.T @ r, 0, atol=1e-12)                       # residual is orthogonal to the columns
    assert np.allclose(fit_qr(A, F), [k, F0]) and np.allclose(np.linalg.lstsq(A, F, rcond=None)[0], [k, F0])
    # an ill-conditioned fit: degree-11 polynomial in raw x on [10, 11]
    t = np.linspace(10, 11, 40)
    V = np.vander(t, 12)
    y = np.cos(t)
    c_qr, c_ne = fit_qr(V, y), np.linalg.lstsq(V.T @ V, V.T @ y, rcond=None)[0]
    e_qr, e_ne = np.linalg.norm(V @ c_qr - y), np.linalg.norm(V @ c_ne - y)
    print(f"cond(V) = {np.linalg.cond(V):.1e}; residual with QR {e_qr:.1e}, with normal equations {e_ne:.1e}")
    assert e_qr < 1e-6 and e_ne > 100 * e_qr
