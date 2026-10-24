"""Hydraulic jump: conjugate depths from momentum, and the energy it destroys."""
import math

G = 9.81


def momentum_function(y, q):
    """Force plus momentum flux per unit width, divided by rho g: M = y^2/2 + q^2/(g y)."""
    return y * y / 2 + q * q / (G * y)


def conjugate_bisect(y1, q):
    """The other depth with the same M, found numerically on the opposite branch of the curve."""
    yc = (q * q / G) ** (1 / 3)
    M1 = momentum_function(y1, q)
    lo, hi = (yc, 50.0) if y1 < yc else (1e-6, yc)
    for _ in range(200):
        m = (lo + hi) / 2
        if (momentum_function(m, q) - M1) * (momentum_function(lo, q) - M1) <= 0: hi = m
        else: lo = m
    return (lo + hi) / 2


def belanger(y1, Fr1):
    return y1 * (math.sqrt(1 + 8 * Fr1 * Fr1) - 1) / 2


def energy(y, q):
    return y + q * q / (2 * G * y * y)


if __name__ == "__main__":
    # water leaves a spillway apron 0.25 m deep carrying q = 2 m^2/s
    y1, q = 0.25, 2.0
    V1 = q / y1; Fr1 = V1 / math.sqrt(G * y1)
    y2 = conjugate_bisect(y1, q)
    print(f"V1 = {V1:.3f} m/s, Fr1 = {Fr1:.4f}; conjugate depth {y2:.5f} m (Belanger {belanger(y1, Fr1):.5f})")
    assert abs(y2 - belanger(y1, Fr1)) < 1e-9
    dE = energy(y1, q) - energy(y2, q)
    print(f"E1 = {energy(y1, q):.4f} m, E2 = {energy(y2, q):.4f} m, loss {dE:.4f} m = (y2-y1)^3/(4 y1 y2) = {(y2-y1)**3/(4*y1*y2):.4f}")
    print(f"power dissipated per metre width: {1000*G*q*dE/1000:.2f} kW; Fr2 = {q/y2/math.sqrt(G*y2):.4f}")
    assert dE > 0 and abs(dE - (y2 - y1) ** 3 / (4 * y1 * y2)) < 1e-9
    # a 'jump' from deep to shallow would need energy to be created: forbidden
    y_back = conjugate_bisect(y2, q)
    assert abs(y_back - y1) < 1e-9 and energy(y2, q) - energy(y_back, q) < 0
    for F in (1.5, 3, 6, 10):
        r = (math.sqrt(1 + 8 * F * F) - 1) / 2
        print(f"Fr1 = {F:4.1f}: y2/y1 = {r:.3f}, fraction of E1 lost {((r-1)**3/(4*r)) / (1 + F*F/2):.3f}")
