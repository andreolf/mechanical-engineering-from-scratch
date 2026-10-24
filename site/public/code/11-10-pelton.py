"""Euler's turbine equation applied to a Pelton wheel: power against bucket speed, for an Alpine high-head plant."""
import math
import numpy as np

RHO, G = 1000.0, 9.81


def euler_torque(mdot, r1, cu1, r2, cu2):
    """Torque the fluid gives the runner: mdot (r1 cu1 - r2 cu2)."""
    return mdot * (r1 * cu1 - r2 * cu2)


def pelton_power(Q, V, u, beta_deg=165.0, k=1.0):
    """Power (W) from a jet of speed V on buckets moving at u; the bucket turns the relative flow by beta,
    k is the relative-speed loss factor across the bucket."""
    w1 = V - u                                     # relative speed into the bucket
    cu2 = u - k * w1 * math.cos(math.radians(180 - beta_deg))     # absolute tangential speed leaving
    return RHO * Q * u * (V - cu2)                 # Euler with r1 = r2: P = mdot u (cu1 - cu2)


if __name__ == "__main__":
    H, Q, Cv = 800.0, 2.0, 0.98                    # assumed plant: 800 m net head, 2 m^3/s
    V = Cv * math.sqrt(2 * G * H)
    print(f"jet speed {V:.2f} m/s; hydraulic power rho g Q H = {RHO*G*Q*H/1e6:.2f} MW")
    us = np.linspace(0, V, 2001)
    P = np.array([pelton_power(Q, V, u) for u in us])
    i = P.argmax()
    print(f"best bucket speed {us[i]:.2f} m/s = {us[i]/V:.3f} V; power {P[i]/1e6:.3f} MW; efficiency {P[i]/(RHO*G*Q*H):.4f}")
    assert abs(us[i] / V - 0.5) < 1e-3                 # ideal: optimum at u = V/2
    # ideal bucket turning the flow by 180 degrees with no losses captures all the jet's kinetic energy
    Pid = pelton_power(Q, V, V / 2, beta_deg=180.0)
    assert abs(Pid - 0.5 * RHO * Q * V ** 2) < 1e-6
    print(f"180 deg ideal bucket at V/2: {Pid/1e6:.3f} MW = jet kinetic power {0.5*RHO*Q*V**2/1e6:.3f} MW")
    # the same result from Euler's equation as a torque, for a 2.4 m pitch diameter runner
    r = 1.2; u = V / 2; w1 = V - u; cu2 = u - w1 * math.cos(math.radians(15))
    T = euler_torque(RHO * Q, r, V, r, cu2); n = u / r * 60 / (2 * math.pi)
    print(f"runner 2.4 m pitch diameter: {n:.0f} rpm, torque {T/1e3:.1f} kN m, power {T*u/r/1e6:.3f} MW")
    assert abs(T * u / r - pelton_power(Q, V, u)) < 1e-3
