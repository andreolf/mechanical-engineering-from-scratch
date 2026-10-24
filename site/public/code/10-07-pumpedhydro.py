"""Pumped-storage hydropower: stored energy rho g h V, penstock friction, and the round-trip efficiency for an Alpine plant (round, clearly assumed numbers)."""
import math

RHO, G = 1000.0, 9.81


def stored_energy(V, h):
    """Gravitational energy (J) of volume V (m^3) lifted through head h (m)."""
    return RHO * G * h * V


def head_loss(Q, L, D, f=0.012):
    """Darcy-Weisbach friction head (m) for flow Q (m^3/s) in a penstock of length L and diameter D."""
    V = Q / (math.pi * D * D / 4)
    return f * L / D * V * V / (2 * G)


if __name__ == "__main__":
    # assumed plant, loosely modelled on a large Alpine scheme: 25 million m^3, 300 m mean head,
    # 900 MW, two penstocks 1.4 km long and 7 m in diameter
    V, h, P = 25e6, 300.0, 900e6
    E = stored_energy(V, h)
    print(f"stored: {E:.3e} J = {E/3.6e12:.2f} GWh")
    assert abs(stored_energy(2 * V, h) - 2 * E) < 1e-3 and abs(stored_energy(V, 2 * h) - 2 * E) < 1e-3
    Q = P / (RHO * G * h * 0.90)                 # flow at full turbine power (turbine x generator 0.90)
    hf = head_loss(Q / 2, 1400, 7.0)               # same loss used for pumping (assumes similar flow)
    print(f"flow at 900 MW: {Q:.0f} m^3/s; friction head per penstock {hf:.2f} m ({hf/h*100:.2f} % of the head)")
    eta_t = 0.92 * 0.98 * (1 - hf / h)          # turbine, generator, penstock
    eta_p = 0.91 * 0.98 / (1 + hf / h)          # pump, motor, penstock (extra head to overcome)
    rt = eta_t * eta_p
    print(f"generating efficiency {eta_t:.3f}, pumping efficiency {eta_p:.3f}, round trip {rt:.3f}")
    print(f"electricity out {E*eta_t/3.6e12:.2f} GWh for {E/eta_p/3.6e12:.2f} GWh in")
    print(f"hours at full power: {E*eta_t/P/3600:.1f} h")
    print(f"1 kWh needs {3.6e6/(RHO*G*h):.2f} m^3 of water falling {h:.0f} m")
