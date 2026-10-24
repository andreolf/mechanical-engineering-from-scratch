"""One-dimensional Reynolds equation for a plane slider bearing: finite-difference pressure against the closed-form solution, and why only a converging film carries load."""
import math
import numpy as np


def film(x, L, h_in, h_out):
    return h_in + (h_out - h_in) * x / L


def reynolds_fd(L, U, mu, h_in, h_out, n=2001):
    """d/dx(h^3 dp/dx) = 6 mu U dh/dx with p = 0 at both ends (surface moving at U in +x)."""
    x = np.linspace(0, L, n)
    dx = x[1] - x[0]
    h = film(x, L, h_in, h_out)
    hm = film(0.5 * (x[1:] + x[:-1]), L, h_in, h_out) ** 3  # h^3 at mid-points
    A = np.zeros((n, n)); b = np.zeros(n)
    A[0, 0] = A[-1, -1] = 1.0
    for i in range(1, n - 1):
        A[i, i - 1] = hm[i - 1]
        A[i, i] = -(hm[i - 1] + hm[i])
        A[i, i + 1] = hm[i]
        b[i] = 6 * mu * U * (film(x[i] + dx / 2, L, h_in, h_out) - film(x[i] - dx / 2, L, h_in, h_out)) * dx
    p = np.linalg.solve(A, b)
    return x, p


def trapz(y, x):
    return float(np.sum(0.5 * (y[1:] + y[:-1]) * np.diff(x)))


def load_closed_form(L, U, mu, h_in, h_out):
    """Load per unit width (N/m) of an inclined pad, K = h_in/h_out."""
    K = h_in / h_out
    if abs(K - 1) < 1e-12:
        return 0.0
    return 6 * mu * U * L**2 / (h_out**2 * (K - 1) ** 2) * (math.log(K) - 2 * (K - 1) / (K + 1))


if __name__ == "__main__":
    L, U, mu, h_out = 0.05, 10.0, 0.03, 20e-6  # 50 mm pad, 10 m/s, hot SAE 30 oil, 20 um minimum film
    for K in (2.2, 1.0, 0.5):
        x, p = reynolds_fd(L, U, mu, K * h_out, h_out)
        W = trapz(p, x)
        Wc = load_closed_form(L, U, mu, K * h_out, h_out)
        print(f"K = {K}: peak pressure {p.max()/1e6:.3f} MPa, min {p.min()/1e6:.3f} MPa, load {W/1000:.2f} kN per m width (closed form {Wc/1000:.2f})")
        assert abs(W - Wc) <= 1e-4 * max(abs(Wc), 1.0)
        if K > 1:
            assert W > 0 and p.min() >= -1e-6
        elif K == 1:
            assert abs(W) < 1e-6 * 1e6
        else:
            assert W < 0  # diverging film: suction, which real oil cannot hold (it cavitates)
    # best taper ratio: the load coefficient W h_out^2/(mu U L^2) peaks near K = 2.2
    Ks = np.linspace(1.05, 5, 4000)
    coef = [load_closed_form(1, 1, 1, k, 1) for k in Ks]
    kbest = Ks[int(np.argmax(coef))]
    print(f"best K = {kbest:.3f}, load coefficient {max(coef):.5f}")
    assert 2.1 < kbest < 2.3
