"""Isentropic efficiency of a compressor and a turbine with air as an ideal gas (constant cp)."""
import math

CP, R = 1.005, 0.287      # kJ/(kg K)
K = CP / (CP - R)


def s_change(T1, p1, T2, p2):
    """Entropy change (kJ/(kg K)) of an ideal gas."""
    return CP * math.log(T2 / T1) - R * math.log(p2 / p1)


def compressor(T1, rp, eta):
    T2s = T1 * rp ** ((K - 1) / K)
    T2 = T1 + (T2s - T1) / eta
    return T2s, T2, CP * (T2 - T1)


def turbine(T3, rp, eta):
    T4s = T3 / rp ** ((K - 1) / K)
    T4 = T3 - eta * (T3 - T4s)
    return T4s, T4, CP * (T3 - T4)


if __name__ == "__main__":
    print(f"k = {K:.4f}")
    T1, rp = 293.15, 8.0
    T2s, T2, w = compressor(T1, rp, 0.85)
    print(f"compressor 20 C, rp 8, eta 0.85: T2s = {T2s:.2f} K, T2 = {T2:.2f} K ({T2-273.15:.1f} C), work {w:.2f} kJ/kg")
    print(f"  ideal work {CP*(T2s-T1):.2f} kJ/kg; entropy generated {s_change(T1, 100, T2, 800):.5f} kJ/(kg K)")
    assert abs(s_change(T1, 100, T2s, 800)) < 1e-12              # the isentropic state really is isentropic
    assert abs(compressor(T1, rp, 1.0)[1] - T2s) < 1e-12         # eta = 1 recovers it
    for eta in (0.6, 0.7, 0.8, 0.9, 0.99):
        assert s_change(T1, 100, compressor(T1, rp, eta)[1], 800) > 0
    T4s, T4, wt = turbine(1400.0, rp, 0.90)
    print(f"turbine 1400 K, rp 8, eta 0.90: T4s = {T4s:.2f} K, T4 = {T4:.2f} K, work {wt:.2f} kJ/kg")
    assert s_change(1400, 800, T4, 100) > 0
