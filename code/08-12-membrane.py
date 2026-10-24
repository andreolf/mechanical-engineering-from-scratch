"""Modes of a square membrane by finite differences and scipy.sparse.linalg.eigsh."""
import math
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh


def laplacian_2d(N, h):
    """5-point Laplacian on the N x N interior points of a square with fixed edges (negative definite)."""
    d = sp.diags([1.0, -2.0, 1.0], [-1, 0, 1], shape=(N, N)) / h**2
    I = sp.identity(N)
    return (sp.kron(I, d) + sp.kron(d, I)).tocsc()


if __name__ == "__main__":
    a, N = 1.0, 99                       # unit square, 99 x 99 interior points
    h = a / (N + 1)
    A = -laplacian_2d(N, h)
    lam, V = eigsh(A, k=10, sigma=0, which="LM")
    order = np.argsort(lam); lam, V = lam[order], V[:, order]
    exact = sorted(math.pi**2 * (m * m + n * n) / a**2 for m in range(1, 6) for n in range(1, 6))[:10]
    # exact eigenvalues of the discrete operator, for a sharper test
    disc = sorted((4 / h**2) * (math.sin(m * math.pi * h / (2 * a))**2 + math.sin(n * math.pi * h / (2 * a))**2) for m in range(1, 6) for n in range(1, 6))[:10]
    print("lambda / pi^2:", np.round(lam / math.pi**2, 4))
    print("m^2 + n^2    :", [round(e / math.pi**2) for e in exact])
    assert np.allclose(lam, disc, rtol=1e-9)
    assert np.allclose(lam / math.pi**2, np.round(np.array(exact) / math.pi**2), rtol=2e-3)
    # frequencies of a drum-like membrane: f = c sqrt(lambda) / (2 pi), c = sqrt(T / rho_s)
    T, rho_s, side = 2000.0, 0.25, 0.4      # tension per length N/m, areal density kg/m^2, side m
    c = math.sqrt(T / rho_s)
    f11 = c / (2 * side) * math.sqrt(2)
    print(f"0.4 m square membrane: c = {c:.2f} m/s, f11 = {f11:.2f} Hz; overtone ratios", [round(math.sqrt(e / exact[0]), 3) for e in exact[:6]])
    # degenerate pair (1,2) and (2,1): equal frequencies, so any mix is also a mode (Chladni-like patterns)
    print(f"modes 2 and 3: lambda {lam[1]:.4f} and {lam[2]:.4f} (equal)")
    assert abs(lam[1] - lam[2]) < 1e-8 * lam[1]
