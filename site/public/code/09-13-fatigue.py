"""Fatigue: fit Basquin's law to S-N data, correct for mean stress with Goodman, and sum damage with Miner's rule."""
import math
import numpy as np

SF, B = 1225.0, -0.095       # fatigue strength coefficient (MPa) and exponent, roughly AISI 1045 steel
SU = 725.0                  # ultimate tensile strength, MPa


def basquin_N(sa, sf=SF, b=B):
    """Cycles to failure at fully reversed amplitude sa: sa = sf (2N)^b."""
    return 0.5 * (sa / sf) ** (1 / b)


def goodman_equiv(sa, sm, su=SU):
    """Fully reversed amplitude that does the same damage as amplitude sa with mean sm."""
    return sa / (1 - sm / su)


def fit(N, S):
    """Least squares on log10 S = log10 sf + b log10(2N)."""
    X = np.log10(2 * np.asarray(N)); Y = np.log10(np.asarray(S))
    b, a = np.polyfit(X, Y, 1)
    return 10**a, b


if __name__ == "__main__":
    rng = np.random.default_rng(3)
    S = np.array([650, 580, 500, 440, 390, 350])
    N = np.array([basquin_N(s) for s in S]) * 10 ** rng.normal(0, 0.08, len(S))
    for s, n in zip(S, N):
        print(f"  {s} MPa: failed after {n:.3g} cycles")
    sf, b = fit(N, S)
    print(f"fit: sigma_f' = {sf:.0f} MPa, b = {b:.4f} (true 1225, -0.095)")
    assert abs(b - B) < 0.01 and abs(sf / SF - 1) < 0.15
    Se = SF * (2e6) ** B
    print(f"strength at 10^6 cycles: {Se:.1f} MPa (ratio to UTS {Se/SU:.2f})")
    # a shaft with mean 200 MPa and amplitude 250 MPa
    seq = goodman_equiv(250, 150)
    print(f"amplitude 250 with mean 150: Goodman equivalent {seq:.1f} MPa, life {basquin_N(seq):.3g} cycles (without mean: {basquin_N(250):.3g})")
    assert abs(250 / seq + 150 / SU - 1) < 1e-12
    # Miner: blocks of loading per day
    blocks = [(450, 20), (380, 300), (320, 3000)]
    D = sum(n / basquin_N(s) for s, n in blocks)
    print(f"daily damage {D:.4e}; Miner life {1/D:.0f} days ({1/D/365:.1f} years)")
    for s, n in blocks:
        print(f"  {s} MPa x {n}: {n/basquin_N(s)/D*100:.1f} % of the damage")
    # Basquin is exactly invertible
    assert abs(SF * (2 * basquin_N(333.0)) ** B - 333.0) < 1e-9
