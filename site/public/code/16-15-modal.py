"""Modal analysis with beam elements: consistent mass matrix, the generalised eigenproblem K phi = w^2 M phi solved by Cholesky reduction; cantilever frequencies converge to Euler-Bernoulli theory; first modes of a footbridge."""
import math
import numpy as np


def k_beam(EI, L):
    return EI / L**3 * np.array([[12, 6 * L, -12, 6 * L], [6 * L, 4 * L**2, -6 * L, 2 * L**2], [-12, -6 * L, 12, -6 * L], [6 * L, 2 * L**2, -6 * L, 4 * L**2]])


def m_beam(mbar, L):
    """Consistent mass for mass per length mbar: integral of mbar N N^T over the element."""
    return mbar * L / 420 * np.array([[156, 22 * L, 54, -13 * L], [22 * L, 4 * L**2, 13 * L, -3 * L**2], [54, 13 * L, 156, -22 * L], [-13 * L, -3 * L**2, -22 * L, 4 * L**2]])


def m_beam_integrated(mbar, L):
    x, w = np.polynomial.legendre.leggauss(4); xi = (x + 1) / 2; w = w / 2
    M = np.zeros((4, 4))
    for a, wa in zip(xi, w):
        N = np.array([1 - 3 * a**2 + 2 * a**3, L * (a - 2 * a**2 + a**3), 3 * a**2 - 2 * a**3, L * (a**3 - a**2)])
        M += mbar * np.outer(N, N) * wa * L
    return M


def gen_eig(K, M):
    """K phi = lam M phi with M symmetric positive definite: M = L L^T, then a standard symmetric problem."""
    Lc = np.linalg.cholesky(M); Li = np.linalg.inv(Lc)
    lam, y = np.linalg.eigh(Li @ K @ Li.T)
    return lam, Li.T @ y


def beam_modes(span, ne, EI, mbar, support):
    h = span / ne; n = 2 * (ne + 1); K = np.zeros((n, n)); M = np.zeros((n, n))
    for e in range(ne):
        d = np.arange(2 * e, 2 * e + 4); K[np.ix_(d, d)] += k_beam(EI, h); M[np.ix_(d, d)] += m_beam(mbar, h)
    fixed = [0, 1] if support == "cantilever" else [0, n - 2]
    free = [i for i in range(n) if i not in fixed]
    lam, phi = gen_eig(K[np.ix_(free, free)], M[np.ix_(free, free)])
    return np.sqrt(lam) / (2 * math.pi), phi, free


BETA_L = [1.875104069, 4.694091133, 7.854757438, 10.99554073]     # cantilever roots of cos(bL) cosh(bL) = -1


if __name__ == "__main__":
    assert np.allclose(m_beam_integrated(3.0, 1.7), m_beam(3.0, 1.7))
    # cantilever: a 2 m steel bar, 40 x 40 mm solid
    E, b = 210e9, 0.04; EI = E * b**4 / 12; mbar = 7850 * b * b; L = 2.0
    exact = [(bl / L) ** 2 * math.sqrt(EI / mbar) / (2 * math.pi) for bl in BETA_L]
    print("cantilever theory (Hz):", ", ".join(f"{f:.4f}" for f in exact))
    errs = []
    for ne in (1, 2, 4, 8, 16):
        f, _, _ = beam_modes(L, ne, EI, mbar, "cantilever")
        k = min(4, len(f)); e = [(f[i] - exact[i]) / exact[i] for i in range(k)]
        errs.append(e)
        print(f"{ne:2d} elements: " + ", ".join(f"{f[i]:.4f} ({100*e[i]:+.4f} %)" for i in range(k)))
        assert all(x > -1e-12 for x in e)          # consistent mass: FEM frequencies are upper bounds
    assert abs(errs[-1][0]) < 1e-6 and abs(errs[-1][3]) < 2e-4 and abs(errs[2][0]) < abs(errs[1][0])
    # footbridge: 30 m simply supported span, 1200 kg/m, EI = 210 GPa x 0.009 m^4
    span, mb, EIb = 30.0, 1200.0, 210e9 * 0.009
    f, phi, free = beam_modes(span, 10, EIb, mb, "simple")
    th = [(k * math.pi / span) ** 2 * math.sqrt(EIb / mb) / (2 * math.pi) for k in (1, 2, 3)]
    print("footbridge FEM (Hz):", ", ".join(f"{x:.4f}" for x in f[:3]), " theory:", ", ".join(f"{x:.4f}" for x in th))
    assert all(0 <= (f[i] - th[i]) / th[i] < 1e-3 for i in range(3))
    # mass-normalised modes: phi^T M phi = I
    n = 22; K = np.zeros((n, n)); M = np.zeros((n, n)); h = span / 10
    for e in range(10):
        d = np.arange(2 * e, 2 * e + 4); K[np.ix_(d, d)] += k_beam(EIb, h); M[np.ix_(d, d)] += m_beam(mb, h)
    Mf = M[np.ix_(free, free)]
    assert np.allclose(phi.T @ Mf @ phi, np.eye(len(free)), atol=1e-9)
    print(f"first vertical mode {f[0]:.3f} Hz lies in the walking range of about 1.6 to 2.4 Hz: a designer would stiffen the deck or add a tuned mass damper")
    assert 1.6 < f[0] < 2.4
