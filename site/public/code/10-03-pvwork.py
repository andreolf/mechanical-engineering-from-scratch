"""Boundary work W = integral of p dV for isobaric, isothermal and polytropic processes, by numerical integration against the closed forms."""
import math
import numpy as np


def work_numeric(p_of_V, V1, V2, n=200001):
    V = np.linspace(V1, V2, n); p = p_of_V(V)
    return float(np.sum((p[1:] + p[:-1]) / 2 * np.diff(V)))


if __name__ == "__main__":
    # 0.01 m^3 of air at 100 kPa and 300 K, compressed to 2 L
    p1, V1, T1, R = 100e3, 0.01, 300.0, 287.0
    m = p1 * V1 / (R * T1)
    print(f"mass of air {m*1000:.3f} g")
    V2 = 0.002
    W_iso_b = work_numeric(lambda V: np.full_like(V, p1), V1, V2)
    print(f"isobaric 10 -> 2 L at 100 kPa: W = {W_iso_b:.1f} J (p dV = {p1*(V2-V1):.1f})")
    W_iso_T = work_numeric(lambda V: p1 * V1 / V, V1, V2)
    exact = p1 * V1 * math.log(V2 / V1)
    print(f"isothermal: W = {W_iso_T:.3f} J, nRT ln(V2/V1) = {exact:.3f} J")
    assert abs(W_iso_T - exact) < 1e-3
    for n in (1.3, 1.4):
        W = work_numeric(lambda V: p1 * (V1 / V) ** n, V1, V2)
        p2 = p1 * (V1 / V2) ** n
        closed = (p2 * V2 - p1 * V1) / (1 - n)
        print(f"polytropic n = {n}: W = {W:.3f} J (closed form {closed:.3f}); p2 = {p2/1e3:.1f} kPa, T2 = {p2*V2/(m*R):.1f} K")
        assert abs(W - closed) < 1e-3 * abs(closed)
    # work is path dependent: same end states, different paths
    p2 = p1 * (V1 / V2) ** 1.4
    W_a = p1 * (V2 - V1)                  # compress at p1, then heat at constant volume to p2
    W_b = p2 * (V2 - V1)                  # heat at V1 up to p2, then compress at p2
    print(f"same end states, two rectangular paths: {W_a:.0f} J and {W_b:.0f} J")
