"""Fracture mechanics: Griffith's energy balance, stress intensity, critical crack size and leak-before-break."""
import math
import numpy as np


def K(sigma, a, Y=1.0):
    return Y * sigma * math.sqrt(math.pi * a)


def a_crit(KIC, sigma, Y=1.0):
    return (KIC / (Y * sigma))**2 / math.pi


def griffith_energy(a, sigma, E, gamma):
    """Energy per unit thickness of a through crack of length 2a in a large plate (plane stress)."""
    return -math.pi * sigma**2 * a**2 / E + 4 * a * gamma


if __name__ == "__main__":
    # glass: Griffith balance found by scanning the energy curve
    E, gamma, sigma = 70e9, 1.0, 50e6
    a = np.linspace(1e-9, 1e-4, 200001); U = -math.pi * sigma**2 * a**2 / E + 4 * a * gamma
    a_num = a[np.argmax(U)]; a_formula = 2 * E * gamma / (math.pi * sigma**2)
    print(f"glass at 50 MPa: energy peaks at half-length {a_num*1e6:.2f} um (formula 2 E gamma / (pi sigma^2) = {a_formula*1e6:.2f} um)")
    assert abs(a_num - a_formula) < 1e-9
    print(f"  equivalent K_IC = sqrt(2 E gamma) = {math.sqrt(2*E*gamma)/1e6:.3f} MPa sqrt(m)")
    assert abs(K(sigma, a_formula) - math.sqrt(2 * E * gamma)) < 1e-6
    # steel plate with an edge crack
    for KIC, name in ((50e6, "structural steel"), (150e6, "tough pressure-vessel steel"), (25e6, "7075-T6 aluminium")):
        ac = a_crit(KIC, 300e6, Y=1.12)
        print(f"{name} (K_IC {KIC/1e6:.0f}) at 300 MPa, edge crack: critical depth {ac*1e3:.2f} mm")
    assert abs(K(300e6, a_crit(50e6, 300e6, 1.12), 1.12) - 50e6) < 1e-3
    # leak-before-break: a crack through the wall t must still be subcritical (2a = t)
    t, KIC, sy = 0.012, 150e6, 400e6
    sigma_max = KIC / math.sqrt(math.pi * t / 2)
    print(f"vessel wall 12 mm, K_IC 150: leaks before it breaks while hoop stress < {sigma_max/1e6:.0f} MPa (yield {sy/1e6:.0f})")
    assert sigma_max > sy
