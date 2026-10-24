"""Modal analysis of a 5-storey shear building: modes with scipy.linalg.eigh, then modal superposition
checked against direct integration of all five coupled equations."""
import math
import numpy as np
from scipy.linalg import eigh

n, m, k, zeta = 5, 20e3, 40e6, 0.02          # storeys, floor mass (kg), storey stiffness (N/m), modal damping
M = np.eye(n) * m
K = np.zeros((n, n))
for i in range(n):
    K[i, i] += k
    if i + 1 < n: K[i, i] += k; K[i, i + 1] = K[i + 1, i] = -k
w2, Phi = eigh(K, M)                       # mass-normalised: Phi^T M Phi = I
w = np.sqrt(w2)
ag = lambda t: 2.0 * math.sin(2 * math.pi * 1.5 * t) * (t < 4.0)   # ground acceleration pulse, m/s^2


def rk4(f, s, dt, steps):
    out = [s.copy()]
    for i in range(steps):
        t = i * dt
        k1 = f(t, s); k2 = f(t + dt/2, s + dt/2*k1); k3 = f(t + dt/2, s + dt/2*k2); k4 = f(t + dt, s + dt*k3)
        s = s + dt/6*(k1 + 2*k2 + 2*k3 + k4); out.append(s.copy())
    return np.array(out)


if __name__ == "__main__":
    print("natural frequencies (Hz):", np.round(w / (2 * math.pi), 4))
    print("mode 1 shape (top = 1):", np.round(Phi[:, 0] / Phi[-1, 0], 4))
    assert np.allclose(Phi.T @ M @ Phi, np.eye(n), atol=1e-12)
    # effective modal mass: how much of the total mass each mode moves in a ground shake
    L = Phi.T @ M @ np.ones(n); meff = L**2
    print("effective modal mass (% of total):", np.round(meff / (n * m) * 100, 2))
    dt, T = 0.002, 10.0; steps = int(T / dt)
    # direct: M x'' + C x' + K x = -M 1 ag, with C built to give 2 % in every mode
    C = M @ Phi @ np.diag(2 * zeta * w) @ Phi.T @ M
    Mi = np.linalg.inv(M)
    f = lambda t, s: np.r_[s[n:], Mi @ (-M @ np.ones(n) * ag(t) - C @ s[n:] - K @ s[:n])]
    X = rk4(f, np.zeros(2 * n), dt, steps)[:, :n]
    # modal: five independent oscillators q'' + 2 zeta w q' + w^2 q = -L ag
    def g(t, s):
        q, qd = s[:n], s[n:]
        return np.r_[qd, -L * ag(t) - 2 * zeta * w * qd - w2 * q]
    Q = rk4(g, np.zeros(2 * n), dt, steps)[:, :n]
    Xm = Q @ Phi.T
    err = np.max(np.abs(Xm - X)) / np.max(np.abs(X))
    print(f"peak roof displacement {np.max(np.abs(X[:, -1]))*1000:.3f} mm; modal vs direct max difference {err:.1e} (relative)")
    assert err < 1e-9
    X1 = np.outer(Q[:, 0], Phi[:, 0])
    print(f"mode 1 alone gives a roof peak of {np.max(np.abs(X1[:, -1]))*1000:.3f} mm")
    base_shear = np.max(np.abs(k * X[:, 0]))
    print(f"peak base shear {base_shear/1e3:.1f} kN")
