"""Stokes' first problem: a plate suddenly set moving under still fluid. Finite differences versus the erfc solution."""
import math
import numpy as np


def exact(y, t, U, nu):
    return U * np.array([math.erfc(yy / (2 * math.sqrt(nu * t))) for yy in np.atleast_1d(y)])


def simulate(U, nu, t_end, H, n=400):
    """Explicit FTCS for u_t = nu u_yy on 0 <= y <= H, u(0) = U, u(H) = 0."""
    y = np.linspace(0, H, n + 1); dy = y[1]; dt = 0.4 * dy * dy / nu
    steps = int(math.ceil(t_end / dt)); dt = t_end / steps
    u = np.zeros(n + 1); u[0] = U
    r = nu * dt / dy ** 2
    for _ in range(steps):
        u[1:-1] = u[1:-1] + r * (u[2:] - 2 * u[1:-1] + u[:-2])
    return y, u


def thickness99(y, u, U):
    """Depth where the velocity has fallen to 1 % of the plate speed (linear interpolation)."""
    i = np.argmax(u < 0.01 * U)
    return y[i - 1] + (0.01 * U - u[i - 1]) * (y[i] - y[i - 1]) / (u[i] - u[i - 1])


if __name__ == "__main__":
    U, nu = 0.5, 1.0e-6                     # water above a plate jerked to 0.5 m/s
    deltas = []
    for t in (2.5, 10.0, 40.0):
        y, u = simulate(U, nu, t, H=0.06)
        err = np.max(np.abs(u - exact(y, t, U, nu)))
        d = thickness99(y, u, U); deltas.append(d)
        print(f"t = {t:5.1f} s: max error vs erfc {err:.2e} m/s, 99 % layer {d*1000:.3f} mm, 3.643 sqrt(nu t) = {3.643*math.sqrt(nu*t)*1000:.3f} mm")
        assert err < 2e-3
    print(f"ratios for 4x the time: {deltas[1]/deltas[0]:.4f}, {deltas[2]/deltas[1]:.4f}")
    assert all(abs(deltas[i + 1] / deltas[i] - 2) < 0.01 for i in range(2))    # the layer grows as sqrt(nu t)
    # the exact 1 % point: erfc(eta) = 0.01 at eta = 1.8214, so delta = 2 * 1.8214 sqrt(nu t)
    lo, hi = 0.0, 5.0
    for _ in range(100):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if math.erfc(m) > 0.01 else (lo, m)
    print(f"erfc(eta) = 0.01 at eta = {lo:.4f}: delta99 = {2*lo:.4f} sqrt(nu t)")
    mu = 1000 * nu                          # dynamic viscosity of water, Pa s
    print(f"wall shear at t = 10 s: mu U / sqrt(pi nu t) = {mu*U/math.sqrt(math.pi*nu*10):.4f} Pa")
