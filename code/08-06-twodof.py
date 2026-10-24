"""Two-DOF systems: modes of coupled pendulums, M-orthogonality and beats."""
import math
import numpy as np


def modes(M, K):
    """Solve (K - w^2 M) phi = 0 via the symmetric form L^-1 K L^-T (M = L L^T); mass-normalised modes."""
    L = np.linalg.cholesky(M); Li = np.linalg.inv(L)
    lam, V = np.linalg.eigh(Li @ K @ Li.T)
    return np.sqrt(lam), Li.T @ V


if __name__ == "__main__":
    g, l, m, ks = 9.81, 1.0, 1.0, 0.5             # two 1 m pendulums joined at the bobs by a soft spring
    M = np.diag([m * l**2, m * l**2])
    K = np.array([[m * g * l + ks * l**2, -ks * l**2], [-ks * l**2, m * g * l + ks * l**2]])
    w, Phi = modes(M, K)
    print(f"mode 1: {w[0]:.4f} rad/s, shape {Phi[:,0]/Phi[0,0]}; mode 2: {w[1]:.4f} rad/s, shape {Phi[:,1]/Phi[0,1]}")
    assert abs(w[0] - math.sqrt(g / l)) < 1e-12 and abs(w[1] - math.sqrt(g / l + 2 * ks / m)) < 1e-12
    print("Phi^T M Phi =\n", np.round(Phi.T @ M @ Phi, 12), "\nPhi^T K Phi diag =", np.round(np.diag(Phi.T @ K @ Phi), 6))
    assert np.allclose(Phi.T @ M @ Phi, np.eye(2), atol=1e-12)
    assert np.allclose(Phi.T @ K @ Phi, np.diag(w**2), atol=1e-10)
    # beats: start pendulum 1 at 0.1 rad, pendulum 2 at rest; exact modal solution
    q0 = Phi.T @ M @ np.array([0.1, 0.0])
    t = np.linspace(0, 60, 60001)
    th = Phi @ (q0[:, None] * np.cos(np.outer(w, t)))
    Tb = 2 * math.pi / (w[1] - w[0])
    i = np.argmin(np.abs(t - Tb / 2))
    print(f"beat period {Tb:.2f} s: at t = {t[i]:.2f} s pendulum 1 swings with envelope {np.max(np.abs(th[0, i-1500:i+1500])):.4f} rad, pendulum 2 {np.max(np.abs(th[1, i-1500:i+1500])):.4f} rad")
    assert np.max(np.abs(th[1, i-1500:i+1500])) > 0.099
    # an unequal 2-DOF chain: wall - k1 - m1 - k2 - m2
    M2 = np.diag([2.0, 1.0]); K2 = np.array([[3000.0, -1000.0], [-1000.0, 1000.0]])
    w2, P2 = modes(M2, K2)
    print(f"chain: {w2[0]:.4f} and {w2[1]:.4f} rad/s, shapes {P2[:,0]/P2[0,0]} and {P2[:,1]/P2[0,1]}")
    assert abs(P2[:, 0] @ M2 @ P2[:, 1]) < 1e-12 and abs(P2[:, 0] @ P2[:, 1]) > 1e-3   # M-orthogonal, not plainly orthogonal
    print(f"plain dot product of the modes {P2[:,0] @ P2[:,1]:.4f}; with M in between {P2[:,0] @ M2 @ P2[:,1]:.1e}")
