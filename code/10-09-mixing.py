"""Entropy generation when two water streams mix (a shower mixer), and a check that it is never negative."""
import math
import numpy as np

C = 4.186   # kJ/(kg K), liquid water treated as incompressible


def mix(m1, T1, m2, T2):
    """Adiabatic steady mixing: exit temperature (K) and entropy generation rate (kW/K) for flows in kg/s."""
    T3 = (m1 * T1 + m2 * T2) / (m1 + m2)
    Sgen = m1 * C * math.log(T3 / T1) + m2 * C * math.log(T3 / T2)
    return T3, Sgen


if __name__ == "__main__":
    # a shower: 0.08 kg/s hot at 60 C and 0.04 kg/s cold at 15 C
    T3, S = mix(0.08, 333.15, 0.04, 288.15)
    print(f"shower: mixed at {T3-273.15:.2f} C, entropy generated {S*1000:.4f} W/K")
    T0 = 288.15
    print(f"  lost work potential T0 x Sgen = {T0*S*1000:.2f} W")
    # the second law: never negative, zero only when T1 = T2
    rng = np.random.default_rng(3)
    for _ in range(100000):
        m1, m2 = rng.uniform(0.01, 5, 2); T1, T2 = rng.uniform(275, 370, 2)
        assert mix(m1, T1, m2, T2)[1] >= -1e-15
    assert abs(mix(1, 300, 2, 300)[1]) < 1e-15
    print("100 000 random mixings: S_gen >= 0 every time")
    # entropy is a property: heating 1 kg of water 15 -> 60 C reversibly or by stirring gives the same Delta S
    dS = C * math.log(333.15 / 288.15)
    print(f"heating 1 kg of water from 15 to 60 C: delta S = {dS:.5f} kJ/K, whatever the process")
    # but stirring (work turned to heat) generates all of it; reversible heating from a reservoir at each T generates none
    print(f"from a 60 C reservoir instead: S_gen = {dS - C*45/333.15:.5f} kJ/K")
    assert dS - C * 45 / 333.15 > 0
