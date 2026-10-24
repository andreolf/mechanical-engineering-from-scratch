"""A mass on a string pulled through a hole: angular momentum is conserved, so it spins up."""
import math
import numpy as np


def simulate(r0, w0, rdot, t_end, dt=1e-4):
    """Polar equations with the radius pulled in at a set rate: the string force is radial, so
    the transverse equation r theta'' + 2 r' theta' = 0 is integrated with RK4."""
    def f(t, s):
        th, w = s
        r = r0 + rdot * t
        return np.array([w, -2 * rdot * w / r])
    s, t = np.array([0.0, w0]), 0.0
    n = int(round(t_end / dt))
    for _ in range(n):
        k1 = f(t, s); k2 = f(t + dt / 2, s + dt / 2 * k1); k3 = f(t + dt / 2, s + dt / 2 * k2); k4 = f(t + dt, s + dt * k3)
        s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4); t += dt
    return s, r0 + rdot * t_end


if __name__ == "__main__":
    m, r0, w0 = 0.2, 0.8, 2 * math.pi            # 200 g at 0.8 m, one turn per second
    (th, w), r1 = simulate(r0, w0, -0.15, 4.0)    # pull 0.6 m of string in over 4 s
    L0, L1 = m * r0**2 * w0, m * r1**2 * w
    print(f"radius {r0} -> {r1:.2f} m: omega {w0:.4f} -> {w:.4f} rad/s ({w / (2 * math.pi):.3f} rev/s), predicted {w0 * (r0 / r1) ** 2:.4f}")
    print(f"angular momentum {L0:.6f} -> {L1:.6f} kg m^2/s (relative change {abs(L1 / L0 - 1):.1e})")
    assert abs(L1 / L0 - 1) < 1e-9
    T0, T1 = 0.5 * m * (r0 * w0) ** 2, 0.5 * m * (r1 * w) ** 2
    print(f"kinetic energy {T0:.3f} -> {T1:.3f} J: the hand pulling the string did {T1 - T0:.3f} J of work")
    # string tension needed at the end (centripetal, ignoring the slow pull): m r w^2
    print(f"string tension: start {m * r0 * w0**2:.2f} N, end {m * r1 * w**2:.2f} N")
    # and the work done equals the integral of tension times pull-in distance
    rs = np.linspace(r1, r0, 200001)
    Wq = np.trapezoid(m * rs * (w0 * r0**2 / rs**2) ** 2, rs)
    print(f"integral of m r w^2 dr = {Wq:.3f} J")
    assert abs(Wq - (T1 - T0)) < 1e-6
