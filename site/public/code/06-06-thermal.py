"""Thermal stress: a fully constrained bar, a bar with an expansion gap, and a continuous welded rail."""
import math


def constrained_stress(E, alpha, dT):
    """Free thermal strain alpha dT is prevented completely: mechanical strain -alpha dT, stress -E alpha dT."""
    return -E * alpha * dT


def gap_stress(E, alpha, dT, L, gap):
    """The bar expands freely until it closes the gap, then is constrained. Compression only if alpha dT L > gap."""
    free = alpha * dT * L
    return 0.0 if free <= gap else -E * (free - gap) / L


if __name__ == "__main__":
    E, alpha = 210e3, 11.5e-6                       # MPa, 1/K for rail steel
    A = 7686.0                                      # mm^2, a UIC 60 rail
    T_neutral = 25.0                                # rail laid stress-free at 25 C
    for T in (55.0, -20.0):
        s = constrained_stress(E, alpha, T - T_neutral)
        print(f"rail at {T:5.1f} C: stress {s:8.2f} MPa, axial force {s * A / 1e3:8.1f} kN ({'compression' if s < 0 else 'tension'})")
    assert abs(constrained_stress(E, alpha, 30) + E * alpha * 30) < 1e-12
    # the strain gauge on a constrained rail reads zero: total strain = thermal + mechanical = alpha dT + s / E = 0
    s = constrained_stress(E, alpha, 30)
    assert abs(alpha * 30 + s / E) < 1e-15
    # old jointed track: 25 m rails with 5 mm gaps, laid at 10 C
    for T in (30.0, 45.0):
        s = gap_stress(E, alpha, T - 10.0, 25000.0, 5.0)
        print(f"jointed 25 m rail with a 5 mm gap at {T:.0f} C: free expansion {alpha * (T - 10) * 25000:.3f} mm, stress {s:.2f} MPa")
    # gap closes at dT = gap / (alpha L)
    dT_close = 5.0 / (alpha * 25000.0)
    print(f"the gap closes {dT_close:.2f} K above the laying temperature")
    assert gap_stress(E, alpha, dT_close - 1e-9, 25000, 5) == 0 and gap_stress(E, alpha, dT_close + 1, 25000, 5) < 0
    # aluminium expands twice as much as steel but is three times softer: the product E alpha sets the stress
    print(f"E alpha: steel {E * alpha:.4f} MPa/K, aluminium {70e3 * 23e-6:.4f} MPa/K")
