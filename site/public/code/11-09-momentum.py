"""Control-volume momentum: force of a jet on plates and vanes, and the anchor force on a pipe bend."""
import math
import numpy as np

RHO = 998.0


def jet_on_vane(V, A, theta_deg, u_vane=0.0):
    """Force (N) on a vane turning a free jet by theta, vane moving away at u_vane. Returns (Fx, Fy) exerted on the vane."""
    Vr = V - u_vane
    mdot = RHO * A * Vr                                   # mass flow meeting a single moving vane
    th = math.radians(theta_deg)
    return mdot * Vr * (1 - math.cos(th)), -mdot * Vr * math.sin(th)     # jet leaves along (cos, sin) relative to the vane


def bend_force(Q, D1, D2, p1, theta_deg, p2=None):
    """Force (N) the fluid exerts on a horizontal reducing bend; inlet along +x, outlet turned by theta. p in Pa gauge."""
    A1, A2 = math.pi * D1 ** 2 / 4, math.pi * D2 ** 2 / 4
    V1, V2 = Q / A1, Q / A2
    if p2 is None:
        p2 = p1 + 0.5 * RHO * (V1 ** 2 - V2 ** 2)         # Bernoulli across the bend (losses neglected)
    th = math.radians(theta_deg)
    m = RHO * Q
    # momentum balance on the fluid: F_wall_on_fluid + p1 A1 n1 + p2 A2 n2 = m (V2 - V1)
    e1, e2 = np.array([1.0, 0.0]), np.array([math.cos(th), math.sin(th)])
    F_on_fluid = m * (V2 * e2 - V1 * e1) - p1 * A1 * e1 + p2 * A2 * e2
    return -F_on_fluid, V1, V2, p2


if __name__ == "__main__":
    V, d = 20.0, 0.03
    A = math.pi * d * d / 4
    print(f"jet 30 mm at 20 m/s: mass flow {RHO*A*V:.3f} kg/s")
    for th in (90, 135, 180):
        Fx, _ = jet_on_vane(V, A, th)
        print(f"  turned by {th} deg: Fx = {Fx:.1f} N")
    assert abs(jet_on_vane(V, A, 90)[0] - RHO * A * V * V) < 1e-9          # flat plate: F = mdot V
    assert abs(jet_on_vane(V, A, 180)[0] - 2 * RHO * A * V * V) < 1e-9     # full reversal doubles it
    F, V1, V2, p2 = bend_force(0.2, 0.30, 0.20, 150e3, 90)
    print(f"90 deg reducing bend, 200 L/s, 300 -> 200 mm, 150 kPa: V1 {V1:.3f}, V2 {V2:.3f} m/s, p2 {p2/1000:.2f} kPa")
    print(f"  force on the bend: Fx = {F[0]:.0f} N, Fy = {F[1]:.0f} N, magnitude {np.hypot(*F):.0f} N")
    # with no flow only pressure acts: a 90 deg bend with equal ends feels p A along +x and along -y
    F0, *_ = bend_force(0.0, 0.3, 0.3, 150e3, 90)
    A1 = math.pi * 0.09 / 4
    assert np.allclose(F0, [150e3 * A1, -150e3 * A1])
