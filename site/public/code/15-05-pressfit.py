"""Press fit of a hub on a solid shaft: contact pressure from Lame's thick-cylinder solution, checked against a finite-difference solution of the radial displacement equation, then torque capacity and a key for comparison."""
import math
import numpy as np


def lame_pressure(delta_r, R, ro, Eo, nuo, Ei, nui, ri=0.0):
    """Interface pressure (MPa) for radial interference delta_r (mm) between a hub (outer radius ro) and a shaft (bore ri)."""
    hub = ((ro**2 + R**2) / (ro**2 - R**2) + nuo) / Eo
    shaft = ((R**2 + ri**2) / (R**2 - ri**2) - nui) / Ei
    return delta_r / (R * (hub + shaft))


def fd_radial_displacement(a, b, E, nu, pa, pb, n=4001):
    """Plane stress annulus a <= r <= b (a may be 0) with pressures pa inside and pb outside.
    Solves u'' + u'/r - u/r^2 = 0 by central differences; returns u at r = a and r = b."""
    if a == 0:
        a_eff = b * 1e-6  # tiny hole replaced by the symmetry condition u(0) = 0
    else:
        a_eff = a
    r = np.linspace(a_eff, b, n)
    h = r[1] - r[0]
    A = np.zeros((n, n)); rhs = np.zeros(n)
    for k in range(1, n - 1):
        A[k, k - 1] = 1 / h**2 - 1 / (2 * h * r[k])
        A[k, k] = -2 / h**2 - 1 / r[k] ** 2
        A[k, k + 1] = 1 / h**2 + 1 / (2 * h * r[k])
    c = E / (1 - nu**2)
    # sigma_r = c (u' + nu u / r), second-order one-sided differences at the ends
    def bc(row, k, sign, p):
        if sign > 0:
            A[row, k], A[row, k + 1], A[row, k + 2] = -1.5 / h, 2 / h, -0.5 / h
        else:
            A[row, k], A[row, k - 1], A[row, k - 2] = 1.5 / h, -2 / h, 0.5 / h
        A[row, k] += nu / r[k]
        rhs[row] = -p / c
    if a == 0:
        A[0, 0] = 1.0; rhs[0] = 0.0
    else:
        bc(0, 0, +1, pa)
    bc(n - 1, n - 1, -1, pb)
    u = np.linalg.solve(A, rhs)
    return u[0], u[-1]


def fd_pressure(delta_r, R, ro, E, nu):
    """Unit pressure gives the hub bore growth and shaft shrinkage; the response is linear, so scale to close the gap."""
    hub_in, _ = fd_radial_displacement(R, ro, E, nu, 1.0, 0.0)
    _, shaft_out = fd_radial_displacement(0.0, R, E, nu, 0.0, 1.0)
    return delta_r / (hub_in - shaft_out)


if __name__ == "__main__":
    # scooter gear hub: steel, 20 mm shaft, 60 mm hub, 25 mm long, 20 um diametral interference
    E, nu, R, ro, L, mu = 207e3, 0.29, 10.0, 30.0, 25.0, 0.15
    delta_r = 0.010
    p = lame_pressure(delta_r, R, ro, E, nu, E, nu)
    closed = E * delta_r * (ro**2 - R**2) / (2 * R * ro**2)  # same material, solid shaft
    pf = fd_pressure(delta_r, R, ro, E, nu)
    print(f"contact pressure: Lame {p:.3f} MPa, same-material formula {closed:.3f}, finite differences {pf:.3f}")
    assert abs(p - closed) < 1e-9 and abs(pf / p - 1) < 1e-4
    T = 2 * math.pi * R**2 * L * mu * p
    F = 2 * math.pi * R * L * mu * p
    hoop = p * (ro**2 + R**2) / (ro**2 - R**2)
    print(f"torque capacity {T/1000:.1f} N m, push-out force {F/1000:.2f} kN, hub bore hoop stress {hoop:.1f} MPa")
    assert abs(T / 1000 - 216.8) < 0.1
    # a 6 x 6 mm parallel key, 25 mm long, for 100 N m
    Tk, w, hk = 100e3, 6.0, 6.0
    tau = 2 * Tk / (2 * R * w * L)
    crush = 4 * Tk / (2 * R * hk * L)
    print(f"key: shear {tau:.1f} MPa, bearing (crushing) {crush:.1f} MPa")
    assert abs(crush - 2 * tau) < 1e-9
