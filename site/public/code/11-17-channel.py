"""Open-channel flow: specific energy, critical depth and the Froude number in a rectangular channel."""
import math
import numpy as np

G = 9.81


def specific_energy(y, q):
    return y + q * q / (2 * G * y * y)


def critical_depth(q):
    return (q * q / G) ** (1 / 3)


def alternate_depths(E, q):
    """The subcritical and supercritical depths with the same specific energy (bisection on each branch)."""
    yc = critical_depth(q)
    def solve(lo, hi):
        for _ in range(200):
            m = (lo + hi) / 2
            if (specific_energy(m, q) - E) * (specific_energy(lo, q) - E) <= 0: hi = m
            else: lo = m
        return (lo + hi) / 2
    return solve(yc, 10 * E), solve(1e-6, yc)


if __name__ == "__main__":
    # a canal 3 m wide carrying 6 m^3/s: q = 2 m^2/s per metre width
    q = 6.0 / 3.0
    yc = critical_depth(q)
    ys = np.linspace(0.2, 3, 280001)
    E = specific_energy(ys, q)
    y_min = ys[E.argmin()]
    print(f"critical depth {yc:.4f} m; numerical minimum of E at {y_min:.4f} m; E_min = {E.min():.4f} m (1.5 yc = {1.5*yc:.4f})")
    Fr = lambda y: q / (y * math.sqrt(G * y))
    print(f"Froude number at the minimum: {Fr(y_min):.4f}")
    assert abs(y_min - yc) < 1e-4 and abs(Fr(yc) - 1) < 1e-12              # minimum specific energy at Fr = 1
    y1 = 1.5
    Es = specific_energy(y1, q)
    sub, sup = alternate_depths(Es, q)
    print(f"flow 1.5 m deep: V = {q/y1:.3f} m/s, Fr = {Fr(y1):.4f} (subcritical), E = {Es:.4f} m")
    print(f"  alternate supercritical depth {sup:.4f} m, V = {q/sup:.3f} m/s, Fr = {Fr(sup):.4f}")
    # a smooth hump on the bed lowers the available energy: the largest hump before the flow chokes
    print(f"largest bed hump before choking: {Es - 1.5*yc:.4f} m")
