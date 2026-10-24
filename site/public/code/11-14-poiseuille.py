"""Hagen-Poiseuille flow in a round pipe: the parabolic profile, flow rate, and a finite-difference check in r."""
import math
import numpy as np


def profile(r, R, dpdx, mu):
    """u(r) = (-dp/dx) (R^2 - r^2) / (4 mu)."""
    return -dpdx * (R * R - r * r) / (4 * mu)


def flow_rate(R, dp, L, mu):
    return math.pi * R ** 4 * dp / (8 * mu * L)


def fd_profile(R, dpdx, mu, n=201):
    """Solve (1/r) d/dr (r du/dr) = (1/mu) dp/dx with du/dr = 0 at r = 0 and u(R) = 0, finite volumes on a radial grid."""
    r = np.linspace(0, R, n); dr = r[1] - r[0]
    A = np.zeros((n, n)); b = np.full(n, dpdx / mu)
    A[0, 0], A[0, 1] = -4 / dr ** 2, 4 / dr ** 2                 # axis: limit r -> 0 gives 2 u''
    for i in range(1, n - 1):
        rp, rm = r[i] + dr / 2, r[i] - dr / 2
        A[i, i - 1], A[i, i], A[i, i + 1] = rm / (r[i] * dr * dr), -(rp + rm) / (r[i] * dr * dr), rp / (r[i] * dr * dr)
    A[-1, -1] = 1; b[-1] = 0
    return r, np.linalg.solve(A, b)


if __name__ == "__main__":
    # olive oil (mu 0.084 Pa s, rho 910) in a 20 mm pipe, 5 m long, 2 kPa pressure difference
    R, L, dp, mu, rho = 0.010, 5.0, 2000.0, 0.084, 910.0
    Q = flow_rate(R, dp, L, mu)
    umax = profile(0, R, -dp / L, mu); umean = Q / (math.pi * R * R)
    print(f"Q = {Q*1e6:.2f} mL/s; centre speed {umax:.4f} m/s; mean {umean:.4f} m/s; ratio {umean/umax:.4f}")
    assert abs(umean / umax - 0.5) < 1e-12
    Re = rho * umean * 2 * R / mu
    print(f"Reynolds number {Re:.1f}: laminar (below about 2300), so the formula applies")
    wall_tau = dp * R / (2 * L)                                     # force balance on the fluid cylinder
    print(f"wall shear stress {wall_tau:.3f} Pa = R dp / (2L)")
    r, u = fd_profile(R, -dp / L, mu)
    assert np.max(np.abs(u - profile(r, R, -dp / L, mu))) < 1e-6 * umax
    Q_fd = float(np.sum((2 * np.pi * r[1:] * u[1:] + 2 * np.pi * r[:-1] * u[:-1]) / 2 * np.diff(r)))
    print(f"finite differences: centre {u[0]:.4f} m/s, Q {Q_fd*1e6:.2f} mL/s")
    print(f"halving the radius cuts Q by a factor of {flow_rate(R, dp, L, mu)/flow_rate(R/2, dp, L, mu):.0f}")
